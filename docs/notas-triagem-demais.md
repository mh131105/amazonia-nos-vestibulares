# Triagem documental inicial: UEA, UFRR, UERR e instituições fora do Norte

Consulta em **11/11/2026**. Responsável: Codex, com revisão humana pendente. Este registro aplica o mesmo procedimento a História e Geografia; a disciplina é um campo da evidência e dos futuros indicadores.

Os dados estruturados estão em [triagem_demais.json](../data/registry/triagem_demais.json). São nove processos candidatos, em seis instituições principais, além da UEMASUL, atendida pelo mesmo PAES da UEMA. Nenhum foi promovido a recorrência confirmada nesta triagem: localizar uma edição ou duas não cumpre o limiar principal de três anos distintos de aplicação.

## Evidências utilizáveis e pendências

| Instituição e processo | Evidência examinada | Resultado da triagem inicial |
| --- | --- | --- |
| UFRR — Prova Integral | Manuais das edições 2025 e 2026, cadernos e gabaritos oficiais | Previsão substantiva de História e Geografia amazônicas em aplicações de 2024 e 2025. Falta um terceiro ano para a regra principal. |
| UFRR — PSS | Mesmos manuais, com conteúdo organizado por E1, E2 e E3 | Manter etapas separadas. Não transportar História regional de E2 para E1. |
| UFRR — Vestibular Indígena/PSEI | Notícia institucional com links para edital e manual | Processo especial identificado; leitura dos documentos e regularidade ainda pendentes. |
| UEA — SIS | Anexo II do SIS 2020 ligado pelo próprio índice institucional | Programa regional confirmado; a aplicação mudou de data durante a pandemia e exige confirmação posterior ao evento. |
| UEA — Vestibular | Edital 044/2024 e portal da Vunesp | Anexo II incorporado, mas a versão oficial do programa ainda precisa ser localizada. A rota de provas da edição 2024 requer login. |
| UERR — Vestibular presencial | Edital 41/2022, programa e gabarito definitivo | História e Geografia amazônicas previstas. Edição chamada 2023 foi aplicada em 23/10/2022. Caderno publicado retorna HTTP 403 nesta consulta. |
| UEMA — PAES | Edital 57/2025, programa e índice histórico oficial | Conteúdo de Brasil/Maranhão nesta edição não confirma, sozinho, previsão amazônica substantiva. Não extrapolar a toda a década. |
| UNEMAT — Vestibular com prova | Notícia institucional e portal indicado pela universidade | Portal em ciclo de redirecionamento. Anexo candidato localizado, mas sua incorporação oficial e regionalidade continuam pendentes. |
| UEPG — Vestibular | Programa oficial de 2024, incorporado pelo manual | Temas nacionais e regionalização ampla; não foi confirmado tópico amazônico específico nesta edição. Isso não mede a presença nas questões. |

UEMA (MA), UNEMAT (MT) e UEPG (PR) foram examinadas para evitar restringir a busca à Região Norte. São apenas três pontos de partida fora do Norte, não prova de completude nacional. Localização institucional, Amazônia Legal e história regional não são critérios intercambiáveis.

## Datas e denominadores que exigem atenção

