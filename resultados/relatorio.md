# O que os vestibulares cobram de História e Geografia da Amazônia?

Nas **43 provas com programa regional integral e triagem completa**, **141 de 682 tópicos com previsão regional explícita tiveram cobrança identificada (20.7%)**. O cálculo conta pares **prova × tópico padronizado**; um mesmo conteúdo previsto em cinco provas entra cinco vezes. Não é uma porcentagem de todo o conhecimento sobre a Amazônia.

## Banco analisado

São **196 questões amazônicas**, de **62 provas com ocorrências**, selecionadas após examinar **1401 itens** dos blocos pertinentes. O cadastro de cobertura contém 70 provas, incluindo 8 sem questões elegíveis. A unidade é a questão numerada: subitens permanecem juntos. Fase/etapa é um atributo da prova no mesmo dataset.

| Origem | Questões |
| --- | --- |
| Inep | 17 |
| UEA | 107 |
| UERR | 10 |
| UFAM | 45 |
| UFRR | 9 |
| USP | 8 |

### Distribuição por ano de aplicação

| Ano | Questões |
| --- | --- |
| 2017 | 17 |
| 2018 | 19 |
| 2019 | 15 |
| 2020 | 1 |
| 2021 | 15 |
| 2022 | 29 |
| 2023 | 17 |
| 2024 | 35 |
| 2025 | 32 |
| 2026 | 16 |

O recorte é 01/01/2017 a 11/11/2026. Ano da edição, ingresso e aplicação são distintos: UEA2020 e Enem2020 foram aplicados em 2021; UEA2021, em 2022. Quando o dia efetivo não foi corroborado, a data fica vazia e a base anual está nas observações. As quantidades descrevem o acervo coletado; lacunas de cobertura não são anos sem cobrança. No Enem, o exame é a origem; não se atribui a questão a uma universidade específica.

## Conteúdos mais presentes

| Tópico padronizado | Questões | % do banco | Provas |
| --- | --- | --- | --- |
| Migrações e urbanização | 15 | 7.65 | 12 |
| Ciclos da borracha e sistema de aviamento | 12 | 6.12 | 11 |
| Clima e relações entre água e floresta | 11 | 5.61 | 11 |
| Transportes, hidrovias e integração | 10 | 5.10 | 10 |
| Ditadura, integração e grandes projetos | 10 | 5.10 | 8 |
| Povos indígenas e comunidades tradicionais | 9 | 4.59 | 8 |
| Desmatamento e queimadas | 7 | 3.57 | 7 |
| Conservação e desenvolvimento sustentável | 7 | 3.57 | 6 |
| Reformas pombalinas e Diretório dos Índios | 7 | 3.57 | 7 |
| Cultura, identidade e patrimônio amazônico | 7 | 3.57 | 7 |
| Mineração e garimpo | 6 | 3.06 | 6 |
| Produção familiar e economia solidária | 6 | 3.06 | 4 |

Cada questão recebe um tópico principal para esta distribuição; pode se relacionar com vários itens do programa. A taxonomia está em [topicos.csv](../dados/topicos.csv), organizada por disciplina, conteúdo e tópico. Esses três campos seguem a classificação principal; `disciplina_origem` conserva a identificação registrada na coleta. Os nomes originais dos editais permanecem em [ementas.csv](../dados/ementas.csv).

### Conteúdos previstos sem cobrança identificada

| Tópico previsto | Provas com previsão explícita | Provas com cobrança vinculada |
| --- | --- | --- |
| Primeira República na Amazônia | 15 | 0 |
| Delimitações e regionalização da Amazônia | 11 | 0 |
| Drogas do sertão e economia colonial | 9 | 0 |
| Economia regional e organização da produção | 6 | 0 |
| Populismo e democracia na Amazônia | 6 | 0 |
| Coronelismo, clientelismo e poder regional | 6 | 0 |
| Comércio fluvial e regatões | 2 | 0 |
| Questão do Acre e Tratado de Petrópolis | 2 | 0 |

Esses zeros se referem às provas comparáveis com previsão explícita do tópico e exigem vínculo com o item correspondente. A tabela [frequencia-topicos.csv](frequencia-topicos.csv) também mostra a frequência por múltiplos tópicos e a proporção de provas que cobraram cada tópico entre aquelas que o previam. Um tópico pode aparecer no banco sob uma cláusula geral e continuar sem cobrança vinculada ao recorte explícito desta tabela.

## Quanto da ementa apareceu em cada prova?

Entre as provas comparáveis, a mediana foi **18.8%**, com valores de **0.0% a 62.5%**.

