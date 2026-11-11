#!/usr/bin/env python3
"""Segmenta itens de provas com regras explícitas de layout e origem geométrica.

O CSV público contém somente metadados. Textos extraídos permanecem em JSONL
local; nenhuma classificação regional ou validação humana é produzida aqui.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.2.0'
HEADINGS = {'HISTÓRIA', 'GEOGRAFIA', 'BIOLOGIA', 'FÍSICA', 'QUÍMICA',
            'MATEMÁTICA', 'LITERATURA', 'LÍNGUA PORTUGUESA', 'LÍNGUA ESTRANGEIRA'}


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(''.join(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n'
                                 for row in rows), encoding='utf-8')
    temporary.replace(path)


def bbox(words):
    return [min(w['bbox'][0] for w in words), min(w['bbox'][1] for w in words),
            max(w['bbox'][2] for w in words), max(w['bbox'][3] for w in words)]


def ordered_lines(pages, layout):
    """Reconstrói a leitura por coluna; ordem dos fluxos do XML não é confiável."""
    result = []
    for page in sorted(pages, key=lambda item: item['pagina']):
        if page['pagina'] < layout['pagina_inicial']:
            continue
        split = page['largura'] * layout['divisao_colunas_fracao']
        columns = [[], []]
        for source_line in page['linhas']:
            for column in (0, 1):
                words = [w for w in source_line['palavras']
                         if (0 if (w['bbox'][0] + w['bbox'][2]) / 2 < split else 1) == column
                         and layout['y_min'] <= w['bbox'][1] <= layout['y_max']]
                if not words:
                    continue
                words.sort(key=lambda w: w['bbox'][0])
                line = {'pagina': page['pagina'], 'coluna': column + 1,
                        'bbox': bbox(words), 'palavras': words,
                        'texto': ' '.join(w['texto'] for w in words)}
                # Número da página de UFAM fica no centro, junto ao rodapé.
                if (re.fullmatch(r'\d+', line['texto']) and line['bbox'][1] > 780
                        and abs((line['bbox'][0] + line['bbox'][2]) / 2 - split) < 16):
                    continue
                if line['texto'].strip(' -–—') in HEADINGS:
                    continue
                if any(re.fullmatch(pattern, line['texto']) for pattern in layout.get('ignorar_linhas', [])):
                    continue
                columns[column].append(line)
        for column in columns:
            column.sort(key=lambda line: (line['bbox'][1], line['bbox'][0]))
            # Poppler ocasionalmente divide uma linha visual em dois fluxos.
            merged = []
            for line in column:
                if (merged and abs(merged[-1]['bbox'][1] - line['bbox'][1]) <= 1.6
                        and merged[-1]['bbox'][2] <= line['bbox'][0] + 1):
                    previous = merged[-1]
                    words = sorted(previous['palavras'] + line['palavras'], key=lambda w: w['bbox'][0])
                    previous.update(palavras=words, bbox=bbox(words), texto=' '.join(w['texto'] for w in words))
                else:
                    merged.append(line)
            result.extend(merged)
    return result


def markers(lines, layout):
    result = []
    for index, line in enumerate(lines):
        match = re.match(layout['marcador_questao'], line['texto'])
        if not match:
            continue
        if layout.get('margens_inicio_questao'):
            margin = layout['margens_inicio_questao'][line['coluna'] - 1]
            if abs(line['bbox'][0] - margin) > layout['tolerancia_margem']:
                continue
        number = int(match.group(1))
        if 1 <= number <= layout['numero_maximo']:
            result.append({'indice': index, 'numero': number})
    return result


def regions(lines, pages, layout, next_line):
    """Regiões incluem espaço visual entre linhas, preservando acesso às imagens."""
    page_lookup = {page['pagina']: page for page in pages}
    groups = []
    for line in lines:
        key = (line['pagina'], line['coluna'])
        if not groups or groups[-1]['key'] != key:
            groups.append({'key': key, 'linhas': []})
        groups[-1]['linhas'].append(line)
    result = []
    for group_index, group in enumerate(groups):
        number, column = group['key']
        page = page_lookup[number]
        split = page['largura'] * layout['divisao_colunas_fracao']
        first = group['linhas'][0]
        y_end = layout['y_max']
        if next_line and (next_line['pagina'], next_line['coluna']) == group['key']:
            y_end = next_line['bbox'][1]
        # Se a questão termina nesta coluna e segue na próxima, vai até o fim do corpo.
        result.append({'pagina': number, 'coluna': column,
                       'bbox_regiao': [0 if column == 1 else split,
                                       first['bbox'][1] if group_index == 0 else layout['y_min'],
                                       split if column == 1 else page['largura'], y_end],
                       'bbox_texto': [min(line['bbox'][0] for line in group['linhas']),
                                      min(line['bbox'][1] for line in group['linhas']),
                                      max(line['bbox'][2] for line in group['linhas']),
                                      max(line['bbox'][3] for line in group['linhas'])],
                       'sistema_coordenadas': 'pontos_pdf_origem_superior_esquerda',
                       'largura_pagina': page['largura'], 'altura_pagina': page['altura']})
    return result


def alternative_label_lines(lines, layout):
    """Distingue o glifo de opção do artigo A por medidas do layout verificado."""
    geometry = layout.get('geometria_rotulos_alternativas')
    if not geometry:
        return None
    accepted = set()
    for index, line in enumerate(lines):
        words = line['palavras']
        if len(words) < 2 or words[0]['texto'] not in set('ABCDE'):
            continue
        first, second = words[:2]
        width = first['bbox'][2] - first['bbox'][0]
        gap = second['bbox'][0] - first['bbox'][2]
        margin = geometry['margens'][line['coluna'] - 1]
        if (geometry['largura_min'] <= width <= geometry['largura_max']
                and geometry['gap_min'] <= gap <= geometry['gap_max']
                and abs(first['bbox'][0] - margin) <= geometry['tolerancia_margem']):
            accepted.add(index)
    return accepted


def split_alternatives(text, pattern=None, allowed_lines=None):
    # O padrão pertence ao layout verificado. UERR/Cebraspe usa letras sem
    # parênteses; a regra padrão A) não trata enumerações a./b./c. como respostas.
    matches = list(re.finditer(pattern or r'(?m)^([a-eA-E])\)\s+', text))
    if allowed_lines is not None:
        matches = [match for match in matches if text[:match.start()].count('\n') in allowed_lines]
    labels = [match.group(1).lower() for match in matches]
    if labels != list('abcde'):
        return None, labels
    alternatives = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        alternatives.append({'rotulo': match.group(1).upper(),
                             'texto_extraido': text[match.end():end].strip()})
    if any(not alternative['texto_extraido'] for alternative in alternatives):
        return None, labels
    return alternatives, labels


def segment(root=ROOT):
    root = Path(root).resolve()
    config_path = root / 'data/registry/regras-segmentacao.json'
    config = json.loads(config_path.read_text(encoding='utf-8'))
    documents = {d['documento_id']: d for d in read_jsonl(root / 'data/registry/documentos.jsonl')}
    public_rows, local_rows, executions = [], [], []
    for rule in config['documentos']:
        doc_id = rule['documento_id']
        document = documents.get(doc_id)
        if not document or document.get('status') != 'coletado':
            raise ValueError(f'Original não coletado: {doc_id}')
        source = root / document['caminho_local']
        if document['sha256'] != rule['documento_sha256'] or digest(source) != document['sha256']:
            raise ValueError(f'Original difere do hash fixado nas regras: {doc_id}')
        pages_path = root / 'data/interim/extraido' / document['sha256'] / 'paginas.jsonl'
        pages = read_jsonl(pages_path)
        if any(page.get('documento_sha256') != document['sha256'] for page in pages):
            raise ValueError(f'Extração não pertence ao original: {doc_id}')
        layout = config['layouts'][rule['layout']]
        lines = ordered_lines(pages, layout)
        found = markers(lines, layout)
        selected = []
        for section in rule['secoes']:
            for number in range(section['inicio'], section['fim'] + 1):
                positions = [index for index, marker in enumerate(found) if marker['numero'] == number]
                if len(positions) != 1:
                    raise ValueError(f'Início da questão {number} não é único: {doc_id} ({len(positions)})')
                marker_index = positions[0]
                start = found[marker_index]['indice']
                following = found[marker_index + 1] if marker_index + 1 < len(found) else None
                end = following['indice'] if following else len(lines)
                item_lines = lines[start:end]
                text = '\n'.join(line['texto'] for line in item_lines).strip()
                alternatives, labels = split_alternatives(
                    text, layout.get('marcador_alternativa'), alternative_label_lines(item_lines, layout))
                issues = []
                allowed_end = (not following and number == layout['numero_maximo']
                               and layout.get('fecha_ultima_questao_no_fim_do_documento') is True)
                if (not following and not allowed_end) or (following and following['numero'] != number + 1):
                    issues.append('proxima_questao_ausente_ou_nao_consecutiva')
                if alternatives is None:
                    issues.append('alternativas_textuais_nao_formam_A_E_em_ordem_unica')
                if '\ufffd' in text:
                    issues.append('caractere_de_substituicao_na_extracao')
                if len(text) < 70:
                    issues.append('texto_extraido_curto_revisar')
                occurrence = f"{document['aplicacao_id']}-q{number:02d}"
                source_regions = regions(item_lines, pages, layout, lines[end] if end < len(lines) else None)
                metadata = {
                    'ocorrencia_id': occurrence,
                    'aplicacao_id': document['aplicacao_id'],
                    'processo_id': document['processo_id'],
                    'instituicao_sigla': document['instituicao_sigla'],
                    'documento_id': doc_id,
                    'documento_sha256': document['sha256'],
                    'url_origem': document['url_origem'],
                    'numero_questao': number,
                    'disciplina': section['disciplina'],
                    'paginas_pdf': sorted({line['pagina'] for line in item_lines}),
                    'regioes_origem': source_regions,
                    'quantidade_caracteres_extraidos': len(text),
                    'alternativas_rotulos_detectados': [label.upper() for label in labels],
                    'alternativas_textuais_completas': alternatives is not None,
                    'status_estrutural': 'estrutura_textual_completa_revisao_pendente' if not issues else 'incompleta_ou_ambigua_revisar',
                    'problemas_extracao': issues,
                    'dependencia_visual': 'a_verificar',
                    'integridade_revisada_humano': False,
                    'apto_denominador_validado': False,
                    'origem_segmentacao': 'regra_automatica_de_layout',
                    'versao_segmentador': VERSION,
                    'regionalidade': None,
                    'conteudo_equivalente_id': None,
                    'hash_texto_sha256': hashlib.sha256(' '.join(text.split()).encode('utf-8')).hexdigest(),
                    'hash_texto_uso': 'indicio_de_equivalencia_nao_inclui_imagens',
                }
                public_rows.append(metadata)
                local_rows.append({**metadata, 'texto_bruto_segmentado': text,
                                   'texto_corrigido_humano': None,
                                   'alternativas': alternatives,
                                   'linhas_origem': [{'pagina': line['pagina'], 'coluna': line['coluna'],
                                                     'bbox': line['bbox'], 'texto': line['texto']}
                                                    for line in item_lines]})
                selected.append(metadata)
        executions.append({'documento_id': doc_id, 'documento_sha256': document['sha256'],
                           'extracao_paginas_sha256': digest(pages_path),
                           'regras_sha256': digest(config_path), 'layout': rule['layout'],
                           'versao_segmentador': VERSION,
                           'questoes_esperadas': sum(s['fim'] - s['inicio'] + 1 for s in rule['secoes']),
                           'questoes_segmentadas': len(selected),
                           'estrutura_textual_completa': sum(not row['problemas_extracao'] for row in selected),
                           'denominadores_validados': 0,
                           'status': 'segmentado_revisao_visual_e_humana_pendente'})
    if len({row['ocorrencia_id'] for row in public_rows}) != len(public_rows):
        raise ValueError('Identidade de ocorrência duplicada')
    public_rows.sort(key=lambda row: row['ocorrencia_id'])
    local_rows.sort(key=lambda row: row['ocorrencia_id'])
    output = root / 'data/processed'
    output.mkdir(parents=True, exist_ok=True)
    with (output / 'questoes.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(public_rows[0]), lineterminator='\n')
        writer.writeheader()
        for row in public_rows:
            writer.writerow({key: json.dumps(value, ensure_ascii=False, sort_keys=True)
                             if isinstance(value, (list, dict)) else value
                             for key, value in row.items()})
    write_jsonl(output / 'questoes-texto.jsonl', local_rows)
    write_jsonl(root / 'data/registry/segmentacoes.jsonl', executions)
    return executions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    for row in segment(args.root):
        print(f"{row['documento_id']}: {row['questoes_segmentadas']}/{row['questoes_esperadas']} itens; "
              f"{row['estrutura_textual_completa']} com alternativas textuais A–E; revisão pendente")


if __name__ == '__main__':
    main()
