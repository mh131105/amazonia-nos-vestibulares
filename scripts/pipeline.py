#!/usr/bin/env python3
"""Coleta e extração documental retomáveis, sem serviços nem chamadas de IA."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = Path('data/registry')
USER_AGENT = 'Amazoniavestibulares/0.1 (pesquisa documental; cache local)'
MAX_BYTES = 25 * 1024 * 1024
MIN_INTERVAL = 1.0


class SourceVersionChanged(ValueError):
    pass


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def read_jsonl(path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(''.join(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n' for row in rows), encoding='utf-8')
    temporary.replace(path)


def append_jsonl(path, row):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n')


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path):
    if not path.exists():
        return []
    with path.open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))


def checked_path(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Caminho fora do projeto')
    return path


def validate_expected(rows):
    ids = set()
    for row in rows:
        key = row['documento_id']
        if not re.fullmatch(r'[a-z0-9-]+', key) or key in ids:
            raise ValueError(f'ID inválido ou duplicado: {key}')
        ids.add(key)
        url = urllib.parse.urlsplit(row['url_origem'])
        if url.scheme != 'https' or not url.hostname or url.username or url.password:
            raise ValueError(f'URL de origem inválida: {key}')
        for field in ['aplicacao_id', 'instituicao_sigla', 'processo_id', 'tipo', 'publicador', 'fonte_url', 'condicoes_uso']:
            if not row.get(field):
                raise ValueError(f'Campo ausente: {key}/{field}')


def fetch_pdf(url, max_bytes=MAX_BYTES, timeout=30):
    request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT, 'Accept': 'application/pdf'})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        final = response.geturl()
        if urllib.parse.urlsplit(final).scheme != 'https':
            raise ValueError('Redirecionamento para conexão sem HTTPS')
        declared = response.headers.get('Content-Length')
        if declared and int(declared) > max_bytes:
            raise ValueError('Documento excede limite configurado')
        content = response.read(max_bytes + 1)
        if len(content) > max_bytes:
            raise ValueError('Documento excede limite configurado')
        if b'%PDF-' not in content[:1024]:
            raise ValueError('Resposta não é PDF; login, erro HTML ou outro formato')
        return content, final, response.headers.get_content_type()


def collect(root, *, only=None, attempts=3, interval=MIN_INTERVAL, update=False):
    if not 1 <= attempts <= 3 or interval < MIN_INTERVAL:
        raise ValueError('Usar 1–3 tentativas e intervalo mínimo de 1 segundo')
    expected = read_jsonl(root / REGISTRY / 'documentos-esperados.jsonl')
    validate_expected(expected)
    path = root / REGISTRY / 'documentos.jsonl'
    previous = read_jsonl(path)
    records = {row['documento_id']: row for row in previous}
    if len(records) != len(previous):
        raise ValueError('IDs duplicados no manifesto; investigar antes da coleta')
    if only and not only.issubset({r['documento_id'] for r in expected}):
        raise ValueError('Filtro contém documento não cadastrado')
    last_request = {}
    failed = 0
    for item in expected:
        key = item['documento_id']
        if only and key not in only:
            continue
        cached = records.get(key)
        if cached and cached.get('status') == 'coletado' and cached['url_origem'] == item['url_origem'] and not update:
            local = checked_path(root, cached['caminho_local'])
            if local.exists():
                if sha256(local) != cached['sha256']:
                    raise ValueError(f'Cache adulterado: {key}; investigar antes de substituir')
                print(f'cache {key}')
                continue
        host = urllib.parse.urlsplit(item['url_origem']).hostname
        record = {**item, 'coletado_em': None, 'url_final': None, 'sha256': None,
                  'tamanho_bytes': None, 'caminho_local': None, 'mime': None}
        for attempt in range(1, attempts + 1):
            time.sleep(max(0, interval - (time.monotonic() - last_request.get(host, 0))))
            last_request[host] = time.monotonic()
            try:
                content, final, mime = fetch_pdf(item['url_origem'])
                digest = hashlib.sha256(content).hexdigest()
                relative = Path('data/raw/documentos') / (digest + '.pdf')
                local = root / relative
                local.parent.mkdir(parents=True, exist_ok=True)
                if local.exists():
                    if sha256(local) != digest:
                        raise ValueError(f'Colisão ou corrupção no original {digest}')
                else:
                    with local.open('xb') as stream:
                        stream.write(content)
                if cached and cached.get('sha256') and digest != cached['sha256'] and not update:
                    raise SourceVersionChanged(f'URL retornou outra versão: esperado {cached["sha256"]}; recebido {digest}')
                record.update(status='coletado', coletado_em=now(), url_final=final, sha256=digest,
                              tamanho_bytes=len(content), caminho_local=str(relative), mime=mime, erro=None)
                break
            except SourceVersionChanged as error:
                append_jsonl(root / REGISTRY / 'aquisicoes.jsonl', {
                    'documento_id': key, 'em': now(), 'status': 'divergencia_versao_origem',
                    'url_origem': item['url_origem'], 'sha256_esperado': cached['sha256'],
                    'sha256_recebido': digest, 'caminho_nova_versao': str(relative), 'erro': str(error)})
                print(f'divergencia_versao_origem {key}; manifesto preservado', flush=True)
                failed += 1
                record = None
                break
            except (urllib.error.URLError, TimeoutError, OSError, ValueError) as error:
                record.update(status='falha_coleta', erro=f'{type(error).__name__}: {error}')
                append_jsonl(root / REGISTRY / 'aquisicoes.jsonl', {
                    'documento_id': key, 'em': now(), 'tentativa': attempt,
                    'url_origem': item['url_origem'], 'status': 'falha', 'erro': record['erro']})
                retry = (isinstance(error, urllib.error.HTTPError) and error.code in {429, 500, 502, 503, 504})
                retry = retry or (isinstance(error, (urllib.error.URLError, TimeoutError)) and not isinstance(error, urllib.error.HTTPError))
                if not retry or attempt == attempts:
                    break
                time.sleep(min(2 ** attempt, 8))
        if record is None:
            continue
        if record['status'] == 'coletado':
            append_jsonl(root / REGISTRY / 'aquisicoes.jsonl', {
                'documento_id': key, 'em': record['coletado_em'], 'status': 'coletado',
                'url_origem': record['url_origem'], 'url_final': record['url_final'],
                'sha256': record['sha256'], 'tamanho_bytes': record['tamanho_bytes'],
                'sha256_anterior': cached.get('sha256') if cached else None,
                'atualizacao_explicita': update})
        else:
            failed += 1
        records[key] = record
        write_jsonl(path, [records[k] for k in sorted(records)])
        print(f"{record['status']} {key}", flush=True)
    return failed


def parse_bbox(xml_path):
    tree = ET.parse(xml_path)
    namespace = {'x': 'http://www.w3.org/1999/xhtml'}
    result = []
    for number, page in enumerate(tree.findall('.//x:page', namespace), 1):
        lines = []
        for line in page.findall('.//x:line', namespace):
            words = []
            for word in line.findall('x:word', namespace):
                words.append({'texto': ''.join(word.itertext()),
                              'bbox': [float(word.attrib[k]) for k in ['xMin', 'yMin', 'xMax', 'yMax']]})
            lines.append({'texto': ' '.join(word['texto'] for word in words), 'palavras': words})
        result.append({'pagina': number, 'largura': float(page.attrib['width']),
                       'altura': float(page.attrib['height']), 'linhas': lines,
                       'texto_bruto': '\n'.join(line['texto'] for line in lines),
                       'palavras': sum(len(line['palavras']) for line in lines)})
    if not result:
        raise ValueError('Extração sem páginas')
    return result


def poppler_version():
    result = subprocess.run(['pdftotext', '-v'], text=True, capture_output=True, check=True)
    return (result.stdout + result.stderr).splitlines()[0]


def extract_pypdf(source):
    from pypdf import PdfReader
    pages = []
    for number, page in enumerate(PdfReader(source).pages, 1):
        text = page.extract_text(extraction_mode='layout') or ''
        pages.append({'pagina': number, 'largura': float(page.mediabox.width),
                      'altura': float(page.mediabox.height), 'linhas': [],
                      'texto_bruto': text, 'palavras': len(text.split())})
    if not pages:
        raise ValueError('Extração alternativa sem páginas')
    return pages


def extract(root):
    import pypdf
    records = read_jsonl(root / REGISTRY / 'documentos.jsonl')
    existing_path = root / REGISTRY / 'extracoes.jsonl'
    summaries = {r['documento_id']: r for r in read_jsonl(existing_path)}
    version = poppler_version() + f'; pypdf {pypdf.__version__}; esquema 3'
    for doc in records:
        if doc['status'] != 'coletado':
            continue
        source = checked_path(root, doc['caminho_local'])
        digest = sha256(source)
        if digest != doc['sha256']:
            raise ValueError(f"Original alterado: {doc['documento_id']}")
        directory = root / 'data/interim/extraido' / digest
        directory.mkdir(parents=True, exist_ok=True)
        metadata_path = directory / 'metadados.json'
        cache_ok = False
        if metadata_path.exists():
            metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
            cache_ok = metadata['ferramenta'] == version and all(
                (directory / name).exists() and sha256(directory / name) == recorded
                for name, recorded in metadata.get('artefatos_sha256', {}).items())
            cache_ok = cache_ok and bool(metadata.get('artefatos_sha256'))
        if not cache_ok:
            engine = 'poppler_bbox_layout'
            failure = None
            try:
                subprocess.run(['pdftotext', '-bbox-layout', '-enc', 'UTF-8', str(source), str(directory / 'poppler.xml')],
                               check=True, capture_output=True, timeout=60)
                subprocess.run(['pdftotext', '-layout', '-enc', 'UTF-8', str(source), str(directory / 'texto-layout.txt')],
                               check=True, capture_output=True, timeout=60)
                pages = parse_bbox(directory / 'poppler.xml')
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, ET.ParseError) as error:
                failure = f'{type(error).__name__}: retorno={getattr(error, "returncode", None)}'
                if getattr(error, 'stderr', None):
                    (directory / 'poppler-erros.txt').write_bytes(error.stderr)
                engine = 'pypdf_layout_alternativo'
                pages = extract_pypdf(source)
                (directory / 'texto-layout.txt').write_text('\f'.join(p['texto_bruto'] for p in pages), encoding='utf-8')
            for page in pages:
                page['documento_sha256'] = digest
            write_jsonl(directory / 'paginas.jsonl', pages)
            normalized = [{'pagina': page['pagina'], 'documento_sha256': digest,
                           'texto_normalizado': re.sub(r'[ \t]+', ' ', page['texto_bruto'])} for page in pages]
            write_jsonl(directory / 'normalizado.jsonl', normalized)
            pending_pages = [p['pagina'] for p in pages if p['palavras'] < 10]
            replacements = sum(p['texto_bruto'].count('\ufffd') for p in pages)
            extraction_status = 'texto_extraido_nao_revisado'
            if replacements:
                extraction_status = 'revisar_codificacao'
            if pending_pages:
                extraction_status = 'revisar_ocr_ou_pagina_visual'
            metadata = {'documento_sha256': digest, 'ferramenta': version,
                        'motor_utilizado': engine, 'falha_motor_primario': failure,
                        'artefato_poppler_valido': engine == 'poppler_bbox_layout',
                        'coordenadas_disponiveis': engine == 'poppler_bbox_layout',
                        'extraido_em': now(), 'paginas': len(pages),
                        'palavras': sum(p['palavras'] for p in pages),
                        'paginas_texto_insuficiente': pending_pages,
                        'caracteres_substituicao': replacements,
                        'status': extraction_status,
                        'artefatos_sha256': {name: sha256(directory / name) for name in [
                            'poppler.xml', 'texto-layout.txt', 'paginas.jsonl', 'normalizado.jsonl', 'poppler-erros.txt']
                            if (directory / name).exists()}}
            metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        summaries[doc['documento_id']] = {'documento_id': doc['documento_id'], **metadata,
                                        'caminho_metadados': str(metadata_path.relative_to(root))}
        write_jsonl(existing_path, [summaries[k] for k in sorted(summaries)])
        print(f"extraído {doc['documento_id']}: {metadata['paginas']} páginas", flush=True)
    write_jsonl(existing_path, [summaries[k] for k in sorted(summaries)])


def verify(root, *, require_local=True):
    expected = read_jsonl(root / REGISTRY / 'documentos-esperados.jsonl')
    validate_expected(expected)
    expected_by_id = {r['documento_id']: r for r in expected}
    records = read_jsonl(root / REGISTRY / 'documentos.jsonl')
    ids = [r['documento_id'] for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError('IDs duplicados no manifesto')
    for doc in records:
        if doc['documento_id'] not in expected_by_id:
            raise ValueError(f"Documento sem registro esperado: {doc['documento_id']}")
        if doc['status'] == 'coletado':
            if not re.fullmatch('[a-f0-9]{64}', doc['sha256']):
                raise ValueError('SHA-256 inválido')
            if require_local:
                path = checked_path(root, doc['caminho_local'])
                if not path.is_file() or sha256(path) != doc['sha256'] or path.stat().st_size != doc['tamanho_bytes']:
                    raise ValueError(f"Original ausente ou alterado: {doc['documento_id']}")
    by_id = {row['documento_id']: row for row in records}
    for extraction in read_jsonl(root / REGISTRY / 'extracoes.jsonl'):
        doc = by_id[extraction['documento_id']]
        if doc['sha256'] != extraction['documento_sha256']:
            raise ValueError('Extração associada a outro original')
        if require_local:
            directory = checked_path(root, extraction['caminho_metadados']).parent
            for name, digest in extraction['artefatos_sha256'].items():
                if sha256(directory / name) != digest:
                    raise ValueError(f'Extração alterada: {name}')
    verify_relations(root, by_id)
    print(f'Integridade documental: {len(records)} registros verificados; originais locais={require_local}.')


def unique_index(rows, key):
    indexed = {r[key]: r for r in rows}
    if len(indexed) != len(rows):
        raise ValueError(f'Chave duplicada: {key}')
    return indexed


def verify_relations(root, documents):
    institutions = unique_index(read_csv(root / REGISTRY / 'instituicoes.csv'), 'instituicao_id')
    processes = unique_index(read_csv(root / REGISTRY / 'processos.csv'), 'processo_id')
    applications = unique_index(read_csv(root / REGISTRY / 'aplicacoes.csv'), 'aplicacao_id')
    for process in processes.values():
        if process['instituicao_id'] not in institutions:
            raise ValueError('Processo sem instituição no inventário')
    for app in applications.values():
        if app['processo_id'] not in processes or app['instituicao_id'] not in institutions:
            raise ValueError('Aplicação sem processo ou instituição')
        if app['data_aplicacao'] and not '2017-01-01' <= app['data_aplicacao'] <= '2026-11-11':
            raise ValueError('Aplicação observada fora da janela')
        if app['situacao'] == 'futura_na_data_de_corte' and (app['data_aplicacao'] or app['data_prevista'] <= '2026-11-11'):
            raise ValueError('Aplicação futura com data inconsistente')
    questions = unique_index(read_csv(root / 'data/processed/questoes.csv'), 'ocorrencia_id')
    for question in questions.values():
        doc = documents.get(question['documento_id'])
        if not doc or question['documento_sha256'] != doc['sha256']:
            raise ValueError('Questão vinculada a original ausente ou de outra versão')
        if applications and question['aplicacao_id'] not in applications:
            raise ValueError('Questão sem aplicação')
        if question['aplicacao_id'] != doc['aplicacao_id'] or doc['tipo'] != 'prova':
            raise ValueError('Questão associada a documento incompatível')
        if question['disciplina'] not in {'historia', 'geografia'}:
            raise ValueError('Disciplina do piloto não reconhecida')
    keys = unique_index(read_csv(root / 'data/processed/gabaritos.csv'), 'ocorrencia_id')
    for key in keys.values():
        question = questions.get(key['ocorrencia_id'])
        doc = documents.get(key['documento_id'])
        if not question or not doc or doc['sha256'] != key['documento_sha256']:
            raise ValueError('Gabarito sem questão ou original correspondente')
        if doc['aplicacao_id'] != question['aplicacao_id'] or key['numero_questao'] != question['numero_questao']:
            raise ValueError('Gabarito de outra aplicação ou número')
        if key['estado_oficial'] == 'anulada' and key['alternativa_oficial']:
            raise ValueError('Questão anulada com alternativa preenchida')
    for annotation in read_csv(root / 'data/annotation/rotulos-humanos.csv'):
        question = questions.get(annotation['ocorrencia_id'])
        if not question or annotation['documento_sha256'] != question['documento_sha256']:
            raise ValueError('Fila de revisão refere-se a ocorrência ausente ou outra versão')


def make_report(root):
    expected = read_jsonl(root / REGISTRY / 'documentos-esperados.jsonl')
    validate_expected(expected)
    collected = {r['documento_id']: r for r in read_jsonl(root / REGISTRY / 'documentos.jsonl')}
    all_extracts = {r['documento_id']: r for r in read_jsonl(root / REGISTRY / 'extracoes.jsonl')}
    extracts = {key: row for key, row in all_extracts.items()
                if collected.get(key, {}).get('status') == 'coletado'
                and collected[key].get('sha256') == row.get('documento_sha256')}
    rows = []
    for item in expected:
        doc = collected.get(item['documento_id'], {})
        ext = extracts.get(item['documento_id'], {})
        rows.append({'documento_id': item['documento_id'], 'instituicao': item['instituicao_sigla'],
                     'aplicacao_id': item['aplicacao_id'], 'tipo': item['tipo'],
                     'status_coleta': doc.get('status', 'nao_tentado'),
                     'status_extracao': ext.get('status', 'desatualizada' if item['documento_id'] in all_extracts else 'nao_extraido'),
                     'paginas': ext.get('paginas'), 'palavras': ext.get('palavras'),
                     'sha256': doc.get('sha256'), 'url_origem': item['url_origem']})
    fields = ['documento_id', 'instituicao', 'aplicacao_id', 'tipo', 'status_coleta', 'status_extracao',
              'paginas', 'palavras', 'sha256', 'url_origem']
    write_csv(root / 'reports/tabelas/cobertura-documentos.csv', rows, fields)
    count = sum(row['status_coleta'] == 'coletado' for row in rows)
    extracted_count = sum(row['documento_id'] in extracts for row in rows)
    lines = ['# Cobertura documental inicial', '',
             f'Documentos previstos no piloto: **{len(rows)}**. Coletados: **{count}**. Com extração registrada: **{extracted_count}**.', '',
             'Essas contagens descrevem somente os documentos selecionados para testar o procedimento. Não medem cobertura nacional, edições esperadas na década, incidência regional ou dificuldade das questões.', '',
             '| Documento | Tipo | Coleta | Páginas | Extração |',
             '| --- | --- | --- | --- | --- |']
    for row in rows:
        lines.append(f"| {row['documento_id']} | {row['tipo']} | {row['status_coleta']} | {row['paginas'] if row['paginas'] is not None else '—'} | {row['status_extracao']} |")
    lines.extend(['', 'A tabela CSV inclui os URLs e os hashes dos originais. `texto_extraido_nao_revisado` não significa seção disciplinar completa: a conferência de itens, imagens, gabaritos e retificações é uma etapa própria.', '',
                  'Páginas com menos de dez palavras são sinalizadas para inspeção visual/OCR; podem ser páginas de imagens ou em branco. O sinalizador não diagnostica sozinho um PDF digitalizado.', '',
                  'Não há referência humana anotada nem avaliação da IA nesta versão. Não foram executadas chamadas pagas de IA.', '',
                  'Reprodução: `uv run python scripts/pipeline.py relatorio`. A geração usa somente os registros locais; não requer rede ou IA.'])
    report = root / 'reports/cobertura-inicial.md'
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    study_report = make_study_report(root)
    inventory = root / 'data/registry/instituicoes.csv'
    inputs = [root / REGISTRY / name for name in ['documentos-esperados.jsonl', 'documentos.jsonl', 'extracoes.jsonl']]
    if inventory.exists():
        inputs.append(inventory)
    inputs.extend(p for p in [root / REGISTRY / name for name in [
        'processos.csv', 'aplicacoes.csv', 'evidencias-programa.csv', 'cobertura-anual.csv',
        'regras-segmentacao.json', 'segmentacoes.jsonl']] if p.exists())
    inputs.extend(p for p in [root / 'data/processed/questoes.csv', root / 'data/processed/gabaritos.csv',
                              root / 'data/annotation/rotulos-humanos.csv'] if p.exists())
    inputs.extend(sorted((root / 'scripts').glob('*.py')))
    inputs.extend(p for p in [root / name for name in ['.python-version', 'pyproject.toml', 'uv.lock',
                         'docs/protocolo.md', 'docs/decisoes.md', 'data/registry/triagem_ufam.json',
                         'data/registry/triagem_demais.json', 'data/registry/fontes_inventario.json']] if p.exists())
    outputs = [report, root / 'reports/tabelas/cobertura-documentos.csv']
    if study_report:
        outputs.append(study_report)
    snapshot = {'versao': '0.1.0', 'tipo': 'cobertura_piloto_nao_corpus_analitico',
                'data_corte_aplicacoes': '2026-11-11', 'fuso_corte': 'America/Manaus',
                'entradas_sha256': {str(p.relative_to(root)): sha256(p) for p in inputs if p.exists()},
                'saidas_sha256': {str(p.relative_to(root)): sha256(p) for p in outputs}}
    (root / 'reports/manifesto-cobertura.json').write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Relatório: {count}/{len(rows)} documentos coletados; {extracted_count} extraídos.')


def make_study_report(root):
    institutions = read_csv(root / REGISTRY / 'instituicoes.csv')
    processes = read_csv(root / REGISTRY / 'processos.csv')
    if not institutions or not processes:
        return None
    apps = {r['aplicacao_id']: r for r in read_csv(root / REGISTRY / 'aplicacoes.csv')}
    questions = read_csv(root / 'data/processed/questoes.csv')
    verify_relations(root, {r['documento_id']: r for r in read_jsonl(root / REGISTRY / 'documentos.jsonl')})
    keys = read_csv(root / 'data/processed/gabaritos.csv')
    annotations = read_csv(root / 'data/annotation/rotulos-humanos.csv')
    human_labels = [r for r in annotations if r.get('anotador') and r.get('anotado_em') and r.get('regionalidade')]
    by_app = defaultdict(list)
    for question in questions:
        if question['aplicacao_id'] not in apps:
            raise ValueError('Questão sem aplicação identificada')
        by_app[question['aplicacao_id']].append(question)
    regions = Counter(r['regiao'] for r in institutions)
    classes = Counter(r['disciplina'] for r in questions)
    complete = sum(r['alternativas_textuais_completas'] == 'True' for r in questions)
    lines = ['# História e Geografia da Amazônia nos vestibulares públicos', '',
             'Relatório de implantação documental — versão 0.1.0. Referência: 11/11/2026, Manaus.', '',
             '## Resumo', '',
             f'O inventário inicial reúne **{len(institutions)} IES da rede pública no Censo 2024**. A triagem inicial registra **{len(processes)} processos** de **{len({r["instituicao_id"] for r in processes})} IES**. O piloto segmentou **{len(questions)} ocorrências** em **{len(by_app)} cadernos**, sendo **{classes.get("historia", 0)} de História** e **{classes.get("geografia", 0)} de Geografia**.', '',
             'Essas quantidades descrevem o trabalho documental e os itens extraídos. Ainda não respondem qual é a incidência regional, o que mudou nas provas ou como a IA se compara a humanos. O estudo e o inventário histórico permanecem em andamento.', '',
             '## Pergunta e seleção', '',
             'O estudo investiga a previsão nos programas e a cobrança substantiva de conhecimentos históricos e geográficos da Amazônia. As disciplinas usam o mesmo procedimento e denominadores próprios. A motivação sobre procura e dificuldade é uma hipótese; os documentos não demonstram demanda comercial nem dificuldade empírica.', '',
             'A fotografia nacional de 2024 não substitui o histórico de 2017–2026. Ela inclui instituições de todas as regiões, sem filtro geográfico:', '',
             '| Região da sede | IES públicas em 2024 |', '| --- | ---: |']
    lines.extend(f'| {name} | {count} |' for name, count in sorted(regions.items()))
    lines.extend(['', 'Fonte: [microdados oficiais do Inep](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-da-educacao-superior). `data/registry/fontes_inventario.json` identifica membro, coleta e hashes. As 28 instituições de categoria Especial foram conservadas pelo campo de rede pública e exigem verificação da esfera administrativa.', '',
                  '## Evidências iniciais de programa', '',
                  'O PSC/UFAM atende ao limiar documental de três anos no processo para cada disciplina, pelas evidências atualmente localizadas. História aparece em 2019, 2024, 2025 e 2026; Geografia em 2024, 2025 e 2026. O terceiro ano de Geografia inclui a etapa 2: isso não demonstra três anos de previsão na etapa 3. Fontes, páginas, retificações e revisão pendente estão nas tabelas de processos e evidências.', '',
                  'Na UFRR, há dois anos de programa regional verificados (aplicações 2024 e 2025): caso auxiliar para o limiar de dois anos, ainda candidato ao corpus principal. UERR possui evidência em 2022. UEA apresenta pendências de calendário e acesso. As leituras iniciais de UEMA e UEPG não confirmaram previsão amazônica substantiva nas edições examinadas; a UNEMAT exige autenticação documental. Nenhum desses achados exclui automaticamente uma instituição inteira ou toda a década.', '',
                  'Essas decisões são triagem assistida por IA, com revisão humana pendente. `evidencias-programa.csv` contém pistas documentais, não o inventário integral de tópicos nem vínculos de cada questão ao programa.', '',
                  '## Acervo e integridade', '',
                  '| Aplicação do piloto | Data efetiva registrada | Etapa | História | Geografia |',
                  '| --- | --- | --- | ---: | ---: |'])
    for app_id, items in sorted(by_app.items(), key=lambda pair: (apps[pair[0]]['data_aplicacao'], pair[0])):
        app = apps[app_id]
        counts = Counter(r['disciplina'] for r in items)
        lines.append(f'| {app_id} | {app["data_aplicacao"]} | {app["etapa"]} | {counts.get("historia", 0)} | {counts.get("geografia", 0)} |')
    lines.extend(['',
                  f'**{complete}/{len(questions)}** itens apresentam a estrutura textual A–E. Os demais exigem revisão de alternativas gráficas ou segmentação. Essa conferência estrutural não garante integridade de enunciados, imagens, legendas ou textos compartilhados. Todos os itens do piloto mantêm `apto_denominador_validado=false`.', '',
                  f'Registros de gabarito vinculados: **{len(keys)}**. A extração de resposta oficial não é validação humana do item. Anulações permanecem identificadas; não são descartadas da cobrança aplicada.', '',
                  'Originais são preservados por SHA-256. Extrações bruta e normalizada ficam em camadas separadas, com página e coordenadas quando disponíveis. Falhas reais do Poppler acionam pypdf e são registradas; há caracteres danificados em editais recentes e páginas visuais sinalizadas. Os materiais experimentados têm camada digital; processamento de documentos escaneados e OCR ainda exige validação própria.', '',
                  'O edital PSC2027 E3 registra aplicação futura em 29/11/2026, depois do corte. Não entra no corpus de questões desta versão. Ausência de caderno em um processo não vira zero questões. A grade `cobertura-anual.csv` registra investigação pendente, sem afirmar que houve prova em cada célula.', '',
                  'Na UFRR, PI e PSS-E3 compartilham caderno, mas o subconjunto para pontuação PSS é diferente. O piloto representa PI e não duplica o mesmo documento como outra observação agregada.', '',
                  '## Comparação temporal planejada', '',
                  '| Estrato com questões segmentadas | 2017–2021: cadernos | 2022–2023: cadernos | 2024: cadernos | 2025–2026: cadernos | Contraste de incidência |',
                  '| --- | ---: | ---: | ---: | ---: | --- |'])
    strata = defaultdict(Counter)
    for app_id in by_app:
        app = apps[app_id]
        strata[(app['instituicao_sigla'], app['processo_id'], app['etapa'])][app['periodo_calendario']] += 1
    for (sigla, process, stage), counts in sorted(strata.items()):
        values = [str(counts[b]) if counts[b] else 'Sem caderno segmentado' for b in ['2017-2021', '2022-2023', '2024', '2025-2026']]
        lines.append(f'| {sigla} / {process} / {stage} | ' + ' | '.join(values) + ' | Não calculado |')
    lines.extend(['',
                  'O contraste obrigatório será 2017–2021 versus 2024–2026, com 2022–2023 fora desse contraste e posterior separado em 2024 e 2025–2026. O piloto UFAM E3 contém cadernos dos dois lados, mas ainda não tem classificações regionais e denominadores validados. Os outros estratos não simulam uma comparação pareada inexistente. Não foi estimado efeito causal da reforma.', '',
                  'Sensibilidades pendentes: limiar de dois anos, exclusão de 2026 (2017–2025, nove anos), painel comparável versus acervo total, itens interdisciplinares e versão válida para pontuação. Ainda não há indicador final a submeter a essas sensibilidades.', '',
                  '## Avaliação da IA', '',
                  f'Linhas com autor, data e regionalidade preenchidos na fila: **{len(human_labels)}**. O preenchimento da fila é uma etapa de trabalho e ainda requer auditoria; linhas vazias não são anotações. Não existe teste humano congelado, baseline avaliado ou métricas de extração/classificação nesta versão. F1, precisão, revocação e custo comparativo permanecem indisponíveis.', '',
                  'As investigações e inspeções do Codex foram identificadas como assistência de IA. O pipeline não fez chamadas pagas de API de modelos; custos da assistência no aplicativo não foram quantificados. A metodologia futura está em `docs/manual-anotacao.md`.', '',
                  '## Limitações e reuso', '',
                  'Faltam reconciliação institucional histórica, triagem da maior parte das IES, cobertura da década, OCR validado, revisão dos itens, grupos de equivalência, tópicos completos, classificação, avaliação humana e análise substantiva. Não há exportação liberada para o banco educacional. Direitos dos originais e imagens ainda precisam ser examinados por documento.', '',
                  'Os metadados e referências estão preparados para continuidade. Originais, imagens e enunciados permanecem locais enquanto não houver condição de redistribuição demonstrada; o Git conserva código, metadados e relatório.', '',
                  '## Reprodução', '',
                  'Use a sequência do README. `uv run python scripts/pipeline.py relatorio` reconstrói este relatório sem rede ou IA a partir dos registros versionados. `reports/manifesto-cobertura.json` registra hashes das entradas e saídas. A obtenção e nova extração dos originais são modos separados, dependentes da disponibilidade das fontes oficiais.', '',
                  'Próxima entrega: expandir o inventário histórico e as aplicações dos processos; revisar os itens do piloto e formar referência humana antes de avaliar ou ajustar o classificador.'])
    path = root / 'reports/relatorio-inicial.md'
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('etapa', choices=['coletar', 'extrair', 'verificar', 'relatorio'])
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--somente', nargs='*', help='IDs de documentos a coletar')
    parser.add_argument('--somente-metadados', action='store_true', help='Verificar manifesto sem exigir acervo local')
    parser.add_argument('--atualizar', action='store_true', help='Consultar fonte novamente e aceitar nova versão preservando histórico')
    args = parser.parse_args()
    if args.etapa == 'coletar':
        return int(collect(args.root, only=set(args.somente) if args.somente else None, update=args.atualizar) > 0)
    if args.etapa == 'extrair':
        extract(args.root)
    elif args.etapa == 'verificar':
        verify(args.root, require_local=not args.somente_metadados)
    else:
        make_report(args.root)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, subprocess.CalledProcessError, ET.ParseError) as error:
        print(f'ERRO: {error}', file=sys.stderr)
        sys.exit(2)