A edição **UFRR 2025** foi aplicada em **24/11/2024**. O item 8.1 do [manual](https://editais.ufrr.br/editais/arquivo/322/manual-do-candidato-2025.pdf), página 13 do PDF, traz a data. A [publicação dos cadernos](https://ufrr.br/noticias/cpv-ufrr-divulga-gabarito-preliminar-e-tambem-os-cadernos-de-prova-do-vestibular-2025/) ocorreu no mesmo dia. O programa histórico regional está na página 32 do PDF; o programa geográfico amazônico está na página 28.

A edição **UFRR 2026** foi aplicada em **30/11/2025**, conforme o cronograma do [manual](https://editais.ufrr.br/editais/arquivo/951/manual-do-candidato-vestibular-ufrr-2026.pdf) e a [publicação institucional dos cadernos](https://ufrr.br/noticias/cpv-ufrr-divulga-cadernos-de-prova-e-gabarito-preliminar-da-prova-objetiva-do-vestibular-2026/). O programa geográfico regional está na página 31 do PDF e o histórico regional nas páginas 34–35. Páginas físicas do PDF e números impressos diferem; o JSON registra a convenção.

Na UFRR, PI e PSS-E3 compartilham caderno. O manual 2026, itens 7.1.4 e 7.3, página 14 do PDF, estabelece que o PSS pontua apenas as três últimas questões de cada disciplina; o candidato recebe nove questões por disciplina e pode concorrer também pela PI. Conservar o conjunto apresentado e o subconjunto pontuado em campos separados. O mesmo item físico não deve inflar o total agregado por estar vinculado a duas modalidades.

Na UERR, o [gabarito definitivo](https://cpc.uerr.edu.br/wp-content/uploads/2022/11/Gab_DEFINITIVO_Matriz_741_VEST_UERR_001.pdf) informa a aplicação em 23/10/2022. O programa substantivo aparece na página 10 do [edital](https://www.uerr.edu.br/wp-content/uploads/2022/08/SEI_GRR-5728859-Edital.pdf), nas seções 7 e 8. O lema amazônico nos cabeçalhos foi desconsiderado como evidência curricular. Há anulações oficiais, a preservar no tratamento dos itens.

O índice oficial do [PAES/UEMA](https://dados.uema.br/editais-do-paes-uema/) distingue aplicação e ingresso: PAES 2026 corresponde à aplicação em 30/11/2025. UEMA e UEMASUL compartilham esse processo nesta edição; o mesmo caderno não representa duas aplicações independentes.

## Acesso e autenticidade

- Na UEA, o [índice do SIS 2020](https://selecao1.uea.edu.br/?dest=info&selecao=3021) liga diretamente o [Anexo II](https://selecao1.uea.edu.br/xfiles/data/xselecao/6740.pdf). O edital inicial previa janeiro de 2021; um comunicado em compêndio oficial informa novo calendário para junho de 2021. O último calendário localizado é uma previsão, não confirmação suficiente da data efetiva. A edição permanece sem data efetiva no JSON.
- As rotas “Provas e Gabaritos” dos portais Vunesp [UEAM2401](https://www.vunesp.com.br/UEAM2401) e [UEAM2402](https://www.vunesp.com.br/UEAM2402) redirecionam para identificação do candidato. Não houve autenticação nem tentativa de contornar esse controle.
- Na UERR, o índice publica um caderno cuja rota antiga contém `/wpadmin/wp-content/`. A abertura retorna 403; o caminho `/wp-content/` também foi verificado e retornou 403 para o caderno. A localização documental foi registrada, mas o arquivo não foi declarado coletado.
- A [notícia da UNEMAT](https://unemat.br/noticias/5-11-2025-unemat-divulga-locais-de-realizacao-das-provas-do-vestibular) aponta para o Portal do Candidato. A abertura desse portal retorna ciclo de redirecionamento. O PDF candidato encontrado no armazenamento do portal não foi contado como documento oficial autenticado: falta verificar seu vínculo com o edital aplicável. Conteúdo sobre Mato Grosso, por si só, não resolve sua regionalidade amazônica.
- Os PDFs foram inspecionados por extração indexada com localização por página. Essa inspeção identifica programa e fontes; não constitui revisão humana de questões nem certificação visual de toda a extração.

## Verificações e continuidade

Foram conferidos IDs únicos e referências entre fontes, evidências e processos no JSON. As datas desconhecidas permanecem nulas; previsões têm campos separados. Aberturas malsucedidas não foram convertidas em evidência de ausência de documentos ou conteúdo.

Próxima ação: coletar pelo pipeline os conjuntos oficiais completos da UFRR, registrar hashes e integridade, localizar um terceiro programa aplicável e recuperar as aplicações antigas. Em paralelo, verificar Anexo II do vestibular UEA, confirmar o calendário final do SIS 2020 e completar a autenticação documental da UNEMAT. A confirmação de três anos em um processo deverá gerar coleta de todas as aplicações da década, não apenas das edições com menções regionais.
