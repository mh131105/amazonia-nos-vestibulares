# UFMS — modalidades e versões, ciclo 4

Consulta em 11/11/2026. O [registro estruturado](../data/registry/expansao-ufms-c4.json) preserva os três IDs do ciclo 3, com seis variantes documentais e 15 documentos públicos indicados para coleta. Não foram alterados os cadastros canônicos, scripts ou a recorrência integrada registrada no ciclo 3.

## Eventos preservados e estrutura comprovada

| ID de evento C3 | Aplicação efetiva | Presencial | Digital on-line |
| --- | --- | --- | --- |
| `ufms-vestibular2024-unica` | 03/12/2023 | 60 questões; 15 de Humanas; caderno publicado com Humanas Q46–60, pp. 17–20 | 50 questões; 10 de Humanas; base pública `UFMS2301 / 001-ConhecGerais`; números do bloco Humanas ainda não confirmados |
| `ufms-vestibular2025-unica` | 01/12/2024 | 60 questões; 15 de Humanas; Humanas Q46–60, pp. 16–19 | 60 questões; 15 de Humanas; base pública `UFMS2401 / 001-ConhecGerais`; números do bloco Humanas ainda não confirmados |
| `ufms-vestibular2026-unica` | 07/12/2025 | 60 questões; 15 de Humanas; Humanas Q46–60, pp. 19–22 | 60 questões; 15 de Humanas; base pública no Anexo III do definitivo; Humanas Q46–60, pp. 23–28 do PDF do edital |

