"""Integração C3 com fontes reais imutáveis e saídas exclusivamente temporárias."""

import copy
import csv
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import gabaritos, pipeline

with patch.dict(sys.modules, {'pipeline': pipeline}):
    from scripts import consolidar_registro as consolidate

ROOT = Path(__file__).resolve().parents[1]
PURPOSE = 'definitivo_indicado_no_indice_sem_confirmacao_no_arquivo'


class AuditConsolidationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.registry = Path(temporary.name)
        for name in ['expansao-ufam-c2.json', 'auditoria-datas-c3.json']:
            (self.registry / name).write_bytes((ROOT / 'data/registry' / name).read_bytes())
        pipeline.write_jsonl(self.registry / 'documentos-esperados.jsonl', [])
        self.audit = json.loads((self.registry / 'auditoria-datas-c3.json').read_text())
        self.process = {'processo_id': 'ufam-psc', 'estado_triagem': 'candidato_evidencia_insuficiente',
                        'anos_previsao_historia': '[]', 'anos_previsao_geografia': '[]',
                        'anos_programa_verificavel_historia': '[]',
                        'anos_programa_verificavel_geografia': '[]'}

    def expand(self):
        apps, evidence, processes = [], [], [copy.deepcopy(self.process)]
        docs = consolidate.expand(self.registry, {'UFAM': 'inep_teste'}, apps, evidence, processes)
        return {a['aplicacao_id']: a for a in apps}, evidence, processes, docs

    def test_primary_dates_enter_recurrence_and_five_forecasts_stay_pending(self):
        source = self.registry / 'expansao-ufam-c2.json'
        original = source.read_bytes()
        apps, _, processes, _ = self.expand()
        for stage in [1, 2, 3]:
            app = apps[f'ufam-psc2019-e{stage}']
            self.assertEqual(app['data_aplicacao'], '2018-12-02')
            self.assertEqual(app['data_prevista'], '2018-12-02')
            self.assertEqual(app['ano_aplicacao'], 2018)
            self.assertEqual(app['periodo_calendario'], '2017-2021')
            self.assertIn('/9148-', app['fonte_data'])
            self.assertIn('Edital_', app['fonte_cronograma'])
            self.assertEqual(app['revisao_humana'], 'pendente')
        pending = {row['aplicacao_id']: row['data_aplicacao_prevista']
                   for row in self.audit['verificacoes'] if row['data_aplicacao_confirmada'] is None}
        self.assertEqual(len(pending), 5)
        for key, forecast in pending.items():
            with self.subTest(application=key):
                self.assertIsNone(apps[key]['data_aplicacao'])
                self.assertIsNone(apps[key]['ano_aplicacao'])
                self.assertIsNone(apps[key]['periodo_calendario'])
                self.assertEqual(apps[key]['data_prevista'], forecast)
                self.assertIn('noticia_terceiro_pos_evento', apps[key]['fonte_corrobora'])
        for discipline in ['historia', 'geografia']:
            years = json.loads(processes[0]['anos_previsao_' + discipline])
            self.assertIn(2018, years)
            self.assertNotIn(2021, years)
            self.assertNotIn(2023, years)
        self.assertEqual(source.read_bytes(), original)

    def test_future_announcement_cannot_supply_a_confirmed_day(self):
        row = next(r for r in self.audit['verificacoes'] if r['aplicacao_id'] == 'ufam-psc2021-e3')
        row['data_aplicacao_confirmada'] = row['data_aplicacao_prevista']
        (self.registry / 'auditoria-datas-c3.json').write_text(json.dumps(self.audit))
        with self.assertRaisesRegex(ValueError, 'sem confirmação primária'):
            self.expand()

    def test_additional_documents_have_four_stable_links_for_three_urls(self):
        _, _, _, docs = self.expand()
        added = [d for d in docs if d.get('escopo_coleta') == 'auditoria_documental_ciclo3']
        self.assertEqual(len(added), 4)
        self.assertEqual(len({d['url_origem'] for d in added}), 3)
        self.assertEqual({d['aplicacao_id'] for d in added}, {'ufam-psc2019-e1', 'ufam-psc2019-e2'})
        self.assertTrue(all(d['transporte'] == 'curl_tls_sistema' and d['publicador'] == 'COMPEC/UFAM'
                            and d['origem_oficial'] for d in added))
        pipeline.validate_expected(docs)
        pipeline.write_jsonl(self.registry / 'documentos-esperados.jsonl', docs)
        repeated = self.expand()[3]
        self.assertEqual(docs, repeated)
        key = next(d for d in repeated if d['documento_id'] == 'ufam-psc2019-e2-gabarito-definitivo')
        self.assertEqual(key['tipo'], 'gabarito_definitivo')
        self.assertEqual(key['finalidade_documental'], PURPOSE)
        self.assertEqual(key['sha256_finalidade_documental'],
                         self.audit['auditoria_gabaritos'][0]['sha256_arquivo'])

    def test_cached_collection_refreshes_purpose_without_replacing_original_bytes(self):
        root = self.registry
        registry = root / pipeline.REGISTRY
        registry.mkdir(parents=True)
        local = root / 'data/raw/fixture.pdf'
        local.parent.mkdir(parents=True)
        local.write_bytes(b'%PDF-1.4\n% fixture somente para testar cache\n%%EOF\n')
        digest = hashlib.sha256(local.read_bytes()).hexdigest()
        source = {'documento_id': 'teste-gabarito', 'aplicacao_id': 'teste-aplicacao',
                  'instituicao_sigla': 'TESTE', 'processo_id': 'teste', 'tipo': 'gabarito_definitivo',
                  'publicador': 'Publicador de teste', 'fonte_url': 'https://example.invalid/indice',
                  'url_origem': 'https://example.invalid/gabarito.pdf', 'condicoes_uso': 'nao_verificadas',
                  'status': 'coletado', 'caminho_local': 'data/raw/fixture.pdf', 'sha256': digest,
                  'coletado_em': '2026-11-11T00:00:00Z', 'url_final': 'https://example.invalid/gabarito.pdf',
                  'mime': 'application/pdf', 'tamanho_bytes': local.stat().st_size}
        expected = {k: v for k, v in source.items() if k not in {
            'status', 'caminho_local', 'sha256', 'coletado_em', 'url_final', 'mime', 'tamanho_bytes'}}
        expected.update(finalidade_documental=PURPOSE, sha256_finalidade_documental=digest)
        pipeline.write_jsonl(registry / 'documentos.jsonl', [source])
        pipeline.write_jsonl(registry / 'documentos-esperados.jsonl', [expected])
        with patch.object(pipeline, 'fetch_pdf', side_effect=AssertionError('cache não deve baixar')):
            pipeline.collect(root, attempts=1, interval=1)
        collected = pipeline.read_jsonl(registry / 'documentos.jsonl')[0]
        self.assertEqual(collected['finalidade_documental'], PURPOSE)
        for field in ['sha256', 'coletado_em', 'url_final', 'caminho_local', 'tamanho_bytes']:
            self.assertEqual(collected[field], source[field])
        self.assertEqual(hashlib.sha256(local.read_bytes()).hexdigest(), digest)
        self.assertEqual(collected['tipo'], 'gabarito_definitivo')


