#!/usr/bin/env python3
"""Valida anotações declaradas humanas e incorpora ao CSV preservando versões."""

import argparse
import json
from datetime import datetime
from pathlib import Path

from pipeline import ROOT, append_jsonl, now, read_csv, sha256, write_csv
from preparar_revisao import FIELDS

CATEGORIES = {'regional_substantiva', 'mencao_contextual', 'nao_regional', 'ambiguo_revisar'}


def import_annotations(path, root=ROOT, *, replace=False):
    root, path = Path(root), Path(path)
    exported = json.loads(path.read_text(encoding='utf-8-sig'))
    if exported.get('origem') != 'anotacao_humana_declarada' or not isinstance(exported.get('anotacoes'), list):
        raise ValueError('Arquivo não declara o formato de anotação humana do caderno')
    questions = {r['ocorrencia_id']: r for r in read_csv(root / 'data/processed/questoes.csv')}
    config = json.loads((root / 'data/annotation/configuracao.json').read_text(encoding='utf-8'))
    annotations_path = root / 'data/annotation/rotulos-humanos.csv'
    previous = read_csv(annotations_path)
    by_id = {r['ocorrencia_id']: r for r in previous}
    if len(by_id) != len(previous):
        raise ValueError('CSV existente contém IDs duplicados')
    incoming = []
    ids = set()
    for row in exported['anotacoes']:
        key = row.get('ocorrencia_id')
        question = questions.get(key)
        if key in ids or not question:
            raise ValueError('Ocorrência duplicada ou desconhecida na importação')
        ids.add(key)
        if row.get('documento_sha256') != question['documento_sha256']:
            raise ValueError('A anotação refere-se a outra versão do original')
        if row.get('anotador', '').strip() != config['anotador_previsto']:
            raise ValueError('Anotador difere da configuração; reconciliar identidade antes de importar')
        if row.get('regionalidade') not in CATEGORIES or not row.get('evidencia_classificacao', '').strip():
            raise ValueError('Regionalidade ou evidência inválida')
        if row.get('integridade_enunciado') not in {'completo', 'incompleto', 'a_revisar'}:
            raise ValueError('Integridade de enunciado não preenchida')
        allowed_alternatives = ({'nao_se_aplica_discursiva', 'a_revisar'} if question.get('tipo_resposta') == 'discursiva'
                                else {'completas', 'incompletas', 'a_revisar'})
        if row.get('integridade_alternativas') not in allowed_alternatives:
            raise ValueError('Integridade das alternativas não preenchida')
        if row.get('dependencia_visual') not in {'sim', 'nao', 'a_verificar'} or row.get('conferido_pdf') != 'sim':
            raise ValueError('Conferência da fonte visual pendente')
        try:
            timestamp = datetime.fromisoformat(row['anotado_em'])
            if timestamp.tzinfo is None:
                raise ValueError('Data sem fuso horário')
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError('Data de anotação inválida ou sem fuso') from error
        normalized = {field: str(row.get(field, '')) for field in FIELDS}
        old = by_id.get(key)
        if old and old.get('anotador') and old != normalized and not replace:
            raise ValueError('Anotação já preenchida e diferente; use --substituir para correção explícita')
        incoming.append(normalized)
    # Toda validação ocorre antes de qualquer alteração; cópia histórica preserva o CSV.
    if not incoming:
        print('Nenhuma anotação preenchida no arquivo; CSV preservado.')
        return 0
    backup = root / 'data/annotation/historico' / (sha256(annotations_path) + '.csv')
    backup.parent.mkdir(parents=True, exist_ok=True)
    if not backup.exists():
        backup.write_bytes(annotations_path.read_bytes())
    for row in incoming:
        by_id[row['ocorrencia_id']] = row
    write_csv(annotations_path, [by_id[key] for key in sorted(by_id)], FIELDS)
    append_jsonl(root / 'data/annotation/importacoes.jsonl', {
        'importado_em': now(), 'arquivo_sha256': sha256(path), 'pacote_id': exported.get('pacote_id'),
        'origem_declarada': exported['origem'], 'anotador_declarado': config['anotador_previsto'],
        'ocorrencias_ids': [r['ocorrencia_id'] for r in incoming], 'substituicao_explicita': replace,
        'csv_anterior_sha256': backup.stem, 'csv_resultante_sha256': sha256(annotations_path)})
    print(f'Importadas {len(incoming)} anotações declaradas humanas. Revisão e teste congelado continuam etapas próprias.')
    return len(incoming)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('arquivo', type=Path)
    parser.add_argument('--substituir', action='store_true', help='Aceitar correção explícita preservando CSV anterior')
    args = parser.parse_args()
    import_annotations(args.arquivo, replace=args.substituir)
