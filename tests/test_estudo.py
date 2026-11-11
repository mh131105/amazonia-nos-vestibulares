"""Protege a limpeza e o denominador da pergunta principal com dados fictícios."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from limpeza import limpar, gravar_csv, ler_csv
from analise import analisar


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
        with self.assertRaises(AssertionError):
            limpar(self.root)


if __name__ == '__main__':
    unittest.main()
