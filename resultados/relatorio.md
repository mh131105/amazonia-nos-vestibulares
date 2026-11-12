# Uma ementa ampla, uma prova seletiva: História e Geografia da Amazônia

## Resposta à pergunta do estudo

**Quanto da ementa realmente apareceu?** Nas **43 provas com programa regional integral e triagem completa**, houve cobrança identificada de **141/682 pares prova × tópico padronizado: 20,7%**. Essas provas reúnem 156 das 196 questões do banco.

O resultado descreve o recorte que cada prova faz de seu próprio programa. Um tópico previsto em cinco provas entra cinco vezes. Os conteúdos vêm das ementas; os nomes, agrupamentos e desdobramentos são decisões de curadoria documentadas. Portanto, a porcentagem depende dessa granularidade. Ela não mede extensão de texto, carga horária nem chance de cair no próximo vestibular.

A resposta ganha três nuances: a frequência se concentra em alguns conteúdos; questões regionais também se vinculam a cláusulas gerais; e a evolução temporal varia entre fases. Na UEA, a primeira fase cresce no contraste de calendário enquanto a segunda recua. Os dados não sustentam uma mudança uniforme nem um efeito causal do Novo Ensino Médio.

## 1. O universo que conseguimos observar

O acervo contém **196 questões amazônicas**, selecionadas entre **1401 itens examinados**, em **70 provas**, das quais 62 têm ocorrências e 8 não têm questões elegíveis. São 53 tópicos padronizados, 50 observados com ao menos uma etiqueta e 344 associações questão–tópico. As associações não são questões adicionais.

| Origem | Provas examinadas | Itens triados | Questões amazônicas | Provas com comparação de ementa | Cobertura por tópico |
| --- | --- | --- | --- | --- | --- |
| Inep | 9 | 405 | 17 | 0 | Não calculada |
| UEA | 20 | 480 | 107 | 18 | 77/406 (19,0%) |
| UERR | 2 | 36 | 10 | 2 | 12/28 (42,9%) |
| UFAM | 27 | 324 | 45 | 21 | 43/202 (21,3%) |
| UFRR | 2 | 36 | 9 | 2 | 9/46 (19,6%) |
| USP | 10 | 120 | 8 | 0 | Não calculada |

**Fonte:** [provas.csv](../dados/provas.csv), [questoes.csv](../dados/curado/questoes.csv) e [previsto-cobrado.csv](previsto-cobrado.csv). O Enem é uma origem única, sem replicação por universidade usuária da nota. UEA/PSC têm blocos de História e Geografia; Enem tem Ciências Humanas; FUVEST usa compilações discursivas de H/G. Esses denominadores não representam blocos idênticos.

O núcleo UEA cobre as edições Vestibular/Macro 2017–2026, nas duas fases selecionadas; o PSC cobre edições 2018–2026 nas três etapas aplicadas dentro do recorte. O complemento reúne Enem regular impresso 2017–2025, FUVEST segunda fase 2017–2026 e UERR/UFRR 2025/2026. Não é um censo nacional. Uma cor equivalente por aplicação evita multiplicar questões; subitens discursivos permanecem na questão numerada.

A janela é **01/01/2017 a 11/11/2026**, por ano de aplicação, com 2026 parcial. A edição UEA 2020 e o Enem 2020 foram aplicados em 2021; UEA 2021 foi aplicada em 2022. Há duas edições UEA aplicadas em 2022 e nenhuma observação UEA em 2020. Edição, ingresso e aplicação não são intercambiáveis.

| Ano de aplicação | Provas | Itens triados | Questões amazônicas | Provas com programa comparável |
| --- | --- | --- | --- | --- |
| 2017 | 7 | 141 | 17 | 1 |
| 2018 | 7 | 141 | 19 | 5 |
| 2019 | 7 | 141 | 15 | 5 |
| 2020 | 1 | 12 | 1 | 0 |
| 2021 | 6 | 162 | 15 | 3 |
| 2022 | 11 | 213 | 29 | 9 |
| 2023 | 9 | 165 | 17 | 5 |
| 2024 | 8 | 159 | 35 | 5 |
| 2025 | 9 | 177 | 32 | 6 |
| 2026 | 5 | 90 | 16 | 4 |

