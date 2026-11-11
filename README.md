# História e Geografia da Amazônia nos vestibulares

Banco curado de **196 questões amazônicas**, organizado em **53 tópicos padronizados**, com origem por instituição, prova, edição, fase/etapa, número, página e PDF. A pergunta da análise é: **quanto do conteúdo previsto na ementa realmente apareceu nas provas?**

Leia a [análise exploratória](resultados/relatorio.md) e abra o [dataset limpo](dados/curado/questoes.csv). A comparação considera os tópicos previstos e as questões efetivamente relacionadas a eles; assuntos com nomes diferentes são reconciliados na mesma taxonomia.

Nas **43 provas com ementa regional integral e triagem completa**, houve cobrança identificada em **141 de 682 pares prova × tópico previsto (20,7%)**. A [lista padronizada de conteúdos e tópicos](dados/topicos.csv) orienta tanto a classificação das questões quanto essa comparação.

## Executar

Requer **Python 3.10 ou superior**, sem instalar bibliotecas. Execute na raiz do repositório:

```sh
python3 scripts/limpeza.py
python3 scripts/analise.py
python3 -m unittest discover -s tests -v
```

Os dois primeiros comandos reconstroem o dataset limpo e os resultados a partir dos dados versionados. Funcionam sem internet e sem chamadas de IA. A curadoria semântica já está registrada nos dados brutos.

Para recuperar e conferir os PDFs catalogados, com `curl` instalado:

```sh
python3 scraping/coletar.py

# Opcional: extrair a camada textual dos PDFs; requer pdftotext/Poppler
python3 scraping/coletar.py --extrair
```

Os originais ficam em `acervo/`, fora do Git, e são reaproveitados quando íntegros. O coletor confere SHA-256 antes de aceitar um arquivo. Fontes cujo original não foi recuperado permanecem identificadas como pendentes. A disponibilidade externa dos endereços não é necessária para reproduzir a análise.

## O que cada arquivo faz

| Arquivo | Função |
| --- | --- |
| `scraping/coletar.py` | Um coletor para todos os PDFs do catálogo, com verificação de integridade e extração textual opcional. |
| `scripts/limpeza.py` | Padroniza texto, remove duplicatas exatas e confere IDs, fontes e vínculos; gera o dataset curado. |
| `scripts/analise.py` | Calcula frequências, cobertura da ementa e comparação das fases; gera o relatório e as tabelas. |
| `dados/topicos.csv` | Taxonomia: disciplina → conteúdo → tópico, com definição de cada categoria. |
| `dados/fontes.csv` | Catálogo dos PDFs: endereço de download, publicação institucional, hash e origem oficial ou cópia pública identificada. |
| `dados/provas.csv` | Provas examinadas, inclusive as sem questões elegíveis; anos, fases, extensão da triagem e cobertura das ementas. |
| `dados/ementas.csv` | Redação dos itens previstos, páginas, fontes e correspondência com os tópicos padronizados. |
| `dados/brutos/questoes.jsonl` | Questões selecionadas pelos agentes, antes da padronização final, com decisões de curadoria. |
| `dados/brutos/triagem.csv` | Registro dos itens examinados e da decisão de incluir ou excluir; permite conferir o recorte do banco. |
| `dados/curado/questoes.csv` | Dataset final: uma linha por questão, com texto, alternativas, tópicos, ementa e origem. |
| `resultados/relatorio.md` | Análise exploratória e resposta à pergunta do estudo. |
| `resultados/frequencia-topicos.csv` | Frequência dos tópicos principais, anos, provas e instituições, inclusive categorias sem questões. |
| `resultados/previsto-cobrado.csv` | Quantidade e proporção de tópicos previstos/cobrados em cada prova. |
| `resultados/itens-ementa.csv` | Detalhamento dos itens oficiais, questões associadas e tópicos com ou sem cobrança identificada. |
| `tests/test_estudo.py` | Verifica integridade da limpeza e se o cálculo exige um vínculo pertinente com a ementa. |
| `.gitignore` e `.gitattributes` | Mantêm originais e arquivos temporários fora do Git e padronizam as quebras de linha. |