class AuditAnswerTests(unittest.TestCase):
    def test_audit_requires_both_document_identity_and_hash(self):
        finding = {'documento_id': 'ufam-psc2019-e2-gabarito-definitivo',
                   'sha256_arquivo': 'a' * 64, 'resultado': PURPOSE}
        for document in [
            {'documento_id': 'outro-gabarito', 'sha256': 'a' * 64},
            {'documento_id': finding['documento_id'], 'sha256': 'b' * 64},
        ]:
            with self.subTest(document=document):
                self.assertIsNone(gabaritos.documentary_purpose(document, [finding]))
        self.assertEqual(gabaritos.documentary_purpose(
            {'documento_id': finding['documento_id'], 'sha256': 'a' * 64}, [finding]), PURPOSE)

    def test_link_preserves_published_letters_and_annulment_with_pending_purpose(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry = root / 'data/registry'
            processed = root / 'data/processed'
            registry.mkdir(parents=True)
            processed.mkdir(parents=True)
            digest = gabaritos.UFAM_LEGACY_VERIFIED[(2019, 2)]['sha256']
            document = {'documento_id': 'ufam-psc2019-e2-gabarito-definitivo',
                        'aplicacao_id': 'ufam-psc2019-e2', 'sha256': digest,
                        'status': 'coletado', 'origem_oficial': True, 'tipo': 'gabarito_definitivo',
                        'url_origem': 'https://example.invalid/gabarito.pdf'}
            pipeline.write_jsonl(registry / 'documentos.jsonl', [document])
            pipeline.write_jsonl(registry / 'extracoes.jsonl', [])
            (registry / 'auditoria-datas-c3.json').write_text(json.dumps({'auditoria_gabaritos': [{
                'documento_id': document['documento_id'], 'sha256_arquivo': digest, 'resultado': PURPOSE}]}))
            pipeline.write_csv(processed / 'questoes.csv', [
                {'ocorrencia_id': f'fixture-q{number}', 'aplicacao_id': 'ufam-psc2019-e2',
                 'numero_questao': number, 'disciplina': 'historia'} for number in [17, 18]],
                ['ocorrencia_id', 'aplicacao_id', 'numero_questao', 'disciplina'])
            # Página sintética: testa propagação da finalidade, não o conteúdo do PDF real.
            pages = [(1, 'PROCESSO SELETIVO CONTÍNUO PSC\nPROJETO 2020 / 2ª ETAPA\nGABARITO\n17 C\n18 ANULAR')]
            with patch.object(gabaritos, 'load_pages', return_value=pages):
                rows = gabaritos.link(root)
            self.assertEqual(rows[0]['alternativa_oficial'], 'C')
            self.assertEqual(rows[0]['estado_oficial'], 'alternativa_publicada')
            self.assertIsNone(rows[1]['alternativa_oficial'])
            self.assertEqual(rows[1]['estado_oficial'], 'anulada')
            self.assertEqual(rows[1]['marcador_oficial'], 'ANULAR')
            self.assertTrue(all(row['finalidade_documental'] == PURPOSE for row in rows))
            self.assertTrue(all(json.loads(row['problemas']) == [] for row in rows))
            self.assertEqual(pipeline.read_jsonl(registry / 'documentos.jsonl')[0]['tipo'], 'gabarito_definitivo')
            with (processed / 'gabaritos.csv').open(newline='') as stream:
                exported = list(csv.DictReader(stream))
            self.assertTrue(all(row['finalidade_documental'] == PURPOSE for row in exported))


if __name__ == '__main__':
    unittest.main()