A série anual completa, inclusive células sem observação, está em [temporal.csv](temporal.csv). Uma célula com zero provas tem proporção vazia; uma prova examinada sem questão amazônica tem proporção zero. A variação dos totais anuais também reflete a cobertura e os calendários.

## 2. O que significa cobrir 20,7% da ementa?

O denominador reúne os tópicos associados a **cláusulas regionais explícitas** de cada prova comparável, com repetição interna removida. O numerador exige uma questão vinculada ao item pertinente e interseção entre os tópicos da questão e os do item. Uma questão sobre Acre/Petrópolis em 1903 não demonstra cobrança de um item exclusivo sobre Madri em 1750, mesmo que ambos tratem de fronteiras.

Os 43 programas/provas comparáveis são UEA, UFAM, UERR e UFRR. Ficam fora da proporção as 19 provas nacionais com vínculo programático amplo, as duas fases UEA 2017 e PSC 2018 E1/E2 com programa pendente, além de quatro PSC E1 recentes sem previsão regional explícita registrada. Ausência de denominador regional não vira cobertura zero.

![Cobertura dos tópicos regionais por prova e origem](figuras/cobertura-ementa.png)

**Figura 1.** Cada ponto pequeno é uma prova; o losango mostra a razão dos totais de tópicos cobrados/previstos de sua origem. A linha marca o agregado de 20,7%. UERR/UFRR têm apenas duas provas cada. Fonte: [previsto-cobrado.csv](previsto-cobrado.csv); reprodução: `python scripts/figuras.py`.

A mediana das proporções por prova é 18,8%, a média simples é 21,6% e a faixa vai de 0,0% a 62,5%. A razão 141/682 dá mais peso a provas com mais tópicos previstos; a média simples dá peso igual a cada prova.

Por registros de cláusulas regionais transcritas, há algum vínculo registrado em **240/849 (28,3%)**. Essa é outra unidade: uma cláusula pode reunir vários tópicos, e qualquer vínculo não demonstra domínio de toda a cláusula. Exigindo também interseção de etiquetas por cláusula, são **228/849 (26,9%)**: 12 registros ligados a questões não compartilham suas etiquetas. Essa diferença entre vínculo semântico e etiquetas merece revisão; os totais por tópico continuam sendo o indicador principal. A redação original e as correspondências podem ser conferidas em [itens-ementa.csv](itens-ementa.csv).

| Área dos tópicos | Pares cobrados | Pares previstos | Cobertura (%) |
| --- | --- | --- | --- |
| História | 75 | 410 | 18,3 |
| Geografia | 66 | 272 | 24,3 |

A diferença entre áreas descreve a taxonomia e os programas observados; as questões interdisciplinares podem contribuir com um tópico em cada área, sem serem duplicadas no banco.

### Zero de cobertura não é ausência de questão regional

Há 52 questões ligadas somente a cláusulas gerais, 90 somente a regionais explícitas, 38 a ambas e 16 sem item localizado. Isso difere dos rótulos de força do vínculo: direto, amplo e não localizado.

A UEA 2026, segunda fase de Humanas, tem **três questões regionais e 0/14 tópicos regionais explícitos cobrados**. Os objetos são independência no Pará (Q05, p.3), terra preta (Q13, p.5) e rios voadores (Q16, p.7). Os vínculos pertinentes são cláusulas gerais: “Revoluções e independências nas Américas” (programa p.8), “Solo.” e “A dinâmica climática da Terra” (p.9). O zero não demonstra ausência de cobrança amazônica nem questão fora do edital.