## Cobertura

Recorte de aplicação: **01/01/2017 a 11/11/2026**, com 2026 parcial.

| Origem | Recorte examinado | Questões amazônicas |
| --- | --- | --- |
| UEA — Vestibular/Macro | Edições 2017–2026, Conhecimentos Gerais e Conhecimentos Específicos de Humanas | 107 |
| UFAM — PSC | Edições 2018–2026, três etapas, aplicadas dentro do recorte | 45 |
| Enem — Inep | Aplicação regular impressa, caderno azul de Humanas, edições 2017–2025 | 17 |
| USP — FUVEST | História e Geografia da segunda fase, edições 2017–2026 | 8 |
| UERR | Vestibulares 2025/2026 | 10 |
| UFRR | Prova Integral 2025/2026 | 9 |

Cada fase/etapa tem seu identificador de prova, dentro do mesmo dataset. Cores e ordenações equivalentes não são multiplicadas. Subitens discursivos ficam na mesma questão.

O levantamento inclui **70 provas**. UEA e PSC formam o núcleo; as outras origens permitem observar a cobrança fora dele. A cobertura não representa todas as instituições e modalidades brasileiras. O Enem 2026 já teve o [primeiro dia aplicado em 08/11/2026](https://www.gov.br/inep/pt-br/centrais-de-conteudo/noticias/enem/participantes-concluem-primeiro-dia-do-enem-2026), mas seu PDF oficial não foi localizado na consulta. O programa UEA 2017 e dois editais PSC 2018 permanecem sem recuperação integral; suas questões continuam no banco e essas provas ficam fora da proporção programática.

## Curadoria e leitura dos dados

A lista de conteúdos parte das ementas. Os agentes selecionaram questões cujo objeto é histórico ou geográfico amazônico, incluindo Amazonas e outras partes da Amazônia. Instituição regional, nome de uma pessoa ou Amazônia em um distrator não bastam. Questões gerais sobre guerras, tratados ou outros assuntos entram somente quando há cobrança amazônica substantiva.

`topico_id` é a classificação principal; `topicos_ids` contém os demais tópicos exigidos. `ementa_itens` aponta os itens da ementa correspondente. Campos com várias referências usam `|`. Os códigos dos itens são internos; a redação original e a página permitem localizar a fonte.

`disciplina`, `conteudo` e `topico` seguem a hierarquia do tópico principal. `disciplina_origem` preserva a identificação registrada na coleta; ela pode diferir da classificação analítica em questões interdisciplinares.

`tipo_vinculo_ementa` distingue **direto**, **amplo** e **não localizado**. Uma questão regional pode estar amparada por uma cláusula geral do edital. Por isso, a proporção principal usa apenas a previsão regional explícita e integralmente levantada; vínculos amplos ficam disponíveis para consulta. Ausência de vínculo não significa questão fora do edital.

`foco_regional` distingue conteúdo central de cobrança regional substantiva em contexto misto. A curadoria foi feita por agentes de IA (Codex), identificada como tal. A reprodução executa as decisões registradas; não depende de anotação manual nem de nova classificação por um modelo.

Os enunciados conservam as alternativas publicadas, inclusive distratores incorretos. Gabarito vazio significa não incorporado; não houve resolução automática para preenchê-lo. Mapas, gráficos e alternativas visuais devem ser consultados no PDF na página indicada. O texto limpo tem hash próprio, distinto do hash do documento.

O repositório anterior foi substituído por esta estrutura. O histórico permanece no Git; notas, protótipos, inventário institucional e módulo de anotação antigos foram preservados em arquivo local externo à pasta ativa.

Autoria do projeto: **Matheus Garcia**, com pesquisa, curadoria e implementação assistidas por Codex.
