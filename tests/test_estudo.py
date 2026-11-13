"""Protege a limpeza e o denominador da pergunta principal com dados fictícios."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from limpeza import limpar, gravar_csv, ler_csv
from analise import analisar, serie_temporal, fmt
from preparar_dashboard import preparar


class Estudo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'dados/brutos').mkdir(parents=True)
        (self.root / 'resultados').mkdir()
        self.prova = dict(prova_id='p', instituicao='Fictícia', processo='Vestibular',
                          edicao='2024', ano_aplicacao='2024', data_aplicacao='', etapa='2ª fase',
                          fonte_prova_id='pdf', fonte_ementa_id='edital', questoes_triadas='2',
                          triagem_completa='sim', ementa_regional_completa='sim', observacao='')
        self.gravar('provas', [self.prova])
        self.gravar('fontes', [dict(fonte_id='pdf', tipo='prova', sha256='a'*64,
                                   url='https://exemplo.edu.br/prova.pdf'),
                               dict(fonte_id='edital', tipo='ementa', sha256='b'*64,
                                    url='https://exemplo.edu.br/edital.pdf')])
        self.gravar('topicos', [dict(topico_id='H06', disciplina='História', conteudo='Fronteiras', topico='Tratados coloniais'),
                                dict(topico_id='G03', disciplina='Geografia', conteudo='Natureza', topico='Clima')])
        base = dict(prova_id='p', disciplina='História', fonte_id='edital', url='https://exemplo.edu.br/edital.pdf', paginas_pdf='1', observacao='')
        self.gravar('ementas', [{**base, 'ementa_item_id':'colonial', 'texto_oficial':'Madri em 1750', 'topicos_ids':'H06', 'escopo':'regional explícito'},
                                {**base, 'ementa_item_id':'clima', 'texto_oficial':'Clima amazônico', 'topicos_ids':'G03', 'escopo':'regional explícito'},
                                {**base, 'ementa_item_id':'geral', 'texto_oficial':'Relações internacionais', 'topicos_ids':'H06', 'escopo':'geral'}])
        comum = {k:self.prova[k] for k in ['prova_id', 'instituicao', 'processo', 'edicao', 'ano_aplicacao', 'data_aplicacao', 'etapa']}
        comum.update(dict(fonte_prova_id='pdf', fonte_sha256='a'*64, url_prova='https://exemplo.edu.br/prova.pdf',
                          paginas_pdf='2', enunciado='Amazo\u0302nia\n  regional', foco_regional='central',
                          justificativa='Caso fictício para o cálculo.', tipo_vinculo_ementa='direto'))
        self.dados = [{**comum, 'questao_id':'q1', 'numero':'1', 'disciplina':'História', 'topico_id':'H06', 'topicos_ids':'H06', 'ementa_itens':'geral'},
                      {**comum, 'questao_id':'q2', 'numero':'2', 'disciplina':'História', 'topico_id':'G03', 'topicos_ids':'G03', 'ementa_itens':'clima'}]
        self.bruto = self.root / 'dados/brutos/questoes.jsonl'

    def gravar(self, nome, linhas):
        gravar_csv(self.root / f'dados/{nome}.csv', linhas, list(linhas[0]))

    def test_limpeza_e_cobertura_exigem_vinculo_pertinente(self):
        original = '\n'.join(json.dumps(r) for r in self.dados + [self.dados[0]]) + '\n'
        self.bruto.write_text(original)
        limpas = limpar(self.root)
        self.assertEqual(len(limpas), 2)
        self.assertEqual(limpas[0]['enunciado'], 'Amazônia regional')
        self.assertEqual(limpas[1]['disciplina_origem'], 'História')
        self.assertEqual(limpas[1]['disciplina'], 'Geografia')
        self.assertEqual(self.bruto.read_text(), original)
        cobertura = analisar(self.root)[0]
        self.assertEqual(cobertura['topicos_padronizados_previstos'], 2)
        self.assertEqual(cobertura['topicos_padronizados_cobrados'], 1)
        self.assertEqual(cobertura['cobertura_topicos_percentual'], '50.00')
        self.prova['ementa_regional_completa'] = 'não'
        self.gravar('provas', [self.prova])
        self.assertEqual(analisar(self.root)[0]['cobertura_topicos_percentual'], '')

    def test_hash_conflitante_e_recusado(self):
        self.dados[0]['fonte_sha256'] = 'c'*64
        self.bruto.write_text(json.dumps(self.dados[0]) + '\n')
        with self.assertRaisesRegex(ValueError, 'SHA-256 divergente'):
            limpar(self.root)

    def test_identificador_ausente_e_fonte_de_outra_prova_sao_recusados(self):
        fontes = ler_csv(self.root / 'dados/fontes.csv')
        fontes.append(dict(fonte_id='outro_pdf', tipo='prova', sha256='c'*64,
                           url='https://exemplo.edu.br/outra-prova.pdf'))
        self.gravar('fontes', fontes)
        casos = [({'questao_id': ''}, 'questao_id ausente'),
                 ({'fonte_prova_id': 'outro_pdf', 'fonte_sha256': 'c'*64,
                   'url_prova': 'https://exemplo.edu.br/outra-prova.pdf'},
                  'Fonte diferente da prova cadastrada')]
        for mudanca, mensagem in casos:
            with self.subTest(mudanca=mudanca):
                self.bruto.write_text(json.dumps({**self.dados[0], **mudanca}) + '\n')
                with self.assertRaisesRegex(ValueError, mensagem):
                    limpar(self.root)

    def test_analise_rejeita_duplicata_antes_de_sobrescrever_resultados(self):
        self.bruto.write_text('\n'.join(json.dumps(r) for r in self.dados) + '\n')
        limpas = limpar(self.root)
        analisar(self.root)
        arquivos = {p.name: p.read_bytes() for p in (self.root / 'resultados').iterdir()}
        gravar_csv(self.root / 'dados/curado/questoes.csv', limpas + [limpas[0]], list(limpas[0]))
        with self.assertRaisesRegex(ValueError, 'IDs de questões ausentes ou duplicados'):
            analisar(self.root)
        self.assertEqual(arquivos, {p.name: p.read_bytes() for p in (self.root / 'resultados').iterdir()})

    def test_publicacao_remove_assets_retirados_da_origem(self):
        origem = self.root / 'dashboard'
        (origem / 'assets').mkdir(parents=True)
        (origem / 'index.html').write_text('<h1>Estudo</h1>')
        (origem / 'assets/antigo.svg').write_text('<svg/>')
        (origem / 'README.md').write_text('Documentação')
        with patch('preparar_dashboard.montar_dataset', return_value={'questions': [], 'exams': []}):
            preparar(self.root)
            self.assertTrue((self.root / 'dist/assets/antigo.svg').exists())
            (origem / 'assets/antigo.svg').unlink()
            (origem / 'assets/atual.svg').write_text('<svg id="atual"/>')
            preparar(self.root)
        self.assertFalse((self.root / 'dist/assets/antigo.svg').exists())
        self.assertEqual((self.root / 'dist/assets/atual.svg').read_text(), '<svg id="atual"/>')
        self.assertFalse((self.root / 'dist/README.md').exists())

    def test_temporal_preserva_lacunas_zeros_e_etapas(self):
        provas = [self.prova,
                  {**self.prova, 'prova_id': 'anterior', 'ano_aplicacao': '2018'},
                  {**self.prova, 'prova_id': 'outro-dia', 'ano_aplicacao': '2018', 'etapa': '3º dia'}]
        serie = serie_temporal(provas, [{'prova_id': 'p'}, {'prova_id': 'outro-dia'}], [])
        grupo = [r for r in serie if r['nivel'] == 'estrato' and r['etapa'] == '2ª fase']
        zero = next(r for r in grupo if r['tipo'] == 'ano' and r['janela'] == '2018')
        lacuna = next(r for r in grupo if r['tipo'] == 'ano' and r['janela'] == '2019')
        self.assertEqual(zero['incidencia_percentual'], 0)
        self.assertIsNone(lacuna['incidencia_percentual'])
        posterior = next(r for r in grupo if r['tipo'] == 'período' and r['janela'] == '2024–2026')
        self.assertEqual(posterior['diferenca_incidencia_pp_referencia'], 50)
        painel = next(r for r in serie if r['nivel'] == 'painel comum' and r['janela'] == '2017–2021')
        self.assertEqual(painel['provas'], 1)
        self.assertEqual(painel['questoes_amazonicas'], 0)
        self.assertEqual(fmt(-3.125, 2), '-3,13')


if __name__ == '__main__':
    unittest.main()
