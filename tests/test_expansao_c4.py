"""Integração C4 em memória; datas, identidade e proveniência sem rede."""

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts import expansao_documental as expansion


URL = 'https://example.invalid/prova.pdf'
PROGRAM = 'https://example.invalid/programa.pdf'
HASH = hashlib.sha256(b'Fixture sintetica de programa').hexdigest()


class ExpansionCycleFourTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.registry = Path(temporary.name)
        self.item = {
            'aplicacao_id': 'teste-2026', 'processo_id': 'teste-processo',
            'instituicao_sigla': 'TESTE', 'etapa': 'unica', 'edicao': 'Edição2026',
            'ano_ingresso': 2026, 'data_aplicacao': '2025-12-07',
            'data_aplicacao_prevista': None, 'situacao': 'aplicada_documentos_localizados',
            'evidencia_data': {'url': 'https://example.invalid/noticia',
                               'natureza': 'noticia_pos_aplicacao', 'localizacao': 'Cabeçalho e relato'},
            'fonte_landing': 'https://example.invalid/processo',
            'documentos': [{'documento_id': 'teste-2026-prova', 'tipo': 'prova',
                            'url': URL, 'publicador': 'Instituição fictícia', 'origem_oficial': True}],
        }
        self.applications, self.evidence, self.expected = [], [], []
        self.processes = [{'processo_id': 'teste-processo', 'etapas': '[]',
                           'estado_triagem': 'candidato_evidencia_insuficiente'}]

    def save(self, value):
        (self.registry / 'expansao-fixture-c4.json').write_text(
            json.dumps(value, ensure_ascii=False), encoding='utf-8')

    def invoke(self, payload=None):
        if payload is not None:
            self.save(payload)
        expansion.integrar(self.registry, {'TESTE': 'inep_teste'}, self.applications,
                            self.evidence, self.processes, self.expected)

    def program(self):
        return {'disciplina': 'geografia', 'previsao_regional': 'substantiva',
                'paginas_pdf': [4], 'localizacao': 'Programa sintético',
                'trecho_curto': 'Conteúdo fictício', 'fonte_url': PROGRAM}

    def test_repeated_integration_keeps_ids_metadata_and_counts_identical(self):
        self.item['programa'] = [self.program()]
        self.invoke({'aplicacoes': [self.item]})
        before = copy.deepcopy((self.applications, self.evidence, self.processes, self.expected))
        self.invoke()
        self.assertEqual((self.applications, self.evidence, self.processes, self.expected), before)
        self.assertEqual(len(self.applications), 1)
        self.assertEqual(len(self.expected), 1)
        self.assertEqual(self.applications[0]['ano_aplicacao'], 2025)
        self.assertEqual(self.applications[0]['ano_ingresso'], 2026)
        self.assertEqual(json.loads(self.processes[0]['anos_previsao_geografia']), [2025])
        self.assertEqual(self.processes[0]['estado_triagem'], 'candidato_evidencia_insuficiente')
        self.assertEqual(self.evidence[0]['revisao_humana'], 'pendente')

    def test_same_document_identity_cannot_silently_switch_url(self):
        self.invoke({'aplicacoes': [self.item]})
        old = copy.deepcopy(self.expected[0])
        self.item['documentos'][0]['url'] = 'https://example.invalid/outra-versao.pdf'
        with self.assertRaisesRegex(ValueError, 'conflita com identidade'):
            self.invoke({'aplicacoes': [self.item]})
        self.assertEqual(self.expected, [old])

    def test_later_program_version_is_preserved_without_claiming_its_pre_exam_adoption(self):
        program = self.program()
        program.update(vigencia_confirmada=False,
                       previsao_regional_documento='substantiva',
                       previsao_regional='pendente_vigencia_versao_programa')
        self.item['programa'] = [program]
        self.invoke({'aplicacoes': [self.item]})
        self.assertEqual(self.evidence[0]['previsao_regional_documento'], 'substantiva')
        self.assertFalse(self.evidence[0]['vigencia_confirmada'])
        self.assertNotIn('anos_previsao_geografia', self.processes[0])
        self.assertNotIn('anos_programa_verificavel_geografia', self.processes[0])

    def test_explicitly_distinct_versions_keep_two_files_and_one_application(self):
        second = {**self.item['documentos'][0], 'documento_id': 'teste-2026-prova-digital',
                  'url': 'https://example.invalid/digital.pdf', 'modalidade': 'digital'}
        self.item['documentos'].append(second)
        self.invoke({'aplicacoes': [self.item]})
        self.assertEqual(len(self.applications), 1)
        self.assertEqual(len(self.expected), 2)
        self.assertEqual({d['url_origem'] for d in self.expected}, {URL, second['url']})

    def test_future_forecast_does_not_create_actual_year_or_recurrence(self):
        self.item.update(data_aplicacao=None, data_aplicacao_prevista='2026-12-06',
                         situacao='futura_na_data_de_corte', programa=[self.program()])
        self.item['evidencia_data']['natureza'] = 'cronograma_edital'
        self.invoke({'aplicacoes': [self.item]})
        row = self.applications[0]
        self.assertIsNone(row['data_aplicacao'])
        self.assertIsNone(row['ano_aplicacao'])
        self.assertIsNone(row['periodo_calendario'])
        self.assertEqual(row['data_prevista'], '2026-12-06')
        self.assertNotIn('anos_previsao_geografia', self.processes[0])
        self.assertNotIn('anos_programa_verificavel_geografia', self.processes[0])

    def test_actual_date_backed_only_by_schedule_is_rejected(self):
        self.item['evidencia_data']['natureza'] = 'cronograma_edital'
        with self.assertRaisesRegex(ValueError, 'sem natureza primária de realização'):
            self.invoke({'aplicacoes': [self.item]})
        self.assertFalse(self.applications)
        self.assertFalse(self.expected)

    def test_dated_official_answer_key_is_recognized_as_actual_evidence(self):
        self.item['evidencia_data']['natureza'] = 'gabarito_oficial_pos_aplicacao'
        self.invoke({'aplicacoes': [self.item]})
        self.assertEqual(self.applications[0]['data_aplicacao'], '2025-12-07')
        self.assertEqual(self.applications[0]['qualidade_evidencia_data'],
                         'gabarito_oficial_pos_aplicacao')

    def test_2016_application_and_its_documents_stay_outside_main_window(self):
        self.item.update(data_aplicacao='2016-12-18', situacao='excluido_fora_janela',
                         programa=[self.program()])
        self.invoke({'aplicacoes': [self.item]})
        self.assertEqual((self.applications, self.evidence, self.expected), ([], [], []))
        self.assertEqual(self.processes[0]['etapas'], '[]')
        self.item['situacao'] = 'aplicada_documentos_localizados'
        with self.assertRaisesRegex(ValueError, 'fora da janela sem exclusão explícita'):
            self.invoke({'aplicacoes': [self.item]})

    def test_invalid_calendar_date_is_not_accepted_by_string_order(self):
        self.item['data_aplicacao'] = '2025-02-31'
        with self.assertRaises(ValueError):
            self.invoke({'aplicacoes': [self.item]})
        self.assertFalse(self.applications)

    def test_top_level_documents_keep_source_metadata_and_expected_hash(self):
        doc = self.item.pop('documentos')[0]
        doc.update(aplicacao_id=self.item['aplicacao_id'], sha256_esperado=HASH,
                   origem_documentada={'url_indice': 'https://example.invalid/indice', 'rotulo': 'Prova'},
                   modalidade='digital', paginas_pdf_total=7,
                   escopo_paginas_publicas=[{'finalidade': 'gabarito', 'paginas_pdf': [2]}],
                   bases_digital=[{'anexo': 'III', 'intervalo_pdf': [3, 7]}],
                   fonte_url='https://example.invalid/publicacao-especifica')
        self.invoke({'aplicacoes': [self.item], 'documentos': [doc]})
        result = self.expected[0]
        for field in ['origem_documentada', 'modalidade', 'paginas_pdf_total',
                      'escopo_paginas_publicas', 'bases_digital', 'fonte_url']:
            self.assertEqual(result[field], doc[field])
        self.assertEqual(result['sha256_auditado'], HASH)
        self.assertEqual(result['bases_digitais'], doc['bases_digital'])
        self.assertEqual(result['url_origem'], URL)

    def test_conflicting_pinned_hash_cannot_be_overwritten(self):
        self.item['documentos'][0]['sha256_auditado'] = HASH
        self.invoke({'aplicacoes': [self.item]})
        old = copy.deepcopy(self.expected)
        self.item['documentos'][0]['sha256_auditado'] = 'f' * 64
        with self.assertRaisesRegex(ValueError, 'hash já preservado'):
            self.invoke({'aplicacoes': [self.item]})
        self.assertEqual(self.expected, old)

    def test_shared_program_owned_in_c4_keeps_one_source_hash_and_links_both_days(self):
        first = copy.deepcopy(self.item)
        second = copy.deepcopy(self.item)
        second.update(aplicacao_id='teste-2026-dia2', data_aplicacao='2025-12-08')
        first['documentos'] = [{'documento_id': 'programa-compartilhado', 'tipo': 'programa',
                               'url': PROGRAM, 'publicador': 'Instituição fictícia',
                               'origem_oficial': True, 'sha256_esperado': HASH}]
        second['documentos'] = []
        for item in [first, second]:
            item['programa_documento_id'] = 'programa-compartilhado'
            item['programa'] = [self.program()]
        shared = {'documento_id': 'programa-compartilhado', 'url': PROGRAM,
                  'fonte_adocao': 'https://example.invalid/edicao', 'sha256_auditado': HASH,
                  'paginas_pdf': [4], 'retificacoes': ['R1-sintetica']}
        # A referência pode aparecer antes da aplicação que possui o arquivo.
        self.invoke({'aplicacoes': [second, first], 'programas_compartilhados': [shared]})
        self.assertEqual(len(self.applications), 2)
        self.assertEqual(len(self.expected), 1)
        known = self.expected[0]
        self.assertEqual(known['aplicacao_id'], first['aplicacao_id'])
        self.assertEqual(known['sha256_auditado'], HASH)
        self.assertEqual(known['fonte_adocao'], shared['fonte_adocao'])
        self.assertEqual(known['referencia_programa_compartilhado']['retificacoes'], ['R1-sintetica'])
        self.assertEqual(known['aplicacoes_vinculadas'], sorted([first['aplicacao_id'], second['aplicacao_id']]))
        self.assertEqual({e['documento_id_programa'] for e in self.evidence}, {'programa-compartilhado'})
        before = copy.deepcopy((self.applications, self.evidence, self.expected))
        self.invoke()
        self.assertEqual((self.applications, self.evidence, self.expected), before)

    def test_shared_program_cannot_change_the_existing_url_or_hash(self):
        self.expected.append({'documento_id': 'programa-compartilhado',
                              'aplicacao_id': 'dono-c3', 'url_origem': PROGRAM,
                              'sha256_auditado': HASH, 'tipo': 'programa'})
        before = copy.deepcopy(self.expected)
        for changes in [{'url': URL}, {'sha256_esperado': 'f' * 64}]:
            shared = {'documento_id': 'programa-compartilhado', 'url': PROGRAM, **changes}
            with self.assertRaises(ValueError):
                self.invoke({'aplicacoes': [self.item], 'programas_compartilhados': [shared]})
            self.assertEqual(self.expected, before)

    def test_real_ufms_variants_enrich_three_existing_events_without_making_six(self):
        root = Path(__file__).resolve().parents[1]
        source = json.loads((root / 'data/registry/expansao-ufms-c4.json').read_text())
        self.save(source)
        apps = [{k: a[k] for k in ['aplicacao_id', 'processo_id', 'data_aplicacao']}
                for a in source['aplicacoes']]
        processes = [{'processo_id': 'ufms-vestibular', 'etapas': '["objetiva_redacao"]',
                      'estado_triagem': 'candidato_evidencia_insuficiente'}]
        evidence, expected = [], []
        expansion.integrar(self.registry, {'UFMS': 'inep_694'}, apps, evidence, processes, expected)
        self.assertEqual(len(apps), 3)
        self.assertEqual(len(expected), len(source['documentos']))
        self.assertEqual(sum(len(json.loads(a['variantes_documentadas'])) for a in apps), 6)
        self.assertEqual(len([d for d in expected if d.get('bases_digitais')]), 3)
        self.assertEqual(len([d for d in expected if d.get('sha256_auditado')]), 3)
        self.assertTrue(all(d.get('origem_documentada') for d in expected))
        self.assertFalse(evidence)
        self.assertEqual(processes[0]['estado_triagem'], 'candidato_evidencia_insuficiente')
        self.assertTrue(all('denominadores_validados' not in a for a in apps))
        before = copy.deepcopy((apps, expected))
        expansion.integrar(self.registry, {'UFMS': 'inep_694'}, apps, evidence, processes, expected)
        self.assertEqual((apps, expected), before)

    def test_real_fuvest_programs_are_shared_without_repeating_owner_files(self):
        root = Path(__file__).resolve().parents[1]
        source = json.loads((root / 'data/registry/expansao-fuvest-c4.json').read_text())
        self.save(source)
        apps, evidence, expected = [], [], []
        process_id = source['aplicacoes'][0]['processo_id']
        processes = [{'processo_id': process_id, 'etapas': '[]',
                      'estado_triagem': 'candidato_evidencia_insuficiente'}]
        expansion.integrar(self.registry, {'USP': 'inep_teste'}, apps, evidence, processes, expected)
        self.assertEqual(len(apps), len(source['aplicacoes']))
        programs = [d for d in expected if d['documento_id'] in
                    {p['documento_id'] for p in source['programas_compartilhados']}]
        self.assertEqual(len(programs), len(source['programas_compartilhados']))
        self.assertEqual(len({d['documento_id'] for d in expected}), len(expected))
        self.assertTrue(all(a['revisao_humana'] == 'pendente' for a in apps))
        self.assertTrue(all(e['revisao_humana'] == 'pendente' for e in evidence))
        self.assertEqual(processes[0]['estado_triagem'], 'candidato_evidencia_insuficiente')


if __name__ == '__main__':
    unittest.main()