| Prova | Aplicação | Etapa/fase | Tópicos previstos | Tópicos cobrados | % |
| --- | --- | --- | --- | --- | --- |
| ufam-psc2018-e3 | 2017 | PSC — 3ª etapa | 4 | 1 | 25.00 |
| uea-vest2018-ce | 2018 | 2ª fase — Humanas | 26 | 3 | 11.54 |
| uea-vest2018-cg | 2018 | 1ª fase — Conhecimentos Gerais | 26 | 4 | 15.38 |
| ufam-psc2019-e1 | 2018 | PSC — 1ª etapa | 8 | 5 | 62.50 |
| ufam-psc2019-e2 | 2018 | PSC — 2ª etapa | 13 | 1 | 7.69 |
| ufam-psc2019-e3 | 2018 | PSC — 3ª etapa | 4 | 0 | 0.00 |
| uea-vest2019-ce | 2019 | 2ª fase — Humanas | 26 | 5 | 19.23 |
| uea-vest2019-cg | 2019 | 1ª fase — Conhecimentos Gerais | 26 | 5 | 19.23 |
| ufam-psc2020-e1 | 2019 | PSC — 1ª etapa | 8 | 1 | 12.50 |
| ufam-psc2020-e2 | 2019 | PSC — 2ª etapa | 13 | 2 | 15.38 |
| ufam-psc2020-e3 | 2019 | PSC — 3ª etapa | 4 | 1 | 25.00 |
| uea-vest2020-ce | 2021 | 2ª fase — Humanas | 11 | 3 | 27.27 |
| uea-vest2020-cg | 2021 | 1ª fase — Conhecimentos Gerais | 11 | 2 | 18.18 |
| ufam-psc2021-e3 | 2021 | PSC — 3ª etapa | 4 | 2 | 50.00 |
| uea-vest2021-ce | 2022 | 2ª fase — Humanas | 11 | 2 | 18.18 |
| uea-vest2021-cg | 2022 | 1ª fase — Conhecimentos Gerais | 11 | 4 | 36.36 |
| uea-vest2022-ce | 2022 | 2ª fase — Humanas | 19 | 1 | 5.26 |
| uea-vest2022-cg | 2022 | 1ª fase — Conhecimentos Gerais | 19 | 5 | 26.32 |
| ufam-psc2021-e1 | 2022 | PSC — 1ª etapa | 8 | 4 | 50.00 |
| ufam-psc2021-e2 | 2022 | PSC — 2ª etapa | 13 | 2 | 15.38 |
| ufam-psc2022-e1 | 2022 | PSC — 1ª etapa | 8 | 1 | 12.50 |
| ufam-psc2022-e2 | 2022 | PSC — 2ª etapa | 13 | 2 | 15.38 |
| ufam-psc2022-e3 | 2022 | PSC — 3ª etapa | 4 | 0 | 0.00 |
| uea-vest2023-ce | 2023 | 2ª fase — Humanas | 32 | 6 | 18.75 |
| uea-vest2023-cg | 2023 | 1ª fase — Conhecimentos Gerais | 32 | 5 | 15.62 |
| ufam-psc2023-e2 | 2023 | PSC — 2ª etapa | 13 | 2 | 15.38 |
| ufam-psc2023-e3 | 2023 | PSC — 3ª etapa | 4 | 1 | 25.00 |
| ufam-psc2024-e3 | 2023 | PSC — 3ª etapa | 4 | 1 | 25.00 |
| uea-vest2024-ce | 2024 | 2ª fase — Humanas | 32 | 5 | 15.62 |
| uea-vest2024-cg | 2024 | 1ª fase — Conhecimentos Gerais | 32 | 10 | 31.25 |
| ufam-psc2024-e2 | 2024 | PSC — 2ª etapa | 19 | 5 | 26.32 |
| ufam-psc2025-e3 | 2024 | PSC — 3ª etapa | 10 | 2 | 20.00 |
| ufrr-vestibular2025-pi | 2024 | Etapa única | 23 | 7 | 30.43 |
| uea-vest2025-ce | 2025 | 2ª fase — Humanas | 32 | 6 | 18.75 |
| uea-vest2025-cg | 2025 | 1ª fase — Conhecimentos Gerais | 32 | 9 | 28.12 |
| uerr-vestibular2025 | 2025 | Etapa única | 14 | 7 | 50.00 |
| ufam-psc2025-e2 | 2025 | PSC — 2ª etapa | 19 | 5 | 26.32 |
| ufam-psc2026-e3 | 2025 | PSC — 3ª etapa | 10 | 2 | 20.00 |
| ufrr-vestibular2026-pi | 2025 | Etapa única | 23 | 2 | 8.70 |
| uea-vest2026-ce | 2026 | 2ª fase — Humanas | 14 | 0 | 0.00 |
| uea-vest2026-cg | 2026 | 1ª fase — Conhecimentos Gerais | 14 | 2 | 14.29 |
| uerr-vestibular2026 | 2026 | Etapa única | 14 | 5 | 35.71 |
| ufam-psc2026-e2 | 2026 | PSC — 2ª etapa | 19 | 3 | 15.79 |

