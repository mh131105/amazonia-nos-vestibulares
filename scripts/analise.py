"""Calcula os indicadores e gera cinco tabelas, sem alterar o relatório editorial."""
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from statistics import median
from limpeza import exigir, gravar_csv, ler_csv

ROOT = Path(__file__).resolve().parents[1]


def validar_entrada(root, questoes, provas):
    ids = {q['questao_id'] for q in questoes}
    exigir('' not in ids and len(ids) == len(questoes), 'IDs de questões ausentes ou duplicados')
    exigir(len({(q['prova_id'], q['numero']) for q in questoes}) == len(questoes),
           'Prova/número duplicado')
    triagem_path = root / 'dados/brutos/triagem.csv'
    if triagem_path.exists():
        triagem = ler_csv(triagem_path)
        exigir(len(triagem) == sum(int(p['questoes_triadas']) for p in provas),
               'Triagem diverge do total cadastrado')
        exigir(len({t['questao_id'] for t in triagem}) == len(triagem), 'IDs de triagem repetidos')
        exigir({t['questao_id'] for t in triagem if t['decisao'] == 'incluir'} == ids,
               'Seleção e banco divergem')
        por_prova = Counter(t['prova_id'] for t in triagem)
        exigir(all(por_prova[p['prova_id']] == int(p['questoes_triadas']) for p in provas),
               'Triagem por prova divergente')


def analisar(root=ROOT):
    questoes = ler_csv(root / 'dados/curado/questoes.csv')
    provas = ler_csv(root / 'dados/provas.csv')
    ementas = ler_csv(root / 'dados/ementas.csv')
    topicos = {r['topico_id']: r for r in ler_csv(root / 'dados/topicos.csv')}
    validar_entrada(root, questoes, provas)
    por_prova, por_item = defaultdict(list), defaultdict(set)
    for q in questoes:
        exigir(q['topico_id'] in topicos, f"Tópico desconhecido: {q['questao_id']}")
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

    indicadores = consolidar_resultados(root, questoes, provas, ementas, topicos, cobertura, frequencias)
    print(f"EDA: {indicadores['questoes']} questões; {indicadores['provas_comparaveis']} provas comparáveis; "
          f"{indicadores['pares_cobrados']}/{indicadores['pares_previstos']} pares prova × tópico cobrados.")
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


def consolidar_resultados(root, questoes, provas, ementas, topicos, cobertura, frequencias):
    """Grava séries e sensibilidades e retorna os indicadores para conferência."""
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
    return {
        'questoes': n,
        'questoes_triadas': triadas,
        'questoes_comparaveis': sum(q['prova_id'] in comp_ids for q in questoes),
        'provas': len(provas),
        'provas_com_questoes': sum(bool(contagem[p['prova_id']]) for p in provas),
        'provas_sem_questoes': sum(not contagem[p['prova_id']] for p in provas),
        'provas_comparaveis': len(comp),
        'topicos': len(topicos),
        'associacoes_questao_topico': sum(len(q['topicos_ids'].split('|')) for q in questoes),
        'pares_previstos': previsto,
        'pares_cobrados': cobrado,
        'itens_regionais_previstos': itens_prev,
        'itens_regionais_com_vinculo': itens_cob,
        'itens_regionais_com_topico_compartilhado': itens_com_intersecao,
        'cobertura_por_prova': {
            'mediana': median(taxas) if taxas else None,
            'media': sum(taxas) / len(taxas) if taxas else None,
            'minimo': min(taxas) if taxas else None,
            'maximo': max(taxas) if taxas else None,
        },
        'por_instituicao': por_ies,
        'questoes_por_area': dict(areas),
        'questoes_por_escopo': dict(grupo_escopo),
        'disciplina_principal': dict(principal),
        'disciplina_origem': dict(origem),
        'topicos_mais_frequentes': principais,
        'questoes_top5': top5,
        'topicos_sem_cobranca': lacunas,
        'topicos_observados': sorted(observados),
        'uea_topicos_comuns': sorted(comuns_topicos),
        'uea_cobertura_topicos_comuns': tabela_comuns,
        'uea_cobranca_por_topico_comum': composicao_comuns,
        'contrastes_temporais': contraste,
        'periodos_uea': periodos_uea,
        'agregados_temporais': agregados,
        'serie_anual': anuais,
        'por_fase': fases,
        'cobertura_por_area': por_area,
        'cortes_psc': cortes_psc,
        'questoes_sem_vinculo': sem_vinculo,
        'questoes_sem_gabarito': sem_gabarito,
        'questoes_sem_data_completa': sum(not q['data_aplicacao'] for q in questoes),
        'questoes_anuladas': anuladas,
        'fontes': len(fontes),
        'fontes_com_hash': sum(bool(f['sha256']) for f in fontes),
        'duplicatas': dup,
    }


if __name__ == '__main__':
    analisar()
