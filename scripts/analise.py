"""Gera a análise exploratória e as tabelas de cobrança a partir do dataset limpo."""
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_HALF_UP
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

    apresentar(root, questoes, provas, ementas, topicos, cobertura, frequencias)
    return cobertura


def percentual(n, d):
    return 100 * n / d if d else None


def fmt(valor, casas=1):
    if valor is None:
        return '—'
    arredondado = Decimal(f'{valor:.6f}').quantize(Decimal(1).scaleb(-casas), rounding=ROUND_HALF_UP)
    return f'{arredondado:.{casas}f}'.replace('.', ',')


def estrato(prova):
    return tuple(prova[k] for k in ['instituicao', 'processo', 'etapa'])


def nome_estrato(chave):
    ies, processo, etapa = chave
    return f'{ies} — {processo} — {etapa}'


def resumir(provas, questoes, cobertura):
    ids = {p['prova_id'] for p in provas}
    qs = [q for q in questoes if q['prova_id'] in ids]
    comp = [c for c in cobertura if c['prova_id'] in ids and c['comparacao_completa'] == 'sim']
    triadas = sum(int(p['questoes_triadas']) for p in provas)
    previstas = sum(int(c['topicos_padronizados_previstos']) for c in comp)
    cobradas = sum(int(c['topicos_padronizados_cobrados']) for c in comp)
    contagem = Counter(q['prova_id'] for q in qs)
    taxas_prova = [100 * contagem[p['prova_id']] / int(p['questoes_triadas'])
                  for p in provas if int(p['questoes_triadas'])]
    return dict(provas=len(provas), provas_ids='|'.join(sorted(ids)),
                questoes_triadas=triadas, questoes_amazonicas=len(qs),
                incidencia_percentual=percentual(len(qs), triadas),
                media_provas_percentual=sum(taxas_prova)/len(taxas_prova) if taxas_prova else None,
                provas_com_ementa_completa=len(comp),
                topicos_previstos=previstas, topicos_cobrados=cobradas,
                cobertura_percentual=percentual(cobradas, previstas))


def serie_temporal(provas, questoes, cobertura):
    chaves = sorted({estrato(p) for p in provas})
    referencia = {estrato(p) for p in provas if 2017 <= int(p['ano_aplicacao']) <= 2021}
    posterior = {estrato(p) for p in provas if 2024 <= int(p['ano_aplicacao']) <= 2026}
    comuns = referencia & posterior
    janelas = [('2017–2021', 2017, 2021), ('2022–2023', 2022, 2023),
               ('2024', 2024, 2024), ('2025–2026', 2025, 2026),
               ('2024–2026', 2024, 2026), ('2024–2025', 2024, 2025)]
    saida = []
    grupos = [('estrato', k, [p for p in provas if estrato(p) == k]) for k in chaves]
    grupos += [('painel comum', ('Todas', 'Mesmos estratos', 'Todas'),
                [p for p in provas if estrato(p) in comuns]),
               ('acervo inteiro', ('Todas', 'Todos', 'Todas'), provas)]
    for nivel, chave, grupo in grupos:
        ref = resumir([p for p in grupo if 2017 <= int(p['ano_aplicacao']) <= 2021], questoes, cobertura)
        periodos = [('ano', str(y), y, y) for y in range(2017, 2027)]
        periodos += [('período', *j) for j in janelas]
        if nivel == 'estrato' and chave[0:2] == ('UFAM', 'PSC'):
            corte = 2022 + int(chave[2].split('—')[1].strip()[0]) - 1
            periodos += [('corte seriado', f'Antes de {corte}', 2017, corte-1),
                         ('corte seriado', f'A partir de {corte}', corte, 2026)]
        for tipo, janela, inicio, fim in periodos:
            ps = [p for p in grupo if inicio <= int(p['ano_aplicacao']) <= fim]
            r = resumir(ps, questoes, cobertura)
            r = dict(nivel=nivel, instituicao=chave[0], processo=chave[1], etapa=chave[2],
                     tipo=tipo, janela=janela, inicio=inicio, fim=fim,
                     pertence_painel_comum='sim' if nivel == 'painel comum' or chave in comuns else 'não', **r)
            for medida in ['incidencia', 'cobertura']:
                a, b = r[f'{medida}_percentual'], ref[f'{medida}_percentual']
                r[f'diferenca_{medida}_pp_referencia'] = a-b if tipo == 'período' and a is not None and b is not None else None
            taxas = [resumir([p for p in ps if estrato(p) == k], questoes, cobertura)['incidencia_percentual']
                     for k in comuns] if nivel == 'painel comum' else []
            r['media_estratos_percentual'] = sum(taxas)/len(taxas) if taxas and all(t is not None for t in taxas) else None
            saida.append(r)
    return saida


def pares_cobrados(questoes, ementas, provas_ids):
    regionais = {e['ementa_item_id']: e for e in ementas
                 if e['prova_id'] in provas_ids and e['escopo'] == 'regional explícito'}
    pares = set()
    for q in questoes:
        for item in q['ementa_itens'].split('|'):
            if item in regionais:
                pares.update((q['prova_id'], t) for t in
                             set(q['topicos_ids'].split('|')) & set(regionais[item]['topicos_ids'].split('|')) if t)
    return pares


