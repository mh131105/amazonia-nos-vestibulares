"""Regressões de controles XML, geometria e transporte TLS; sem rede ou corpus."""

import json
from pathlib import Path
import ssl
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

from scripts import pipeline

URL = 'https://fonte.example.invalid/prova.pdf'
PDF = b'%PDF-1.4\n% Fixture sintetica exclusiva do teste.\n'


class ExtractionCycleTwoTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def xml(self, content):
        path = self.root / 'fixture.xml'
        path.write_text(content, encoding='utf-8')
        return path

    def curl(self, *, body=PDF, final=URL, code=0, status=200, mime='application/pdf'):
        def invoke(command, **kwargs):
            self.assertEqual(command[0], 'curl')
            path = Path(command[command.index('--output') + 1])
            path.write_bytes(body)
            return subprocess.CompletedProcess(command, code,
                json.dumps({'url_effective': final, 'http_code': status, 'content_type': mime}).encode(),
                b'Diagnostico sintetico de teste' if code else b'')
        return invoke

    def test_bbox_replaces_illegal_control_without_dropping_text_or_coordinates(self):
        path = self.xml('<html xmlns="http://www.w3.org/1999/xhtml"><body><doc>'
                        '<page width="595.32" height="842.04"><flow><block><line>'
                        '<word xMin="20.5" yMin="41.25" xMax="83.75" yMax="55.5">Amaz\x01ônia</word>'
                        '<word xMin="85" yMin="41.25" xMax="105" yMax="55.5">teste</word>'
                        '</line></block></flow></page></doc></body></html>')
        original = path.read_bytes()
        pages = pipeline.parse_bbox(path)
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(pages[0]['texto_bruto'], 'Amaz\ufffdônia teste')
        self.assertEqual(pages[0]['palavras'], 2)
        self.assertEqual(pages[0]['linhas'][0]['palavras'][0]['bbox'], [20.5, 41.25, 83.75, 55.5])
        self.assertEqual(pipeline.xml_text(path)[1], 1)

    def test_pdftohtml_preserves_real_fragment_box_without_inventing_word_boxes(self):
        path = self.xml('<pdf2xml><page number="1" width="600" height="840">'
                        '<text top="22.5" left="31.25" width="180.75" height="14.5" font="0">'
                        'Texto <b>de exemplo</b> completo</text>'
                        '<text top="22.5" left="320" width="115" height="14.5">Outra coluna</text>'
                        '</page></pdf2xml>')
        pages, controls = pipeline.parse_pdftohtml(path)
        first = pages[0]['linhas'][0]
        self.assertEqual(controls, 0)
        self.assertEqual(first['texto'], 'Texto de exemplo completo')
        self.assertEqual(len(first['palavras']), 1)
        self.assertEqual(first['palavras'][0], {'texto': 'Texto de exemplo completo',
                                               'bbox': [31.25, 22.5, 212.0, 37.0]})
        self.assertEqual(first['granularidade_coordenadas'], 'fragmento_textual')
        self.assertEqual(pages[0]['palavras'], 6)
        self.assertEqual(pages[0]['linhas'][1]['palavras'][0]['bbox'], [320.0, 22.5, 435.0, 37.0])

    def test_pdftohtml_keeps_blank_page_and_marks_replacement_without_rewriting_source(self):
        path = self.xml('<pdf2xml><page number="1" width="600" height="840">'
                        '<text top="10" left="10" width="100" height="12">Parte\x0b final</text>'
                        '</page><page number="2" width="600" height="840"/></pdf2xml>')
        before = path.read_bytes()
        pages, controls = pipeline.parse_pdftohtml(path)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(controls, 1)
        self.assertEqual(pages[0]['texto_bruto'], 'Parte\ufffd final')
        self.assertEqual(pages[1]['pagina'], 2)
        self.assertEqual(pages[1]['linhas'], [])
        self.assertEqual(pages[1]['palavras'], 0)

    def test_curl_enforces_https_and_certificate_verification_with_bounded_body(self):
        with patch.object(pipeline.subprocess, 'run', side_effect=self.curl()) as run:
            result = pipeline.fetch_pdf_curl(URL, max_bytes=1000, timeout=12)
        command = run.call_args.args[0]
        self.assertNotIn('--insecure', command)
        self.assertNotIn('-k', command)
        self.assertEqual(command[command.index('--proto') + 1], '=https')
        self.assertEqual(command[command.index('--proto-redir') + 1], '=https')
        self.assertEqual(command[command.index('--max-filesize') + 1], '1000')
        self.assertEqual(command[command.index('--max-time') + 1], '12')
        self.assertEqual(run.call_args.kwargs['timeout'], 17)
        self.assertEqual(result, (PDF, URL, 'application/pdf'))

    def test_curl_rejects_html_even_with_pdf_content_type(self):
        with patch.object(pipeline.subprocess, 'run', side_effect=self.curl(body=b'<html>Login</html>')):
            with self.assertRaisesRegex(ValueError, 'não é PDF'):
                pipeline.fetch_pdf_curl(URL)

    def test_curl_checks_actual_bytes_and_its_own_size_limit_error(self):
        with patch.object(pipeline.subprocess, 'run', side_effect=self.curl(body=PDF + b'x' * 200)):
            with self.assertRaisesRegex(ValueError, 'excede limite'):
                pipeline.fetch_pdf_curl(URL, max_bytes=100)
        with patch.object(pipeline.subprocess, 'run', side_effect=self.curl(code=63, status=0)):
            with self.assertRaisesRegex(ValueError, 'excede limite'):
                pipeline.fetch_pdf_curl(URL)

    def test_curl_rejects_non_https_final_url(self):
        with patch.object(pipeline.subprocess, 'run', side_effect=self.curl(final='http://fonte.example.invalid/prova.pdf')):
            with self.assertRaisesRegex(ValueError, 'sem HTTPS'):
                pipeline.fetch_pdf_curl(URL)

    def test_curl_preserves_certificate_refusal_as_tls_error(self):
        with patch.object(pipeline.subprocess, 'run', side_effect=self.curl(code=60, status=0)):
            with self.assertRaises(urllib.error.URLError) as error:
                pipeline.fetch_pdf_curl(URL)
        self.assertIsInstance(error.exception.reason, ssl.SSLCertVerificationError)

    def test_curl_preserves_http_failure_status_for_bounded_retry_policy(self):
        with patch.object(pipeline.subprocess, 'run', side_effect=self.curl(code=22, status=403)):
            with self.assertRaises(urllib.error.HTTPError) as error:
                pipeline.fetch_pdf_curl(URL)
        self.assertEqual(error.exception.code, 403)

    def test_external_curl_deadline_is_a_retryable_timeout_for_collector(self):
        with patch.object(pipeline.subprocess, 'run', side_effect=subprocess.TimeoutExpired(['curl'], 35)):
            with self.assertRaisesRegex(TimeoutError, 'curl'):
                pipeline.fetch_pdf_curl(URL)


if __name__ == '__main__':
    unittest.main()
