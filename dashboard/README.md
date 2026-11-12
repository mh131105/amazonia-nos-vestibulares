# Dashboard: Amazônia nas provas

[Abrir a versão publicada](https://amazonia-nas-provas-matheus.quick-grebe-6416.chatgpt.site)

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

Os filtros de instituição, aplicação, disciplina e fase atualizam os indicadores. As barras anuais e as origens também filtram o estudo. A busca e o tópico selecionado afetam o banco de questões; os detalhes exibem a origem, a página do PDF e os itens do programa associados. O CSV exporta o recorte do banco. A tela de metodologia permite baixar a base completa em JSON.

Os dados do navegador derivam de `dados/`, e não recebem edição manual. Os critérios de curadoria e as limitações estão na [análise exploratória](../resultados/relatorio.md). A mudança de pasta preserva os textos, a estrutura e o tema da interface publicada.

## Referências visuais

Método: *Fundamentos do Vibe Design* e *Extract HTML Design System*, do material local em `matheus/design`. O trabalho partiu dos HTMLs e design systems do banco, depois adaptou tokens, componentes e estados para o dashboard.

- **CryptoLearn / `hu169yr`**: Manrope, base azul-clara, superfícies brancas, cartões e animações `animate-slide-up`/`animate-fade-in` de 0,8 s.
- **`dashboard-list`**: organização de indicadores, listas e controles.
- **`sidebar`**: navegação agrupada e estados de seleção.

O tema amazônico combina verde de floresta, turquesa de rio, amarelo de sol e coral sobre fundo creme. A estrutura e os textos do dashboard continuam iguais aos da primeira versão. Os cartões recebem ícones vetoriais; as linhas do rio e a folha da barra lateral têm animações em CSS. A preferência por movimento reduzido desativa essas animações. A fonte local acompanha a licença SIL Open Font License.

A ilustração foi criada com o ImageGen integrado e convertida para WebP sem dependências no dashboard. A marca e os cinco ícones foram desenhados em SVG. Todos os assets são locais.

<details>
<summary>Prompt da ilustração</summary>

Use case: stylized-concept. Original wide decorative illustrated panorama for an Amazon-region educational data dashboard header. A vibrant, sophisticated editorial illustration of the Brazilian Amazon: a sinuous turquoise river among layered emerald-green rainforest canopies, palm fronds and dense tropical foliage; a warm golden-yellow sun with coral-orange accents, subtle carved-print lines and natural paper grain. Rich botanical depth, precise confident shapes, luminous tropical colors, fine printmaking details. Flat illustrated editorial medium, no 3D, not photorealistic. Very wide panoramic 3:1 landscape canvas. Artwork concentrated in the right half. Reserve the left half as almost empty warm ivory/cream paper (#fff8e8) for the existing headline. Details on the far right and lower right, fading organically into ivory near the center. Not a map. Palette: #073f35, #087f5b, #18b8aa, #f5bf32, #f47850, #fff8e8. No text, labels, letters, numbers, logos, watermarks, frame or UI. Do not imitate or invent Indigenous patterns or symbols. No people, buildings, animals or extraneous props.

</details>
