#!/usr/bin/env python3
"""Prepara uma fila de revisão sem inventar rótulos ou sobrescrever anotação."""

import csv
from pathlib import Path

from pipeline import ROOT, write_csv

FIELDS = ['ocorrencia_id', 'documento_sha256', 'anotador', 'anotado_em', 'integridade_enunciado',
          'integridade_alternativas', 'dependencia_visual', 'conferido_pdf', 'conferido_gabarito',
          'regionalidade', 'evidencia_classificacao', 'recorte_territorial', 'temas', 'demanda_cognitiva',
          'topicos_programa', 'tipo_vinculo', 'particao', 'observacoes']


def prepare(root=ROOT):
    root = Path(root)
    with (root / 'data/processed/questoes.csv').open(encoding='utf-8', newline='') as stream:
        questions = list(csv.DictReader(stream))
    ids = [row['ocorrencia_id'] for row in questions]
    if len(ids) != len(set(ids)):
        raise ValueError('Questões duplicadas na fila')
    path = root / 'data/annotation/rotulos-humanos.csv'
    previous = []
    if path.exists():
        with path.open(encoding='utf-8', newline='') as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != FIELDS:
                raise ValueError('Esquema dos rótulos foi alterado; reconciliar antes de escrever')
            previous = list(reader)
    by_id = {row['ocorrencia_id']: row for row in previous}
    if len(by_id) != len(previous):
        raise ValueError('Rótulos com IDs duplicados; nenhuma anotação foi substituída')
    new = []
    for item in questions:
        old = by_id.get(item['ocorrencia_id'])
        if old and old['documento_sha256'] != item['documento_sha256']:
            raise ValueError('Original mudou para uma questão já na fila; reconciliar anotações')
        if not old:
            new.append({field: item.get(field, '') if field in ['ocorrencia_id', 'documento_sha256'] else '' for field in FIELDS})
    if new or not path.exists():
        write_csv(path, previous + new, FIELDS)
    queue_fields = ['ocorrencia_id', 'documento_id', 'documento_sha256', 'aplicacao_id', 'numero_questao',
                    'disciplina', 'paginas_pdf', 'status_estrutural', 'texto_local']
    queue = [{**item, 'texto_local': 'data/processed/questoes-texto.jsonl'} for item in questions]
    write_csv(root / 'data/annotation/fila.csv', queue, queue_fields)
    print(f'Fila: {len(questions)} questões; {len(new)} linhas vazias acrescentadas. Anotações anteriores preservadas.')


if __name__ == '__main__':
    prepare()
