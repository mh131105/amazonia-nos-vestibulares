"""Invariantes de segmentação; conteúdo sintético apenas em diretórios temporários."""

import copy
import csv
import hashlib
import json
from pathlib import Path
import random
import tempfile
import unittest

from scripts import segmentar


def line(text, x, y):
    return {"texto": text, "palavras": [{"texto": text,
                                          "bbox": [x, y, x + min(245, max(8, len(text) * 3)), y + 10]}]}


def page(number, lines, digest):
    return {"pagina": number, "largura": 595.32, "altura": 842.04,
            "documento_sha256": digest, "linhas": lines}


class SegmentarTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.registry = self.root / "data/registry"
        self.registry.mkdir(parents=True)
        self.original = self.root / "data/raw/documentos/fixture.pdf"
        self.original.parent.mkdir(parents=True)
        self.original.write_bytes(b"%PDF-1.4\n% Documento sintetico exclusivo de teste.\n")
        self.sha = hashlib.sha256(self.original.read_bytes()).hexdigest()
        self.pages_path = self.root / "data/interim/extraido" / self.sha / "paginas.jsonl"
        self.pages_path.parent.mkdir(parents=True)
        self.layout = {
            "pagina_inicial": 3, "divisao_colunas_fracao": 0.5,
            "y_min": 50, "y_max": 796,
            "marcador_questao": r"^(\d{1,2})\.\s+",
            "margens_inicio_questao": [28.08, 311.69], "tolerancia_margem": 14,
            "numero_maximo": 54,
        }
        self.pages = [
            page(3, [
                line("PROCESSO SELETIVO FICTÍCIO", 28.08, 38),
                line("18. Questão vizinha que não pode entrar no item 19.", 28.08, 100),
                line("HISTÓRIA", 120, 650),
                line("19. Enunciado sintético iniciado no fim da coluna esquerda.", 28.08, 700),
                line("CONTINUAÇÃO À DIREITA: este texto pertence à questão 19.", 311.69, 53),
                line("a. Categoria interna, não alternativa de resposta.", 311.69, 70),
                line("b. Segunda categoria interna do enunciado.", 311.69, 85),
                line("c. Terceira categoria interna do enunciado.", 311.69, 100),
                line("a)", 311.69, 125), line("Resposta A da questão 19.", 330, 125),
                line("b) Resposta B da questão 19.", 311.69, 145),
                line("c) Resposta C da questão 19.", 311.69, 165),
                line("d) Resposta D da questão 19.", 311.69, 185),
                line("e) Resposta E da questão 19.", 311.69, 205),
                line("20. Enunciado sintético que continua na próxima página.", 311.69, 700),
                line("3", 294.89, 796),
            ], self.sha),
            page(4, [
                line("PROCESSO SELETIVO FICTÍCIO", 28.08, 38),
                line("CONTINUAÇÃO NA PÁGINA SEGUINTE: ainda é questão 20.", 28.08, 160),
                line("a) Resposta A da questão 20.", 28.08, 200),
                line("b) Resposta B da questão 20.", 28.08, 220),
                line("c) Resposta C da questão 20.", 28.08, 240),
                line("d) Resposta D da questão 20.", 28.08, 260),
                line("e) Resposta E da questão 20.", 28.08, 280),
                line("GEOGRAFIA", 120, 350),
                line("21. Questão seguinte não deve entrar no item anterior.", 28.08, 400),
                line("4", 294.89, 796),
            ], self.sha),
        ]
        self.document = {
            "documento_id": "prova-ficticia", "status": "coletado",
            "sha256": self.sha, "caminho_local": "data/raw/documentos/fixture.pdf",
            "aplicacao_id": "aplicacao-ficticia", "processo_id": "processo-ficticio",
            "instituicao_sigla": "FICTICIA", "tipo": "prova",
            "url_origem": "https://example.invalid/prova-ficticia.pdf",
        }
        self.config = {"layouts": {"fixture_duas_colunas": self.layout}, "documentos": [{
            "documento_id": "prova-ficticia", "documento_sha256": self.sha,
            "layout": "fixture_duas_colunas", "secoes": [
                {"disciplina": "historia", "inicio": 19, "fim": 19},
                {"disciplina": "geografia", "inicio": 20, "fim": 20},
            ],
        }]}
        self.save_inputs()

    def save_inputs(self):
        (self.registry / "regras-segmentacao.json").write_text(
            json.dumps(self.config, ensure_ascii=False), encoding="utf-8")
        segmentar.write_jsonl(self.registry / "documentos.jsonl", [self.document])
        segmentar.write_jsonl(self.pages_path, self.pages)

    def segment(self):
        segmentar.segment(self.root)
        return segmentar.read_jsonl(self.root / "data/processed/questoes-texto.jsonl")

    def test_discursive_codes_keep_subitems_together_and_exclude_answer_sheets(self):
        self.layout.update(pagina_inicial=3, divisao_colunas_fracao=1.0,
                           paginas_corpo=[3, 5], marcador_questao=r'^([GH]\d{2})$',
                           codigos_questoes=['G01', 'G02', 'H01', 'H02'],
                           fecha_ultima_questao_no_fim_do_documento=True)
        self.layout.pop('margens_inicio_questao')
        self.config['documentos'][0]['secoes'] = [
            {'disciplina': 'geografia', 'codigos': ['G01', 'G02'], 'tipo_resposta': 'discursiva'},
            {'disciplina': 'historia', 'codigos': ['H01', 'H02'], 'tipo_resposta': 'discursiva'},
        ]
        self.pages = [page(3, [
            line('G01', 30, 80), line('Enunciado sintético de Geografia, sem alternativas objetivas.', 30, 100),
            line('a) Primeiro subitem discursivo.', 30, 120), line('b) Segundo subitem discursivo.', 30, 140),
            line('c) Terceiro subitem discursivo.', 30, 160),
            line('G02', 30, 400), line('Segundo enunciado geográfico sintético, conservado como uma questão integral.', 30, 420),
        ], self.sha), page(4, [line('H01', 30, 80), line('FOLHA DE RESPOSTA EXCLUÍDA, sem enunciado.', 30, 100)], self.sha),
            page(5, [line('H01', 30, 80), line('Enunciado histórico sintético, cujo ordinal também é 01 sem colidir com G01.', 30, 100),
                     line('H02', 30, 400), line('Último enunciado histórico sintético, fechado explicitamente ao fim do corpo.', 30, 420)], self.sha)]
        self.save_inputs()
        rows = self.segment()
        self.assertEqual(len(rows), 4)
        self.assertEqual(len({r['ocorrencia_id'] for r in rows}), 4)
        first = next(r for r in rows if r['numero_questao'] == 'G01')
        self.assertEqual(first['ocorrencia_id'], 'aplicacao-ficticia-q-g01')
        self.assertIn('Terceiro subitem discursivo', first['texto_bruto_segmentado'])
        self.assertNotIn('G02', first['texto_bruto_segmentado'])
        self.assertEqual(first['subitens_rotulos_detectados'], ['a', 'b', 'c'])
        self.assertTrue(all(r['tipo_resposta'] == 'discursiva' and r['alternativas'] is None
                            and r['alternativas_textuais_completas'] is None for r in rows))
        self.assertTrue(all(not r['problemas_extracao'] and not r['apto_denominador_validado'] for r in rows))
        self.assertTrue(all(4 not in r['paginas_pdf'] for r in rows))
        self.assertTrue(all(region['bbox_regiao'][2] == 595.32 for r in rows for region in r['regioes_origem']))

    def test_shuffled_flows_keep_column_order_and_join_split_alternative(self):
        expected = segmentar.ordered_lines(self.pages, self.layout)
        shuffled = copy.deepcopy(self.pages)
        for p in shuffled:
            random.Random(29).shuffle(p["linhas"])
        actual = segmentar.ordered_lines(shuffled, self.layout)
        self.assertEqual(actual, expected)
        texts = [item["texto"] for item in actual]
        self.assertLess(texts.index(self.pages[0]["linhas"][3]["texto"]),
                        texts.index(self.pages[0]["linhas"][4]["texto"]))
        self.assertIn("a) Resposta A da questão 19.", texts)
        self.assertFalse(any(text == "HISTÓRIA" or "PROCESSO SELETIVO" in text for text in texts))

    def test_page_order_is_numeric_even_if_page_records_are_shuffled(self):
        expected = segmentar.ordered_lines(self.pages, self.layout)
        self.assertEqual(segmentar.ordered_lines(list(reversed(self.pages)), self.layout), expected)

    def test_item_crosses_column_and_page_without_neighbor_contamination(self):
        rows = {row["numero_questao"]: row for row in self.segment()}
        self.assertEqual(set(rows), {19, 20})
        first, second = rows[19], rows[20]
        self.assertIn("CONTINUAÇÃO À DIREITA", first["texto_bruto_segmentado"])
        self.assertNotIn("18. Questão", first["texto_bruto_segmentado"])
        self.assertNotIn("20. Enunciado", first["texto_bruto_segmentado"])
        self.assertEqual(first["paginas_pdf"], [3])
        self.assertEqual([region["coluna"] for region in first["regioes_origem"]], [1, 2])
        self.assertIn("CONTINUAÇÃO NA PÁGINA SEGUINTE", second["texto_bruto_segmentado"])
        self.assertNotIn("21. Questão", second["texto_bruto_segmentado"])
        self.assertEqual(second["paginas_pdf"], [3, 4])
        continuation = second["regioes_origem"][1]
        # A região começa no topo do corpo para preservar possível imagem antes da primeira linha.
        self.assertEqual(continuation["bbox_regiao"][1], self.layout["y_min"])
        self.assertEqual(continuation["bbox_regiao"][3], 400)
        self.assertEqual([a["rotulo"] for a in first["alternativas"]], list("ABCDE"))
        self.assertEqual(first["alternativas"][0]["texto_extraido"], "Resposta A da questão 19.")
        self.assertEqual(second["alternativas"][-1]["texto_extraido"], "Resposta E da questão 20.")

    def test_enumerations_are_not_alternatives_and_duplicate_answer_sets_are_ambiguous(self):
        text = "a. Categoria\nb. Categoria\nc. Categoria\n" + "\n".join(f"{label}) Resposta {label}" for label in "ABCDE")
        alternatives, labels = segmentar.split_alternatives(text)
        self.assertEqual(labels, list("abcde"))
        self.assertEqual([a["rotulo"] for a in alternatives], list("ABCDE"))
        alternatives, labels = segmentar.split_alternatives(text + "\nA) Outra resposta")
        self.assertIsNone(alternatives)
        self.assertEqual(labels[-1], "a")

    def test_graphical_answers_remain_pending_without_invented_alternatives(self):
        self.pages[0]["linhas"] = [ln for ln in self.pages[0]["linhas"]
                                     if not (125 <= ln["palavras"][0]["bbox"][1] <= 205)]
        self.save_inputs()
        rows = {row["numero_questao"]: row for row in self.segment()}
        graphical = rows[19]
        self.assertIsNone(graphical["alternativas"])
        self.assertFalse(graphical["alternativas_textuais_completas"])
        self.assertIn("alternativas_textuais_nao_formam_A_E_em_ordem_unica", graphical["problemas_extracao"])
        self.assertEqual(graphical["status_estrutural"], "incompleta_ou_ambigua_revisar")
        self.assertEqual(graphical["dependencia_visual"], "a_verificar")
        self.assertFalse(graphical["apto_denominador_validado"])
        self.assertIsNone(graphical["regionalidade"])
        self.assertFalse(graphical["integridade_revisada_humano"])

    def test_answer_labels_without_text_do_not_count_as_complete_alternatives(self):
        alternatives, labels = segmentar.split_alternatives("A)\nB)\nC)\nD)\nE)\n")
        self.assertEqual(labels, list("abcde"))
        self.assertIsNone(alternatives)

    def test_changed_original_is_rejected_before_outputs(self):
        self.original.write_bytes(b"%PDF-1.4\n% Original alterado.\n")
        with self.assertRaisesRegex(ValueError, "Original difere do hash"):
            segmentar.segment(self.root)
        self.assertFalse((self.root / "data/processed/questoes.csv").exists())

    def test_wrong_extraction_source_hash_is_rejected(self):
        self.pages[0]["documento_sha256"] = "0" * 64
        self.save_inputs()
        with self.assertRaisesRegex(ValueError, "Extração não pertence ao original"):
            segmentar.segment(self.root)

    def test_duplicate_item_marker_is_rejected_instead_of_picking_one(self):
        self.pages[1]["linhas"].append(line("19. Outro início duplicado.", 311.69, 500))
        self.save_inputs()
        with self.assertRaisesRegex(ValueError, "Início da questão 19 não é único"):
            segmentar.segment(self.root)

    def test_offline_reexecution_is_identical_and_public_csv_has_no_question_text(self):
        self.segment()
        outputs = [self.root / "data/processed/questoes.csv",
                   self.root / "data/processed/questoes-texto.jsonl",
                   self.registry / "segmentacoes.jsonl"]
        before = [p.read_bytes() for p in outputs]
        self.segment()
        self.assertEqual(before, [p.read_bytes() for p in outputs])
        with outputs[0].open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 2)
        self.assertNotIn("texto_bruto_segmentado", rows[0])
        self.assertNotIn("alternativas", rows[0])
        self.assertNotIn("Enunciado sintético", outputs[0].read_text())


if __name__ == "__main__":
    unittest.main()