def sensibilidades(questoes, provas, ementas, cobertura):
    comp = {c['prova_id'] for c in cobertura if c['comparacao_completa'] == 'sim'}
    variantes = [('Base', lambda q: True, comp),
                 ('Sem anuladas', lambda q: q['gabarito'] != 'ANULADA', comp),
                 ('Somente foco central', lambda q: q['foco_regional'] == 'central', comp),
                 ('Central sem anuladas', lambda q: q['foco_regional'] == 'central' and q['gabarito'] != 'ANULADA', comp),
                 ('Sem 2026', lambda q: int(q['ano_aplicacao']) <= 2025,
                  {p['prova_id'] for p in provas if p['prova_id'] in comp and int(p['ano_aplicacao']) <= 2025})]
    saida = []
    for nome, regra, ids in variantes:
        qs = [q for q in questoes if regra(q)]
        previstos = {(e['prova_id'], t) for e in ementas
                     if e['prova_id'] in ids and e['escopo'] == 'regional explícito'
                     for t in e['topicos_ids'].split('|') if t}
        cobrados = pares_cobrados(qs, ementas, ids)
        saida.append(dict(cenario=nome, questoes_banco=len(qs),
                          questoes_comparaveis=sum(q['prova_id'] in ids for q in qs),
                          provas_comparaveis=len(ids), pares_previstos=len(previstos),
                          pares_cobrados=len(cobrados), cobertura_percentual=percentual(len(cobrados), len(previstos))))
    return saida


def gravar_numeros(caminho, linhas):
    gravar_csv(caminho, [{k: '' if v is None else f'{v:.6f}' if isinstance(v, float) else v
                         for k, v in r.items()} for r in linhas], list(linhas[0]))


