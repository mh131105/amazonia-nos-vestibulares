# Amazônia nas provas

Dashboard de História e Geografia da Amazônia nos vestibulares. O acervo reúne **196 questões**, **70 provas examinadas**, **53 tópicos padronizados** e **151 referências documentais**, com aplicações entre 2017 e 11 de novembro de 2026.

[Abrir o dashboard](https://amazonia-nas-provas-matheus.quick-grebe-6416.chatgpt.site)

## Executar

Requer Python 3. Não há instalação de dependências nem etapa de build.

```sh
python3 -m http.server 8765 --directory dist
```

Abra [http://localhost:8765](http://localhost:8765). O dashboard também funciona em hospedagem estática: publique o conteúdo de `dist/`.

## Consultar

- Filtre por instituição/exame, ano de aplicação, disciplina e fase/etapa. Os indicadores e gráficos acompanham o recorte.
- Clique em uma origem ou barra anual para filtrar. Selecione um tópico para consultar suas questões.
- Busque no banco, ordene os resultados e abra uma questão para ler o enunciado, as alternativas, os tópicos e os itens da ementa associados.
- Consulte o PDF na página indicada. Questões que dependem de gráficos ou imagens avisam isso nos detalhes.
- Baixe o recorte em CSV ou a base completa em JSON. “Copiar link” preserva os filtros na URL.

O indicador principal é **141/682 pares prova × tópico com cobrança identificada (20,7%)**, em **43 provas com programa regional integral e triagem completa**. Os 50 tópicos identificados nas questões incluem etiquetas secundárias; o catálogo tem 53. Os filtros História/Geografia incluem questões com qualquer tópico da área, com 25 questões presentes nas duas áreas.

Enem e FUVEST têm vínculos programáticos amplos e ficam fora dessa proporção regional explícita. “—” indica ausência de base comparável; zero exige um denominador observado. As duas questões anuladas continuam no acervo por terem constado dos cadernos. O dashboard apresenta conteúdo e previsão programática, sem indicadores de desempenho dos candidatos.

As telas “Sobre os dados”, “Conferir por prova” e “Fontes consultadas” detalham as regras, os limites e a proveniência. O acervo cobre seis origens e não representa um censo de todos os vestibulares públicos brasileiros.

## Arquivos

| Arquivo | Função |
| --- | --- |
| `dist/index.html` | Estrutura da página, navegação, filtros e diálogos. |
| `dist/styles.css` | Tokens visuais, componentes, estados e layout responsivo. |
| `dist/app.js` | Gráficos, consulta das questões, busca, paginação, exportação e compartilhamento. |
| `dist/model.js` | Filtros e cálculo da cobertura a partir dos registros, preservando provas sem questões. |
| `dist/dataset.json` | Questões, provas, tópicos, itens dos programas e fontes do acervo curado. |
| `dist/assets/mark.svg` | Marca vetorial com rio, folha e sol. |
| `dist/assets/amazonia-icons.svg` | Cinco ícones vetoriais originais: rio, floresta, folha, sol e bússola. |
| `dist/assets/amazonia-panorama.webp` | Ilustração original do cabeçalho, em WebP (312 KB). |
| `dist/assets/manrope-latin.woff2` | Fonte local; a página funciona sem serviços de tipografia externos. |
| `dist/assets/OFL-Manrope.txt` | Licença da fonte Manrope. |
| `.openai/hosting.json` | Configuração da hospedagem estática e identidade do site. |
| `.gitignore` e `.gitattributes` | Exclusão de arquivos locais e padronização de texto. |

## Dados e método

`dataset.json` mantém cinco conjuntos: `questions`, `exams`, `topics`, `syllabus` e `sources`. Os identificadores relacionam os registros; páginas são posições do PDF contadas a partir de 1. Valores ausentes usam `null`.

`model.js` calcula a razão dos totais, sem fazer média dos percentuais por prova. Para cada prova comparável, reúne os tópicos regionais explícitos do programa e conta aqueles exigidos por uma questão ligada ao item pertinente. Tópicos repetidos em itens do mesmo programa contam uma vez. Uma etiqueta compartilhada com uma cláusula sem vínculo não basta.

O ano é o da aplicação. Edição e ingresso permanecem nos detalhes. A UEA aplicou duas edições em 2022; o número de provas varia ao longo dos anos, e 2026 é parcial. As barras anuais descrevem o acervo observado.

Os textos das questões mantêm os distratores publicados. Gabarito ausente significa não incorporado ao banco. As fontes distinguem documento institucional e cópia pública identificada, com URL e hash. A questão UEA2026 Humanas Q05 tem um vínculo geral adicional em revisão, sinalizado nos detalhes; ele não modifica 141/682.

Autoria: **Matheus Garcia**, com pesquisa, curadoria e implementação assistidas por Codex. A versão anterior da pesquisa e seus scripts permanecem no histórico Git, com referência em `f88597d`; uma cópia de trabalho foi preservada fora desta pasta antes da reorganização.

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
