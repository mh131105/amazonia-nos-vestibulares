"""Gera as quatro figuras estáticas do relatório, sem alterar as bases curadas."""
from pathlib import Path
from math import nan
from decimal import Decimal, ROUND_HALF_UP
from textwrap import fill
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from limpeza import ler_csv

ROOT = Path(__file__).resolve().parents[1]
DESTINO = ROOT / 'resultados/figuras'
VERDE, CLARO, CINZA, LARANJA = '#1d6652', '#bed3c8', '#7d8984', '#bc592d'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                     'figure.facecolor': '#fbfcfa', 'axes.facecolor': '#fbfcfa',
                     'text.color': '#20392f', 'axes.labelcolor': '#20392f',
                     'xtick.color': '#40564c', 'ytick.color': '#40564c',
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.spines.left': False, 'axes.spines.bottom': False,
                     'axes.axisbelow': True, 'grid.color': '#dce4de',
                     'grid.linewidth': .7, 'savefig.dpi': 180})


def numero(x, casas=1):
    valor = Decimal(f'{x:.6f}').quantize(Decimal(1).scaleb(-casas), rounding=ROUND_HALF_UP)
    return f'{valor:.{casas}f}'.replace('.', ',')


def acabamento(fig, nome, titulo, subtitulo, fonte):
    fig.suptitle(titulo, x=.055, y=.96, ha='left', fontsize=17, weight='bold')
    fig.text(.055, .865, subtitulo, fontsize=10.5, va='top')
    fig.text(.055, .035, fonte, fontsize=9, color='#52665b', va='bottom')
    DESTINO.mkdir(parents=True, exist_ok=True)
    fig.savefig(DESTINO / nome, metadata={'Software': f'Matplotlib {matplotlib.__version__}'})
    plt.close(fig)
    print(DESTINO.relative_to(ROOT) / nome)


def cobertura():
    dados = [r for r in ler_csv(ROOT / 'resultados/previsto-cobrado.csv') if r['comparacao_completa'] == 'sim']
    agregado = 100 * sum(int(r['topicos_padronizados_cobrados']) for r in dados) / sum(int(r['topicos_padronizados_previstos']) for r in dados)
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.subplots_adjust(left=.14, right=.72, bottom=.22, top=.75)
    for y, ies in enumerate(['UEA', 'UFAM', 'UFRR', 'UERR']):
        grupo = sorted([r for r in dados if r['instituicao'] == ies], key=lambda r: float(r['cobertura_topicos_percentual']))
        desloc = [0] if len(grupo) == 1 else [-.13 + .26*i/(len(grupo)-1) for i in range(len(grupo))]
        taxas = [100 * int(r['topicos_padronizados_cobrados']) / int(r['topicos_padronizados_previstos']) for r in grupo]
        ax.scatter(taxas, [y+d for d in desloc], s=42, color=CLARO, edgecolors=VERDE, linewidths=.6, zorder=3)
        num = sum(int(r['topicos_padronizados_cobrados']) for r in grupo)
        den = sum(int(r['topicos_padronizados_previstos']) for r in grupo)
        ax.scatter([100*num/den], [y], marker='D', s=100, color=VERDE, zorder=4)
        ax.text(1.025, y, f'{len(grupo)} provas · {num}/{den}\n{numero(100*num/den)}%',
                transform=ax.get_yaxis_transform(), va='center', fontsize=11)
    ax.axvline(agregado, color=LARANJA, linestyle='--', lw=1.4, label=f'Agregado: {numero(agregado)}%')
    ax.set(yticks=range(4), yticklabels=['UEA', 'UFAM — PSC', 'UFRR — PI', 'UERR'],
           xlim=(-1, 70), ylim=(-.6, 3.6), xlabel='Tópicos cobrados / tópicos previstos na prova (%)')
    ax.invert_yaxis()
    ax.xaxis.set_major_formatter(PercentFormatter(100, decimals=0))
    ax.grid(axis='x')
    ax.legend(loc='upper left', bbox_to_anchor=(0, -.19), frameon=False, fontsize=10)
    acabamento(fig, 'cobertura-ementa.png',
               f'A cobertura agregada é {numero(agregado)}%; as provas variam de 0% a 62,5%',
               '43 provas com programa regional integral e triagem completa · aplicações 2017–11/11/2026\n'
               'Pontos: provas individuais. Losangos: razão dos totais por origem.',
               'Fonte: resultados/previsto-cobrado.csv. Unidade: par prova × tópico regional explícito.\n'
               'UERR e UFRR: somente duas provas cada. Taxonomia padronizada na curadoria; não mede extensão textual da ementa.')