def apresentar(root, questoes, provas, ementas, topicos, cobertura, frequencias):
    temporal = serie_temporal(provas, questoes, cobertura)
    sens = sensibilidades(questoes, provas, ementas, cobertura)
    gravar_numeros(root / 'resultados/temporal.csv', temporal)
    gravar_numeros(root / 'resultados/sensibilidade.csv', sens)
    comp = [c for c in cobertura if c['comparacao_completa'] == 'sim']
    comp_ids = {c['prova_id'] for c in comp}
    previsto = sum(int(c['topicos_padronizados_previstos']) for c in comp)
    cobrado = sum(int(c['topicos_padronizados_cobrados']) for c in comp)
    itens_prev = sum(int(c['itens_regionais_previstos']) for c in comp)
    itens_cob = sum(int(c['itens_regionais_cobrados']) for c in comp)
    itens_com_intersecao = sum(any(e['ementa_item_id'] in q['ementa_itens'].split('|')
                                  and set(e['topicos_ids'].split('|')) & set(q['topicos_ids'].split('|'))
                                  for q in questoes)
                              for e in ementas if e['prova_id'] in comp_ids and e['escopo'] == 'regional explícito')
    taxas = [100 * int(c['topicos_padronizados_cobrados']) / int(c['topicos_padronizados_previstos']) for c in comp]
    n, triadas = len(questoes), sum(int(p['questoes_triadas']) for p in provas)
    origens = sorted({p['instituicao'] for p in provas})
    contagem = Counter(q['prova_id'] for q in questoes)
    por_ies = []
    for ies in origens:
        ps = [p for p in provas if p['instituicao'] == ies]
        r = resumir(ps, questoes, cobertura)
        por_ies.append([ies, r['provas'], r['questoes_triadas'], r['questoes_amazonicas'],
                        r['provas_com_ementa_completa'],
                        f"{r['topicos_cobrados']}/{r['topicos_previstos']} ({fmt(r['cobertura_percentual'])}%)" if r['topicos_previstos'] else 'Não calculada'])
    areas = Counter()
    for q in questoes:
        ds = {topicos[t]['disciplina'] for t in q['topicos_ids'].split('|')}
        areas['História + Geografia' if len(ds) > 1 else next(iter(ds))] += 1
    grupo_escopo = Counter()
    indice_ementas = {e['ementa_item_id']: e for e in ementas}
    for q in questoes:
        escopos = {indice_ementas[i]['escopo'] for i in q['ementa_itens'].split('|') if i}
        grupo_escopo['ambos' if len(escopos) > 1 else next(iter(escopos)) if escopos else 'sem vínculo'] += 1
    principal = Counter(q['disciplina'] for q in questoes)
    origem = Counter(q['disciplina_origem'] for q in questoes)
    principais = [f for f in frequencias if f['questoes']][:12]
    top5 = sum(f['questoes'] for f in principais[:5])
    lacunas = sorted([f for f in frequencias if f['provas_com_previsao_regional'] and not f['provas_com_cobranca_regional']],
                     key=lambda f: -f['provas_com_previsao_regional'])
    observados = {t for q in questoes for t in q['topicos_ids'].split('|')}
    notas = []
    # Conferências referenciadas ao acervo real; não alteram a base curada.
    if any(q['questao_id'] == 'uea-2026-ce-q05' for q in questoes):
        notas.append('A questão `uea-2026-ce-q05` (Pará, 1823, prova p.3) contém um vínculo adicional ao item '
                     '`uea-vest2026-ce__uea-vest2026-historia-027` (“Império Brasileiro: 2º Reinado.”, programa p.8). '
                     'Esse vínculo adicional é cronologicamente inadequado. A análise do exemplo usa o item H024 '
                     '(“Revoluções e independências nas Américas”), também registrado. A simulação de retirar somente H027 '
                     'não modifica 141/682 nem 0/14, pois H027 tem escopo geral. O registro curado foi preservado e a ressalva fica explícita para revisão.')
    # Sensibilidade com o mesmo conjunto de tópicos nas provas UEA dos dois períodos.
    uea_comp = [c for c in comp if c['instituicao'] == 'UEA' and
                (2017 <= int(c['ano_aplicacao']) <= 2021 or 2024 <= int(c['ano_aplicacao']) <= 2026)]
    comuns_topicos = set.intersection(*(set(c['topicos_previstos_ids'].split('|')) for c in uea_comp)) if uea_comp else set()
    tabela_comuns = []
    composicao_comuns = {t: [] for t in sorted(comuns_topicos)}
    for label, a, b in [('2017–2021', 2017, 2021), ('2024–2026', 2024, 2026)]:
        cs = [c for c in uea_comp if a <= int(c['ano_aplicacao']) <= b]
        numerador = sum(len(set(c['topicos_cobrados_ids'].split('|')) & comuns_topicos) for c in cs)
        denominador = len(cs) * len(comuns_topicos)
        tabela_comuns.append([label, len(cs), len(comuns_topicos), f'{numerador}/{denominador}', fmt(percentual(numerador, denominador))])
        for t in composicao_comuns:
            composicao_comuns[t].append(f"{sum(t in c['topicos_cobrados_ids'].split('|') for c in cs)}/{len(cs)}")
    def rows_temporal(nivel, janela):
        return [r for r in temporal if r['nivel'] == nivel and r['tipo'] == 'período' and r['janela'] == janela]
    antes = {(r['instituicao'], r['processo'], r['etapa']): r for r in rows_temporal('estrato', '2017–2021')}
    depois = rows_temporal('estrato', '2024–2026')
    contraste = []
    for r in depois:
        if r['pertence_painel_comum'] != 'sim':
            continue
        ref = antes[(r['instituicao'], r['processo'], r['etapa'])]
        contraste.append([nome_estrato((r['instituicao'], r['processo'], r['etapa'])),
                          f"{ref['questoes_amazonicas']}/{ref['questoes_triadas']} ({fmt(ref['incidencia_percentual'])}%)",
                          f"{r['questoes_amazonicas']}/{r['questoes_triadas']} ({fmt(r['incidencia_percentual'])}%)",
                          fmt(r['diferenca_incidencia_pp_referencia'], 2)])
    periodos_uea = []
    for janela in ['2017–2021', '2022–2023', '2024', '2025–2026', '2024–2026', '2024–2025']:
        cs = [r for r in rows_temporal('estrato', janela) if r['instituicao'] == 'UEA']
        periodos_uea.append([janela] + [f"{r['questoes_amazonicas']}/{r['questoes_triadas']} ({fmt(r['incidencia_percentual'])}%)" for r in cs])
    agregados = []
    for nivel in ['acervo inteiro', 'painel comum']:
        for janela in ['2017–2021', '2024–2026', '2024–2025']:
            r = rows_temporal(nivel, janela)[0]
            agregados.append([nivel, janela, r['provas'], f"{r['questoes_amazonicas']}/{r['questoes_triadas']}",
                              fmt(r['incidencia_percentual']), fmt(r['media_provas_percentual']), fmt(r['media_estratos_percentual'])])
    anuais = [r for r in temporal if r['nivel'] == 'acervo inteiro' and r['tipo'] == 'ano']
    fases = []
    for chave in sorted({estrato(p) for p in provas if p['instituicao'] in {'UEA', 'UFAM'}}):
        r = resumir([p for p in provas if estrato(p) == chave], questoes, cobertura)
        fases.append([nome_estrato(chave), r['provas'], r['questoes_amazonicas'],
                      f"{r['questoes_amazonicas'] / r['provas']:.2f}", r['provas_com_ementa_completa'],
                      f"{r['topicos_cobrados']}/{r['topicos_previstos']}", fmt(r['cobertura_percentual'])])
    por_area = []
    for disciplina in ['História', 'Geografia']:
        prev = {(c['prova_id'], t) for c in comp for t in c['topicos_previstos_ids'].split('|') if t and topicos[t]['disciplina'] == disciplina}
        cob = {(c['prova_id'], t) for c in comp for t in c['topicos_cobrados_ids'].split('|') if t and topicos[t]['disciplina'] == disciplina}
        por_area.append([disciplina, len(cob), len(prev), fmt(percentual(len(cob), len(prev)))])
    cortes_psc = []
    for etapa in sorted({r['etapa'] for r in temporal if r['tipo'] == 'corte seriado'}):
        rs = [r for r in temporal if r['tipo'] == 'corte seriado' and r['etapa'] == etapa]
        cortes_psc.append([etapa] + [f"{r['janela']}: {r['questoes_amazonicas']}/{r['questoes_triadas']} ({fmt(r['incidencia_percentual'])}%)" for r in rs])
    sem_vinculo = sum(q['tipo_vinculo_ementa'] == 'não localizado' for q in questoes)
    sem_gabarito = sum(not q['gabarito'] for q in questoes)
    anuladas = [q['questao_id'] for q in questoes if q['gabarito'] == 'ANULADA']
    fontes = ler_csv(root / 'dados/fontes.csv')
    dup = {k: len(questoes) - len({q[k] for q in questoes}) for k in ['questao_id', 'sha256_texto_limpo']}
    assert not dup['questao_id'], 'IDs duplicados'
    assert len({(q['prova_id'], q['numero']) for q in questoes}) == n, 'Prova/número duplicado'
    triagem_path = root / 'dados/brutos/triagem.csv'
    if triagem_path.exists():
        triagem = ler_csv(triagem_path)
        assert len(triagem) == triadas, 'Triagem diverge do total cadastrado'
        assert len({t['questao_id'] for t in triagem}) == len(triagem), 'IDs de triagem repetidos'
        assert {t['questao_id'] for t in triagem if t['decisao'] == 'incluir'} == {q['questao_id'] for q in questoes}, 'Seleção e banco divergem'
        por_prova_triagem = Counter(t['prova_id'] for t in triagem)
        assert all(por_prova_triagem[p['prova_id']] == int(p['questoes_triadas']) for p in provas), 'Triagem por prova divergente'
    relatorio = f"""# Uma ementa ampla, uma prova seletiva: História e Geografia da Amazônia

## Resposta à pergunta do estudo

**Quanto da ementa realmente apareceu?** Nas **{len(comp)} provas com programa regional integral e triagem completa**, houve cobrança identificada de **{cobrado}/{previsto} pares prova × tópico padronizado: {fmt(percentual(cobrado, previsto))}%**. Essas provas reúnem {sum(q['prova_id'] in comp_ids for q in questoes)} das {n} questões do banco.

O resultado descreve o recorte que cada prova faz de seu próprio programa. Um tópico previsto em cinco provas entra cinco vezes. Os conteúdos vêm das ementas; os nomes, agrupamentos e desdobramentos são decisões de curadoria documentadas. Portanto, a porcentagem depende dessa granularidade. Ela não mede extensão de texto, carga horária nem chance de cair no próximo vestibular.

A resposta ganha três nuances: a frequência se concentra em alguns conteúdos; questões regionais também se vinculam a cláusulas gerais; e a evolução temporal varia entre fases. Na UEA, a primeira fase cresce no contraste de calendário enquanto a segunda recua. Os dados não sustentam uma mudança uniforme nem um efeito causal do Novo Ensino Médio.

## 1. O universo que conseguimos observar

O acervo contém **{n} questões amazônicas**, selecionadas entre **{triadas} itens examinados**, em **{len(provas)} provas**, das quais {sum(bool(contagem[p['prova_id']]) for p in provas)} têm ocorrências e {sum(not contagem[p['prova_id']] for p in provas)} não têm questões elegíveis. São {len(topicos)} tópicos padronizados, {len(observados)} observados com ao menos uma etiqueta e {sum(len(q['topicos_ids'].split('|')) for q in questoes)} associações questão–tópico. As associações não são questões adicionais.

{tabela(['Origem', 'Provas examinadas', 'Itens triados', 'Questões amazônicas', 'Provas com comparação de ementa', 'Cobertura por tópico'], por_ies)}

**Fonte:** [provas.csv](../dados/provas.csv), [questoes.csv](../dados/curado/questoes.csv) e [previsto-cobrado.csv](previsto-cobrado.csv). O Enem é uma origem única, sem replicação por universidade usuária da nota. UEA/PSC têm blocos de História e Geografia; Enem tem Ciências Humanas; FUVEST usa compilações discursivas de H/G. Esses denominadores não representam blocos idênticos.

O núcleo UEA cobre as edições Vestibular/Macro 2017–2026, nas duas fases selecionadas; o PSC cobre edições 2018–2026 nas três etapas aplicadas dentro do recorte. O complemento reúne Enem regular impresso 2017–2025, FUVEST segunda fase 2017–2026 e UERR/UFRR 2025/2026. Não é um censo nacional. Uma cor equivalente por aplicação evita multiplicar questões; subitens discursivos permanecem na questão numerada.

A janela é **01/01/2017 a 11/11/2026**, por ano de aplicação, com 2026 parcial. A edição UEA 2020 e o Enem 2020 foram aplicados em 2021; UEA 2021 foi aplicada em 2022. Há duas edições UEA aplicadas em 2022 e nenhuma observação UEA em 2020. Edição, ingresso e aplicação não são intercambiáveis.

{tabela(['Ano de aplicação', 'Provas', 'Itens triados', 'Questões amazônicas', 'Provas com programa comparável'], [[r['janela'], r['provas'], r['questoes_triadas'], r['questoes_amazonicas'], r['provas_com_ementa_completa']] for r in anuais])}

A série anual completa, inclusive células sem observação, está em [temporal.csv](temporal.csv). Uma célula com zero provas tem proporção vazia; uma prova examinada sem questão amazônica tem proporção zero. A variação dos totais anuais também reflete a cobertura e os calendários.

## 2. O que significa cobrir 20,7% da ementa?

O denominador reúne os tópicos associados a **cláusulas regionais explícitas** de cada prova comparável, com repetição interna removida. O numerador exige uma questão vinculada ao item pertinente e interseção entre os tópicos da questão e os do item. Uma questão sobre Acre/Petrópolis em 1903 não demonstra cobrança de um item exclusivo sobre Madri em 1750, mesmo que ambos tratem de fronteiras.

Os {len(comp)} programas/provas comparáveis são UEA, UFAM, UERR e UFRR. Ficam fora da proporção as 19 provas nacionais com vínculo programático amplo, as duas fases UEA 2017 e PSC 2018 E1/E2 com programa pendente, além de quatro PSC E1 recentes sem previsão regional explícita registrada. Ausência de denominador regional não vira cobertura zero.

![Cobertura dos tópicos regionais por prova e origem](figuras/cobertura-ementa.png)

**Figura 1.** Cada ponto pequeno é uma prova; o losango mostra a razão dos totais de tópicos cobrados/previstos de sua origem. A linha marca o agregado de {fmt(percentual(cobrado, previsto))}%. UERR/UFRR têm apenas duas provas cada. Fonte: [previsto-cobrado.csv](previsto-cobrado.csv); reprodução: `python scripts/figuras.py`.

A mediana das proporções por prova é {fmt(median(taxas) if taxas else None)}%, a média simples é {fmt(sum(taxas)/len(taxas) if taxas else None)}% e a faixa vai de {fmt(min(taxas) if taxas else None)}% a {fmt(max(taxas) if taxas else None)}%. A razão {cobrado}/{previsto} dá mais peso a provas com mais tópicos previstos; a média simples dá peso igual a cada prova.

Por registros de cláusulas regionais transcritas, há algum vínculo registrado em **{itens_cob}/{itens_prev} ({fmt(percentual(itens_cob, itens_prev))}%)**. Essa é outra unidade: uma cláusula pode reunir vários tópicos, e qualquer vínculo não demonstra domínio de toda a cláusula. Exigindo também interseção de etiquetas por cláusula, são **{itens_com_intersecao}/{itens_prev} ({fmt(percentual(itens_com_intersecao, itens_prev))}%)**: {itens_cob-itens_com_intersecao} registros ligados a questões não compartilham suas etiquetas. Essa diferença entre vínculo semântico e etiquetas merece revisão; os totais por tópico continuam sendo o indicador principal. A redação original e as correspondências podem ser conferidas em [itens-ementa.csv](itens-ementa.csv).

{tabela(['Área dos tópicos', 'Pares cobrados', 'Pares previstos', 'Cobertura (%)'], por_area)}

A diferença entre áreas descreve a taxonomia e os programas observados; as questões interdisciplinares podem contribuir com um tópico em cada área, sem serem duplicadas no banco.

### Zero de cobertura não é ausência de questão regional

Há {grupo_escopo['geral']} questões ligadas somente a cláusulas gerais, {grupo_escopo['regional explícito']} somente a regionais explícitas, {grupo_escopo['ambos']} a ambas e {grupo_escopo['sem vínculo']} sem item localizado. Isso difere dos rótulos de força do vínculo: direto, amplo e não localizado.

A UEA 2026, segunda fase de Humanas, tem **três questões regionais e 0/14 tópicos regionais explícitos cobrados**. Os objetos são independência no Pará (Q05, p.3), terra preta (Q13, p.5) e rios voadores (Q16, p.7). Os vínculos pertinentes são cláusulas gerais: “Revoluções e independências nas Américas” (programa p.8), “Solo.” e “A dinâmica climática da Terra” (p.9). O zero não demonstra ausência de cobrança amazônica nem questão fora do edital.

{tabela(['Fase/etapa', 'Provas', 'Questões', 'Questões/prova', 'Programas comparáveis', 'Pares cobrados/previstos', 'Cobertura (%)'], fases)}

As duas fases UEA permanecem no mesmo dataset. Os blocos triados têm 24 itens H/G por fase, enquanto cada etapa PSC tem 12. A contagem de questões por prova não mede profundidade ou dificuldade.

## 3. Alguns conteúdos voltam; outros não foram observados

Os cinco tópicos principais mais frequentes reúnem **{top5}/{n} questões ({fmt(percentual(top5, n))}%)**. A classificação principal distribui cada questão uma vez; a classificação múltipla preserva conexões entre assuntos.

![Conteúdos recorrentes em classificações principais e adicionais](figuras/topicos-recorrentes.png)

**Figura 2.** Cada barra conta questões distintas com o tópico; o segmento escuro mostra as que o têm como tópico principal. A soma entre tópicos pode superar {n}. Período: aplicações 2017–11/11/2026. Fonte: [frequencia-topicos.csv](frequencia-topicos.csv) e [questoes.csv](../dados/curado/questoes.csv).

{tabela(['Tópico principal', 'Questões principais', 'Questões com o tópico', 'Provas como principal'], [[f['topico'], f['questoes'], f['questoes_multitopico'], f['provas']] for f in principais])}

Migrações e urbanização lideram como tópico principal. Considerando etiquetas adicionais, povos indígenas e comunidades tradicionais alcançam 21 questões em 20 provas e nas seis origens do banco. Recorrência no acervo não é probabilidade futura: a UEA fornece 107 das 196 questões e influencia o agregado.

Há conexões entre processos históricos e geográficos. `uea2017-geral-q19` (p.10), sobre um caucheiro, articula borracha e deslocamentos; `uea-2025-ce-q19` (p.8) pede leitura de saldo migratório e tipos de migração. São exemplos de objetos cobrados, sem inferência de mudança de dificuldade.

{tabela(['Tópico sem cobrança vinculada', 'Provas com previsão explícita', 'Questões com o tópico em todo o banco'], [[f['topico'], f['provas_com_previsao_regional'], f['questoes_multitopico']] for f in lacunas])}

Os zeros da tabela se limitam às provas que previram explicitamente o tópico e ao vínculo com a cláusula correspondente. Primeira República aparece em questões nacionais mesmo sem cobrança vinculada nas 15 provas com previsão regional explícita; Acre/Petrópolis aparece em duas questões do banco, embora não nas duas provas com sua previsão explícita. Populismo, coronelismo e organização da produção não têm etiqueta em nenhuma questão coletada; suas seis previsões correspondem a duas fases de três edições UEA. Ausência no acervo não autoriza abandonar o conteúdo na preparação.

## 4. História, Geografia e interdisciplinaridade

Pelo tópico principal, são **{principal['História']} questões de História e {principal['Geografia']} de Geografia**. Pelo conjunto de etiquetas, são **{areas['História']} somente História, {areas['Geografia']} somente Geografia e {areas['História + Geografia']} com ambas**. Esse último é o critério operacional de interdisciplinaridade usado aqui; não é uma anotação oficial das bancas.

A disciplina de origem registra {origem['História']} questões como História e {origem['Geografia']} como Geografia. Seis questões mudam de área na classificação principal; os dois campos foram preservados. “Foco regional misto” tem outro significado: há conteúdo amazônico substantivo em um contexto mais amplo. As 19 questões assim marcadas não são as 25 interdisciplinares H/G. Nenhuma dessas distinções duplica o total de questões.

## 5. O que mudou no tempo, em torno do Novo Ensino Médio?

### Cortes e alcance da comparação

A comparação é **observacional por calendário de aplicação**. O plano temporal segue quatro faixas: **2017–2021**, **2022–2023**, **2024** e **2025–2026**. O contraste principal compara 2017–2021 com 2024–2026, deixando 2022–2023 fora dele; a sensibilidade posterior sem 2026 usa 2024–2025. Esses cortes constam da seção6 do protocolo histórico, acessível com `git show 3f044af^:docs/protocolo.md`. A referência antecede o cronograma geral, mas pode conter pilotos ou implantações locais.

A [Lei 13.415/2017, art.12](https://www2.camara.leg.br/legin/fed/lei/2017/lei-13415-16-fevereiro-2017-784336-publicacaooriginal-152003-pl.html) é um marco legal, sem demonstrar mudança simultânea das redes. O cronograma original da [Portaria MEC 521/2021, art.4º](https://www.seduc.pa.gov.br/site/public/upload/arquivo/probncc/PORTARIA%20N%C2%BA%20521%2C%20DE%2013%20DE%20JULHO%20DE%202021-e03b6.pdf) previa primeira série em 2022, primeiras duas em 2023 e todas em 2024. A chegada de uma coorte iniciada em 2022 à terceira série em 2024 é uma inferência normativa.

A [suspensão de prazos em 2023](https://www.gov.br/secom/pt-br/assuntos/obrasilvoltou/cuidado/cronograma-de-implementacao-do-novo-ensino-medio-e-suspenso) não demonstra paralisação uniforme da implantação. A [Lei 14.945/2024, art.5º, II](https://www2.camara.leg.br/legin/fed/lei/2024/lei-14945-31-julho-2024-796017-publicacaooriginal-172512-pl.html) prevê início da revisão em 2025; as [DCNEM 2/2024, arts.39 e 42, pp.23–24](https://www.seduc.pa.gov.br/site/public/upload/arquivo/probncc/RESOLUCAO%20CNE-CEB%202-2024-f599f.pdf) permitem transições e coexistência curricular. Os ingressantes mencionados nesses artigos são do ensino médio. Logo, 2025–2026 não forma um período curricular homogêneo.

No Enem, o [Edital 52/2025, item3.1](https://download.inep.gov.br/enem/edital_52_de_23_de_maio_de_2025.pdf), também publicado no [DOU de 23/05/2025, seção3 extra, p.1](https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?captchafield=firstAccess&data=23%2F05%2F2025&jornal=608&pagina=1), ainda remete à matriz de referência histórica; não há justificativa para rotular automaticamente as questões Enem 2024 como um novo formato curricular. Implantação escolar, currículo de um candidato e alteração da matriz da prova são variáveis distintas.

### As fases da UEA seguem direções diferentes

![Série anual de cobrança amazônica nas fases da UEA](figuras/serie-uea.png)

**Figura 3.** O painel superior divide questões amazônicas pelos itens H/G triados; o inferior divide tópicos cobrados pelos previstos regionalmente. A lacuna de 2020 significa ausência de aplicação observada; em 2022 há duas edições por fase. Fonte: [temporal.csv](temporal.csv). As faixas são calendário, sem atribuição causal ao currículo.

{tabela(['Aplicação', 'UEA — primeira fase', 'UEA — segunda fase Humanas'], periodos_uea)}

A primeira fase passa de **19/96 (19,8%)** para **26/72 (36,1%)**, diferença de **+16,32 pontos percentuais**. A segunda fase passa de **23/96 (24,0%)** para **15/72 (20,8%)**, diferença de **−3,13 pontos**. São quatro provas por fase na referência e três no período posterior. O agregado UEA sobe de 42/192 para 41/144 (+6,60 pontos), mas esconde as direções distintas. Sem 2026, a segunda fase fica em 12/48 (25,0%): a pequena queda deixa de aparecer.

A mudança do programa também importa: cada fase UEA tem 26 tópicos previstos em 2018/2019, 11 em 2020/2021, 19 em 2022, 32 em 2023–2025 e 14 em 2026. O programa 2017 está ausente. A cobertura dos programas disponíveis passa de 22/126 (17,5%) para 32/156 (20,5%). Quando restringimos aos tópicos explicitamente presentes em **todas** as provas UEA comparáveis desses dois períodos, o resultado é:

{tabela(['Período', 'Provas com programa', 'Tópicos comuns por prova', 'Pares cobrados/previstos', 'Cobertura (%)'], tabela_comuns)}

Tópicos comuns: {', '.join(f"{t} — {topicos[t]['topico']}" for t in sorted(comuns_topicos)) or 'nenhum'}. A estabilidade dessa sensibilidade contrasta com o aumento no programa variável. Nenhuma das medidas, isoladamente, identifica efeito do NEM.

{tabela(['Tópico comum', 'Provas com cobrança / previstas em 2017–2021', 'Em 2024–2026'], [[topicos[t]['topico'], *valores] for t, valores in composicao_comuns.items()])}

A igualdade da taxa agregada não significa os mesmos tópicos cobrados: a composição se desloca de hidrografia e sociedades indígenas para conservação e Zona Franca.

### Comparar os mesmos estratos muda a leitura do agregado

![Contrastes temporais por instituição, processo e etapa](figuras/comparacao-temporal.png)

**Figura 4.** Referência 2017–2021 versus aplicações 2024–2026; cada linha mantém instituição × processo × etapa presentes nos dois lados. Os números ao lado são questões amazônicas/itens triados. Fonte: [temporal.csv](temporal.csv). FUVEST dia3, UERR e UFRR não entram nesse painel por falta de um dos lados.

{tabela(['Estrato', '2017–2021', '2024–2026', 'Diferença (p.p.)'], contraste)}

O PSC também é heterogêneo: a primeira etapa cai e a segunda cresce. As contagens posteriores de Enem e FUVEST são pequenas; FUVEST dia2 é separado do dia3 antigo para preservar a etapa documentada. O número de questões discursivas oferecidas não representa a exposição de um candidato a todos os componentes.

{tabela(['Conjunto', 'Período', 'Provas', 'Amazônicas/triadas', 'Razão global (%)', 'Média por prova (%)', 'Média dos mesmos estratos (%)'], agregados)}

A razão global pesa os blocos pelo número de itens; a média por prova dá peso igual às provas; a média dos mesmos estratos dá peso igual aos sete estratos comuns. UERR/UFRR só entram na visão de todo o acervo. Esses agregados descrevem desenhos diferentes e não substituem a leitura estratificada.

Nos seriados, cortes aproximados por série seriam E1/2022, E2/2023 e E3/2024. A sensibilidade abaixo divide o **calendário**, preservando as etapas:

{tabela(['Etapa PSC', 'Antes do corte', 'A partir do corte'], cortes_psc)}

Esses cortes não classificam exposição curricular: o PSC 2021 E1/E2 foi aplicado em 2022 com série-alvo anterior, e o PSC 2026 E2 foi aplicado em 2026 para série-alvo 2025. Sem trajetória escolar e evidência local vinculada, uma comparação por coorte real não é identificável nesta base. Os resultados dos cortes estão em `temporal.csv`, tipo `corte seriado`, sem inventar esse atributo dos candidatos.

## 6. Robustez e conferência dos indicadores

{tabela(['Cenário', 'Questões no banco', 'Questões nas comparáveis', 'Provas comparáveis', 'Pares cobrados/previstos', 'Cobertura (%)'], [[r['cenario'], r['questoes_banco'], r['questoes_comparaveis'], r['provas_comparaveis'], f"{r['pares_cobrados']}/{r['pares_previstos']}", fmt(r['cobertura_percentual'])] for r in sens])}

Nos quatro primeiros cenários, mantêm-se as provas e o denominador original, inclusive quando a remoção deixa uma prova sem questões. “Sem 2026” muda a janela e seu universo de programas. As retiradas são simulações em memória; os dados curados permanecem intactos. Fonte: [sensibilidade.csv](sensibilidade.csv).

As anulações conhecidas são {', '.join(f'`{i}`' for i in anuladas) or 'nenhuma'}. A presença no caderno sustenta a análise principal de cobrança aplicada. Excluir somente as anulações conhecidas não produz uma medida de prova válida para pontuação: há **{sem_gabarito} gabaritos vazios**, incluindo oito discursivos. Não presumimos validade dos demais itens nem resolvemos respostas por IA.

A conferência encontrou {dup['questao_id']} IDs repetidos e {dup['sha256_texto_limpo']} hashes de texto limpo repetidos; prova/número também é único. Os totais de triagem foram reconciliados com o cadastro e a seleção. Há {sem_vinculo} questões sem vínculo localizado, 14 por programas pendentes e duas sem associação pertinente identificada. Datas diárias ausentes ({sum(not q['data_aplicacao'] for q in questoes)} questões) não foram preenchidas por suposição; o ano e sua evidência permanecem no cadastro.

**Divergências e ressalvas da verificação complementar:**

{' '.join(notas) or 'Nenhuma ressalva específica do acervo real aplicável a este conjunto.'}

Os tipos de resposta `objetiva` e `objetiva_multipla_escolha` são tratados como a mesma família na descrição; os valores originais são preservados. As diferenças entre disciplina de origem e principal são documentadas, e não erros de soma. A verificação confirma o indicador principal; não substitui validação humana integral da curadoria feita por agentes de IA.

## 7. Limites e implicações

**O que observamos:** recortes programáticos modestos em cada prova, recorrência de alguns conteúdos e trajetórias temporais diferentes entre fases e etapas. Os tópicos previstos sem cobrança identificada continuam parte do universo potencial de estudo.

**O que interpretamos:** o percentual depende do recorte regional explícito, da taxonomia e da janela. Mudanças de ementa, pandemia, formato, banca e disponibilidade documental podem acompanhar as diferenças. Não há respostas comparáveis de candidatos, medida de procura por curso nem classificação sistemática de demanda cognitiva. Não podemos concluir que as provas ficaram mais difíceis, que a reforma causou mudanças ou que a aprendizagem se alterou.

**O que recomendamos para a plataforma educacional:** organizar a navegação por disciplina → conteúdo → tópico, preservando múltiplas etiquetas e filtros de prova/etapa; apresentar frequência junto ao número de provas observadas; manter conteúdos previstos sem ocorrência e ligações a cláusulas gerais. Antes de usar o banco para correção automática, completar os gabaritos ausentes, revisar decisões semânticas e oferecer os recursos visuais originais nas páginas indicadas. Essas são recomendações de uso, não resultados sobre desempenho.

Os programas UEA 2017 e PSC 2018 E1/E2 permanecem pendentes. O Enem 2026 já teve o [primeiro dia aplicado em 08/11/2026](https://www.gov.br/inep/pt-br/centrais-de-conteudo/noticias/enem/participantes-concluem-primeiro-dia-do-enem-2026), mas seu PDF oficial não foi localizado na consulta; 2026 não é uma edição nacional com zero questões regionais. Enem PPL, digital, reaplicações e outras variantes não integram este recorte.

São {len(fontes)} referências de fonte, {sum(bool(f['sha256']) for f in fontes)} com hash do PDF recuperado. O catálogo distingue publicações institucionais de cópias públicas identificadas. Texto e alternativas conservam os distratores, inclusive afirmações falsas; imagens, mapas e gráficos exigem consultar o PDF. A curadoria semântica foi feita por agentes de IA.

## 8. Reprodução e referências dos resultados

O [README](../README.md) contém as regras de inclusão, o dicionário dos campos centrais e os comandos. O protocolo/dicionário antigos foram consultados no arquivo da versão anterior; as definições operacionais atuais estão neste relatório e no README. O histórico anterior permanece no Git. As bases em `dados/` são entradas desta exploração e não são reclassificadas pelo código de análise.

```sh
python3 scripts/analise.py
python3 -m unittest discover -s tests -v
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/figuras.py
```

O cálculo tabular usa apenas Python 3.10+ e biblioteca padrão. As quatro figuras PNG usam Matplotlib na versão indicada em [requirements.txt](../requirements.txt), sem internet após a instalação. `scripts/analise.py` reconstitui relatório e cinco tabelas; `scripts/figuras.py` lê essas saídas e gera as imagens. Todas as figuras trazem unidade, período, denominador e fonte; a matriz temporal conserva IDs das provas para conferir cada agregado.

| Evidência | Fonte de reprodução |
| --- | --- |
| Universo, cobertura e calendários | `dados/provas.csv`, `dados/fontes.csv`, `resultados/temporal.csv` |
| Texto, área, anulação, tópicos e exemplos | `dados/curado/questoes.csv`, PDF e página registrados |
| Conteúdo previsto e padronização | `dados/ementas.csv`, `dados/topicos.csv`, `resultados/itens-ementa.csv` |
| Razão principal e diferenças entre provas | `resultados/previsto-cobrado.csv` |
| Frequências e zeros condicionais | `resultados/frequencia-topicos.csv` |
| Série anual, períodos e painel comum | `resultados/temporal.csv` |
| Anulações, foco regional e exclusão de 2026 | `resultados/sensibilidade.csv` |

As fontes primárias dos marcos curriculares estão ligadas na seção temporal, com artigo/página. Elas contextualizam os cortes; os números de questões e programas vêm exclusivamente dos arquivos do acervo. Consulta documental: 11/11/2026.
"""
    (root / 'resultados/relatorio.md').write_text(relatorio, encoding='utf-8')
    print(f'EDA: {n} questões; {len(comp)} provas comparáveis; {cobrado}/{previsto} pares prova × tópico cobrados.')


if __name__ == '__main__':
    analisar()