As quantidades são oficiais: [edital 283/2023, p. 9, item 11.1](https://ingresso.ufms.br/files/2023/09/edital_prograd_2023_283_CONSOLIDADO.pdf), [edital digital 284/2023, p. 9, item 11.1](https://ingresso.ufms.br/files/2023/08/edital_prograd_2023_284_CONSOLIDADO-1.pdf), [edital 303/2024, pp. 12–14, item 12.1](https://ingresso.ufms.br/files/2024/10/edital_prograd_2024_303_1_consolidado.pdf) e [edital 394/2025 consolidado, p. 10, item 12.1](https://ingresso.ufms.br/files/2026/01/edital_prograd_394_consolidado_2.pdf). As datas efetivas já confirmadas no ciclo 3 são corroboradas pelos atos de gabarito.

Em 2024, há atos formalmente distintos: PSV-UFMS para o presencial e PSVD-UFMS para o digital. Em 2025 e 2026, o edital do PSV regula os dois formatos. Os IDs existentes foram mantidos como eventos de referência; a continuidade histórica entre esses desenhos não foi presumida.

As capas presenciais indicam manhã e início às 08h. Para o digital, os editais estabelecem 08h–13h no horário de Mato Grosso do Sul, com primeira parte de Linguagens/Humanas até 10h, intervalo de 15 minutos e segunda parte a partir de 10h15. O campo de rótulo de turno digital permanece nulo; os horários estão explícitos. Cor e tipo presencial não foram identificados: o nome `PB` no arquivo de 2024 não foi convertido em cor ou código de versão.

## Cadernos e gabaritos públicos

Os cadernos presenciais das três edições estão vinculados na seção “Provas Aplicadas” do [portal institucional](https://ingresso.ufms.br/vestibular/). Foram conferidas cópias temporárias obtidas no ciclo 3, com hashes de referência registrados no JSON; isso não equivale a uma nova coleta binária neste ciclo.

| Ato definitivo | Conteúdo e localização física |
| --- | --- |
| [415/2023 — presencial 2024](https://ingresso.ufms.br/files/2023/12/edital_prograd_415.pdf) | Anexo Único, p. 3: gabarito presencial. Asterisco significa questão anulada. |
| [417/2023 — digital 2024](https://ingresso.ufms.br/files/2023/12/edital_prograd_417.pdf) | Anexo I, pp. 3–65: prova-base com redação e anexos do caderno. Anexo II, p. 66: gabarito dos 50 números. Item 1.1 declara que o preliminar não mudou. |
| [8/2025 — ambas as modalidades de 2025](https://ingresso.ufms.br/files/2025/01/edital_prograd_2025_8_1.pdf) | Anexo I, p. 3: presencial. Anexo II, p. 4: digital. Anexo III, pp. 5–73: prova-base digital e redação. |
| [518/2025 — ambas as modalidades de 2026](https://ingresso.ufms.br/files/2025/12/edital_prograd_518.pdf) | Anexo I, p. 3: presencial. Anexo II, p. 4: digital. Anexo III, pp. 5–32: prova-base digital e redação. |

Os preliminares [389/2023](https://ingresso.ufms.br/files/2023/12/edital_prograd_2023_389.pdf), [390/2023](https://ingresso.ufms.br/files/2023/12/edital_prograd_2023_390.pdf), [375/2024](https://ingresso.ufms.br/files/2024/12/edital_prograd_375.pdf) e [500/2025](https://ingresso.ufms.br/files/2025/12/edital_prograd_500.pdf) também constam em `documentos[]` para rastrear versões. Um item reaparecer no preliminar e no definitivo não representa duas ocorrências aplicadas.

As bases digitais resolvem o acesso público ao material sem buscar prova individual. A rota “Provas e Gabaritos” da [Vunesp UFMS2301](https://www.vunesp.com.br/UFMS2301) redireciona para login; o PDF 417/2023, publicado pela própria UFMS, oferece a base e a chave pública. Os atos digitais informam ordem aleatória de questões e alternativas por candidato: [390/2023, item 1.1](https://ingresso.ufms.br/files/2023/12/edital_prograd_2023_390.pdf), [8/2025, item 1.2.1](https://ingresso.ufms.br/files/2025/01/edital_prograd_2025_8_1.pdf) e [518/2025, item 1.2.1](https://ingresso.ufms.br/files/2025/12/edital_prograd_518.pdf). A numeração do acervo deve ser a da base publicada, sem fingir que corresponde à posição individual sorteada.

## Decisão de segmentação

- Os três presenciais e a base digital de 2026 permitem localizar Q46–60 pelo cabeçalho oficial de Humanas e pela numeração. Essa é uma unidade integrada. Em 2026, as tabelas dos dois gabaritos também nomeiam conjuntamente Geografia, Filosofia, História e Sociologia.
- Nos presenciais de 2024 e 2025, os gabaritos distinguem um rótulo de Geografia e outro de Filosofia/História/Sociologia. A fronteira exata entre células deverá ser conferida visualmente depois da coleta dos PDFs. Nenhum conjunto foi convertido em História exclusiva ou classificado por assunto.
- Nas bases digitais de 2024 e 2025, a quantidade de Humanas é conhecida, mas o mapa oficial de números não foi localizado nas fontes examinadas. Os arquivos integrais podem ser coletados; a segmentação disciplinar automática permanece pendente. Não foi usada a sequência aparentemente temática das perguntas para atribuir disciplina.
- As páginas indicadas são janelas de busca. Em particular, a p. 17 do presencial 2024 contém o fim da área anterior antes de começar Q46; a p. 23 do PDF definitivo 2026 também contém questões anteriores à Q46. Recortar pelos números e cabeçalhos, não rotular a página inteira como Humanas.
- Os arquivos apresentam Espanhol e Inglês como alternativas de língua estrangeira: Q1–5 nos presenciais e na base digital 2026, Q11–15 nas bases digitais 2024/2025. Preservar os ramos de idioma sem duplicar o bloco comum de Humanas nem aumentar o total de questões respondidas por candidato.

## Contrato de integração C4

O JSON informa `etapa=objetiva_redacao`, situação documental, data prevista nula e `evidencia_data` para cada evento. A natureza temporal é `noticia_pos_aplicacao`, conferida nas fontes do ciclo 3 e na constante `REALIZACAO` do integrador; as datas efetivas continuam as mesmas. Os gabaritos pós-aplicação aparecem como fontes corroborantes, com suas páginas e natureza próprias. `fonte_landing`, banca, formato e `estrutura` tornam explícita a estrutura oficial sem alterar os seis registros de variantes ou seus mapas disciplinares.

Os 15 documentos continuam no topo de `documentos[]`, associados aos três IDs existentes. `origem_documentada` conserva a página oficial e o critério do vínculo. Os campos compatíveis `bases_digitais` e `sha256_auditado` foram acrescentados como correspondentes de `bases_digital` e `sha256_esperado`, preservados para rastreio. Há três hashes auditados, apenas dos cadernos presenciais cujas cópias temporárias já existiam e tiveram seus bytes reconferidos; os PDFs novos continuam sem hash. Essa compatibilidade de schema não constitui coleta nova, revisão humana, validação de denominadores ou equivalência entre modalidades.

## Cautelas para coleta e revisão

O definitivo de 2025 conserva cabeçalhos de “PRELIMINAR/375/2024” juntamente com os de “DEFINITIVO/8/2025” nos anexos. O registro conserva o ato e aponta essa inconsistência; a correspondência final entre base e chave deve passar por revisão. As anulações transcritas do gabarito presencial são Q24, Q32, Q41, Q53 e Q57 em 2024; Q20 em 2025; Q16 em 2026. A transcrição continua pendente de revisão humana e não elimina esses itens do inventário temático.

A camada textual do caderno presencial de 2024 perde caracteres e alguns números. Renderizações locais confirmaram capa, fim de Q60 na p. 20 e início da redação na p. 21. A extração exige conferência visual e, se necessário, OCR seletivo; número ausente na extração não significa questão inexistente.

A página de abertura de 2026 atualmente vincula o consolidado em `files/2026/01/edital_prograd_394_consolidado_2.pdf`. A rota antiga em `files/2025/09/Edital_Prograd_394_2025_CONSOLIDADO.pdf` retornou 404 e ficou fora da fila de coleta. O consolidado consultado é posterior à aplicação; quantidades e formatos são corroborados pelos documentos efetivamente aplicados e pelos gabaritos.

Os PDFs novos foram lidos pelo indexador web. As tentativas de download binário local neste ciclo falharam por timeout de conexão TCP/443 ao domínio da UFMS; não foram inventados hashes nem declarada preservação desses arquivos. `documentos[]` fornece URLs diretas, vínculo com as páginas oficiais, tipo e páginas de cada papel para a coleta reprodutível pelo agente principal.

O edital de recursos 7/2025 contém lista nominal de candidatos. Sua existência foi registrada como fonte auxiliar com coleta desaconselhada; não integra `documentos[]`. Nenhuma lista pessoal foi gravada no projeto. Esta etapa prepara acervo e estrutura oficial, sem anotação humana de regionalidade ou equivalência entre as duas modalidades.

## Integração posterior da coleta

O coletor central recuperou os quinze documentos indicados sem falhas. As três cópias presenciais já inspecionadas foram preservadas por hash, com evento de aquisição que distingue preservação local de publicação. A limitação de download da pesquisa inicial foi superada; permanecem as lacunas de versão, mapa disciplinar, continuidade dos processos e revisão humana descritas acima. Nenhuma variante digital foi multiplicada como nova aplicação.
