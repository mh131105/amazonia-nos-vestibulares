"""Integração C3 sem rede: fontes ausentes, eventos e disciplinas independentes."""

import copy
import csv
import json
from pathlib import Path
import re
import tempfile
import unittest

from scripts import triagem_nacional as national


ROOT = Path(__file__).resolve().parents[1]


class NationalTriageTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.registry = Path(temporary.name)
        self.inputs = {}
        for filename in national.ARQUIVOS:
            self.inputs[filename] = json.loads((ROOT / 'data/registry' / filename).read_text())
        with (ROOT / 'data/registry/instituicoes.csv').open() as stream:
            self.institutions = {r['sigla'].upper(): r['instituicao_id'] for r in csv.DictReader(stream)}

    def integrate(self):
        for filename, content in self.inputs.items():
            (self.registry / filename).write_text(json.dumps(content))
        apps, evidence, processes = [], [], []
        result = national.integrar(self.registry, self.institutions, apps, evidence, processes)
        self.assertIsNone(result)
        return apps, evidence, processes

    def test_real_inputs_integrate_counts_and_canonical_ids(self):
        apps, evidence, processes = self.integrate()
        self.assertEqual((len(apps), len(evidence), len(processes)), (7, 35, 21))
        for rows, field in [(apps, 'aplicacao_id'), (evidence, 'evidencia_id'), (processes, 'processo_id')]:
            self.assertEqual(len({r[field] for r in rows}), len(rows))
            self.assertTrue(all(re.fullmatch('[a-z0-9-]+', r[field]) for r in rows))
        self.assertEqual({r['disciplina'] for r in evidence},
                         {'historia', 'geografia', 'ciencias_humanas_integradas'})
        for app in apps:
            process = next(p for p in processes if p['processo_id'] == app['processo_id'])
            self.assertIn(app['etapa'], json.loads(process['etapas']))
            self.assertTrue(app['fonte_data_id_origem'])
        self.assertTrue({p['estado_triagem'] for p in processes} <= {
            'incluido_recorrencia_confirmada', 'candidato_evidencia_insuficiente',
            'pendente_por_lacuna_documental', 'excluido_ingresso_apenas_enem_sisu'})
        unesp = next(p for p in processes if p['processo_id'] == 'unesp-vestibular')
        self.assertEqual(unesp['estado_triagem_origem'], 'pendente_programa_incorporado')

    def test_recurrence_uses_distinct_effective_years_per_discipline(self):
        _, evidence, processes = self.integrate()
        indexed = {p['processo_id']: p for p in processes}
        fuvest = indexed['usp-fuvest']
        self.assertEqual(fuvest['estado_triagem'], 'incluido_recorrencia_confirmada')
        self.assertEqual(json.loads(fuvest['anos_previsao_geografia']), [2021, 2022, 2023])
        self.assertEqual(json.loads(fuvest['anos_previsao_historia']), [])
        self.assertEqual([p['processo_id'] for p in processes
                          if p['estado_triagem'] == 'incluido_recorrencia_confirmada'], ['usp-fuvest'])
        self.assertTrue(all(r['revisao_humana'] == 'pendente' for r in evidence))

    def test_integrated_ufms_is_one_record_per_event_without_disciplinary_duplication(self):
        apps, evidence, processes = self.integrate()
        ufms_evidence = [r for r in evidence if r['processo_id'] == 'ufms-vestibular']
        self.assertEqual(len(ufms_evidence), 3)
        self.assertTrue(all(r['disciplina'] == 'ciencias_humanas_integradas' for r in ufms_evidence))
        self.assertEqual(len({r['aplicacao_id'] for r in ufms_evidence}), 3)
        process = next(p for p in processes if p['processo_id'] == 'ufms-vestibular')
        self.assertEqual(json.loads(process['anos_previsao_integrada']), [2023, 2024, 2025])
        self.assertTrue(process['recorrencia_integrada_confirmada'])
        for discipline in ['historia', 'geografia']:
            self.assertEqual(json.loads(process['anos_previsao_' + discipline]), [])
        for app in apps:
            if app['processo_id'] == 'ufms-vestibular':
                self.assertEqual(app['formato'], 'presencial_e_online_variantes_nao_conferidas')
                self.assertIsNone(app['cadernos_identificados'])
                self.assertFalse(app['variantes_conferidas'])

    def test_uel_shares_the_first_phase_event_without_inventing_program_year(self):
        apps, evidence, processes = self.integrate()
        app = next(a for a in apps if a['processo_id'] == 'uel-vestibular')
        self.assertEqual((app['data_aplicacao'], app['ano_aplicacao'], app['ano_ingresso']),
                         ('2023-10-29', 2023, 2024))
        records = [r for r in evidence if r['processo_id'] == 'uel-vestibular']
        self.assertEqual({r['aplicacao_id'] for r in records}, {app['aplicacao_id']})
        self.assertTrue(all(r['previsao_regional'] == 'pendente_fonte_documental' for r in records))
        process = next(p for p in processes if p['processo_id'] == 'uel-vestibular')
        self.assertEqual(json.loads(process['anos_programa_verificavel_geografia']), [])

    def test_missing_program_source_does_not_become_a_negative(self):
        item = self.inputs['triagem-ne-co-c3.json']['evidencias'][0]
        item['fonte_programa_id'] = 'fonte-ainda-nao-recuperada'
        item['previsao_regional'] = False
        _, evidence, processes = self.integrate()
        record = next(r for r in evidence if r['evidencia_id'] == national._id(item['evidencia_id']))
        self.assertEqual(record['previsao_regional'], 'pendente_fonte_documental')
        self.assertIsNone(record['fonte_url'])
        self.assertFalse(record['programa_verificavel'])
        process = next(p for p in processes if p['processo_id'] == 'ufms-vestibular')
        self.assertEqual(json.loads(process['anos_previsao_integrada']), [2024, 2025])
        self.assertFalse(process['recorrencia_integrada_confirmada'])

    def test_forecast_cannot_supply_a_past_actual_year_or_confirm_recurrence(self):
        sources = self.inputs['triagem-sul-sudeste-c3.json']['fontes']
        next(s for s in sources if s['fonte_id'] == 'fuvest_data_2022')['tipo'] = 'cronograma_edital'
        apps, evidence, processes = self.integrate()
        self.assertEqual(len(apps), 6)
        process = next(p for p in processes if p['processo_id'] == 'usp-fuvest')
        self.assertEqual(json.loads(process['anos_previsao_geografia']), [2022, 2023])
        self.assertEqual(process['estado_triagem'], 'candidato_evidencia_insuficiente')
        record = next(e for e in evidence if e['evidencia_id'] == 'fuvest-2022-geografia-amazonia')
        self.assertIsNone(record['aplicacao_id'])
        self.assertFalse(any(a['processo_id'] == 'uece-vestibular' for a in apps))

    def test_institutional_branches_preserve_scope_as_unconfirmed_leads(self):
        apps, _, processes = self.integrate()
        for key in ['ufmt-ead', 'ufmt-proinq', 'ufrgs-concurso-vestibular']:
            row = next(p for p in processes if p['processo_id'] == key)
            self.assertEqual(row['situacao_identificacao_processo'], 'pista_sem_desenho_confirmado')
            self.assertTrue(row['alcance_triagem'])
            self.assertFalse(any(a['processo_id'] == key for a in apps))
        self.assertFalse(any(p['estado_triagem'].startswith('excluido')
                             for p in processes if p['processo_id'] == 'uva-vestibular'))

    def test_program_requests_are_six_official_programs_without_cadernos(self):
        apps, _, _ = self.integrate()
        docs = national.documentos_selecionados(self.registry, apps)
        self.assertEqual(len(docs), 6)
        self.assertEqual({d['tipo'] for d in docs}, {'programa'})
        self.assertEqual({d['instituicao_sigla'] for d in docs}, {'USP', 'UFMS'})
        for doc in docs:
            self.assertEqual(doc['documento_id'], doc['aplicacao_id'] + '-programa')
            self.assertEqual(doc['escopo_coleta'], 'triagem_nacional_ciclo3')
            self.assertTrue(doc['url_origem'].startswith('https://'))
            self.assertTrue(doc['fonte_url'].startswith('https://'))
            self.assertIsNone(doc['redistribuicao_autorizada'])
        fuvest = next(d for d in docs if d['aplicacao_id'] == 'usp-fuvest2022-f1')
        self.assertTrue(fuvest['url_origem'].startswith('https://www.fuvest.br/'))
        self.assertEqual(national.documentos_selecionados(self.registry, []), [])

    def test_repeated_integration_is_idempotent(self):
        apps, evidence, processes = self.integrate()
        before = copy.deepcopy((apps, evidence, processes))
        national.integrar(self.registry, self.institutions, apps, evidence, processes)
        self.assertEqual((apps, evidence, processes), before)

    def test_existing_unrelated_records_are_preserved(self):
        self.integrate()  # Grava apenas os JSONs de entrada na pasta temporária.
        apps = [{'aplicacao_id': 'ufam-psc2020-e3', 'processo_id': 'ufam-psc'}]
        evidence = [{'evidencia_id': 'evidencia-anterior', 'processo_id': 'ufam-psc'}]
        processes = [{'processo_id': 'ufam-psc', 'estado_triagem': 'incluido_recorrencia_confirmada'}]
        originals = copy.deepcopy((apps[0], evidence[0], processes[0]))
        national.integrar(self.registry, self.institutions, apps, evidence, processes)
        self.assertEqual((apps[0], evidence[0], processes[0]), originals)

    def test_conflicting_effective_year_and_out_of_window_date_are_rejected(self):
        item = self.inputs['triagem-sul-sudeste-c3.json']['evidencias'][0]
        item['ano_aplicacao_verificado'] = 2022
        with self.assertRaisesRegex(ValueError, 'diverge'):
            self.integrate()
        item.update(data_aplicacao='2016-12-12', ano_aplicacao_verificado=2016)
        with self.assertRaisesRegex(ValueError, 'fora da janela'):
            self.integrate()


if __name__ == '__main__':
    unittest.main()
