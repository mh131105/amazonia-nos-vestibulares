# Ampliação documental UFAM — ciclo 2

Triagem em 11/11/2026, assistida pelo Codex; revisão humana pendente. O arquivo [expansao-ufam-c2.json](../data/registry/expansao-ufam-c2.json) acrescenta **15 conjuntos de aplicações candidatas** ao levantamento inicial, sem alterar os quatro cadernos UFAM já preservados no piloto. São localizações de fontes e leituras iniciais: a aquisição definitiva com hashes continua a cargo do coletor do projeto.

## Fontes e alcance

Foram examinados o [índice legado oficial da Compec](https://antigocompec.ufam.edu.br/psc.htm), as páginas de itens do [repositório administrativo Edoc](https://edoc.ufam.edu.br/handle/123456789/552) e notícias institucionais. O índice legado identifica editais, provas, gabaritos e retificações de edições antigas; o Edoc reúne conjuntos posteriores, inclusive documentos da pandemia. As duas fontes se complementam: falta de um item no índice atual não demonstra que a prova não existiu.

O resultado não cobre todas as aplicações de todas as etapas em 2017–2026. A lista de candidatos ainda não examinados fica separada no JSON, com sua página de origem. Não foram baixados arquivos de candidatos, listas de desempenho ou documentação individual.

## Datas: sete conjuntos com aplicação sustentada

| ID da aplicação | Data efetiva registrada | Série-alvo / ano letivo | Evidência |
| --- | --- | --- | --- |
| `ufam-psc2018-e3` | 03/12/2017 | 3ª / 2017 | Cronograma do edital, p. PDF 29, e notícia institucional pós-evento, com divergência no nome da edição. |
| `ufam-psc2020-e1` | 01/12/2019 | 1ª / 2019 | Data explícita na capa da prova, p. PDF 1. |
| `ufam-psc2020-e2` | 01/12/2019 | 2ª / 2019 | Data explícita na capa da prova, p. PDF 1. |
| `ufam-psc2021-e1` | 06/03/2022 | 1ª / 2020 | Retificação de cronograma e notícia institucional posterior. |
| `ufam-psc2021-e2` | 06/03/2022 | 2ª / 2020 | Retificação de cronograma e notícia institucional posterior. |
| `ufam-psc2022-e1` | 23/10/2022 | 1ª / 2021 | Cronograma e notícia institucional de 25/10/2022. |
| `ufam-psc2022-e2` | 23/10/2022 | 2ª / 2021 | Cronograma e notícia institucional de 25/10/2022. |

A [notícia de 13/12/2017](https://antigo.ufam.edu.br/2013-04-29-19-37-05/arquivo-de-noticias/7471-compec-divulga-gabaritos-definitivos-do-psc-2017) confirma a realização das três etapas no dia 3 de dezembro, mas chama a edição de PSC2017, enquanto edital, caderno e índice a identificam como PSC2018. Essa inconsistência permanece registrada; a publicação não autoriza trocar silenciosamente os identificadores de edição.

A [notícia de 25/10/2022](https://www.ufam.edu.br/noticias-destaque/4222-ufam-aplica-as-provas-das-etapas-1-e-2-do-processo-seletivo-continuo-2022.html) confirma a aplicação das etapas 1 e 2 do PSC2022 em 23 de outubro e relata o adiamento das etapas 1 e 2 do PSC2021 de 30 de janeiro para 6 de março. Os editais e as retificações ligam essas datas ao ano de 2022. Assim, há **duas edições da mesma etapa no mesmo ano-calendário**, que devem permanecer como aplicações distintas.

Os editais PSC2021 E1/E2 dizem expressamente que o público cursou a respectiva série em **2020**. Nos editais PSC2022 E1/E2, o ano letivo é **2021**. A aplicação em 2022 não demonstra que esses candidatos pertenciam à coorte que iniciou o ensino médio naquele ano.

## Oito conjuntos com data exata ainda pendente

| Conjunto | Última data prevista localizada | Situação da evidência |
| --- | --- | --- |
| PSC2019 E1, E2 e E3 | 02/12/2018 | Editais e provas/gabaritos localizados; falta corroboração primária suficiente do dia efetivo. |
| PSC2021 E3 | 31/10/2021 | Edital, reaberturas, prova e definitivo localizados; capa sem data preenchida. |
| PSC2022 E3 | 17/07/2022 | Edital, retificações, prova e definitivo localizados; notícias encontradas são anteriores à aplicação. |
| PSC2023 E1 e E2 | 30/07/2023 | Programas, provas, definitivos e notícias pré-evento localizados. |
| PSC2023 E3 | 30/04/2023 | Edital, prova e definitivo localizados; confirmação primária posterior ainda a completar. |

Esses oito conjuntos têm `data_aplicacao=null` e `data_aplicacao_prevista` separada no JSON. Sua existência documental não foi transformada em confirmação do dia de aplicação. Clippings de imprensa de terceiros hospedados no repositório institucional não foram tratados como notícia original da UFAM: dois resultados encontrados divergem entre 2 e 3 de dezembro de 2018.

## Programas e disciplinas

Os programas foram lidos nas seções de História e Geografia dos editais-base. A vigência final depende ainda da auditoria integral das retificações localizadas. As páginas físicas do PDF estão registradas no JSON; não foram confundidas com o ano de edição ou com páginas impressas.

- História regional aparece nos programas antigos das três etapas, com conteúdo de sociedades indígenas, colonização, organização territorial, economia e políticas públicas, conforme a etapa.
- Geografia regional é explícita nos programas das etapas 1 e 2 de PSC2019, PSC2020, PSC2021 e PSC2022. Portanto, a evidência de previsão geográfica no processo não começa em 2024.
- Nos programas de Geografia da etapa 3 examinados em PSC2018, PSC2019, PSC2021, PSC2022 e PSC2023, não foi identificada previsão amazônica explícita. Isso não prova ausência de questões regionais nem que uma questão esteja fora do edital.
- O edital-base PSC2023 E1, p. PDF 18, apresenta mudança expressiva nas seções de História e Geografia em relação aos programas anteriores. Não foi identificada menção amazônica substantiva nessas duas seções. O caso foi conservado; não se inferiu causa curricular nem ausência de cobrança regional nas questões.

As faixas localizadas nos cadernos são História 17–22 e Geografia 23–28 nas etapas 1 e 2; na etapa 3, História 19–24 e Geografia 25–30. A segmentação e sua integridade devem ser verificadas pelo pipeline, incluindo textos compartilhados e imagens. Os cadernos antigos podem começar diretamente nas questões, sem as duas páginas iniciais de instruções presentes nos formatos recentes.

## Retificações e próximos passos

O JSON preserva as retificações e os comunicados encontrados, sem afirmar que todos foram auditados ou que não existam outros. A reabertura das etapas 1 e 2 de PSC2021 é indispensável para a data correta; há também erros editoriais internos na identificação do projeto em partes do documento, que devem ser resolvidos pelo conjunto de fontes.

Próximas verificações: obter corroboração pós-evento das oito datas pendentes; examinar integralmente as retificações; completar etapas 1 e 2 da edição PSC2018 e os conjuntos posteriores ainda candidatos; pesquisar se houve aplicações na lacuna de 2020, sem converter falha de localização em prova de cancelamento. Após aquisição, conferir hashes, páginas, continuidade e versões dos gabaritos antes de calcular qualquer indicador.
