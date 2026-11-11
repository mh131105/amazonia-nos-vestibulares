"""Preservação de fontes normativas, sem rede nem alteração dos originais reais."""

import contextlib
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts import contexto_normativo as contexto


PDF = b'%PDF-1.4\n% Documento normativo sintetico exclusivo do teste.\n'
URL = 'https://example.invalid/ato.pdf'


class ContextoNormativoTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.manifest = self.root / 'data/registry/contexto-normativo.json'
        self.manifest.parent.mkdir(parents=True)

    def source(self, *, identifier='TESTE', content=PDF, cached=True):
        digest = hashlib.sha256(content).hexdigest()
        local = self.root / 'data/raw/contexto' / (digest + '.pdf')
        if cached:
            local.parent.mkdir(parents=True, exist_ok=True)
            local.write_bytes(content)
        return {'fonte_id': identifier, 'url': URL, 'formato': 'pdf',
                'sha256': digest, 'caminho_local': local.relative_to(self.root).as_posix(),
                'coletado_em': '2026-11-11T10:00:00+00:00', 'status': 'coletado'}

    def save(self, *sources):
        self.manifest.write_text(json.dumps({'fontes': sources}, ensure_ascii=False) + '\n', encoding='utf-8')
        return self.manifest.read_bytes()

    def invoke(self, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return contexto.collect(self.root, **kwargs)

    def events(self):
        return [json.loads(line) for line in
                (self.manifest.parent / 'aquisicoes-contexto.jsonl').read_text().splitlines()]

    def test_real_archived_sources_verify_offline_without_network_or_rewriting(self):
        root = Path(__file__).resolve().parents[1]
        manifest = root / 'data/registry/contexto-normativo.json'
        before = manifest.read_bytes()
        registry = json.loads(before)
        originals = {s['caminho_local']: (root / s['caminho_local']).read_bytes()
                     for s in registry['fontes']}
        with patch.object(contexto, 'fetch_pdf_curl', side_effect=AssertionError('Rede proibida')) as fetch:
            with patch.object(contexto.subprocess, 'run', side_effect=AssertionError('curl proibido')) as run:
                with patch.object(contexto.time, 'sleep', side_effect=AssertionError('Espera desnecessária')):
                    with contextlib.redirect_stdout(io.StringIO()):
                        result = contexto.collect(root, offline=True)
        self.assertEqual({s['fonte_id'] for s in result['fontes']}, {'S2', 'S3', 'S4', 'S5', 'S6'})
        self.assertEqual(manifest.read_bytes(), before)
        for relative, content in originals.items():
            self.assertEqual((root / relative).read_bytes(), content)
        fetch.assert_not_called()
        run.assert_not_called()

    def test_valid_cache_is_reused_without_rewriting_or_network(self):
        source = self.source()
        before = self.save(source)
        original = self.root / source['caminho_local']
        with patch.object(contexto, 'fetch_pdf_curl') as fetch:
            self.invoke()
        fetch.assert_not_called()
        self.assertEqual(self.manifest.read_bytes(), before)
        self.assertEqual(original.read_bytes(), PDF)
        self.assertFalse((self.manifest.parent / 'aquisicoes-contexto.jsonl').exists())

    def test_offline_missing_original_reports_source_and_keeps_manifest(self):
        source = self.source(cached=False)
        before = self.save(source)
        with patch.object(contexto, 'fetch_pdf_curl') as fetch:
            with self.assertRaisesRegex(ValueError, 'offline: TESTE') as failure:
                self.invoke(offline=True)
        fetch.assert_not_called()
        self.assertIn(source['caminho_local'], str(failure.exception))
        self.assertEqual(self.manifest.read_bytes(), before)

    def test_later_tampered_cache_stops_before_acquiring_an_earlier_missing_source(self):
        missing = self.source(identifier='AUSENTE', cached=False)
        damaged = self.source(identifier='ALTERADO', content=PDF + b'Outra fonte')
        local = self.root / damaged['caminho_local']
        local.write_bytes(b'Bytes adulterados')
        before = self.save(missing, damaged)
        with patch.object(contexto, 'fetch_pdf_curl') as fetch:
            with self.assertRaisesRegex(ValueError, 'local alterado: ALTERADO'):
                self.invoke()
        fetch.assert_not_called()
        self.assertEqual(self.manifest.read_bytes(), before)
        self.assertEqual(local.read_bytes(), b'Bytes adulterados')

    def test_offline_never_fetches_if_original_disappears_after_initial_verification(self):
        source = self.source()
        self.save(source)
        local = self.root / source['caminho_local']

        def verify_then_remove(path):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            path.unlink()
            return digest

        with patch.object(contexto, 'sha256', side_effect=verify_then_remove):
            with patch.object(contexto, 'fetch_pdf_curl') as fetch:
                with self.assertRaisesRegex(ValueError, 'offline: TESTE'):
                    self.invoke(offline=True)
        fetch.assert_not_called()
        self.assertFalse(local.exists())

    def test_clean_clone_recovers_known_bytes_without_changing_pinned_metadata(self):
        source = self.source(cached=False)
        before = self.save(source)
        with patch.object(contexto, 'fetch_pdf_curl', return_value=(PDF, URL, 'application/pdf')):
            with patch.object(contexto.time, 'sleep'):
                self.invoke()
        self.assertEqual(self.manifest.read_bytes(), before)
        self.assertEqual((self.root / source['caminho_local']).read_bytes(), PDF)
        self.assertEqual(self.events()[-1]['status'], 'cache_recuperado')

    def test_changed_remote_bytes_are_archived_and_rejected_without_update(self):
        source = self.source(cached=False)
        before = self.save(source)
        changed = PDF + b'Nova versao remota'
        with patch.object(contexto, 'fetch_pdf_curl', return_value=(changed, URL, 'application/pdf')):
            with patch.object(contexto.time, 'sleep'):
                with self.assertRaisesRegex(ValueError, 'Fonte normativa mudou'):
                    self.invoke()
        self.assertEqual(self.manifest.read_bytes(), before)
        event = self.events()[-1]
        self.assertEqual(event['sha256_esperado'], source['sha256'])
        self.assertEqual(event['sha256_recebido'], hashlib.sha256(changed).hexdigest())
        self.assertEqual((self.root / event['caminho_nova_versao']).read_bytes(), changed)

    def test_explicit_update_preserves_previous_original_and_records_both_hashes(self):
        source = self.source()
        self.save(source)
        changed = PDF + b'Atualizacao explicita'
        with patch.object(contexto, 'fetch_pdf_curl', return_value=(changed, URL, 'application/pdf')):
            with patch.object(contexto.time, 'sleep'):
                result = self.invoke(update=True)
        new = result['fontes'][0]
        self.assertEqual((self.root / source['caminho_local']).read_bytes(), PDF)
        self.assertEqual((self.root / new['caminho_local']).read_bytes(), changed)
        self.assertNotEqual(new['sha256'], source['sha256'])
        self.assertEqual(self.events()[-1]['sha256_anterior'], source['sha256'])

    def test_error_html_is_not_archived_as_a_legal_source(self):
        self.save({'fonte_id': 'HTML', 'url': 'https://example.invalid/ato.html',
                   'formato': 'html', 'marcadores_obrigatorios': ['Lei 13.415', 'Art. 12']})
        before = self.manifest.read_bytes()

        def response(command, **kwargs):
            Path(command[command.index('--output') + 1]).write_bytes(b'<html>Limite de acesso</html>')
            return subprocess.CompletedProcess(command, 0,
                stdout=json.dumps({'url_effective': 'https://example.invalid/ato.html',
                                   'content_type': 'text/html'}).encode(), stderr=b'')

        with patch.object(contexto.subprocess, 'run', side_effect=response):
            with patch.object(contexto.time, 'sleep'):
                with self.assertRaisesRegex(ValueError, 'não contém o ato esperado'):
                    self.invoke()
        self.assertEqual(self.manifest.read_bytes(), before)
        self.assertFalse((self.root / 'data/raw/contexto').exists())

    def test_offline_and_update_are_incompatible_before_any_network(self):
        self.save(self.source())
        with patch.object(contexto, 'fetch_pdf_curl') as fetch:
            with self.assertRaisesRegex(ValueError, 'offline não permite atualização'):
                self.invoke(offline=True, update=True)
        fetch.assert_not_called()


if __name__ == '__main__':
    unittest.main()
