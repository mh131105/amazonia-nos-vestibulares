"""Consolidação documental com datas distintas e fixtures apenas temporárias."""

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import pipeline

with patch.dict(sys.modules, {'pipeline': pipeline}):
    from scripts import consolidar_registro as consolidate


class ExpansionCycleTwoTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.registry = Path(temporary.name)
        pipeline.write_jsonl(self.registry / 'documentos-esperados.jsonl', [])
        self.item = {
            'aplicacao_id': 'teste-edicao2026', 'processo_id': 'teste-processo', 'instituicao_sigla': 'TESTE',
            'etapa': 'unica', 'edicao': 'Edição sintética 2026', 'ano_ingresso': 2026,
            'data_aplicacao': '2025-11-30', 'data_aplicacao_prevista': None,
            'situacao': 'aplicada_documentos_localizados', 'banca': 'Banca fictícia',
            'formato': 'formato_sintetico', 'serie_alvo': 2, 'ano_serie_alvo': 2024,
            'evidencia_data': {'url': 'https://fonte.example.invalid/data.pdf', 'localizacao': 'Capa',
                              'natureza': 'Evidência sintética exclusivamente de teste'},
            'fonte_landing': 'https://fonte.example.invalid/processo',
            'programa': [{'disciplina': discipline, 'previsao_regional': 'substantiva',
                          'paginas_pdf': [1], 'localizacao': 'Seção sintética', 'trecho_curto': 'Conteúdo de teste',
                          'fonte_url': 'https://fonte.example.invalid/programa.pdf'}
                         for discipline in ['historia', 'geografia']],
            'documentos': [{'tipo': 'prova', 'url': 'https://fonte.example.invalid/prova.pdf'}],
        }
        self.process = {'processo_id': 'teste-processo', 'estado_triagem': 'candidato_evidencia_insuficiente',
                        'anos_previsao_historia': '[2018,2019]', 'anos_previsao_geografia': '[2018,2019]',
                        'anos_programa_verificavel_historia': '[2018,2019]',
                        'anos_programa_verificavel_geografia': '[2018,2019]', 'motivo_e_pendencias': 'Pendência sintética'}

    def run_expansion(self, items=None):
        path = self.registry / 'expansao-fixture-c2.json'
        path.write_text(json.dumps({'aplicacoes': items if items is not None else [self.item]}), encoding='utf-8')
        applications, evidence, processes = [], [], [copy.deepcopy(self.process)]
        expected = consolidate.expand(self.registry, {'TESTE': 'inep_teste'}, applications, evidence, processes)
        return applications, evidence, processes, expected

    def test_application_uses_effective_date_and_preserves_distinct_edition_cohort_context(self):
        apps, _, processes, expected = self.run_expansion()
        row = apps[0]
        self.assertEqual(row['ano_aplicacao'], 2025)
        self.assertEqual(row['ano_ingresso'], 2026)
        self.assertEqual(row['periodo_calendario'], '2025-2026')
        self.assertEqual(row['serie_alvo'], 2)
        self.assertEqual(row['ano_serie_alvo'], 2024)
        self.assertEqual(row['banca'], 'Banca fictícia')
        self.assertEqual(row['formato'], 'formato_sintetico')
        self.assertEqual(expected[0]['publicador'], 'Banca fictícia')
        self.assertEqual(json.loads(processes[0]['anos_previsao_historia']), [2018, 2019, 2025])

    def test_repeated_reconstruction_preserves_document_ids_and_does_not_duplicate_requests(self):
        apps, evidence, processes, first = self.run_expansion()
        pipeline.write_jsonl(self.registry / 'documentos-esperados.jsonl', first)
        again = self.run_expansion()[3]
        self.assertEqual(first, again)
        self.assertEqual(len(again), 1)
        self.assertEqual(len({row['documento_id'] for row in again}), 1)

    def test_publisher_correction_does_not_change_known_document_identity(self):
        first = self.run_expansion()[3]
        first[0]['publicador'] = 'Instituição sem identificação da banca'
        pipeline.write_jsonl(self.registry / 'documentos-esperados.jsonl', first)
        current = self.run_expansion()[3]
        self.assertEqual(current[0]['documento_id'], first[0]['documento_id'])
        self.assertEqual(current[0]['publicador'], 'Banca fictícia')

    def test_forecast_is_not_promoted_to_effective_year_or_recurrence(self):
        item = copy.deepcopy(self.item)
        item.update(data_aplicacao=None, data_aplicacao_prevista='2018-12-02',
                    situacao='aplicacao_ocorrida_data_exata_a_corrobora')
        apps, evidence, processes, expected = self.run_expansion([item])
        self.assertIsNone(apps[0]['ano_aplicacao'])
        self.assertIsNone(apps[0]['data_aplicacao'])
        self.assertIsNone(apps[0]['periodo_calendario'])
        self.assertEqual(apps[0]['data_prevista'], '2018-12-02')
        self.assertEqual(json.loads(processes[0]['anos_previsao_historia']), [2018, 2019])
        self.assertEqual(processes[0]['estado_triagem'], 'candidato_evidencia_insuficiente')
        self.assertEqual(len(evidence), 2)
        self.assertEqual(len(expected), 1)

    def test_future_program_does_not_supply_an_observed_year(self):
        item = copy.deepcopy(self.item)
        item.update(data_aplicacao=None, data_aplicacao_prevista='2026-11-29', situacao='futura_na_data_de_corte')
        apps, _, processes, _ = self.run_expansion([item])
        self.assertIsNone(apps[0]['ano_aplicacao'])
        self.assertEqual(processes[0]['estado_triagem'], 'candidato_evidencia_insuficiente')

    def test_negative_program_is_verifiable_without_becoming_positive_in_that_discipline(self):
        item = copy.deepcopy(self.item)
        item['programa'][0]['previsao_regional'] = 'nao_identificada_no_programa_examinado'
        _, _, processes, _ = self.run_expansion([item])
        row = processes[0]
        self.assertEqual(json.loads(row['anos_previsao_historia']), [2018, 2019])
        self.assertEqual(json.loads(row['anos_programa_verificavel_historia']), [2018, 2019, 2025])
        self.assertEqual(json.loads(row['anos_previsao_geografia']), [2018, 2019, 2025])
        self.assertIn('geografia', row['motivo_e_pendencias'])

    def test_effective_date_outside_window_is_rejected_without_touching_manifest(self):
        item = copy.deepcopy(self.item)
        item['data_aplicacao'] = '2016-12-01'
        path = self.registry / 'documentos-esperados.jsonl'
        before = path.read_bytes()
        with self.assertRaisesRegex(ValueError, 'fora da janela'):
            self.run_expansion([item])
        self.assertEqual(path.read_bytes(), before)

    def test_duplicate_application_is_rejected_instead_of_double_counted(self):
        with self.assertRaisesRegex(ValueError, 'Aplicação repetida'):
            self.run_expansion([self.item, copy.deepcopy(self.item)])


if __name__ == '__main__':
    unittest.main()
