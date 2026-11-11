#!/usr/bin/env python3
"""Vincula respostas publicadas aos itens do piloto, sem resolver questões.

Lê publicações oficiais cadastradas como gabaritos definitivos e extrações locais
com hash conferido. A finalidade documental pode permanecer pendente na auditoria;
isso não modifica as respostas publicadas. Regras: tabelas UFAM PSC e a linha 37–54
do Anexo I PI/E3 da UFRR. Outra disposição permanece não identificada.

O campo ocorrencia_id referencia a ocorrência estável de questoes.csv.
Revisão humana e conferência de versões de caderno continuam pendentes.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.4.0'
# Faixas do piloto com disciplina conhecida. Línguas têm colunas diferentes e
# não recebem uma resposta por conveniência usando a primeira coluna.
UFAM_SUPPORTED = {1: set(range(17, 29)), 2: set(range(17, 29)), 3: set(range(19, 31))}
# Estes quatro arquivos estão indicados como definitivos no índice oficial
# legado; PSC2019 E2 tem finalidade pendente na auditoria C3. O cabeçalho nomeia
# o projeto de ingresso, que difere da edição nas
# etapas 1 e 2. Só a igualdade dos bytes conhecidos autoriza essa leitura.
UFAM_LEGACY_VERIFIED = {
    (2018, 3): {'projeto': 2018, 'sha256': '7480b62980e531574ae8276a4ea1068b9bd1b8534044a90085d08e40da923a23'},
    (2019, 1): {'projeto': 2021, 'sha256': '2d7bf8dfdaf7cd5035038b804e53887252f981f598a3093cd05f5621a98c02db'},
    (2019, 2): {'projeto': 2020, 'sha256': 'c4e2b1116803a1d6896c3e8ee305a93a50601a3897a800d33b7b1e32f2b7c62d'},
    (2019, 3): {'projeto': 2019, 'sha256': '72902781ecb6d5675e93ecf70de7fe6125d51562aadfac2c014dd8cbc33dcf41'},
}
FUVEST_CONTINUACOES_VERIFICADAS = {
    # As duas páginas repetem código e título e continuam a mesma orientação.
    # Conferência visual pelo Codex; não é revisão humana do item.
    (2024, 'ac5d38390febca1415a61caf3e3e291115662fd9dfb6417c81d857b9e6ccffad'): {'G05': [31, 32]},
}
FIELDS = ['ocorrencia_id', 'aplicacao_id', 'numero_questao',
          'disciplina', 'tipo_resposta', 'alternativa_oficial', 'estado_oficial',
          'marcador_oficial', 'documento_id', 'documento_sha256', 'finalidade_documental', 'pagina_pdf', 'paginas_pdf',
          'secao_gabarito', 'url_origem', 'origem', 'revisao_humana',
          'vinculo_versao_caderno', 'responsavel_extracao', 'versao_extrator',
          'problemas']


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()
            if line.strip()]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def documentary_purpose(document, findings):
    """Anexa a conclusão auditada apenas à identidade e aos bytes conferidos."""
    matches = [row for row in findings
               if row['documento_id'] == document['documento_id']
               and row['sha256_arquivo'] == document['sha256']]
    if len(matches) > 1:
        raise ValueError('Finalidade documental com auditoria duplicada')
    return matches[0]['resultado'] if matches else None


def checked_path(root, value):
    result = (root / value).resolve()
    if not result.is_relative_to(root):
        raise ValueError(f'Caminho fora do projeto: {value}')
    return result


def normalized(text):
    """Remove acentos e expande ligaduras sem mudar linhas ou ordem da tabela."""
    return ''.join(char for char in unicodedata.normalize('NFKD', text)
                   if not unicodedata.combining(char)).upper()


def answer(token, page, section):
    if token in {'ANULADA', 'NULA', 'N'}:
        alternative, state = None, 'anulada'
    elif token in set('ABCDE'):
        alternative, state = token, 'alternativa_publicada'
    else:
        raise ValueError(f'Marcador não reconhecido: {token}')
    return {'alternativa_oficial': alternative, 'estado_oficial': state,
            'marcador_oficial': token, 'pagina_pdf': page,
            'secao_gabarito': section}


def parse_ufam(pages, year, stage, requested, *, source_sha256=None):
    """Restringe os números ao alvo para não confundir opções de língua."""
    legacy = UFAM_LEGACY_VERIFIED.get((year, stage))
    legacy_verified = legacy is not None and source_sha256 == legacy['sha256']
    eligible = []
    for page, original in pages:
        text = normalized(original)
        stage_match = re.search(rf'\b{stage}A\s+ETAPA\b', text)
        current_header = ('GABARITO DEFINITIVO' in text
                          and re.search(rf'\bPSC\s*{year}\b', text))
        project_header = (legacy_verified and 'GABARITO' in text
                          and re.search(r'\bPSC\b', text)
                          and re.search(rf'\bPROJETO\s*{legacy["projeto"]}\b', text))
        if stage_match and (current_header or project_header):
            eligible.append((page, text))
    if len(eligible) != 1:
        return {}, 'pagina_ufam_ano_etapa_nao_unica'
    page, text = eligible[0]
    candidates = defaultdict(list)
    section = f'PSC {year}, {stage}ª Etapa'
    if legacy_verified:
        section += f'; cabeçalho Projeto {legacy["projeto"]}, vínculo ao índice oficial conferido por hash'
    for number, token in re.findall(r'(?<!\d)(\d{1,2})\.?\s*(ANULADA|ANULAR|NULA|[A-E])\b', text):
        number = int(number)
        if number in requested and number in UFAM_SUPPORTED.get(stage, set()):
            result = answer('ANULADA' if token == 'ANULAR' else token, page, section)
            result['marcador_oficial'] = token
            candidates[number].append(result)
    result = {number: entries[0] for number, entries in candidates.items()
              if len(entries) == 1 and 1 <= number <= 54}
    problem = '' if set(result) == set(requested) else 'numero_ausente_ambiguo_ou_fora_da_faixa'
    return result, problem


def parse_ufrr_pi(pages, year, requested):
    """Exige o Anexo PI/E3 e números 37–54; E1/E2 nunca são alternativas."""
    eligible = [(page, normalized(text)) for page, text in pages
                if 'GABARITO OFICIAL DA PROVA INTEGRAL (PI)' in normalized(text)
                and 'SERIADO ETAPA 3 (E3)' in normalized(text)
                and re.search(rf'VESTIBULAR\s+UFRR\s+{year}\b', normalized(text))]
    if len(eligible) != 1:
        return {}, 'anexo_ufrr_pi_e3_nao_unico'
    page, text = eligible[0]
    pattern = (r'^[ \t]*DISCIPLINA[ \t]+GEOGRAFIA[ \t]+HISTORIA[ \t]*\r?\n'
               r'[ \t]*QUESTAO[ \t]+([0-9 \t]+)\r?\n'
               r'[ \t]*GABARITO[ \t]+([A-EN \t]+)[ \t]*$')
    matches = re.findall(pattern, text, re.MULTILINE)
    if len(matches) != 1:
        return {}, 'linha_geografia_historia_nao_unica'
    number_text, token_text = matches[0]
    numbers = [int(value) for value in number_text.split()]
    tokens = token_text.split()
    if numbers != list(range(37, 55)) or len(tokens) != len(numbers):
        return {}, 'faixa_ou_quantidade_de_respostas_incompativel'
    if any(token not in set('ABCDEN') for token in tokens):
        return {}, 'marcador_oficial_desconhecido'
    found = {number: answer(token, page, 'Anexo I, Prova Integral (PI)/E3')
             for number, token in zip(numbers, tokens) if number in requested}
    problem = '' if set(found) == set(requested) else 'numero_fora_da_faixa_suportada'
    return found, problem


def load_pages(root, document, extraction):
    """Recusa originais alterados e extrações antigas antes de vincular respostas."""
    if not extraction or extraction.get('documento_sha256') != document['sha256']:
        raise ValueError(f'Extração ausente ou de outro original: {document["documento_id"]}')
    original = checked_path(root, document['caminho_local'])
    if sha256(original) != document['sha256']:
        raise ValueError(f'Original alterado: {document["documento_id"]}')
    directory = checked_path(root, extraction['caminho_metadados']).parent
    layout = directory / 'texto-layout.txt'
    expected_hash = extraction.get('artefatos_sha256', {}).get('texto-layout.txt')
    if not expected_hash or sha256(layout) != expected_hash:
        raise ValueError(f'Texto de layout alterado ou não registrado: {document["documento_id"]}')
    parts = layout.read_text(encoding='utf-8').split('\f')
    while parts and not parts[-1].strip():
        parts.pop()
    if len(parts) != extraction['paginas']:
        raise ValueError(f'Paginação incompatível com extração: {document["documento_id"]}')
    return list(enumerate(parts, start=1))


def parse_uerr(pages, year, requested):
    """Lê a matriz Cebraspe verificada, sem escolher uma língua estrangeira."""
    supported = {
        2025: ('066_UERR_001_01', set(range(55, 73))),
        2026: ('225_UERR_001_01', set(range(19, 37))),
    }
    if year not in supported or not requested.issubset(supported[year][1]):
        return {}, 'ano_ou_faixa_uerr_sem_regra_verificada'
    code, _ = supported[year]
    eligible = [(page, normalized(text)) for page, text in pages
                if 'GABARITOS OFICIAIS DEFINITIVOS' in normalized(text)
                and code in normalized(text)
                and re.search(rf'PROCESSO\s+SELETIVO\s+VESTIBULAR\s*(?:[-–—]\s*)?{year}\b', normalized(text))]
    if len(eligible) != 1:
        return {}, 'gabarito_uerr_ano_versao_nao_unico'
    page, text = eligible[0]
    pattern = (r'^[ \t]*QUESTAO[ \t]+([0-9 \t]+)\r?\n'
               r'[ \t]*GABARITO[ \t]+([A-EX0 \t]+)[ \t]*$')
    pairs = re.findall(pattern, text, re.MULTILINE)
    expected_rows = [list(range(1, 19)) + [10, 11],
                     list(range(12, 32)), list(range(32, 52)),
                     list(range(52, 72)), [72] + [0] * 19]
    if len(pairs) != len(expected_rows):
        return {}, 'matriz_uerr_linhas_ausentes_ou_ambiguas'
    found = {}
    for (number_text, token_text), expected in zip(pairs, expected_rows):
        numbers, tokens = [int(value) for value in number_text.split()], token_text.split()
        if numbers != expected or len(tokens) != len(numbers):
            return {}, 'matriz_uerr_numeracao_ou_quantidade_incompativel'
        for number, token in zip(numbers, tokens):
            if number == 0 and token != '0':
                return {}, 'matriz_uerr_preenchimento_zero_inconsistente'
            if number not in requested:
                continue
            if token not in set('ABCDEX') or number in found:
                return {}, 'numero_uerr_ausente_ambiguo_ou_resposta_desconhecida'
            result = answer('ANULADA' if token == 'X' else token, page, f'Gabarito definitivo UERR {year}, {code}')
            result['marcador_oficial'] = token
            found[number] = result
    problem = '' if set(found) == requested else 'numero_uerr_ausente_ou_ambiguo'
    return found, problem


def question_number(value):
    return int(value) if str(value).isdigit() else str(value)


def parse_fuvest_discursiva(pages, year, requested, *, source_sha256=None):
    """Localiza a orientação oficial por código; não converte exemplo em letra."""
    header = ' '.join(normalized(text) for _, text in pages[:3])
    header = ' '.join(header.split())
    if (not re.search(rf'FUVEST\s+{year}\b', header) or '2A FASE' not in header
            or not any(title in header for title in ['RESPOSTAS ESPERADAS', 'ABORDAGENS ESPERADAS'])):
        return {}, 'orientacoes_fuvest_ano_fase_nao_confirmados'
    candidates = defaultdict(list)
    for page, original in pages:
        for line in normalized(original).splitlines():
            match = re.match(r'^\s*([GH]\d{2})(?:\s|$)', line)
            code = match.group(1) if match else None
            if code in requested:
                candidates[code].append(page)
    found = {}
    continuations = FUVEST_CONTINUACOES_VERIFICADAS.get((year, source_sha256), {})
    for code, locations in candidates.items():
        if len(locations) == 1 or locations == continuations.get(code):
            found[code] = {'estado_oficial': 'orientacao_discursiva_publicada',
                           'pagina_pdf': locations[0], 'paginas_pdf': locations, 'marcador_oficial': code,
                           'secao_gabarito': f'FUVEST {year}, 2ª fase, orientação para {code}; não esgota respostas possíveis'}
    return found, 'codigo_discursivo_ausente_ou_nao_unico'


def link(root=ROOT):
    root = Path(root).resolve()
    with (root / 'data/processed/questoes.csv').open(encoding='utf-8', newline='') as stream:
        questions = list(csv.DictReader(stream))
    ids = [row['ocorrencia_id'] for row in questions]
    if len(ids) != len(set(ids)):
        raise ValueError('IDs de ocorrência duplicados em questoes.csv')
    documents = read_jsonl(root / 'data/registry/documentos.jsonl')
    latest_findings = {}
    for audit_path in [root / f'data/registry/auditoria-datas-c{cycle}.json' for cycle in (3, 4)]:
        if audit_path.exists():
            for finding in json.loads(audit_path.read_text(encoding='utf-8')).get('auditoria_gabaritos', []):
                latest_findings[finding['documento_id']] = finding
    findings = list(latest_findings.values())
    extracts = {row['documento_id']: row for row in read_jsonl(root / 'data/registry/extracoes.jsonl')}
    by_application = defaultdict(list)
    for document in documents:
        if (document.get('status') == 'coletado' and document.get('origem_oficial') is True
                and document.get('tipo') in {'gabarito_definitivo', 'respostas_esperadas'}):
            by_application[document['aplicacao_id']].append(document)
    groups = defaultdict(list)
    for question in questions:
        groups[question['aplicacao_id']].append(question)
    rows = []
    for application_id, items in sorted(groups.items()):
        available = by_application.get(application_id, [])
        source = available[0] if len(available) == 1 else None
        found, problem = {}, 'gabarito_definitivo_oficial_ausente_ou_nao_unico'
        if source:
            pages = load_pages(root, source, extracts.get(source['documento_id']))
            requested = {question_number(item['numero_questao']) for item in items}
            ufam = re.fullmatch(r'ufam-psc(\d{4})-e([123])', application_id)
            ufrr = re.fullmatch(r'ufrr-vestibular(\d{4})-pi', application_id)
            uerr = re.fullmatch(r'uerr-vestibular(\d{4})', application_id)
            fuvest = re.fullmatch(r'usp-fuvest(\d{4})-f2-d[23]', application_id)
            if ufam:
                found, problem = parse_ufam(pages, *map(int, ufam.groups()), requested,
                                            source_sha256=source['sha256'])
            elif ufrr:
                found, problem = parse_ufrr_pi(pages, int(ufrr.group(1)), requested)
            elif uerr:
                found, problem = parse_uerr(pages, int(uerr.group(1)), requested)
            elif (fuvest and source['tipo'] == 'respostas_esperadas'
                  and all(item.get('tipo_resposta') == 'discursiva' for item in items)):
                found, problem = parse_fuvest_discursiva(pages, int(fuvest.group(1)), requested,
                                                         source_sha256=source['sha256'])
            else:
                problem = 'layout_sem_regra_verificada'
        for item in sorted(items, key=lambda row: str(row['numero_questao']).zfill(3)):
            number = question_number(item['numero_questao'])
            result = found.get(number, {})
            row = {'ocorrencia_id': item['ocorrencia_id'],
                   'aplicacao_id': application_id, 'numero_questao': number,
                   'disciplina': item['disciplina'],
                   'tipo_resposta': item.get('tipo_resposta', 'objetiva_multipla_escolha'),
                   'alternativa_oficial': result.get('alternativa_oficial'),
                   'estado_oficial': result.get('estado_oficial', 'nao_identificado'),
                   'marcador_oficial': result.get('marcador_oficial'),
                   'documento_id': source['documento_id'] if source else None,
                   'documento_sha256': source['sha256'] if source else None,
                   'finalidade_documental': documentary_purpose(source, findings) if source else None,
                   'pagina_pdf': result.get('pagina_pdf'), 'secao_gabarito': result.get('secao_gabarito'),
                   'paginas_pdf': json.dumps(result.get('paginas_pdf', [result['pagina_pdf']] if result.get('pagina_pdf') else [])),
                   'url_origem': source['url_origem'] if source else None,
                   'origem': 'extracao_gabarito_oficial', 'revisao_humana': 'pendente',
                   'vinculo_versao_caderno': 'conferencia_humana_pendente_sem_reordenacao_inferida',
                   'responsavel_extracao': 'Codex', 'versao_extrator': VERSION,
                   'problemas': json.dumps([] if result else [problem], ensure_ascii=False)}
            rows.append(row)
    output = root / 'data/processed/gabaritos.csv'
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix('.csv.tmp')
    with temporary.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(output)
    counts = Counter(row['estado_oficial'] for row in rows)
    print(f'Gabaritos: {len(rows)} ocorrências; {dict(sorted(counts.items()))}. Revisão humana pendente.')
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    link(parser.parse_args().root)
