#!/usr/bin/env python3
"""Importa fotografias anuais de IES públicas sem substituir o cadastro de 2024.

Lê somente os membros institucionais dos ZIPs oficiais e reaproveita o coletor
com cache e hashes. Reconciliar o mesmo código Inep não prova fusão, criação ou
extinção: a saída registra apenas mudanças observadas nos cadastros.
"""

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from xml.etree import ElementTree
import zipfile
from datetime import datetime
from zoneinfo import ZoneInfo

if __package__:
    from . import inventario_ies as base
else:
    import inventario_ies as base

ROOT = base.ROOT
VERSION = '0.1.0'


def read_json(path, default):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else default


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def packed(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def dictionary_evidence(source):
    """Confere a planilha cadastro_ies; termos de cursos não validam a IES."""
    dictionary = next(item for item in source['arquivos'] if item['tipo'] == 'dicionario')
    ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(ROOT / dictionary['caminho_local']) as book:
        strings = [''.join(node.itertext()) for node in ElementTree.fromstring(
            book.read('xl/sharedStrings.xml')).findall('s:si', ns)]
        workbook = ElementTree.fromstring(book.read('xl/workbook.xml'))
        sheets = [s for s in workbook.findall('s:sheets/s:sheet', ns) if s.attrib['name'].lower() == 'cadastro_ies']
        if len(sheets) != 1:
            raise ValueError('Planilha cadastro_ies não identificada de forma única no dicionário')
        relationship_id = sheets[0].attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
        relationships = ElementTree.fromstring(book.read('xl/_rels/workbook.xml.rels'))
        target = next(r.attrib['Target'] for r in relationships if r.attrib['Id'] == relationship_id)
        member = target.lstrip('/') if target.startswith('/') else 'xl/' + target
        tree = ElementTree.fromstring(book.read(member))
        definitions = {}
        for row in tree.findall('.//s:row', ns):
            texts = []
            for cell in row.findall('s:c', ns):
                value = cell.find('s:v', ns)
                if value is not None:
                    texts.append(strings[int(value.text)] if cell.get('t') == 's' else value.text)
            for field in ['TP_REDE', 'TP_CATEGORIA_ADMINISTRATIVA']:
                if field in texts:
                    definition = next((text for text in texts if text.startswith('1. Pública')), None)
                    definitions[field] = {'linha_planilha': int(row.attrib['r']), 'definicao': definition}
    category = definitions.get('TP_CATEGORIA_ADMINISTRATIVA', {}).get('definicao') or ''
    if not all(label in category for label in ['1. Pública Federal', '2. Pública Estadual',
                                              '3. Pública Municipal', '7. Especial']):
        raise ValueError('Dicionário da IES não confirma as categorias 1/2/3/7')
    cadastro = next(item for item in source['arquivos'] if item['tipo'] == 'cadastro_ies')
    with (ROOT / cadastro['caminho_local']).open(encoding='cp1252', newline='') as stream:
        header = next(csv.reader(stream, delimiter=';'))
    has_network = 'TP_REDE' in header
    if has_network and definitions.get('TP_REDE', {}).get('definicao') != '1. Pública\n2. Privada':
        raise ValueError('TP_REDE presente sem mapeamento correspondente na planilha cadastro_ies')
    return {'planilha': 'cadastro_ies', 'membro_xlsx': member,
            'sha256_dicionario': dictionary['sha256'], 'campo_rede_presente_cadastro': has_network,
            'linha_categoria': definitions['TP_CATEGORIA_ADMINISTRATIVA']['linha_planilha'],
            'linha_rede': definitions.get('TP_REDE', {}).get('linha_planilha')}


def load_source(year, known, *, offline=False, update=False):
    """Obtém ou recupera uma fonte conhecida, sem aceitar troca silenciosa."""
    if year == 2024:
        snapshot = read_json(ROOT / 'data/registry/fontes_inventario.json', {'fontes': []})['fontes']
        if len(snapshot) != 1 or snapshot[0]['ano_censo'] != 2024:
            raise ValueError('Fotografia 2024 ausente ou ambígua')
        source = snapshot[0]
        if known and known != source:
            raise ValueError('Fonte 2024 difere da já conciliada; revisar explicitamente a versão do histórico')
    elif known and not update:
        source = known
    else:
        if offline:
            raise ValueError(f'Fonte {year} ainda não coletada; --offline não permite aquisição')
        source = base.acquire(year)
    missing = base.verify_cached(source, allow_missing=True)
    if missing:
        if offline:
            raise ValueError(f'Originais {year} ausentes para --offline: ' + ', '.join(missing))
        base.recover_known_source(source)
    base.verify_cached(source)
    return source


def reconcile(rows, covered_years):
    """Resume observações por código; não atribui eventos jurídicos aos intervalos."""
    groups = defaultdict(list)
    for row in rows:
        groups[row['instituicao_id']].append(row)
    result = []
    for institution, items in sorted(groups.items(), key=lambda pair: int(pair[1][0]['codigo_inep'])):
        items.sort(key=lambda row: int(row['ano_fonte']))
        years = [int(row['ano_fonte']) for row in items]
        if len(years) != len(set(years)):
            raise ValueError(f'Instituição repetida no mesmo ano: {institution}')
        changes = []
        for previous, current in zip(items, items[1:]):
            for field in ['nome', 'sigla', 'uf', 'categoria_administrativa_codigo']:
                if previous[field] != current[field]:
                    changes.append({'campo': field, 'ano_anterior': int(previous['ano_fonte']),
                                    'ano_posterior': int(current['ano_fonte']),
                                    'valor_anterior': previous[field], 'valor_posterior': current[field],
                                    'fonte_anterior': previous['fonte_id'], 'fonte_posterior': current['fonte_id'],
                                    'intervalo_com_lacuna': int(current['ano_fonte']) != int(previous['ano_fonte']) + 1})
        result.append({
            'instituicao_id': institution, 'codigo_inep': items[0]['codigo_inep'],
            'anos_observados_selecao_institucional': packed(years),
            'anos_natureza_publica_confirmada_cadastro': packed([int(row['ano_fonte']) for row in items if row['rede'] != 'especial_a_verificar']),
            'anos_categoria_especial_sem_campo_rede': packed([int(row['ano_fonte']) for row in items if row['rede'] == 'especial_a_verificar']),
            'primeiro_ano_observado': min(years), 'ultimo_ano_observado': max(years),
            'observada_na_fotografia_2024': 2024 in years,
            'anos_cobertos_sem_observacao_selecao': packed(sorted(set(covered_years) - set(years))),
            'nomes_por_ano': packed({row['ano_fonte']: row['nome'] for row in items}),
            'siglas_por_ano': packed({row['ano_fonte']: row['sigla'] for row in items}),
            'categorias_por_ano': packed({row['ano_fonte']: row['categoria_administrativa_codigo'] for row in items}),
            'ufs_por_ano': packed({row['ano_fonte']: row['uf'] for row in items}),
            'mudancas_textuais_observadas': packed(changes),
            'fontes_ids': packed([row['fonte_id'] for row in items]),
            'situacao_reconciliacao': 'mesmo_codigo_inep; vinculos_juridicos_e_processos_a_verificar',
            'limite_interpretacao': 'Primeira/última observação e ausência na seleção não comprovam criação, extinção ou ausência de processo seletivo. Especial sem TP_REDE exige verificação de natureza.',
        })
    return result


def build_history(sources):
    rows, summaries = [], []
    for source in sorted(sources, key=lambda row: row['ano_censo']):
        year = source['ano_censo']
        dictionary = dictionary_evidence(source)
        destination = ROOT / f'data/interim/inventario/historico/instituicoes-{year}.csv'
        summary = base.build_inventory(source, destination=destination, allow_category_fallback=True)
        summary['evidencia_dicionario_ies'] = dictionary
        summaries.append(summary)
        with destination.open(encoding='utf-8', newline='') as stream:
            annual = list(csv.DictReader(stream))
        for row in annual:
            row['registro_ano_id'] = f"{row['instituicao_id']}@{year}"
            row['criterio_selecao_ano'] = summary['criterio']
            row['dicionario_planilha'] = dictionary['planilha']
            row['dicionario_linha_categoria'] = dictionary['linha_categoria']
            row['dicionario_linha_rede'] = dictionary['linha_rede']
            row['dicionario_sha256'] = dictionary['sha256_dicionario']
            rows.append(row)
    rows.sort(key=lambda row: (int(row['ano_fonte']), int(row['codigo_inep'])))
    if len({row['registro_ano_id'] for row in rows}) != len(rows):
        raise ValueError('Chave instituição/ano duplicada no histórico')
    if not rows:
        raise ValueError('Nenhum cadastro institucional validado para exportar')
    years = sorted({int(row['ano_fonte']) for row in rows})
    reconciled = reconcile(rows, years)
    registry = ROOT / 'data/registry'
    history_path = registry / 'instituicoes-historico.csv'
    write_csv(history_path, rows, ['registro_ano_id'] + [field for field in rows[0] if field != 'registro_ano_id'])
    write_csv(registry / 'reconciliacao-instituicoes.csv', reconciled, list(reconciled[0]))
    summary = {'versao': VERSION, 'anos_obtidos': years, 'registros_instituicao_ano': len(rows),
               'instituicoes_distintas_publicas_ou_especiais': len(reconciled),
               'ids_publicos_confirmados_em_ao_menos_um_ano': len({row['instituicao_id'] for row in rows if row['rede'] != 'especial_a_verificar'}),
               'ids_apenas_especial_sem_natureza_confirmada': sum(row['anos_natureza_publica_confirmada_cadastro'] == '[]' for row in reconciled),
               'registros_publicos_confirmados_pelo_cadastro': sum(row['rede'] != 'especial_a_verificar' for row in rows),
               'registros_especiais_sem_campo_rede': sum(row['rede'] == 'especial_a_verificar' for row in rows),
               'ids_nao_observados_na_fotografia_2024': sum(not row['observada_na_fotografia_2024'] for row in reconciled),
               'instituicoes_com_mudanca_textual_observada': sum(row['mudancas_textuais_observadas'] != '[]' for row in reconciled),
               'historico_sha256': hashlib.sha256(history_path.read_bytes()).hexdigest(),
               'resumos_anuais': summaries,
               'cobertura_2017_2026_completa': False,
               'pendencias': ['Cadastros 2025–2026 não obtidos; complementar com e-MEC e fontes institucionais.',
                              'Verificar esfera de categoria Especial e natureza ao longo das aplicações.',
                              'Mudanças de código, fusões e desmembramentos exigem fontes jurídicas/institucionais.',
                              'Instituição observada não comprova processo próprio ou previsão amazônica.']}
    write_json(ROOT / 'data/interim/inventario/historico/resumo.json', summary)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--anos', nargs='+', type=int, default=list(range(2017, 2025)))
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--atualizar', action='store_true')
    args = parser.parse_args(argv)
    if args.offline and args.atualizar:
        parser.error('--offline e --atualizar são incompatíveis')
    if any(year not in range(2017, 2025) for year in args.anos):
        parser.error('Esta versão aceita fontes anuais 2017–2024; 2025–2026 permanecem pendentes')
    path = ROOT / 'data/registry/fontes_inventario_historico.json'
    manifest = read_json(path, {'versao': VERSION, 'fontes': [], 'pendencias_por_ano': []})
    sources = {source['ano_censo']: source for source in manifest['fontes']}
    if len(sources) != len(manifest['fontes']):
        raise ValueError('Ano duplicado no manifesto histórico')
    pending = {item['ano_censo']: item for item in manifest.get('pendencias_por_ano', [])}
    known_failures = []
    for year in sorted(set(args.anos)):
        known = sources.get(year)
        try:
            source = load_source(year, known, offline=args.offline, update=args.atualizar)
            # Valida o esquema/dicionário antes de aceitar a fonte no manifesto.
            destination = ROOT / f'data/interim/inventario/historico/instituicoes-{year}.csv'
            dictionary_evidence(source)
            base.build_inventory(source, destination=destination, allow_category_fallback=True)
        except (OSError, ValueError, StopIteration, KeyError, subprocess.CalledProcessError,
                zipfile.BadZipFile, ElementTree.ParseError) as error:
            pending[year] = {'ano_censo': year, 'estado': 'pendente_aquisicao_ou_validacao',
                             'registrado_em': datetime.now(ZoneInfo('America/Manaus')).isoformat(timespec='seconds'),
                             'erro': f'{type(error).__name__}: {error}'}
            print(f'Pendente {year}: {error}', file=sys.stderr, flush=True)
            if known:
                known_failures.append(year)
        else:
            sources[year] = source
            pending.pop(year, None)
            print(f'Fonte {year} validada.', flush=True)
        manifest = {'versao': VERSION, 'fontes': [sources[y] for y in sorted(sources)],
                    'pendencias_por_ano': [pending[y] for y in sorted(pending)]}
        write_json(path, manifest)
    if known_failures:
        raise ValueError('Fontes conhecidas indisponíveis ou alteradas; tabelas históricas anteriores preservadas: '
                         + ', '.join(map(str, known_failures)))
    summary = build_history(list(sources.values()))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return int(bool(pending))


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, StopIteration, KeyError, subprocess.CalledProcessError,
            zipfile.BadZipFile, ElementTree.ParseError) as error:
        print(f'ERRO: {error}', file=sys.stderr)
        sys.exit(2)
