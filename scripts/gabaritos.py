#!/usr/bin/env python3
"""Vincula respostas publicadas aos itens do piloto, sem resolver questões.

Lê somente gabaritos definitivos oficiais já coletados e extrações locais com
hash conferido. Regras suportadas: tabelas numeradas UFAM PSC e a linha 37–54
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
VERSION = '0.1.0'
# Faixas do piloto com disciplina conhecida. Línguas têm colunas diferentes e
# não recebem uma resposta por conveniência usando a primeira coluna.
UFAM_SUPPORTED = {2: set(range(17, 29)), 3: set(range(19, 31))}
FIELDS = ['ocorrencia_id', 'aplicacao_id', 'numero_questao',
          'disciplina', 'alternativa_oficial', 'estado_oficial',
          'marcador_oficial', 'documento_id', 'documento_sha256', 'pagina_pdf',
          'secao_gabarito', 'url_origem', 'origem', 'revisao_humana',
          'vinculo_versao_caderno', 'responsavel_extracao', 'versao_extrator',
          'problemas']


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()
            if line.strip()]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def parse_ufam(pages, year, stage, requested):
    """Restringe os números ao alvo para não confundir opções de língua."""
    eligible = [(page, normalized(text)) for page, text in pages
                if 'GABARITO DEFINITIVO' in normalized(text)
                and re.search(rf'\bPSC\s*{year}\b', normalized(text))
                and re.search(rf'\b{stage}A\s+ETAPA\b', normalized(text))]
    if len(eligible) != 1:
        return {}, 'pagina_ufam_ano_etapa_nao_unica'
    page, text = eligible[0]
    candidates = defaultdict(list)
    for number, token in re.findall(r'(?<!\d)(\d{1,2})\.\s*(ANULADA|NULA|[A-E])\b', text):
        number = int(number)
        if number in requested and number in UFAM_SUPPORTED.get(stage, set()):
            candidates[number].append(answer(token, page, f'PSC {year}, {stage}ª Etapa'))
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


def link(root=ROOT):
    root = Path(root).resolve()
    with (root / 'data/processed/questoes.csv').open(encoding='utf-8', newline='') as stream:
        questions = list(csv.DictReader(stream))
    ids = [row['ocorrencia_id'] for row in questions]
    if len(ids) != len(set(ids)):
        raise ValueError('IDs de ocorrência duplicados em questoes.csv')
    documents = read_jsonl(root / 'data/registry/documentos.jsonl')
    extracts = {row['documento_id']: row for row in read_jsonl(root / 'data/registry/extracoes.jsonl')}
    by_application = defaultdict(list)
    for document in documents:
        if (document.get('status') == 'coletado' and document.get('origem_oficial') is True
                and document.get('tipo') == 'gabarito_definitivo'):
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
            requested = {int(item['numero_questao']) for item in items}
            ufam = re.fullmatch(r'ufam-psc(\d{4})-e([123])', application_id)
            ufrr = re.fullmatch(r'ufrr-vestibular(\d{4})-pi', application_id)
            if ufam:
                found, problem = parse_ufam(pages, *map(int, ufam.groups()), requested)
            elif ufrr:
                found, problem = parse_ufrr_pi(pages, int(ufrr.group(1)), requested)
            else:
                problem = 'layout_sem_regra_verificada'
        for item in sorted(items, key=lambda row: int(row['numero_questao'])):
            number = int(item['numero_questao'])
            result = found.get(number, {})
            row = {'ocorrencia_id': item['ocorrencia_id'],
                   'aplicacao_id': application_id, 'numero_questao': number,
                   'disciplina': item['disciplina'],
                   'alternativa_oficial': result.get('alternativa_oficial'),
                   'estado_oficial': result.get('estado_oficial', 'nao_identificado'),
                   'marcador_oficial': result.get('marcador_oficial'),
                   'documento_id': source['documento_id'] if source else None,
                   'documento_sha256': source['sha256'] if source else None,
                   'pagina_pdf': result.get('pagina_pdf'), 'secao_gabarito': result.get('secao_gabarito'),
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
