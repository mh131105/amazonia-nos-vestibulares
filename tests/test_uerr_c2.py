"""Fronteiras do layout Cebraspe; fixtures sintéticas só neste arquivo."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts import gabaritos, segmentar


class UERRTests(unittest.TestCase):
    def matrix(self, year=2025):
        code = '066_UERR_001_01' if year == 2025 else '225_UERR_001_01'
        rows = [list(range(1, 19)) + [10, 11], list(range(12, 32)),
                list(range(32, 52)), list(range(52, 72)), [72] + [0] * 19]
        tokens = {55: 'A', 57: 'X', 62: 'X', 72: 'E', 19: 'B', 28: 'D', 36: 'A'}
        text = f'PROCESSO SELETIVO VESTIBULAR – {year}\nGABARITOS OFICIAIS DEFINITIVOS\n{code}\n'
        for numbers in rows:
            text += 'Questão ' + ' '.join(map(str, numbers)) + '\n'
            text += 'Gabarito ' + ' '.join('0' if n == 0 else tokens.get(n, 'C') for n in numbers) + '\n'
        return text

    def test_matrix_keeps_number_binding_and_official_annulment(self):
        found, error = gabaritos.parse_uerr([(1, self.matrix())], 2025, {55, 57, 62, 72})
        self.assertEqual(error, '')
        self.assertEqual(found[55]['alternativa_oficial'], 'A')
        self.assertEqual(found[72]['alternativa_oficial'], 'E')
        for n in [57, 62]:
            self.assertIsNone(found[n]['alternativa_oficial'])
            self.assertEqual(found[n]['estado_oficial'], 'anulada')
            self.assertEqual(found[n]['marcador_oficial'], 'X')

    def test_2026_matrix_uses_other_discipline_number_ranges(self):
        found, error = gabaritos.parse_uerr([(1, self.matrix(2026))], 2026, {19, 28, 36})
        self.assertEqual(error, '')
        self.assertEqual([found[n]['alternativa_oficial'] for n in [19, 28, 36]], ['B', 'D', 'A'])

    def test_foreign_language_duplicates_do_not_get_a_convenient_column(self):
        found, error = gabaritos.parse_uerr([(1, self.matrix())], 2025, {10, 55})
        self.assertFalse(found)
        self.assertTrue(error)

    def test_wrong_year_or_not_definitive_does_not_supply_answers(self):
        for text in [self.matrix(2026), self.matrix().replace('DEFINITIVOS', 'PRELIMINARES')]:
            found, error = gabaritos.parse_uerr([(1, text)], 2025, {55})
            self.assertFalse(found)
            self.assertTrue(error)

    def test_missing_cell_or_duplicate_matrix_is_not_zipped_into_wrong_answers(self):
        text = self.matrix()
        # Retira uma resposta da primeira linha para testar alinhamento.
        lines = text.splitlines()
        index = next(i for i, line in enumerate(lines) if line.startswith('Gabarito '))
        lines[index] = ' '.join(lines[index].split()[:-1])
        for changed in ['\n'.join(lines), text + text]:
            found, error = gabaritos.parse_uerr([(1, changed)], 2025, {55})
            self.assertFalse(found)
            self.assertTrue(error)

    def option_line(self, label, index, *, width=8.5, gap=5.6):
        return {'texto': f'{label} resposta sintética {index}', 'coluna': 1,
                'palavras': [{'texto': label, 'bbox': [28.4, index * 20, 28.4 + width, index * 20 + 10]},
                             {'texto': f'resposta sintética {index}',
                              'bbox': [28.4 + width + gap, index * 20, 200, index * 20 + 10]}]}

    def geometry_layout(self):
        return {'geometria_rotulos_alternativas': {
            'largura_min': 8.2, 'largura_max': 8.8, 'gap_min': 5.0, 'gap_max': 6.3,
            'margens': [28.4, 303.9], 'tolerancia_margem': 1.2}}

    def test_article_a_is_preserved_in_stem_but_not_parsed_as_an_option(self):
        article = self.option_line('A', 0, width=7.1)
        article['texto'] = 'A pergunta sintética começa com artigo.'
        lines = [article] + [self.option_line(label, i) for i, label in enumerate('ABCDE', 1)]
        text = '\n'.join(line['texto'] for line in lines)
        accepted = segmentar.alternative_label_lines(lines, self.geometry_layout())
        self.assertEqual(accepted, {1, 2, 3, 4, 5})
        alternatives, labels = segmentar.split_alternatives(text, r'(?m)^([A-E])\s+', accepted)
        self.assertEqual(labels, list('abcde'))
        self.assertEqual(alternatives[0]['texto_extraido'], 'resposta sintética 1')
        self.assertIn('A pergunta sintética', text)

    def test_unverified_option_geometry_stays_pending(self):
        lines = [self.option_line(label, i, gap=2) for i, label in enumerate('ABCDE')]
        accepted = segmentar.alternative_label_lines(lines, self.geometry_layout())
        alternatives, labels = segmentar.split_alternatives(
            '\n'.join(line['texto'] for line in lines), r'(?m)^([A-E])\s+', accepted)
        self.assertFalse(accepted)
        self.assertIsNone(alternatives)
        self.assertFalse(labels)

    def test_last_question_can_close_at_document_end_only_when_layout_declares_it(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            original = root / 'data/raw/fixture.pdf'
            original.parent.mkdir(parents=True)
            original.write_bytes(b'%PDF-Fixture sintetica apenas de teste')
            digest = hashlib.sha256(original.read_bytes()).hexdigest()
            doc = {'documento_id': 'fixture', 'aplicacao_id': 'fixture-app', 'processo_id': 'fixture-processo',
                   'instituicao_sigla': 'FIXTURE', 'sha256': digest, 'caminho_local': 'data/raw/fixture.pdf',
                   'status': 'coletado', 'url_origem': 'https://example.invalid/fixture.pdf'}
            registry = root / 'data/registry'
            registry.mkdir(parents=True)
            (registry / 'documentos.jsonl').write_text(json.dumps(doc) + '\n')
            text_lines = ['QUESTÃO 72', 'Texto sintético suficientemente longo para testar o final do documento.']
            text_lines += [f'{label} resposta sintética com conteúdo.' for label in 'ABCDE']
            lines = [{'texto': text, 'palavras': [{'texto': text, 'bbox': [20, 30 + i * 20, 250, 40 + i * 20]}]}
                     for i, text in enumerate(text_lines)]
            pages = [{'pagina': 1, 'largura': 600, 'altura': 800, 'documento_sha256': digest, 'linhas': lines}]
            extracted = root / 'data/interim/extraido' / digest
            extracted.mkdir(parents=True)
            (extracted / 'paginas.jsonl').write_text(json.dumps(pages[0]) + '\n')
            layout = {'pagina_inicial': 1, 'divisao_colunas_fracao': 0.5, 'y_min': 10, 'y_max': 750,
                      'numero_maximo': 72, 'marcador_questao': r'^QUESTÃO (\d{1,2})$',
                      'marcador_alternativa': r'(?m)^([A-E])\s+'}
            rule = {'documento_id': 'fixture', 'documento_sha256': digest, 'layout': 'fixture',
                    'secoes': [{'disciplina': 'geografia', 'inicio': 72, 'fim': 72}]}
            for allowed in [False, True]:
                layout['fecha_ultima_questao_no_fim_do_documento'] = allowed
                (registry / 'regras-segmentacao.json').write_text(json.dumps({'layouts': {'fixture': layout}, 'documentos': [rule]}))
                execution = segmentar.segment(root)[0]
                self.assertEqual(execution['estrutura_textual_completa'], int(allowed))
                self.assertEqual(execution['denominadores_validados'], 0)


if __name__ == '__main__':
    unittest.main()