O denominador é o conjunto de tópicos padronizados associados aos itens regionais explícitos da ementa de cada prova. O numerador conta os tópicos exigidos por pelo menos uma questão vinculada semanticamente ao item pertinente. Compartilhar uma categoria ampla não basta: uma questão sobre o Acre em 1903 não é vínculo com um item exclusivo sobre Madri em 1750. Tópicos repetidos em vários itens do mesmo programa contam uma vez. Um item amplo pode conter vários tópicos: a cobrança de um deles não transforma todo o item em conteúdo cobrado. Não se calcula essa porcentagem quando falta o programa regional integral ou a triagem completa da prova. A tabela detalhada também conserva a contagem por item original para permitir conferir a interpretação.

A tabela [itens-ementa.csv](itens-ementa.csv) mostra a redação oficial, a fonte e as questões ligadas a cada item, incluindo os que não tiveram questão identificada. Zero significa ausência no recorte efetivamente examinado; não significa que o assunto nunca caiu. [previsto-cobrado.csv](previsto-cobrado.csv) contém todas as provas e os limites de cobertura.

### As duas fases da UEA

| UEA | Provas | Questões amazônicas | Questões/prova | Cobertura regional explícita |
| --- | --- | --- | --- | --- |
| 1ª fase — Conhecimentos Gerais | 10 | 59 | 5.9 | 22.7% |
| 2ª fase — Humanas | 10 | 48 | 4.8 | 15.3% |

As fases permanecem no mesmo banco; esta comparação usa o atributo da prova. A média de questões é descritiva das dez edições coletadas. A cobertura considera apenas as edições com programa regional integral recuperado. Um valor zero nessa medida significa que as questões não foram ligadas aos itens com previsão regional **explícita**; questões amazônicas podem estar amparadas por cláusulas gerais do programa.

## Coleta, limpeza e curadoria

As fontes são cadernos e programas das instituições e das organizadoras oficiais, obtidos diretamente ou por cópias públicas identificadas como tal. `fontes.csv` distingue o endereço de download da publicação institucional. Cada questão conserva prova, número, página, URL e hash do PDF. Foram mantidas 177 questões de foco central e 19 com cobrança regional substantiva dentro de contexto misto. Menções decorativas à Amazônia, conteúdo geral e “Amazônia Azul” foram excluídos. O campo `justificativa` explica a inclusão.

A limpeza padroniza Unicode e espaços, remove duplicatas exatas de uma mesma prova/número e valida vínculos com fontes, provas e ementas. Não traduz distratores incorretos em afirmações factuais nem preenche respostas por inferência. Mapas, gráficos e imagens devem ser consultados no PDF, na página registrada. Correções de extração conferidas na imagem ficam declaradas no registro bruto.

As 2 questões com anulação oficial permanecem porque constaram dos cadernos; o campo `gabarito=ANULADA` permite identificá-las. A análise de conteúdo conta sua presença na prova, sem tratá-las como itens válidos para pontuação.

A seleção e a classificação semântica foram feitas por agentes de IA (Codex), sem exigir anotação manual de Matheus e sem avaliação de modelos como etapa do estudo. São decisões de curadoria rastreáveis, sujeitas a revisão; não são rótulos humanos. Há 16 questões sem vínculo programático localizado e 2 fontes consultadas sem hash de arquivo local. Nenhuma dessas lacunas foi preenchida por presunção.

## Como interpretar os resultados

Frequência no banco mede a composição do acervo, não a probabilidade de uma questão futura. Comparações entre instituições ou fases precisam considerar o número de provas cobertas, o tamanho dos blocos e a granularidade de cada edital. Compilações discursivas reúnem as questões oferecidas; não representam todas as questões respondidas por um único candidato.

A lista de tópicos previstos sem cobrança e a concentração observada nos tópicos mais recorrentes respondem à pergunta do estudo dentro da cobertura documentada. A fração da ementa mede tópicos e depende da granularidade da taxonomia; não mede extensão do texto, carga horária ou domínio exigido.

Cobertura: núcleo UEA Vestibular 2017–2026 (Conhecimentos Gerais e Específicos/Humanas) e UFAM PSC 2018–2026, aplicados dentro do recorte; Enem regular impresso 2017–2025 e segunda fase FUVEST 2017–2026; complemento UFRR PI 2025/2026 e UERR 2025/2026. O programa UEA 2017 e dois editais PSC 2018 não foram recuperados integralmente. A comparação programática nacional é temática e ampla: Enem/FUVEST não entram na porcentagem regional explícita. O Enem 2026 teve o [primeiro dia aplicado em 08/11/2026](https://www.gov.br/inep/pt-br/centrais-de-conteudo/noticias/enem/participantes-concluem-primeiro-dia-do-enem-2026), mas o PDF oficial não foi localizado até a consulta; isso é lacuna de coleta. O levantamento não é um censo de todas as instituições e modalidades brasileiras.
