"""Auditoria documental C4 em diretórios temporários, sem rótulos humanos."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from scripts import auditoria_temporal

ROOT = Path(__file__).resolve().parents[1]


class TemporalAuditFourTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.registry = Path(temporary.name)
        self.audit = json.loads((ROOT / 'data/registry/auditoria-datas-c4.json').read_text())
        self.path = self.registry / 'auditoria-datas-c4.json'
        self.path.write_text(json.dumps(self.audit))
        self.apps = [{'aplicacao_id': check['aplicacao_id'], 'processo_id': 'ufam-psc',
                      'instituicao_sigla': 'UFAM', 'data_aplicacao': None,
                      'data_prevista': check['data_aplicacao_prevista'], 'ano_aplicacao': None,
                      'fonte_data': 'https://example.invalid/cronograma.pdf'}
                     for check in self.audit['verificacoes']]
        self.apps.append({'aplicacao_id': 'ufam-psc2019-e2', 'processo_id': 'ufam-psc',
                          'instituicao_sigla': 'UFAM', 'data_aplicacao': '2018-12-02',
                          'fonte_data': 'https://example.invalid/noticia'})
        # Classificações sintéticas de programa: testam a separação dos anos,
        # não propõem rótulos para documentos ou questões reais.
        self.evidence = [{'aplicacao_id': check['aplicacao_id'], 'disciplina': discipline,
                          'previsao_regional': 'substantiva' if discipline == 'geografia' else 'nao_identificada_no_programa_examinado'}
                         for check in self.audit['verificacoes'] for discipline in ['historia', 'geografia']]
        self.processes = [{'processo_id': 'ufam-psc', 'anos_previsao_historia': '[2022]',
                           'anos_previsao_geografia': '[2022]'}]
        finding = self.audit['auditoria_gabaritos'][0]
        self.docs = [{'documento_id': finding['documento_id'], 'url_origem': finding['url_arquivo'],
                      'sha256_auditado': finding['sha256_arquivo'],
                      'finalidade_documental': 'definitivo_indicado_no_indice_sem_confirmacao_no_arquivo'}]

    def apply(self):
        auditoria_temporal.integrar(self.registry, self.apps, self.evidence, self.processes, self.docs)

    def test_confirmed_days_are_separate_from_forecasts_and_negative_disciplines(self):
        self.apply()
        confirmed = [a for a in self.apps if a.get('fonte_auditoria_data')]
        self.assertEqual(len(confirmed), 2)
        self.assertTrue(all(a['data_aplicacao'] == '2023-07-30' and a['ano_aplicacao'] == 2023
                            and a['periodo_calendario'] == '2022-2023' for a in confirmed))
        self.assertTrue(all(a['data_prevista'] == '2023-07-30' and a['documento_id_evidencia_data'] for a in confirmed))
        self.assertEqual(sum(a['data_aplicacao'] is None for a in self.apps), 3)
        self.assertEqual(json.loads(self.processes[0]['anos_previsao_historia']), [2022])
        self.assertEqual(json.loads(self.processes[0]['anos_previsao_geografia']), [2022, 2023])

    def test_idempotent_overlay_keeps_previous_source_and_shared_original(self):
        self.apply()
        before = copy.deepcopy((self.apps, self.evidence, self.processes, self.docs))
        self.apply()
        self.assertEqual((self.apps, self.evidence, self.processes, self.docs), before)
        new = [d for d in self.docs if d.get('escopo_coleta') == 'auditoria_documental_ciclo4']
        self.assertEqual(len(new), 4)
        self.assertEqual(len({d['sha256_auditado'] for d in new}), 3)
        self.assertTrue(all(d['extracao_automatica'] is False for d in new))
        self.assertEqual(self.docs[0]['finalidade_documental'], 'definitivo_corrobora_repositorio_e_pos_recursos')

    def test_administrative_emission_or_a_different_original_cannot_supply_confirmation(self):
        check = next(c for c in self.audit['verificacoes'] if c['data_aplicacao_confirmada'])
        check['fonte_tipo'] = 'data_emissao_pagamento'
        self.path.write_text(json.dumps(self.audit))
        with self.assertRaisesRegex(ValueError, 'relato primário'):
            self.apply()
        self.path.write_bytes((ROOT / 'data/registry/auditoria-datas-c4.json').read_bytes())
        self.docs[0]['sha256_auditado'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'original auditado C3'):
            self.apply()

