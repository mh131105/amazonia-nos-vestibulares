"""Regressões dos cabeçalhos antigos UFAM; fixtures apenas neste teste."""

import json
from pathlib import Path
import unittest

from scripts import gabaritos, segmentar


class UFAMCycleTwoTests(unittest.TestCase):
    def legacy_page(self, *, project=2021, stage=1):
        return (f'PROCESSO SELETIVO CONTÍNUO – PSC\nPROJETO {project} / {stage}ª ETAPA\n'
                'GABARITO DEFINITIVO\n17 C\n18 D\n28 D')

    def test_project_year_is_not_assumed_to_equal_edition(self):
        text = self.legacy_page()
        digest = gabaritos.UFAM_LEGACY_VERIFIED[(2019, 1)]['sha256']
        found, error = gabaritos.parse_ufam([(1, text)], 2019, 1, {17, 18, 28}, source_sha256=digest)
        self.assertEqual(error, '')
        self.assertEqual([found[n]['alternativa_oficial'] for n in [17, 18, 28]], ['C', 'D', 'D'])
        self.assertIn('Projeto 2021', found[17]['secao_gabarito'])

    def test_unverified_bytes_wrong_project_or_wrong_stage_cannot_relax_header(self):
        digest = gabaritos.UFAM_LEGACY_VERIFIED[(2019, 1)]['sha256']
        for text, source in [(self.legacy_page(), None), (self.legacy_page(), '0' * 64),
                             (self.legacy_page(project=2019), digest),
                             (self.legacy_page(stage=2), digest)]:
            with self.subTest(text=text, source=source):
                found, error = gabaritos.parse_ufam([(1, text)], 2019, 1, {17}, source_sha256=source)
                self.assertFalse(found)
                self.assertTrue(error)

    def test_index_verified_definitive_key_may_have_only_gabarito_in_header(self):
        # A fonte oficial classifica este PDF como definitivo; o próprio título
        # diz apenas GABARITO e nomeia o Projeto 2020 da segunda etapa PSC2019.
        text = self.legacy_page(project=2020, stage=2).replace('GABARITO DEFINITIVO', 'GABARITO')
        digest = gabaritos.UFAM_LEGACY_VERIFIED[(2019, 2)]['sha256']
        found, error = gabaritos.parse_ufam([(1, text)], 2019, 2, {17}, source_sha256=digest)
        self.assertEqual(error, '')
        self.assertEqual(found[17]['alternativa_oficial'], 'C')
        found, error = gabaritos.parse_ufam([(1, text)], 2019, 2, {17})
        self.assertFalse(found)
        self.assertTrue(error)

    def test_annular_marker_is_preserved_without_becoming_an_alternative(self):
        text = 'PROCESSO SELETIVO CONTÍNUO PSC2021\n3ª Etapa\nGabarito Definitivo\n21. E\n22. ANULAR\n23. B'
        found, error = gabaritos.parse_ufam([(1, text)], 2021, 3, {21, 22, 23})
        self.assertEqual(error, '')
        self.assertEqual(found[22]['marcador_oficial'], 'ANULAR')
        self.assertEqual(found[22]['estado_oficial'], 'anulada')
        self.assertIsNone(found[22]['alternativa_oficial'])

    def test_first_stage_does_not_admit_numbers_outside_known_subject_range(self):
        text = 'PSC2023\n1ª Etapa\nGabarito Definitivo\n16. A C\n17. E'
        found, error = gabaritos.parse_ufam([(1, text)], 2023, 1, {16, 17})
        self.assertNotIn(16, found)
        self.assertEqual(found[17]['alternativa_oficial'], 'E')
        self.assertTrue(error)

    def test_old_layout_preserves_top_continuation_but_excludes_header_and_footer(self):
        root = Path(__file__).resolve().parents[1]
        fragment = json.loads((root / 'data/registry/regras-ufam-c2.json').read_text(encoding='utf-8'))
        layout = fragment['layouts']['ufam_legado_sem_capa_c2']
        content = [('Cabeçalho sintético', 29, 28), ('17. Enunciado sintético', 29, 760),
                   ('a) Continuação da questão', 308, 46), ('18. Próximo item', 308, 140),
                   ('Rodapé sintético', 29, 804)]
        page = {'pagina': 1, 'largura': 595, 'altura': 842,
                'linhas': [{'palavras': [{'texto': text, 'bbox': [x, y, x + 210, y + 12]}]}
                           for text, x, y in content]}
        lines = segmentar.ordered_lines([page], layout)
        self.assertEqual([line['texto'] for line in lines],
                         ['17. Enunciado sintético', 'a) Continuação da questão', '18. Próximo item'])
        markers = segmentar.markers(lines, layout)
        self.assertEqual([marker['numero'] for marker in markers], [17, 18])
        regions = segmentar.regions(lines[:2], [page], layout, lines[2])
        self.assertEqual(regions[1]['bbox_regiao'][1], layout['y_min'])
        self.assertLessEqual(regions[1]['bbox_regiao'][1], 46)


if __name__ == '__main__':
    unittest.main()
