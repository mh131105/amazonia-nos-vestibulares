"""Regressões de seleção de modalidade e anulação; fixtures só neste teste."""

import csv
from pathlib import Path
import unittest

from scripts import gabaritos


class GabaritosTests(unittest.TestCase):
    def test_anulacao_ufam_nao_vira_alternativa(self):
        text = 'Gabarito Deﬁnitivo\n2ª Etapa [PSC 2026 - Projeto 2027]\n26. A 53. C\n27. ANULADA 54. B'
        found, error = gabaritos.parse_ufam([(1, text)], 2026, 2, {26, 27})
        self.assertEqual(error, '')
        self.assertEqual(found[26]['alternativa_oficial'], 'A')
        self.assertIsNone(found[27]['alternativa_oficial'])
        self.assertEqual(found[27]['estado_oficial'], 'anulada')

    def test_etapa_errada_nao_fornece_resposta(self):
        text = 'Gabarito Definitivo\n3ª Etapa PSC 2026\n27. B'
        found, error = gabaritos.parse_ufam([(1, text)], 2026, 2, {27})
        self.assertFalse(found)
        self.assertTrue(error)

    def test_numero_duplicado_permanece_ambiguo(self):
        text = 'Gabarito Definitivo\n3ª Etapa PSC 2026\n27. B\n27. D'
        found, error = gabaritos.parse_ufam([(1, text)], 2026, 3, {27})
        self.assertFalse(found)
        self.assertTrue(error)

    def test_coluna_de_lingua_nao_e_escolhida_por_conveniencia(self):
        text = 'Gabarito Definitivo\n3ª Etapa PSC 2026\n17. E C C'
        found, error = gabaritos.parse_ufam([(1, text)], 2026, 3, {17})
        self.assertFalse(found)
        self.assertTrue(error)

    def ufrr_page(self, answers):
        return ('GABARITO OFICIAL DA PROVA INTEGRAL (PI) E DO SERIADO ETAPA 3 (E3)\n'
                'VESTIBULAR UFRR 2026\nDisciplina GEOGRAFIA HISTÓRIA\n'
                'Questão ' + ' '.join(map(str, range(37, 55))) + '\nGabarito ' + answers)

    def test_ufrr_seleciona_pi_e3_ignorando_e1_e2(self):
        wrong = 'GABARITO OFICIAL DO SERIADO ETAPA 1 (E1)\nVESTIBULAR UFRR 2026\n37. E'
        right = self.ufrr_page(' '.join('A' * 9 + 'B' * 9))
        found, error = gabaritos.parse_ufrr_pi([(2, right), (3, wrong)], 2026, {37, 46, 54})
        self.assertEqual(error, '')
        self.assertEqual(found[37]['alternativa_oficial'], 'A')
        self.assertEqual(found[46]['alternativa_oficial'], 'B')
        self.assertEqual(found[54]['pagina_pdf'], 2)

    def test_tabela_ufrr_incompleta_nao_desloca_respostas(self):
        found, error = gabaritos.parse_ufrr_pi([(2, self.ufrr_page(' '.join('A' * 17)))], 2026, {37})
        self.assertFalse(found)
        self.assertTrue(error)

    def test_somente_e1_nao_fornece_gabarito_pi(self):
        found, error = gabaritos.parse_ufrr_pi([(3, 'GABARITO OFICIAL DO SERIADO ETAPA 1 (E1)')], 2026, {37})
        self.assertFalse(found)
        self.assertTrue(error)

    def test_piloto_completo_e_pontos_conferidos_nos_pdfs(self):
        root = Path(__file__).resolve().parents[1]
        with (root / 'data/processed/gabaritos.csv').open(encoding='utf-8', newline='') as stream:
            answers = list(csv.DictReader(stream))
        with (root / 'data/processed/questoes.csv').open(encoding='utf-8', newline='') as stream:
            questions = list(csv.DictReader(stream))
        by_id = {row['ocorrencia_id']: row for row in answers}
        self.assertEqual(len(answers), len(questions))
        self.assertEqual(set(by_id), {row['ocorrencia_id'] for row in questions})
        annulled = by_id['ufam-psc2026-e2-q27']
        self.assertEqual(annulled['estado_oficial'], 'anulada')
        self.assertEqual(annulled['alternativa_oficial'], '')
        for item_id, alternative, page in [
            ('ufrr-vestibular2025-pi-q37', 'B', '4'),
            ('ufrr-vestibular2025-pi-q46', 'C', '4'),
            ('ufrr-vestibular2025-pi-q54', 'E', '4'),
            ('ufrr-vestibular2026-pi-q37', 'B', '2'),
            ('ufrr-vestibular2026-pi-q46', 'A', '2'),
            ('ufrr-vestibular2026-pi-q54', 'E', '2'),
        ]:
            self.assertEqual(by_id[item_id]['alternativa_oficial'], alternative)
            self.assertEqual(by_id[item_id]['pagina_pdf'], page)
        self.assertTrue(all(row['revisao_humana'] == 'pendente' for row in answers))
        self.assertTrue(all(row['responsavel_extracao'] == 'Codex' for row in answers))


if __name__ == '__main__':
    unittest.main()
