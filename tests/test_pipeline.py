"""Invariantes de coleta, proveniência e extração; fixtures apenas temporárias."""

import contextlib
import csv
from email.message import Message
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import pipeline


URL = "https://vestibular.example.invalid/prova.pdf"
PDF_FIXTURE = b"%PDF-1.4\n% Conteudo sintetico exclusivo deste teste.\n"


class HTTPResponse(io.BytesIO):
    """Resposta HTTP em memória; não substitui a validação real de fetch_pdf."""

    def __init__(self, body, *, declared=None, mime="application/pdf", final=URL):
        super().__init__(body)
        self.headers = Message()
        self.headers["Content-Type"] = mime
        if declared is not None:
            self.headers["Content-Length"] = str(declared)
        self.final = final
        self.read_sizes = []

    def geturl(self):
        return self.final

    def read(self, size=-1):
        self.read_sizes.append(size)
        return super().read(size)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.registry = self.root / "data/registry"
        self.registry.mkdir(parents=True)
        self.item = {
            "documento_id": "prova-teste", "url_origem": URL,
            "aplicacao_id": "aplicacao-teste", "instituicao_sigla": "TESTE",
            "processo_id": "processo-teste", "tipo": "prova",
            "publicador": "Publicador fictício de teste", "fonte_url": URL,
            "condicoes_uso": "Fixture sintética exclusiva de teste",
        }
        self.save("documentos-esperados.jsonl", [self.item])

    def save(self, filename, rows):
        (self.registry / filename).write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
            encoding="utf-8",
        )

    def cached_record(self, content=PDF_FIXTURE, *, create_file=True):
        digest = hashlib.sha256(content).hexdigest()
        relative = Path("data/raw/documentos") / f"{digest}.pdf"
        path = self.root / relative
        if create_file:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        record = {
            **self.item, "status": "coletado", "sha256": digest,
            "caminho_local": relative.as_posix(), "tamanho_bytes": len(content),
            "url_final": URL, "mime": "application/pdf",
        }
        self.save("documentos.jsonl", [record])
        return record, path

    def test_adulterated_cache_stops_before_network_and_preserves_evidence(self):
        _, path = self.cached_record()
        path.write_bytes(b"original adulterado")
        manifest = (self.registry / "documentos.jsonl").read_bytes()
        with patch.object(pipeline, "fetch_pdf") as fetch:
            with self.assertRaisesRegex(ValueError, "Cache adulterado"):
                pipeline.collect(self.root)
        fetch.assert_not_called()
        self.assertEqual(path.read_bytes(), b"original adulterado")
        self.assertEqual((self.registry / "documentos.jsonl").read_bytes(), manifest)

    def test_valid_cache_needs_no_network_or_rewrite(self):
        _, path = self.cached_record()
        manifest = (self.registry / "documentos.jsonl").read_bytes()
        with patch.object(pipeline, "fetch_pdf") as fetch, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(pipeline.collect(self.root), 0)
        fetch.assert_not_called()
        self.assertEqual(path.read_bytes(), PDF_FIXTURE)
        self.assertEqual((self.registry / "documentos.jsonl").read_bytes(), manifest)

    def test_missing_cached_file_can_be_collected_again(self):
        _, missing = self.cached_record(create_file=False)
        self.assertFalse(missing.exists())
        final_url = "https://cdn.example.invalid/prova.pdf"
        with patch.object(pipeline, "fetch_pdf", return_value=(PDF_FIXTURE, final_url, "application/pdf")) as fetch:
            with patch.object(pipeline.time, "sleep"), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(pipeline.collect(self.root), 0)
        fetch.assert_called_once_with(URL)
        record = json.loads((self.registry / "documentos.jsonl").read_text())
        self.assertEqual(record["status"], "coletado")
        self.assertEqual(record["url_final"], final_url)
        self.assertEqual(record["sha256"], hashlib.sha256(PDF_FIXTURE).hexdigest())
        self.assertEqual((self.root / record["caminho_local"]).read_bytes(), PDF_FIXTURE)
        self.assertTrue((self.registry / "aquisicoes.jsonl").exists())

    def test_fetch_rejects_html_even_when_server_claims_pdf(self):
        response = HTTPResponse(b"<!DOCTYPE html><title>Login</title>")
        with patch.object(pipeline.urllib.request, "urlopen", return_value=response):
            with self.assertRaisesRegex(ValueError, "não é PDF"):
                pipeline.fetch_pdf(URL)

    def test_clean_reproduction_rejects_changed_source_and_keeps_known_manifest(self):
        record, _ = self.cached_record(create_file=False)
        before = (self.registry / 'documentos.jsonl').read_bytes()
        changed = PDF_FIXTURE + b'Outra versao oficial.'
        with patch.object(pipeline, 'fetch_pdf', return_value=(changed, URL, 'application/pdf')):
            with patch.object(pipeline.time, 'sleep'), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(pipeline.collect(self.root), 1)
        self.assertEqual((self.registry / 'documentos.jsonl').read_bytes(), before)
        events = pipeline.read_jsonl(self.registry / 'aquisicoes.jsonl')
        self.assertEqual(events[-1]['status'], 'divergencia_versao_origem')
        self.assertEqual(events[-1]['sha256_esperado'], record['sha256'])
        self.assertEqual((self.root / events[-1]['caminho_nova_versao']).read_bytes(), changed)

    def test_explicit_update_preserves_old_original_and_records_new_hash(self):
        record, old_path = self.cached_record()
        changed = PDF_FIXTURE + b'Nova versao explicitamente solicitada.'
        with patch.object(pipeline, 'fetch_pdf', return_value=(changed, URL, 'application/pdf')):
            with patch.object(pipeline.time, 'sleep'), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(pipeline.collect(self.root, update=True), 0)
        updated = pipeline.read_jsonl(self.registry / 'documentos.jsonl')[0]
        self.assertNotEqual(updated['sha256'], record['sha256'])
        self.assertEqual(old_path.read_bytes(), PDF_FIXTURE)
        events = pipeline.read_jsonl(self.registry / 'aquisicoes.jsonl')
        self.assertEqual(events[-1]['sha256_anterior'], record['sha256'])
        self.assertTrue(events[-1]['atualizacao_explicita'])

    def test_fetch_refuses_declared_oversize_without_reading_body(self):
        response = HTTPResponse(PDF_FIXTURE, declared=1000)
        with patch.object(pipeline.urllib.request, "urlopen", return_value=response):
            with self.assertRaisesRegex(ValueError, "excede limite"):
                pipeline.fetch_pdf(URL, max_bytes=100)
        self.assertEqual(response.read_sizes, [])

    def test_fetch_limits_body_when_length_is_not_declared(self):
        response = HTTPResponse(b"%PDF-1.4\n" + b"X" * 1000)
        with patch.object(pipeline.urllib.request, "urlopen", return_value=response):
            with self.assertRaisesRegex(ValueError, "excede limite"):
                pipeline.fetch_pdf(URL, max_bytes=100)
        self.assertEqual(response.read_sizes, [101])

    def test_fetch_preserves_pdf_and_final_url(self):
        final_url = "https://cdn.example.invalid/prova.pdf"
        response = HTTPResponse(PDF_FIXTURE, declared=len(PDF_FIXTURE), final=final_url)
        with patch.object(pipeline.urllib.request, "urlopen", return_value=response):
            content, final, mime = pipeline.fetch_pdf(URL, max_bytes=len(PDF_FIXTURE))
        self.assertEqual(content, PDF_FIXTURE)
        self.assertEqual(final, final_url)
        self.assertEqual(mime, "application/pdf")

    def test_fetch_rejects_redirect_to_http(self):
        response = HTTPResponse(PDF_FIXTURE, final="http://example.invalid/prova.pdf")
        with patch.object(pipeline.urllib.request, "urlopen", return_value=response):
            with self.assertRaisesRegex(ValueError, "sem HTTPS"):
                pipeline.fetch_pdf(URL)
        self.assertEqual(response.read_sizes, [])

    def test_bbox_retains_page_order_blank_page_unicode_and_coordinates(self):
        fixture = self.root / "bbox.xml"
        fixture.write_text('''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml"><body><doc>
 <page width="595.28" height="841.89"><flow><block>
  <line><word xMin="10.25" yMin="20" xMax="48.5" yMax="30">Questão</word>
   <word xMin="50" yMin="20" xMax="60" yMax="30">01</word></line>
  <line><word xMin="11" yMin="40" xMax="75" yMax="52">Amazônia</word></line>
 </block></flow></page>
 <page width="842" height="595" />
</doc></body></html>''', encoding="utf-8")
        pages = pipeline.parse_bbox(fixture)
        self.assertEqual([page["pagina"] for page in pages], [1, 2])
        self.assertEqual(pages[0]["texto_bruto"], "Questão 01\nAmazônia")
        self.assertEqual(pages[0]["palavras"], 3)
        self.assertEqual(pages[0]["largura"], 595.28)
        self.assertEqual(pages[0]["altura"], 841.89)
        self.assertEqual(pages[0]["linhas"][0]["palavras"][0]["bbox"], [10.25, 20.0, 48.5, 30.0])
        self.assertEqual(pages[1]["texto_bruto"], "")
        self.assertEqual(pages[1]["palavras"], 0)
        self.assertEqual(pages[1]["largura"], 842.0)

    def test_duplicate_expected_documents_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicado"):
            pipeline.validate_expected([self.item, dict(self.item)])

    def test_verification_rejects_duplicate_manifest_records(self):
        record, _ = self.cached_record()
        self.save("documentos.jsonl", [record, dict(record)])
        with self.assertRaisesRegex(ValueError, "duplicados"):
            pipeline.verify(self.root, require_local=False)

    def test_collection_rejects_duplicate_manifest_before_network(self):
        record, _ = self.cached_record()
        self.save("documentos.jsonl", [record, dict(record)])
        with patch.object(pipeline, "fetch_pdf") as fetch, contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(ValueError, "duplicad"):
                pipeline.collect(self.root)
        fetch.assert_not_called()

    def test_report_excludes_extraction_from_previous_pdf_version(self):
        record, _ = self.cached_record()
        self.save("extracoes.jsonl", [{
            "documento_id": self.item["documento_id"], "documento_sha256": "0" * 64,
            "status": "texto_extraido_nao_revisado", "paginas": 99, "palavras": 9999,
        }])
        with contextlib.redirect_stdout(io.StringIO()):
            pipeline.make_report(self.root)
        with (self.root / "reports/tabelas/cobertura-documentos.csv").open(encoding="utf-8", newline="") as handle:
            row = next(csv.DictReader(handle))
        self.assertEqual(row["status_extracao"], "desatualizada")
        self.assertEqual(row["paginas"], "")
        self.assertEqual(row["palavras"], "")
        self.assertEqual(row["sha256"], record["sha256"])
        report = (self.root / "reports/cobertura-inicial.md").read_text(encoding="utf-8")
        self.assertIn("Com extração registrada: **0**", report)

    def test_report_counts_extraction_from_current_pdf_version(self):
        record, _ = self.cached_record()
        self.save("extracoes.jsonl", [{
            "documento_id": self.item["documento_id"], "documento_sha256": record["sha256"],
            "status": "texto_extraido_nao_revisado", "paginas": 2, "palavras": 30,
        }])
        with contextlib.redirect_stdout(io.StringIO()):
            pipeline.make_report(self.root)
        with (self.root / "reports/tabelas/cobertura-documentos.csv").open(encoding="utf-8", newline="") as handle:
            row = next(csv.DictReader(handle))
        self.assertEqual(row["status_extracao"], "texto_extraido_nao_revisado")
        self.assertEqual(row["paginas"], "2")
        report = (self.root / "reports/cobertura-inicial.md").read_text(encoding="utf-8")
        self.assertIn("Com extração registrada: **1**", report)


if __name__ == "__main__":
    unittest.main()
