# Dashboard: Amazônia nas provas

[Abrir a versão publicada](https://amazonia.mhvps.site)

Interface estática em HTML, CSS e JavaScript, com fonte, ilustração e ícones locais. A pesquisa, o pipeline e os resultados estão no [README do projeto](../README.md).

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
| `assets/mark.svg` | Marca vetorial com rio, folha e sol. |
| `assets/amazonia-icons.svg` | Ícones de rio, floresta, folha, sol e bússola. |
| `assets/amazonia-panorama.webp` | Ilustração do cabeçalho. |
| `assets/manrope-latin.woff2` | Fonte local. |
| `assets/OFL-Manrope.txt` | Licença da fonte. |

## Consultar

A abertura apresenta a pergunta do estudo e a cobertura da ementa no recorte atual. O percentual acompanha o numerador, o denominador em pares prova × tópico e a quantidade de provas comparáveis. A navegação superior leva à visão geral, aos conteúdos e ao banco de questões.

Os filtros de instituição, aplicação, disciplina e fase atualizam os indicadores. As barras anuais e as origens também filtram o estudo. Os atalhos de 2017–2021, 2022–2023, 2024 e 2025–2026 selecionam faixas do calendário de aplicação; não classificam o currículo vivido pelos candidatos nem demonstram efeitos do Novo Ensino Médio. Os critérios estão na metodologia e na [análise exploratória](../resultados/relatorio.md).

O gráfico anual conta cada questão uma vez pela disciplina principal. A opção **Ver valores por ano** apresenta História, Geografia, total de questões e número de provas em uma tabela. Os filtros por disciplina também consideram tópicos secundários, portanto seus totais podem se sobrepor. “—” distingue ausência de base comparável de zero observado.

A busca e o tópico selecionado afetam o banco de questões. Cada registro dá acesso ao enunciado, às alternativas, à origem, à página do PDF e aos itens associados do programa. O banco mantém busca, ordenação, paginação e consulta dos detalhes em telas menores. O CSV exporta o recorte do banco; a metodologia permite baixar a base completa em JSON, e o compartilhamento conserva os filtros no endereço.

Os dados do navegador derivam de `dados/`, sem edição manual. O redesenho altera a apresentação e os controles de exploração, preservando o modelo de cálculo, os dados curados e os resultados da pesquisa.

## Direção visual e interação

A hierarquia, as proporções e o cuidado com movimento e superfícies usam a Apple como referência, com identidade própria de floresta, rio e argila. A primeira tela destaca a pergunta e o achado principal; abaixo dela, gráficos, comparação com os programas e documentos permitem aprofundar a leitura.

A navegação e os controles usam transparência e desfoque, com fundos de apoio. Gráficos e tabelas ficam sobre branco opaco para manter a leitura estável. **História usa cobre e Geografia usa verde de rio**, sempre acompanhados por nomes e valores. O verde profundo organiza a abertura; o verde claro destaca a cobertura. A fonte Manrope mantém títulos, números, rótulos e notas em uma escala consistente.

A interface tem foco de teclado visível, link para saltar a navegação, controles nativos de seleção, tabela alternativa ao gráfico anual e diálogos com fechamento pelo teclado. Ao abrir o menu compacto, o foco vai à navegação; Escape o devolve ao botão do menu. Filtros anunciam a atualização do recorte; carregamento e erro têm mensagens próprias e opção de tentar novamente. Transições de barras, cobertura e entrada respeitam a preferência por movimento reduzido.

A ilustração de floresta e rio e os traços de contorno são decorativos: não representam coordenadas, distribuição geográfica ou medições. A ilustração foi criada com o ImageGen integrado e convertida para WebP sem dependências no dashboard. A marca e os cinco ícones foram desenhados em SVG. Todos os assets são locais, e a fonte acompanha a licença SIL Open Font License.

O trabalho anterior consultou *Fundamentos do Vibe Design* e *Extract HTML Design System*, do material local em `matheus/design`, além dos exemplos `CryptoLearn / hu169yr`, `dashboard-list` e `sidebar`. O redesenho reorganiza a composição e a navegação, mantendo os assets originais e a stack estática.

<details>
<summary>Prompt da ilustração</summary>

Use case: stylized-concept. Original wide decorative illustrated panorama for an Amazon-region educational data dashboard header. A vibrant, sophisticated editorial illustration of the Brazilian Amazon: a sinuous turquoise river among layered emerald-green rainforest canopies, palm fronds and dense tropical foliage; a warm golden-yellow sun with coral-orange accents, subtle carved-print lines and natural paper grain. Rich botanical depth, precise confident shapes, luminous tropical colors, fine printmaking details. Flat illustrated editorial medium, no 3D, not photorealistic. Very wide panoramic 3:1 landscape canvas. Artwork concentrated in the right half. Reserve the left half as almost empty warm ivory/cream paper (#fff8e8) for the existing headline. Details on the far right and lower right, fading organically into ivory near the center. Not a map. Palette: #073f35, #087f5b, #18b8aa, #f5bf32, #f47850, #fff8e8. No text, labels, letters, numbers, logos, watermarks, frame or UI. Do not imitate or invent Indigenous patterns or symbols. No people, buildings, animals or extraneous props.

</details>