def topicos():
    dados = sorted(ler_csv(ROOT / 'resultados/frequencia-topicos.csv'),
                   key=lambda r: (-int(r['questoes_multitopico']), r['topico_id']))[:10]
    fig, ax = plt.subplots(figsize=(12, 7.2))
    fig.subplots_adjust(left=.43, right=.91, bottom=.2, top=.77)
    for i, r in enumerate(dados):
        principal, todas = int(r['questoes']), int(r['questoes_multitopico'])
        ax.barh(i, principal, color=VERDE, height=.62, label='Tópico principal' if i == 0 else None)
        ax.barh(i, todas-principal, left=principal, color=CLARO, height=.62,
                label='Tópico adicional' if i == 0 else None)
        ax.text(todas+.35, i, str(todas), va='center', weight='bold')
    ax.set(yticks=range(len(dados)), yticklabels=[fill(r['topico'], 43) for r in dados],
           xlabel='Questões distintas com o tópico', xlim=(0, 26))
    ax.invert_yaxis()
    ax.grid(axis='x')
    ax.tick_params(axis='y', length=0, labelsize=10)
    ax.set_xticks(range(0, 26, 5))
    ax.legend(loc='upper left', bbox_to_anchor=(0, -.12), ncol=2, frameon=False, fontsize=10)
    acabamento(fig, 'topicos-recorrentes.png',
               'Migrações, povos indígenas e transportes lideram nas etiquetas múltiplas',
               'Dez tópicos com mais questões associadas · 196 questões · aplicações 2017–11/11/2026\n'
               'Uma questão pode contribuir para vários tópicos; dentro de cada barra, conta uma vez.',
               'Fonte: resultados/frequencia-topicos.csv, derivado de dados/curado/questoes.csv.\n'
               'A frequência descreve este acervo, com 107 questões UEA. Ela não estima probabilidade de cobrança futura.')


def serie_uea():
    dados = ler_csv(ROOT / 'resultados/temporal.csv')
    dados = [r for r in dados if r['nivel'] == 'estrato' and r['instituicao'] == 'UEA']
    fig, axs = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    fig.subplots_adjust(left=.11, right=.95, bottom=.2, top=.77, hspace=.4)
    for ax in axs:
        ax.axvspan(2021.5, 2023.5, color='#edf1f6', zorder=0)
        ax.axvspan(2023.5, 2024.5, color='#f8eee0', zorder=0)
        ax.axvspan(2024.5, 2026.5, color='#edf2e9', zorder=0)
        for x in [2021.5, 2023.5, 2024.5]:
            ax.axvline(x, color='#bdc8bd', lw=.7)
        ax.grid(axis='y')
        ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        ax.yaxis.set_major_formatter(PercentFormatter(100, decimals=0))
    deltas = []
    for prefixo, cor, nome in [('1', VERDE, '1ª fase — Gerais'), ('2', LARANJA, '2ª fase — Humanas')]:
        grupo = [r for r in dados if r['tipo'] == 'ano' and r['etapa'].startswith(prefixo)]
        anos = [int(r['inicio']) for r in grupo]
        incidencia = [float(r['incidencia_percentual']) if r['incidencia_percentual'] else nan for r in grupo]
        cobertura = [float(r['cobertura_percentual']) if r['cobertura_percentual'] else nan for r in grupo]
        axs[0].plot(anos, incidencia, '-o', color=cor, label=nome, lw=2, markersize=5)
        axs[1].plot(anos, cobertura, '-o', color=cor, lw=2, markersize=5)
        for r in grupo:
            if r['incidencia_percentual']:
                outro = next(x for x in dados if x['tipo'] == 'ano' and x['inicio'] == r['inicio'] and not x['etapa'].startswith(prefixo))
                acima = float(r['incidencia_percentual']) > float(outro['incidencia_percentual']) or (r['incidencia_percentual'] == outro['incidencia_percentual'] and prefixo == '1')
                axs[0].annotate(f"{r['questoes_amazonicas']}/{r['questoes_triadas']}",
                                (int(r['inicio']), float(r['incidencia_percentual'])),
                                xytext=(0, 9 if acima else -17), textcoords='offset points',
                                ha='center', color=cor, fontsize=8)
        posterior = next(r for r in dados if r['tipo'] == 'período' and r['janela'] == '2024–2026' and r['etapa'].startswith(prefixo))
        deltas.append(float(posterior['diferenca_incidencia_pp_referencia']))
    axs[0].set(ylabel='Questões amazônicas / itens H/G', ylim=(0, 58))
    axs[1].set(ylabel='Tópicos cobrados / previstos', ylim=(-1, 42), xlim=(2016.6, 2026.4),
               xticks=list(range(2017, 2027)), xlabel='Ano de aplicação — faixas de calendário, sem identificação causal')
    axs[0].legend(loc='upper left', ncol=2, bbox_to_anchor=(0, 1.2), frameon=False, fontsize=10)
    axs[0].text(2020, 6, 'sem\nobservação', ha='center', fontsize=9, color=CINZA)
    axs[1].text(2017, 4, 'programa\npendente', ha='center', fontsize=9, color=CINZA)
    acabamento(fig, 'serie-uea.png',
               f'UEA: {"+" if deltas[0] >= 0 else ""}{numero(deltas[0], 2)} p.p. na primeira fase; {numero(deltas[1], 2)} p.p. em Humanas',
               'Contraste 2017–2021 versus 2024–2026 · série anual por aplicação\n'
               'Faixas: referência 2017–21 | transição 2022–23 | 2024 | revisão 2025–26',
               'Fonte: resultados/temporal.csv. Painel superior: 24 itens H/G por prova; em 2022, duas edições por fase (48 itens).\n'
               'Painel inferior: denominador regional variável, de 11 a 32 tópicos por prova com programa. 2017: programa não recuperado.\n'
               'Lacunas não são zeros. Os marcos de calendário não identificam o currículo dos candidatos nem efeito do Novo Ensino Médio.')