| Fase/etapa | Provas | Questões | Questões/prova | Programas comparáveis | Pares cobrados/previstos | Cobertura (%) |
| --- | --- | --- | --- | --- | --- | --- |
| UEA — Vestibular — 1ª fase — Conhecimentos Gerais | 10 | 59 | 5.90 | 9 | 46/203 | 22,7 |
| UEA — Vestibular — 2ª fase — Humanas | 10 | 48 | 4.80 | 9 | 31/203 | 15,3 |
| UFAM — PSC — PSC — 1ª etapa | 9 | 12 | 1.33 | 4 | 11/32 | 34,4 |
| UFAM — PSC — PSC — 2ª etapa | 9 | 21 | 2.33 | 8 | 22/122 | 18,0 |
| UFAM — PSC — PSC — 3ª etapa | 9 | 12 | 1.33 | 9 | 10/48 | 20,8 |

As duas fases UEA permanecem no mesmo dataset. Os blocos triados têm 24 itens H/G por fase, enquanto cada etapa PSC tem 12. A contagem de questões por prova não mede profundidade ou dificuldade.

## 3. Alguns conteúdos voltam; outros não foram observados

Os cinco tópicos principais mais frequentes reúnem **58/196 questões (29,6%)**. A classificação principal distribui cada questão uma vez; a classificação múltipla preserva conexões entre assuntos.

![Conteúdos recorrentes em classificações principais e adicionais](figuras/topicos-recorrentes.png)

**Figura 2.** Cada barra conta questões distintas com o tópico; o segmento escuro mostra as que o têm como tópico principal. A soma entre tópicos pode superar 196. Período: aplicações 2017–11/11/2026. Fonte: [frequencia-topicos.csv](frequencia-topicos.csv) e [questoes.csv](../dados/curado/questoes.csv).

| Tópico principal | Questões principais | Questões com o tópico | Provas como principal |
| --- | --- | --- | --- |
| Migrações e urbanização | 15 | 23 | 12 |
| Ciclos da borracha e sistema de aviamento | 12 | 18 | 11 |
| Clima e relações entre água e floresta | 11 | 12 | 11 |
| Transportes, hidrovias e integração | 10 | 21 | 10 |
| Ditadura, integração e grandes projetos | 10 | 11 | 8 |
| Povos indígenas e comunidades tradicionais | 9 | 21 | 8 |
| Desmatamento e queimadas | 7 | 15 | 7 |
| Conservação e desenvolvimento sustentável | 7 | 13 | 6 |
| Reformas pombalinas e Diretório dos Índios | 7 | 7 | 7 |
| Cultura, identidade e patrimônio amazônico | 7 | 11 | 7 |
| Mineração e garimpo | 6 | 9 | 6 |
| Produção familiar e economia solidária | 6 | 7 | 4 |

Migrações e urbanização lideram como tópico principal. Considerando etiquetas adicionais, povos indígenas e comunidades tradicionais alcançam 21 questões em 20 provas e nas seis origens do banco. Recorrência no acervo não é probabilidade futura: a UEA fornece 107 das 196 questões e influencia o agregado.

Há conexões entre processos históricos e geográficos. `uea2017-geral-q19` (p.10), sobre um caucheiro, articula borracha e deslocamentos; `uea-2025-ce-q19` (p.8) pede leitura de saldo migratório e tipos de migração. São exemplos de objetos cobrados, sem inferência de mudança de dificuldade.

| Tópico sem cobrança vinculada | Provas com previsão explícita | Questões com o tópico em todo o banco |
| --- | --- | --- |
| Primeira República na Amazônia | 15 | 2 |
| Delimitações e regionalização da Amazônia | 11 | 1 |
| Drogas do sertão e economia colonial | 9 | 4 |
| Economia regional e organização da produção | 6 | 0 |
| Populismo e democracia na Amazônia | 6 | 0 |
| Coronelismo, clientelismo e poder regional | 6 | 0 |
| Comércio fluvial e regatões | 2 | 4 |
| Questão do Acre e Tratado de Petrópolis | 2 | 2 |

