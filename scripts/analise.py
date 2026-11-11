"""Gera a análise exploratória e as tabelas de cobrança a partir do dataset limpo."""
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from limpeza import gravar_csv, ler_csv

ROOT = Path(__file__).resolve().parents[1]


def tabela(colunas, linhas):
    return '\n'.join(['| ' + ' | '.join(colunas) + ' |',
                      '| ' + ' | '.join('---' for _ in colunas) + ' |'] +
                     ['| ' + ' | '.join(str(v).replace('|', ',') for v in linha) + ' |' for linha in linhas])


def analisar(root=ROOT):
    questoes = ler_csv(root / 'dados/curado/questoes.csv')
    provas = ler_csv(root / 'dados/provas.csv')
    ementas = ler_csv(root / 'dados/ementas.csv')
    topicos = {r['topico_id']: r for r in ler_csv(root / 'dados/topicos.csv')}
    por_prova, por_item = defaultdict(list), defaultdict(set)
    for q in questoes:
        assert q['topico_id'] in topicos, q['questao_id']
        por_prova[q['prova_id']].append(q)
        for item in filter(None, q['ementa_itens'].split('|')):
            por_item[item].add(q['questao_id'])

    frequencias = []
    for topico_id, t in topicos.items():
        itens = [q for q in questoes if q['topico_id'] == topico_id]
        frequencias.append({'topico_id': topico_id, 'disciplina': t['disciplina'],
                            'conteudo': t['conteudo'], 'topico': t['topico'],
                            'questoes': len(itens),
                            'percentual_banco': f'{100*len(itens)/len(questoes):.2f}' if questoes else '0.00',
                            'provas': len({q['prova_id'] for q in itens}),
                            'anos': '|'.join(sorted({q['ano_aplicacao'] for q in itens})),
                            'instituicoes': '|'.join(sorted({q['instituicao'] for q in itens}))})
    frequencias.sort(key=lambda r: (-r['questoes'], r['topico_id']))
    cobertura = []
    for p in provas:
        regionais = [e for e in ementas if e['prova_id'] == p['prova_id'] and e['escopo'] == 'regional explícito']
        cobrados = sum(bool(por_item[e['ementa_item_id']]) for e in regionais)
        comparavel = p['triagem_completa'] == 'sim' and p['ementa_regional_completa'] == 'sim' and bool(regionais)
        previstos_topicos = {t for e in regionais for t in e['topicos_ids'].split('|') if t}
        cobrados_topicos = set()
        for e in regionais:
            for q in por_prova[p['prova_id']]:
                if e['ementa_item_id'] in q['ementa_itens'].split('|'):
                    cobrados_topicos.update(set(e['topicos_ids'].split('|')) &
                                             set(q['topicos_ids'].split('|')))
        cobrados_topicos.discard('')
        cobertura.append({'prova_id': p['prova_id'], 'instituicao': p['instituicao'],
                          'processo': p['processo'], 'edicao': p['edicao'],
                          'ano_aplicacao': p['ano_aplicacao'], 'etapa': p['etapa'],
                          'questoes_triadas': p['questoes_triadas'],
                          'questoes_amazonicas': len(por_prova[p['prova_id']]),
                          'itens_regionais_previstos': len(regionais),
                          'itens_regionais_cobrados': cobrados if comparavel else '',
                          'cobertura_itens_percentual': f'{100*cobrados/len(regionais):.2f}' if comparavel else '',
                          'topicos_padronizados_previstos': len(previstos_topicos),
                          'topicos_padronizados_cobrados': len(cobrados_topicos) if comparavel else '',
                          'cobertura_topicos_percentual': f'{100*len(cobrados_topicos)/len(previstos_topicos):.2f}' if comparavel and previstos_topicos else '',
                          'topicos_previstos_ids': '|'.join(sorted(previstos_topicos)),
                          'topicos_cobrados_ids': '|'.join(sorted(cobrados_topicos)) if comparavel else '',
                          'comparacao_completa': 'sim' if comparavel else 'não',
                          'observacao': p['observacao']})
    gravar_csv(root / 'resultados/previsto-cobrado.csv', cobertura, list(cobertura[0]))
    for f in frequencias:
        previstas = [c for c in cobertura if c['comparacao_completa'] == 'sim'
                     and f['topico_id'] in c['topicos_previstos_ids'].split('|')]
        cobradas = [c for c in previstas if f['topico_id'] in c['topicos_cobrados_ids'].split('|')]
        f['questoes_multitopico'] = sum(f['topico_id'] in q['topicos_ids'].split('|') for q in questoes)
        f['provas_com_previsao_regional'] = len(previstas)
        f['provas_com_cobranca_regional'] = len(cobradas)
        f['percentual_provas_previstas_com_cobranca'] = f'{100*len(cobradas)/len(previstas):.2f}' if previstas else ''
    gravar_csv(root / 'resultados/frequencia-topicos.csv', frequencias, list(frequencias[0]))
    itens_resultado = []
    for e in ementas:
        ids = sorted(por_item[e['ementa_item_id']])
        observados = {t for q in questoes if q['questao_id'] in ids for t in q['topicos_ids'].split('|')}
        previstos = set(filter(None, e['topicos_ids'].split('|')))
        itens_resultado.append({**e, 'questoes_identificadas': len(ids), 'questoes_ids': '|'.join(ids),
                               'topicos_cobrados_ids': '|'.join(sorted(previstos & observados)),
                               'topicos_sem_cobranca_ids': '|'.join(sorted(previstos - observados))})
    gravar_csv(root / 'resultados/itens-ementa.csv', itens_resultado, list(itens_resultado[0]))

    por_ies = Counter(q['instituicao'] for q in questoes)
    por_ano = Counter(q['ano_aplicacao'] for q in questoes)
    completos = [c for c in cobertura if c['comparacao_completa'] == 'sim']
    total_previsto = sum(int(c['topicos_padronizados_previstos']) for c in completos)
    total_cobrado = sum(int(c['topicos_padronizados_cobrados']) for c in completos)
    central = sum(q['foco_regional'] == 'central' for q in questoes)
    sem_vinculo = sum(q['tipo_vinculo_ementa'] == 'não localizado' for q in questoes)
    anuladas = sum(q['gabarito'] == 'ANULADA' for q in questoes)
    fontes_sem_hash = sum(not f['sha256'] for f in ler_csv(root / 'dados/fontes.csv'))
    provas_com_questoes = sum(bool(itens) for itens in por_prova.values())
    triadas = sum(int(p['questoes_triadas']) for p in provas)
    por_fase_uea = []
    for prefixo, nome in [('1', '1ª fase — Conhecimentos Gerais'), ('2', '2ª fase — Humanas')]:
        grupo = [p for p in provas if p['instituicao'] == 'UEA' and p['etapa'].startswith(prefixo)]
        comp = [c for c in completos if c['instituicao'] == 'UEA' and c['etapa'].startswith(prefixo)]
        esperado = sum(c['topicos_padronizados_previstos'] for c in comp)
        observado = sum(c['topicos_padronizados_cobrados'] for c in comp)
        n = sum(len(por_prova[p['prova_id']]) for p in grupo)
        por_fase_uea.append([nome, len(grupo), n, f'{n/len(grupo):.1f}' if grupo else '0',
                             f'{100*observado/esperado:.1f}%' if esperado else 'não calculado'])
    resumo_fases = tabela(['UEA', 'Provas', 'Questões amazônicas', 'Questões/prova', 'Cobertura regional explícita'], por_fase_uea)
    taxas = [float(c['cobertura_topicos_percentual']) for c in completos]
    faixa = (f'Entre as provas comparáveis, a mediana foi **{median(taxas):.1f}%**, '
             f'com valores de **{min(taxas):.1f}% a {max(taxas):.1f}%**.' if taxas else '')
    principais = [r for r in frequencias if r['questoes']][:12]
    topico_tabela = tabela(['Tópico padronizado', 'Questões', '% do banco', 'Provas'],
                           [[r['topico'], r['questoes'], r['percentual_banco'], r['provas']] for r in principais])
    sem_cobranca = sorted([f for f in frequencias if f['provas_com_previsao_regional'] and not f['provas_com_cobranca_regional']],
                          key=lambda f: -f['provas_com_previsao_regional'])[:8]
    lacunas_tabela = tabela(['Tópico previsto', 'Provas com previsão explícita', 'Provas com cobrança vinculada'],
                            [[f['topico'], f['provas_com_previsao_regional'], 0] for f in sem_cobranca])
    cobertura_tabela = tabela(['Prova', 'Aplicação', 'Etapa/fase', 'Tópicos previstos', 'Tópicos cobrados', '%'],
                             [[c['prova_id'], c['ano_aplicacao'], c['etapa'], c['topicos_padronizados_previstos'],
                               c['topicos_padronizados_cobrados'], c['cobertura_topicos_percentual']] for c in completos])
    resposta = (f'Nas **{len(completos)} provas com programa regional integral e triagem completa**, '
                f'**{total_cobrado} de {total_previsto} tópicos com previsão regional explícita tiveram cobrança identificada '
                f'({100*total_cobrado/total_previsto:.1f}%)**.' if total_previsto else
                'A cobertura da ementa não foi calculada: ainda não há prova com as duas condições completas.')
    relatorio = f'''# O que os vestibulares cobram de História e Geografia da Amazônia?

{resposta} O cálculo conta pares **prova × tópico padronizado**; um mesmo conteúdo previsto em cinco provas entra cinco vezes. Não é uma porcentagem de todo o conhecimento sobre a Amazônia.

## Banco analisado

São **{len(questoes)} questões amazônicas**, de **{provas_com_questoes} provas com ocorrências**, selecionadas após examinar **{triadas} itens** dos blocos pertinentes. O cadastro de cobertura contém {len(provas)} provas, incluindo {len(provas)-provas_com_questoes} sem questões elegíveis. A unidade é a questão numerada: subitens permanecem juntos. Fase/etapa é um atributo da prova no mesmo dataset.

{tabela(['Origem', 'Questões'], sorted(por_ies.items()))}

### Distribuição por ano de aplicação

{tabela(['Ano', 'Questões'], [(str(y), por_ano[str(y)]) for y in range(2017, 2027)])}

O recorte é 01/01/2017 a 11/11/2026. Ano da edição, ingresso e aplicação são distintos: UEA2020 e Enem2020 foram aplicados em 2021; UEA2021, em 2022. Quando o dia efetivo não foi corroborado, a data fica vazia e a base anual está nas observações. As quantidades descrevem o acervo coletado; lacunas de cobertura não são anos sem cobrança. No Enem, o exame é a origem; não se atribui a questão a uma universidade específica.

## Conteúdos mais presentes

{topico_tabela}

Cada questão recebe um tópico principal para esta distribuição; pode se relacionar com vários itens do programa. A taxonomia está em [topicos.csv](../dados/topicos.csv), organizada por disciplina, conteúdo e tópico. Esses três campos seguem a classificação principal; `disciplina_origem` conserva a identificação registrada na coleta. Os nomes originais dos editais permanecem em [ementas.csv](../dados/ementas.csv).

### Conteúdos previstos sem cobrança identificada

{lacunas_tabela}

Esses zeros se referem às provas comparáveis com previsão explícita do tópico e exigem vínculo com o item correspondente. A tabela [frequencia-topicos.csv](frequencia-topicos.csv) também mostra a frequência por múltiplos tópicos e a proporção de provas que cobraram cada tópico entre aquelas que o previam. Um tópico pode aparecer no banco sob uma cláusula geral e continuar sem cobrança vinculada ao recorte explícito desta tabela.

## Quanto da ementa apareceu em cada prova?

{faixa}

{cobertura_tabela}

O denominador é o conjunto de tópicos padronizados associados aos itens regionais explícitos da ementa de cada prova. O numerador conta os tópicos exigidos por pelo menos uma questão vinculada semanticamente ao item pertinente. Compartilhar uma categoria ampla não basta: uma questão sobre o Acre em 1903 não é vínculo com um item exclusivo sobre Madri em 1750. Tópicos repetidos em vários itens do mesmo programa contam uma vez. Um item amplo pode conter vários tópicos: a cobrança de um deles não transforma todo o item em conteúdo cobrado. Não se calcula essa porcentagem quando falta o programa regional integral ou a triagem completa da prova. A tabela detalhada também conserva a contagem por item original para permitir conferir a interpretação.

A tabela [itens-ementa.csv](itens-ementa.csv) mostra a redação oficial, a fonte e as questões ligadas a cada item, incluindo os que não tiveram questão identificada. Zero significa ausência no recorte efetivamente examinado; não significa que o assunto nunca caiu. [previsto-cobrado.csv](previsto-cobrado.csv) contém todas as provas e os limites de cobertura.

### As duas fases da UEA

{resumo_fases}

As fases permanecem no mesmo banco; esta comparação usa o atributo da prova. A média de questões é descritiva das dez edições coletadas. A cobertura considera apenas as edições com programa regional integral recuperado. Um valor zero nessa medida significa que as questões não foram ligadas aos itens com previsão regional **explícita**; questões amazônicas podem estar amparadas por cláusulas gerais do programa.

## Coleta, limpeza e curadoria

As fontes são cadernos e programas das instituições e das organizadoras oficiais, obtidos diretamente ou por cópias públicas identificadas como tal. `fontes.csv` distingue o endereço de download da publicação institucional. Cada questão conserva prova, número, página, URL e hash do PDF. Foram mantidas {central} questões de foco central e {len(questoes)-central} com cobrança regional substantiva dentro de contexto misto. Menções decorativas à Amazônia, conteúdo geral e “Amazônia Azul” foram excluídos. O campo `justificativa` explica a inclusão.

A limpeza padroniza Unicode e espaços, remove duplicatas exatas de uma mesma prova/número e valida vínculos com fontes, provas e ementas. Não traduz distratores incorretos em afirmações factuais nem preenche respostas por inferência. Mapas, gráficos e imagens devem ser consultados no PDF, na página registrada. Correções de extração conferidas na imagem ficam declaradas no registro bruto.

As {anuladas} questões com anulação oficial permanecem porque constaram dos cadernos; o campo `gabarito=ANULADA` permite identificá-las. A análise de conteúdo conta sua presença na prova, sem tratá-las como itens válidos para pontuação.

A seleção e a classificação semântica foram feitas por agentes de IA (Codex), sem exigir anotação manual de Matheus e sem avaliação de modelos como etapa do estudo. São decisões de curadoria rastreáveis, sujeitas a revisão; não são rótulos humanos. Há {sem_vinculo} questões sem vínculo programático localizado e {fontes_sem_hash} fontes consultadas sem hash de arquivo local. Nenhuma dessas lacunas foi preenchida por presunção.

## Como interpretar os resultados

Frequência no banco mede a composição do acervo, não a probabilidade de uma questão futura. Comparações entre instituições ou fases precisam considerar o número de provas cobertas, o tamanho dos blocos e a granularidade de cada edital. Compilações discursivas reúnem as questões oferecidas; não representam todas as questões respondidas por um único candidato.

A lista de tópicos previstos sem cobrança e a concentração observada nos tópicos mais recorrentes respondem à pergunta do estudo dentro da cobertura documentada. A fração da ementa mede tópicos e depende da granularidade da taxonomia; não mede extensão do texto, carga horária ou domínio exigido.

Cobertura: núcleo UEA Vestibular 2017–2026 (Conhecimentos Gerais e Específicos/Humanas) e UFAM PSC 2018–2026, aplicados dentro do recorte; Enem regular impresso 2017–2025 e segunda fase FUVEST 2017–2026; complemento UFRR PI 2025/2026 e UERR 2025/2026. O programa UEA 2017 e dois editais PSC 2018 não foram recuperados integralmente. A comparação programática nacional é temática e ampla: Enem/FUVEST não entram na porcentagem regional explícita. O Enem 2026 teve o [primeiro dia aplicado em 08/11/2026](https://www.gov.br/inep/pt-br/centrais-de-conteudo/noticias/enem/participantes-concluem-primeiro-dia-do-enem-2026), mas o PDF oficial não foi localizado até a consulta; isso é lacuna de coleta. O levantamento não é um censo de todas as instituições e modalidades brasileiras.
'''
    (root / 'resultados/relatorio.md').write_text(relatorio, encoding='utf-8')
    print(f'EDA: {len(questoes)} questões; {len(completos)} provas comparáveis; '
          f'{total_cobrado}/{total_previsto} pares prova × tópico cobrados.')
    return cobertura


if __name__ == '__main__':
    analisar()
