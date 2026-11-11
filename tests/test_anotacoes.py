"""Anotações sintéticas de teste nunca são gravadas no corpus real."""

import contextlib
import csv
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from importar_anotacoes import import_annotations
from preparar_revisao import FIELDS, prepare
from pipeline import read_csv, write_csv


class AnnotationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.questions = [{'ocorrencia_id': 'fixture-q01', 'documento_sha256': 'a' * 64,
                           'documento_id': 'fixture-prova', 'aplicacao_id': 'fixture-app',
                           'numero_questao': '1', 'disciplina': 'historia', 'paginas_pdf': '[1]',
                           'status_estrutural': 'fixture'}]
        write_csv(self.root / 'data/processed/questoes.csv', self.questions, list(self.questions[0]))
        with contextlib.redirect_stdout(io.StringIO()):
            prepare(self.root)
        (self.root / 'data/annotation/configuracao.json').write_text(json.dumps({'anotador_previsto': 'Anotador de teste'}))
        self.path = self.root / 'data/annotation/rotulos-humanos.csv'
        self.export = self.root / 'fixture-export.json'
        self.row = {field: '' for field in FIELDS}
        self.row.update(ocorrencia_id='fixture-q01', documento_sha256='a' * 64,
                        anotador='Anotador de teste', anotado_em='2026-11-11T14:00:00-04:00',
                        integridade_enunciado='completo', integridade_alternativas='completas',
                        dependencia_visual='nao', conferido_pdf='sim', regionalidade='nao_regional',
                        evidencia_classificacao='Dado sintético exclusivo do teste.')

    def exported(self, rows=None):
        data = {'versao': '0.1.0', 'pacote_id': 'fixture-pacote-antigo',
                'origem': 'anotacao_humana_declarada', 'anotacoes': rows if rows is not None else [self.row]}
        self.export.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    def import_data(self, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return import_annotations(self.export, self.root, **kwargs)

    def test_queue_refresh_preserves_existing_annotation_bytes(self):
        write_csv(self.path, [self.row], FIELDS)
        original = self.path.read_bytes()
        with contextlib.redirect_stdout(io.StringIO()):
            prepare(self.root)
        self.assertEqual(self.path.read_bytes(), original)

    def test_known_occurrence_from_older_package_is_imported_with_audit(self):
        self.exported()
        self.assertEqual(self.import_data(), 1)
        self.assertEqual(read_csv(self.path)[0]['regionalidade'], 'nao_regional')
        event = json.loads((self.root / 'data/annotation/importacoes.jsonl').read_text())
        self.assertEqual(event['pacote_id'], 'fixture-pacote-antigo')
        self.assertTrue((self.root / 'data/annotation/historico' / (event['csv_anterior_sha256'] + '.csv')).exists())

    def test_other_original_version_is_rejected_without_any_write(self):
        self.row['documento_sha256'] = 'b' * 64
        self.exported()
        before = self.path.read_bytes()
        with self.assertRaisesRegex(ValueError, 'outra versão'):
            self.import_data()
        self.assertEqual(self.path.read_bytes(), before)
        self.assertFalse((self.root / 'data/annotation/historico').exists())

    def test_missing_evidence_or_undeclared_author_cannot_be_reference(self):
        for field, invalid in [('anotador', 'Modelo de teste'), ('evidencia_classificacao', '   '),
                               ('regionalidade', 'sem_base'), ('anotado_em', '2026-11-11'), ('conferido_pdf', '')]:
            row = {**self.row, field: invalid}
            self.exported([row])
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.import_data()

    def test_duplicate_or_unknown_occurrences_are_rejected(self):
        for rows in [[self.row, self.row], [{**self.row, 'ocorrencia_id': 'desconhecida'}]]:
            self.exported(rows)
            with self.assertRaises(ValueError):
                self.import_data()

    def test_conflicting_correction_requires_explicit_replace_and_keeps_backup(self):
        self.exported()
        self.import_data()
        before = self.path.read_bytes()
        self.row['regionalidade'] = 'ambiguo_revisar'
        self.exported()
        with self.assertRaisesRegex(ValueError, 'substituir'):
            self.import_data()
        self.assertEqual(self.path.read_bytes(), before)
        self.import_data(replace=True)
        self.assertEqual(read_csv(self.path)[0]['regionalidade'], 'ambiguo_revisar')
        self.assertIn(before, [p.read_bytes() for p in (self.root / 'data/annotation/historico').glob('*.csv')])

    def test_empty_export_does_not_create_reference(self):
        self.exported([])
        before = self.path.read_bytes()
        self.assertEqual(self.import_data(), 0)
        self.assertEqual(self.path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