Os zeros da tabela se limitam às provas que previram explicitamente o tópico e ao vínculo com a cláusula correspondente. Primeira República aparece em questões nacionais mesmo sem cobrança vinculada nas 15 provas com previsão regional explícita; Acre/Petrópolis aparece em duas questões do banco, embora não nas duas provas com sua previsão explícita. Populismo, coronelismo e organização da produção não têm etiqueta em nenhuma questão coletada; suas seis previsões correspondem a duas fases de três edições UEA. Ausência no acervo não autoriza abandonar o conteúdo na preparação.

## 4. História, Geografia e interdisciplinaridade

Pelo tópico principal, são **87 questões de História e 109 de Geografia**. Pelo conjunto de etiquetas, são **67 somente História, 104 somente Geografia e 25 com ambas**. Esse último é o critério operacional de interdisciplinaridade usado aqui; não é uma anotação oficial das bancas.

A disciplina de origem registra 83 questões como História e 113 como Geografia. Seis questões mudam de área na classificação principal; os dois campos foram preservados. “Foco regional misto” tem outro significado: há conteúdo amazônico substantivo em um contexto mais amplo. As 19 questões assim marcadas não são as 25 interdisciplinares H/G. Nenhuma dessas distinções duplica o total de questões.

## 5. O que mudou no tempo, em torno do Novo Ensino Médio?

### Cortes e alcance da comparação

A comparação é **observacional por calendário de aplicação**. O plano temporal segue quatro faixas: **2017–2021**, **2022–2023**, **2024** e **2025–2026**. O contraste principal compara 2017–2021 com 2024–2026, deixando 2022–2023 fora dele; a sensibilidade posterior sem 2026 usa 2024–2025. Esses cortes constam da seção6 do protocolo histórico, acessível com `git show 3f044af^:docs/protocolo.md`. A referência antecede o cronograma geral, mas pode conter pilotos ou implantações locais.

