"""Padroniza o banco amazônico selecionado pelos agentes, sem reclassificar conteúdo."""
import csv
import hashlib
import json
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
COLUNAS = ['questao_id', 'prova_id', 'instituicao', 'processo', 'edicao',
           'ano_aplicacao', 'data_aplicacao', 'etapa', 'disciplina_origem', 'disciplina', 'numero',
           'tipo_resposta', 'enunciado', 'alternativa_a', 'alternativa_b',
           'alternativa_c', 'alternativa_d', 'alternativa_e', 'gabarito',
           'topico_id', 'conteudo', 'topico', 'topicos_ids', 'ementa_itens', 'tipo_vinculo_ementa', 'foco_regional',
           'justificativa', 'fonte_prova_id', 'url_prova', 'paginas_pdf',
           'fonte_sha256', 'recurso_visual', 'observacao', 'curadoria',
           'sha256_texto_limpo']


def texto(valor):
    valor = unicodedata.normalize('NFC', str(valor or '')).replace('\u00ad', '')
    for ligatura, letras in [('ﬁ', 'fi'), ('ﬂ', 'fl'), ('ﬀ', 'ff'), ('ﬃ', 'ffi'), ('ﬄ', 'ffl')]:
        valor = valor.replace(ligatura, letras)
    valor = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\ufeff]', '', valor)
    return re.sub(r'\s+', ' ', valor).strip()


def ler_csv(caminho):
    with caminho.open(encoding='utf-8', newline='') as arquivo:
        return list(csv.DictReader(arquivo))


def gravar_csv(caminho, linhas, colunas):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open('w', encoding='utf-8', newline='') as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=colunas, lineterminator='\n')
        writer.writeheader()
        writer.writerows(linhas)


def indexar(linhas, chave):
    indice = {r[chave]: r for r in linhas}
    if len(indice) != len(linhas) or '' in indice:
        raise ValueError(f'Identificador ausente ou duplicado: {chave}')
    return indice


def exigir(condicao, mensagem):
    if not condicao:
        raise ValueError(mensagem)


def limpar(root=ROOT):
    fontes = indexar(ler_csv(root / 'dados/fontes.csv'), 'fonte_id')
    provas = indexar(ler_csv(root / 'dados/provas.csv'), 'prova_id')
    topicos = indexar(ler_csv(root / 'dados/topicos.csv'), 'topico_id')
    ementas = indexar(ler_csv(root / 'dados/ementas.csv'), 'ementa_item_id')
    for e in ementas.values():
        exigir(e['prova_id'] in provas and e['fonte_id'] in fontes,
               f"Prova ou fonte desconhecida na ementa: {e['ementa_item_id']}")
        exigir(all(t in topicos for t in e['topicos_ids'].split('|') if t),
               f"Tópico desconhecido na ementa: {e['ementa_item_id']}")
    dados = [json.loads(linha) for linha in (root / 'dados/brutos/questoes.jsonl')
             .read_text(encoding='utf-8').splitlines() if linha.strip()]
    saida, vistos, duplicados = [], {}, 0
    for bruto in dados:
        linha = {k: texto(bruto.get(k)) for k in COLUNAS}
        exigir(bool(linha['questao_id']), 'questao_id ausente')
        prova = provas[linha['prova_id']]
        fonte = fontes[linha['fonte_prova_id']]
        exigir(linha['fonte_prova_id'] == prova['fonte_prova_id'],
               f"Fonte diferente da prova cadastrada: {linha['questao_id']}")
        exigir(fonte['tipo'] == 'prova', f"Fonte não é prova: {linha['questao_id']}")
        exigir(fonte['sha256'] == linha['fonte_sha256'], f"SHA-256 divergente: {linha['questao_id']}")
        exigir(fonte['url'] == linha['url_prova'], f"URL divergente: {linha['questao_id']}")
        for chave in ['instituicao', 'processo', 'edicao', 'ano_aplicacao', 'data_aplicacao', 'etapa']:
            exigir(linha[chave] == prova[chave], f"{chave} diverge da prova: {linha['questao_id']}")
        exigir(not linha['ano_aplicacao'] or 2017 <= int(linha['ano_aplicacao']) <= 2026,
               f"Ano fora do recorte: {linha['questao_id']}")
        exigir(linha['disciplina'] in {'História', 'Geografia'}, f"Disciplina inválida: {linha['questao_id']}")
        exigir(linha['foco_regional'] in {'central', 'misto_substantivo'}, f"Foco inválido: {linha['questao_id']}")
        exigir(linha['enunciado'] and linha['justificativa'] and linha['topico_id'],
               f"Enunciado, justificativa ou tópico ausente: {linha['questao_id']}")
        topico = topicos[linha['topico_id']]
        linha['disciplina_origem'] = linha['disciplina']
        linha['disciplina'] = topico['disciplina']
        linha['conteudo'], linha['topico'] = topico['conteudo'], topico['topico']
        topicos_questao = list(dict.fromkeys(filter(None, linha['topicos_ids'].split('|'))))
        exigir(linha['topico_id'] in topicos_questao, f"Tópico principal fora das etiquetas: {linha['questao_id']}")
        exigir(all(t in topicos for t in topicos_questao), f"Tópico desconhecido: {linha['questao_id']}")
        linha['topicos_ids'] = '|'.join(topicos_questao)
        paginas = linha['paginas_pdf'].split('|')
        exigir(paginas and all(p.isdigit() and int(p) > 0 for p in paginas),
               f"Página de PDF inválida: {linha['questao_id']}")
        itens = list(dict.fromkeys(filter(None, linha['ementa_itens'].split('|'))))
        for item in itens:
            exigir(ementas[item]['prova_id'] == linha['prova_id'],
                   f"Item de ementa de outra prova: {linha['questao_id']} / {item}")
        linha['ementa_itens'] = '|'.join(itens)
        exigir(itens or linha['tipo_vinculo_ementa'] == 'não localizado',
               f"Vínculo sem item de ementa: {linha['questao_id']}")
        exigir(linha['tipo_vinculo_ementa'] in {'direto', 'amplo', 'não localizado'},
               f"Tipo de vínculo inválido: {linha['questao_id']}")
        for campo in ['enunciado', 'alternativa_a', 'alternativa_b', 'alternativa_c', 'alternativa_d', 'alternativa_e']:
            exigir('\ufffd' not in linha[campo], f"Texto ilegível: {linha['questao_id']} / {campo}")
        texto_banco = '\n'.join(linha[k] for k in ['enunciado', 'alternativa_a', 'alternativa_b',
                                                  'alternativa_c', 'alternativa_d', 'alternativa_e'])
        linha['sha256_texto_limpo'] = hashlib.sha256(texto_banco.encode()).hexdigest()
        identidade = (linha['prova_id'], linha['numero'])
        if identidade in vistos:
            exigir(vistos[identidade] == linha, f'Duas versões conflitantes: {identidade}')
            duplicados += 1
            continue
        exigir(linha['questao_id'] not in {r['questao_id'] for r in saida},
               f"questao_id duplicado: {linha['questao_id']}")
        vistos[identidade] = linha
        saida.append(linha)
    saida.sort(key=lambda r: (int(r['ano_aplicacao'] or 9999), r['instituicao'], r['prova_id'], r['numero']))
    gravar_csv(root / 'dados/curado/questoes.csv', saida, COLUNAS)
    print(f'{len(dados)} registros brutos → {len(saida)} questões limpas; '
          f'{duplicados} duplicatas exatas removidas.')
    return saida


if __name__ == '__main__':
    limpar()