def comparacao():
    dados = ler_csv(ROOT / 'resultados/temporal.csv')
    dados = [r for r in dados if r['nivel'] == 'estrato' and r['tipo'] == 'período' and r['pertence_painel_comum'] == 'sim']
    anteriores = {(r['instituicao'], r['processo'], r['etapa']): r for r in dados if r['janela'] == '2017–2021'}
    posteriores = sorted([r for r in dados if r['janela'] == '2024–2026'], key=lambda r: (r['instituicao'], r['etapa']))
    fig, ax = plt.subplots(figsize=(13, 7.2))
    fig.subplots_adjust(left=.27, right=.65, bottom=.22, top=.76)
    rotulos = []
    for i, r in enumerate(posteriores):
        anterior = anteriores[(r['instituicao'], r['processo'], r['etapa'])]
        a, b = float(anterior['incidencia_percentual']), float(r['incidencia_percentual'])
        delta = float(r['diferenca_incidencia_pp_referencia'])
        ax.plot([a, b], [i, i], color=CLARO, lw=3, zorder=2)
        ax.scatter([a], [i], color=CINZA, s=60, label='2017–2021' if i == 0 else None, zorder=3)
        ax.scatter([b], [i], color=VERDE, s=60, marker='D', label='2024–2026' if i == 0 else None, zorder=4)
        ax.text(1.03, i, f"{anterior['questoes_amazonicas']}/{anterior['questoes_triadas']} → "
                f"{r['questoes_amazonicas']}/{r['questoes_triadas']}   |   {'+' if delta >= 0 else ''}{numero(delta, 2)} p.p.",
                transform=ax.get_yaxis_transform(), va='center', fontsize=10)
        etapa = r['etapa'].replace('Conhecimentos Gerais', 'Gerais').replace('PSC — ', '')
        rotulos.append(f"{r['instituicao']} · {r['processo']}\n{etapa}")
    ax.set(yticks=range(len(posteriores)), yticklabels=rotulos,
           xlim=(-1, 44), xlabel='Questões amazônicas / itens triados (%)')
    ax.invert_yaxis()
    ax.xaxis.set_major_formatter(PercentFormatter(100, decimals=0))
    ax.grid(axis='x')
    ax.tick_params(axis='y', labelsize=10, length=0)
    ax.legend(loc='upper left', bbox_to_anchor=(0, -.16), ncol=2, frameon=False, fontsize=10)
    acabamento(fig, 'comparacao-temporal.png',
               'A mudança temporal depende da fase e da etapa',
               'Sete estratos com observações nos dois períodos · calendário de aplicação 2017–2026\n'
               'Contagens à direita: questões amazônicas / itens triados; diferenças em pontos percentuais.',
               'Fonte: resultados/temporal.csv. Mantidos instituição × processo × etapa; 2022–2023 fora do contraste.\n'
               'Enem: Humanas; demais blocos: H/G. FUVEST: questões oferecidas, sem equivalência com exposição individual.\n'
               'UERR, UFRR e FUVEST dia 3 não têm os dois lados. Cobertura parcial em 2026. Comparação observacional, sem atribuição ao NEM.')


if __name__ == '__main__':
    cobertura()
    topicos()
    serie_uea()
    comparacao()