A [Lei 13.415/2017, art.12](https://www2.camara.leg.br/legin/fed/lei/2017/lei-13415-16-fevereiro-2017-784336-publicacaooriginal-152003-pl.html) é um marco legal, sem demonstrar mudança simultânea das redes. O cronograma original da [Portaria MEC 521/2021, art.4º](https://www.seduc.pa.gov.br/site/public/upload/arquivo/probncc/PORTARIA%20N%C2%BA%20521%2C%20DE%2013%20DE%20JULHO%20DE%202021-e03b6.pdf) previa primeira série em 2022, primeiras duas em 2023 e todas em 2024. A chegada de uma coorte iniciada em 2022 à terceira série em 2024 é uma inferência normativa.

A [suspensão de prazos em 2023](https://www.gov.br/secom/pt-br/assuntos/obrasilvoltou/cuidado/cronograma-de-implementacao-do-novo-ensino-medio-e-suspenso) não demonstra paralisação uniforme da implantação. A [Lei 14.945/2024, art.5º, II](https://www2.camara.leg.br/legin/fed/lei/2024/lei-14945-31-julho-2024-796017-publicacaooriginal-172512-pl.html) prevê início da revisão em 2025; as [DCNEM 2/2024, arts.39 e 42, pp.23–24](https://www.seduc.pa.gov.br/site/public/upload/arquivo/probncc/RESOLUCAO%20CNE-CEB%202-2024-f599f.pdf) permitem transições e coexistência curricular. Os ingressantes mencionados nesses artigos são do ensino médio. Logo, 2025–2026 não forma um período curricular homogêneo.

No Enem, o [Edital 52/2025, item3.1](https://download.inep.gov.br/enem/edital_52_de_23_de_maio_de_2025.pdf), também publicado no [DOU de 23/05/2025, seção3 extra, p.1](https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?captchafield=firstAccess&data=23%2F05%2F2025&jornal=608&pagina=1), ainda remete à matriz de referência histórica; não há justificativa para rotular automaticamente as questões Enem 2024 como um novo formato curricular. Implantação escolar, currículo de um candidato e alteração da matriz da prova são variáveis distintas.

### As fases da UEA seguem direções diferentes

![Série anual de cobrança amazônica nas fases da UEA](figuras/serie-uea.png)

**Figura 3.** O painel superior divide questões amazônicas pelos itens H/G triados; o inferior divide tópicos cobrados pelos previstos regionalmente. A lacuna de 2020 significa ausência de aplicação observada; em 2022 há duas edições por fase. Fonte: [temporal.csv](temporal.csv). As faixas são calendário, sem atribuição causal ao currículo.

| Aplicação | UEA — primeira fase | UEA — segunda fase Humanas |
| --- | --- | --- |
| 2017–2021 | 19/96 (19,8%) | 23/96 (24,0%) |
| 2022–2023 | 14/72 (19,4%) | 10/72 (13,9%) |
| 2024 | 12/24 (50,0%) | 6/24 (25,0%) |
| 2025–2026 | 14/48 (29,2%) | 9/48 (18,8%) |
| 2024–2026 | 26/72 (36,1%) | 15/72 (20,8%) |
| 2024–2025 | 21/48 (43,8%) | 12/48 (25,0%) |

A primeira fase passa de **19/96 (19,8%)** para **26/72 (36,1%)**, diferença de **+16,32 pontos percentuais**. A segunda fase passa de **23/96 (24,0%)** para **15/72 (20,8%)**, diferença de **−3,13 pontos**. São quatro provas por fase na referência e três no período posterior. O agregado UEA sobe de 42/192 para 41/144 (+6,60 pontos), mas esconde as direções distintas. Sem 2026, a segunda fase fica em 12/48 (25,0%): a pequena queda deixa de aparecer.

A mudança do programa também importa: cada fase UEA tem 26 tópicos previstos em 2018/2019, 11 em 2020/2021, 19 em 2022, 32 em 2023–2025 e 14 em 2026. O programa 2017 está ausente. A cobertura dos programas disponíveis passa de 22/126 (17,5%) para 32/156 (20,5%). Quando restringimos aos tópicos explicitamente presentes em **todas** as provas UEA comparáveis desses dois períodos, o resultado é:

| Período | Provas com programa | Tópicos comuns por prova | Pares cobrados/previstos | Cobertura (%) |
| --- | --- | --- | --- | --- |
| 2017–2021 | 6 | 4 | 4/24 | 16,7 |
| 2024–2026 | 6 | 4 | 4/24 | 16,7 |

Tópicos comuns: G04 — Hidrografia e dinâmica fluvial, G09 — Conservação e desenvolvimento sustentável, H02 — Sociedades indígenas antes da conquista, H16 — Zona Franca de Manaus e industrialização. A estabilidade dessa sensibilidade contrasta com o aumento no programa variável. Nenhuma das medidas, isoladamente, identifica efeito do NEM.

| Tópico comum | Provas com cobrança / previstas em 2017–2021 | Em 2024–2026 |
| --- | --- | --- |
| Hidrografia e dinâmica fluvial | 2/6 | 0/6 |
| Conservação e desenvolvimento sustentável | 1/6 | 3/6 |
| Sociedades indígenas antes da conquista | 1/6 | 0/6 |
| Zona Franca de Manaus e industrialização | 0/6 | 1/6 |

A igualdade da taxa agregada não significa os mesmos tópicos cobrados: a composição se desloca de hidrografia e sociedades indígenas para conservação e Zona Franca.

### Comparar os mesmos estratos muda a leitura do agregado

![Contrastes temporais por instituição, processo e etapa](figuras/comparacao-temporal.png)

**Figura 4.** Referência 2017–2021 versus aplicações 2024–2026; cada linha mantém instituição × processo × etapa presentes nos dois lados. Os números ao lado são questões amazônicas/itens triados. Fonte: [temporal.csv](temporal.csv). FUVEST dia3, UERR e UFRR não entram nesse painel por falta de um dos lados.

| Estrato | 2017–2021 | 2024–2026 | Diferença (p.p.) |
| --- | --- | --- | --- |
| Inep — ENEM — 1º dia — Humanas | 7/225 (3,1%) | 6/90 (6,7%) | 3,56 |
| UEA — Vestibular — 1ª fase — Conhecimentos Gerais | 19/96 (19,8%) | 26/72 (36,1%) | 16,32 |
| UEA — Vestibular — 2ª fase — Humanas | 23/96 (24,0%) | 15/72 (20,8%) | -3,13 |
| UFAM — PSC — PSC — 1ª etapa | 5/36 (13,9%) | 1/36 (2,8%) | -11,11 |
| UFAM — PSC — PSC — 2ª etapa | 3/36 (8,3%) | 12/36 (33,3%) | 25,00 |
| UFAM — PSC — PSC — 3ª etapa | 4/48 (8,3%) | 3/24 (12,5%) | 4,17 |
| USP — FUVEST — 2ª fase — dia 2 | 2/36 (5,6%) | 1/24 (4,2%) | -1,39 |

O PSC também é heterogêneo: a primeira etapa cai e a segunda cresce. As contagens posteriores de Enem e FUVEST são pequenas; FUVEST dia2 é separado do dia3 antigo para preservar a etapa documentada. O número de questões discursivas oferecidas não representa a exposição de um candidato a todos os componentes.

| Conjunto | Período | Provas | Amazônicas/triadas | Razão global (%) | Média por prova (%) | Média dos mesmos estratos (%) |
| --- | --- | --- | --- | --- | --- | --- |
| acervo inteiro | 2017–2021 | 28 | 67/597 | 11,2 | 12,2 | — |
| acervo inteiro | 2024–2026 | 22 | 83/426 | 19,5 | 19,6 | — |
| acervo inteiro | 2024–2025 | 17 | 67/336 | 19,9 | 20,3 | — |
| painel comum | 2017–2021 | 26 | 63/573 | 11,0 | 11,8 | 11,9 |
| painel comum | 2024–2026 | 18 | 64/354 | 18,1 | 18,1 | 16,6 |
| painel comum | 2024–2025 | 14 | 53/282 | 18,8 | 19,1 | 19,1 |

A razão global pesa os blocos pelo número de itens; a média por prova dá peso igual às provas; a média dos mesmos estratos dá peso igual aos sete estratos comuns. UERR/UFRR só entram na visão de todo o acervo. Esses agregados descrevem desenhos diferentes e não substituem a leitura estratificada.

Nos seriados, cortes aproximados por série seriam E1/2022, E2/2023 e E3/2024. A sensibilidade abaixo divide o **calendário**, preservando as etapas:

| Etapa PSC | Antes do corte | A partir do corte |
| --- | --- | --- |
| PSC — 1ª etapa | Antes de 2022: 5/36 (13,9%) | A partir de 2022: 7/72 (9,7%) |
| PSC — 2ª etapa | Antes de 2023: 7/60 (11,7%) | A partir de 2023: 14/48 (29,2%) |
| PSC — 3ª etapa | Antes de 2024: 9/84 (10,7%) | A partir de 2024: 3/24 (12,5%) |

Esses cortes não classificam exposição curricular: o PSC 2021 E1/E2 foi aplicado em 2022 com série-alvo anterior, e o PSC 2026 E2 foi aplicado em 2026 para série-alvo 2025. Sem trajetória escolar e evidência local vinculada, uma comparação por coorte real não é identificável nesta base. Os resultados dos cortes estão em `temporal.csv`, tipo `corte seriado`, sem inventar esse atributo dos candidatos.

## 6. Robustez e conferência dos indicadores

| Cenário | Questões no banco | Questões nas comparáveis | Provas comparáveis | Pares cobrados/previstos | Cobertura (%) |
| --- | --- | --- | --- | --- | --- |
| Base | 196 | 156 | 43 | 141/682 | 20,7 |
| Sem anuladas | 194 | 154 | 43 | 138/682 | 20,2 |
| Somente foco central | 177 | 145 | 43 | 132/682 | 19,4 |
| Central sem anuladas | 175 | 143 | 43 | 129/682 | 18,9 |
| Sem 2026 | 180 | 140 | 39 | 131/621 | 21,1 |

Nos quatro primeiros cenários, mantêm-se as provas e o denominador original, inclusive quando a remoção deixa uma prova sem questões. “Sem 2026” muda a janela e seu universo de programas. As retiradas são simulações em memória; os dados curados permanecem intactos. Fonte: [sensibilidade.csv](sensibilidade.csv).

As anulações conhecidas são `ufam-psc2021-e1-q21`, `uerr-vestibular2025-q57`. A presença no caderno sustenta a análise principal de cobrança aplicada. Excluir somente as anulações conhecidas não produz uma medida de prova válida para pontuação: há **129 gabaritos vazios**, incluindo oito discursivos. Não presumimos validade dos demais itens nem resolvemos respostas por IA.

A conferência encontrou 0 IDs repetidos e 0 hashes de texto limpo repetidos; prova/número também é único. Os totais de triagem foram reconciliados com o cadastro e a seleção. Há 16 questões sem vínculo localizado, 14 por programas pendentes e duas sem associação pertinente identificada. Datas diárias ausentes (111 questões) não foram preenchidas por suposição; o ano e sua evidência permanecem no cadastro.

**Divergências e ressalvas da verificação complementar:**

A questão `uea-2026-ce-q05` (Pará, 1823, prova p.3) contém um vínculo adicional ao item `uea-vest2026-ce__uea-vest2026-historia-027` (“Império Brasileiro: 2º Reinado.”, programa p.8). Esse vínculo adicional é cronologicamente inadequado. A análise do exemplo usa o item H024 (“Revoluções e independências nas Américas”), também registrado. A simulação de retirar somente H027 não modifica 141/682 nem 0/14, pois H027 tem escopo geral. O registro curado foi preservado e a ressalva fica explícita para revisão.

Os tipos de resposta `objetiva` e `objetiva_multipla_escolha` são tratados como a mesma família na descrição; os valores originais são preservados. As diferenças entre disciplina de origem e principal são documentadas, e não erros de soma. A verificação confirma o indicador principal; não substitui validação humana integral da curadoria feita por agentes de IA.

## 7. Limites e implicações

**O que observamos:** recortes programáticos modestos em cada prova, recorrência de alguns conteúdos e trajetórias temporais diferentes entre fases e etapas. Os tópicos previstos sem cobrança identificada continuam parte do universo potencial de estudo.

**O que interpretamos:** o percentual depende do recorte regional explícito, da taxonomia e da janela. Mudanças de ementa, pandemia, formato, banca e disponibilidade documental podem acompanhar as diferenças. Não há respostas comparáveis de candidatos, medida de procura por curso nem classificação sistemática de demanda cognitiva. Não podemos concluir que as provas ficaram mais difíceis, que a reforma causou mudanças ou que a aprendizagem se alterou.

**O que recomendamos para a plataforma educacional:** organizar a navegação por disciplina → conteúdo → tópico, preservando múltiplas etiquetas e filtros de prova/etapa; apresentar frequência junto ao número de provas observadas; manter conteúdos previstos sem ocorrência e ligações a cláusulas gerais. Antes de usar o banco para correção automática, completar os gabaritos ausentes, revisar decisões semânticas e oferecer os recursos visuais originais nas páginas indicadas. Essas são recomendações de uso, não resultados sobre desempenho.

Os programas UEA 2017 e PSC 2018 E1/E2 permanecem pendentes. O Enem 2026 já teve o [primeiro dia aplicado em 08/11/2026](https://www.gov.br/inep/pt-br/centrais-de-conteudo/noticias/enem/participantes-concluem-primeiro-dia-do-enem-2026), mas seu PDF oficial não foi localizado na consulta; 2026 não é uma edição nacional com zero questões regionais. Enem PPL, digital, reaplicações e outras variantes não integram este recorte.

São 151 referências de fonte, 149 com hash do PDF recuperado. O catálogo distingue publicações institucionais de cópias públicas identificadas. Texto e alternativas conservam os distratores, inclusive afirmações falsas; imagens, mapas e gráficos exigem consultar o PDF. A curadoria semântica foi feita por agentes de IA, sem anotação humana integral ou medição de sua taxa de erro.

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
