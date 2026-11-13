# Dashboard: Amazônia nas provas

[Abrir a versão publicada](https://amazonia.mhvps.site)

Interface estática em HTML, CSS e JavaScript, com fonte, imagens e ícones locais. A pesquisa, o pipeline e os resultados estão no [README do projeto](../README.md).

## Executar

Na raiz do repositório:

```sh
python3 scripts/preparar_dashboard.py
python3 -m http.server 8765 --directory dashboard
```

Abra [http://localhost:8765](http://localhost:8765). O primeiro comando lê os CSVs curados, atualiza `dataset.json` e prepara `dist/` para a hospedagem. Depois de alterar os dados ou o código da interface, execute-o antes de publicar. O diretório `dist/` é gerado e fica fora do Git; a configuração de hospedagem permanece em `.openai/hosting.json` na raiz.

## Arquivos

| Arquivo | Função |
| --- | --- |
| `index.html` | Estrutura da página, navegação, filtros e diálogos. |
| `styles.css` | Cores, componentes, animações e layout responsivo. |
| `app.js` | Gráficos, busca, paginação, detalhes, exportação CSV e compartilhamento. |
| `model.js` | Filtros e cálculo da cobertura, preservando provas sem questões. |
| `dataset.json` | Versão gerada dos cinco CSVs canônicos para consulta no navegador. |
| `preview.png` | Captura do dashboard usada na apresentação do projeto. |
| `assets/logo.svg` | Marca completa, com símbolo e nome em traçados vetoriais. |
| `assets/logo-monochrome.svg` | Versão monocromática da marca completa. |
| `assets/mark.svg` | Símbolo isolado: páginas de um livro formam as margens de um rio. |
| `assets/favicon.svg` | Símbolo com fundo próprio para a aba do navegador. |
| `assets/amazonia-icons.svg` | Ícones de rio, floresta, folha, sol e bússola. |
| `assets/floresta-amazonica.webp` | Panorama sintético de floresta e rio na abertura. |
| `assets/folhagem-primeiro-plano.webp` | Folhagem com transparência sobre o panorama. |
| `assets/manrope-latin.woff2` | Fonte local. |
| `assets/OFL-Manrope.txt` | Licença da fonte. |

## Consultar

A abertura apresenta a pergunta do estudo. A cobertura da ementa fica abaixo dos gráficos de tópicos e programas, com o percentual do recorte atual, o numerador, o denominador em pares prova × tópico e a quantidade de provas comparáveis. A navegação superior leva à visão geral, aos conteúdos e ao banco de questões.

Os filtros de instituição, aplicação, disciplina e fase atualizam os indicadores. As barras anuais e as origens também filtram o estudo. Os atalhos de 2017–2021, 2022–2023, 2024 e 2025–2026 selecionam faixas do calendário de aplicação; não classificam o currículo vivido pelos candidatos nem demonstram efeitos do Novo Ensino Médio. Os critérios estão na metodologia e na [análise exploratória](../resultados/relatorio.md).

O gráfico anual conta cada questão uma vez pela disciplina principal. A opção **Ver valores por ano** apresenta História, Geografia, total de questões e número de provas em uma tabela. Os filtros por disciplina também consideram tópicos secundários, portanto seus totais podem se sobrepor. “—” distingue ausência de base comparável de zero observado.

A busca e o tópico selecionado afetam o banco de questões. Cada registro dá acesso ao enunciado, às alternativas, à origem, à página do PDF e aos itens associados do programa. O banco mantém busca, ordenação, paginação e consulta dos detalhes em telas menores. O CSV exporta o recorte do banco; a metodologia permite baixar a base completa em JSON, e o compartilhamento conserva os filtros no endereço.

Os dados do navegador derivam de `dados/`, sem edição manual. O redesenho altera a apresentação e os controles de exploração, preservando o modelo de cálculo, os dados curados e os resultados da pesquisa.

## Direção visual e interação

A hierarquia, as proporções e o cuidado com movimento e superfícies usam a Apple como referência, com identidade própria de floresta, rio e argila. A primeira tela destaca a pergunta e o achado principal; abaixo dela, gráficos, comparação com os programas e documentos permitem aprofundar a leitura.

A navegação e os controles usam transparência e desfoque, com fundos de apoio. Gráficos e tabelas ficam sobre branco opaco para manter a leitura estável. **História usa cobre e Geografia usa verde de rio**, sempre acompanhados por nomes e valores. O verde profundo organiza a abertura; o verde claro destaca a cobertura. A fonte Manrope mantém títulos, números, rótulos e notas em uma escala consistente.

A interface tem foco de teclado visível, link para saltar a navegação, controles nativos de seleção, tabela alternativa ao gráfico anual e diálogos com fechamento pelo teclado. Ao abrir o menu compacto, o foco vai à navegação; Escape o devolve ao botão do menu. Filtros anunciam a atualização do recorte; carregamento e erro têm mensagens próprias e opção de tentar novamente. Transições de barras, cobertura e entrada respeitam a preferência por movimento reduzido.

O panorama de floresta e rio e a folhagem foram criados em duas gerações com o ImageGen integrado e convertidos para WebP. São cenas sintéticas decorativas, não registros de uma localização identificada, mapas ou dados da pesquisa. Os traços de contorno também são decorativos. A marca original une páginas de um livro e um rio em espaço negativo; o nome está convertido em traçados SVG e tem versão monocromática, símbolo isolado e favicon. Os cinco ícones também são SVG. Todos os assets são locais, e a fonte acompanha a licença SIL Open Font License.

O trabalho anterior consultou *Fundamentos do Vibe Design* e *Extract HTML Design System*, do material local em `matheus/design`, além dos exemplos `CryptoLearn / hu169yr`, `dashboard-list` e `sidebar`. A composição e a navegação mantêm a stack estática; a marca e as imagens foram atualizadas para esta identidade.

<details>
<summary>Prompt: floresta-amazonica.webp</summary>

```text
Use case: photorealistic-natural.
Asset type: panoramic photographic background for the approved "Amazônia nas provas" educational data dashboard, not a UI mockup.
Primary request: evoke the feeling of quietly entering the Amazon rainforest.
Scene: a lowland Brazilian Amazon river corridor at dawn, camera near water level, looking into dense layered forest. Tall broadleaf trees with real buttress trunks, intricate humid canopy, naturally dark green-brown calm water and subtle reflections. Gentle mist suspended over the river opening in the middle-right and a little warm early daylight through the canopy. Overhanging real broad leaves and fine branches frame the upper corners; no obvious symmetrical arch.
Composition: very wide 3:1 panorama, about 2400 by 800. Left 42 percent quieter and naturally shaded, with soft forest depth suitable for cream text overlay; the river opening and brighter detail toward the middle-right. Frame edges may crop leaves naturally. Do not add artificial empty panels or a graphic gradient.
Style: convincing premium documentary nature photography, detailed natural bark, irregular leaves, subtle moisture, controlled highlights, realistic depth and lens perspective. Mature and immersive, no illustration or fantasy treatment.
Palette: deep forest greens near #073b34, muted river greens near #138578, natural olive highlights and restrained warm dawn light. No neon turquoise water.
Constraints: no text, typography, logos, watermark, people, boats, animals, buildings, mountains, charts or map. This is a decorative imagined Amazon forest scene, not documentation of an identified location.
```

</details>

<details>
<summary>Prompt: folhagem-primeiro-plano.webp</summary>

```text
Use case: photorealistic-natural.
Asset type: transparent foreground foliage overlay for a refined Amazon rainforest dashboard hero.
Primary request: a sparse natural leafy branch entering ONLY from the top-right corner, with leaves extending toward the upper middle and down the right edge. Most of the lower-left area must be completely transparent negative space.
Subject: 7 to 10 naturally irregular elliptical broad leaves on one fine slender branch, plausible humid Amazon lowland forest foliage. Dark emerald mature leaves, a few soft olive-lime backlit edges, visible subtle leaf veins, delicate natural moisture and very few tiny dew drops.
Style: high-quality real botanical close-up photography, convincing organic texture and thin stems, diffuse warm dawn light from upper right, slight depth variation, no illustration, no waxy CGI surfaces. Keep the silhouette elegant and sparse rather than a dense pile of leaves.
Composition: landscape or square cutout, top-right corner anchored; full leaf shapes inside the canvas except the entering branch at the upper-right border. Make clean antialiased alpha edges and genuine transparency around every leaf, not white, black or checkerboard.
Color palette: deep Amazon forest green near #073b34, subtle #138578 midtones, restrained natural yellow-green highlights.
Constraints: transparent background. No text, logo, watermark, flowers, fruits, insects, animals, people, pots, floor shadows or visible backdrop. This will be a decorative foreground layer over a river photograph; avoid any unrelated objects.
```

</details>
