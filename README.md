# História e Geografia da Amazônia nos vestibulares

Banco curado de **196 questões amazônicas**, organizado em **53 tópicos padronizados**, com origem por instituição, prova, edição, fase/etapa, número, página e PDF. A pergunta da análise é: **quanto do conteúdo previsto na ementa realmente apareceu nas provas?**

Leia a [análise exploratória](resultados/relatorio.md) e abra o [dataset limpo](dados/curado/questoes.csv). A comparação considera os tópicos previstos e as questões efetivamente relacionadas a eles; assuntos com nomes diferentes são reconciliados na mesma taxonomia.

Nas **43 provas com ementa regional integral e triagem completa**, houve cobrança identificada em **141 de 682 pares prova × tópico previsto (20,7%)**. A [lista padronizada de conteúdos e tópicos](dados/topicos.csv) orienta tanto a classificação das questões quanto essa comparação.

Os cinco tópicos principais mais frequentes reúnem **58 das 196 questões (29,6%)**. Há **25 questões com tópicos de História e Geografia combinados**, sem duplicação no total. Na comparação de calendário 2017–2021 versus 2024–2026, a participação regional na UEA sobe **16,32 pontos percentuais na primeira fase** e cai **3,13 pontos na segunda**. As diferenças variam com a fase, a janela e a ementa; não identificam efeito causal do Novo Ensino Médio.

![Cobertura da ementa nas provas comparáveis](resultados/figuras/cobertura-ementa.png)

Cada ponto representa uma prova; o losango resume os totais da origem. Fonte: [previsto-cobrado.csv](resultados/previsto-cobrado.csv), aplicações 2017–11/11/2026. O relatório apresenta outras três figuras, os denominadores, sensibilidades e ressalvas.

## Executar

Para limpeza e cálculos, requer **Python 3.10 ou superior**, com a biblioteca padrão. Execute na raiz do repositório:

```sh
python3 scripts/limpeza.py
python3 scripts/analise.py
python3 -m unittest discover -s tests -v
```

Os dois primeiros comandos reconstroem o dataset limpo e os resultados a partir dos dados versionados. Funcionam sem internet e sem chamadas de IA. A curadoria semântica já está registrada nos dados brutos.

Para reproduzir também as quatro figuras estáticas, instale a dependência gráfica:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/figuras.py
```

O cálculo tabular continua usando apenas a biblioteca padrão. `scripts/analise.py` e `scripts/figuras.py` leem a base curada sem modificá-la; as figuras são entregues em PNG, sem dashboard.

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
| `scripts/analise.py` | Calcula frequências, cobertura, fases, comparação temporal e sensibilidades; gera o relatório e as cinco tabelas. |
| `scripts/figuras.py` | Lê as tabelas e gera as quatro figuras estáticas do relatório. |
| `requirements.txt` | Fixa a versão de Matplotlib, necessária somente para gerar figuras. |
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
| `resultados/temporal.csv` | Série anual, períodos de calendário, sete estratos comuns e sensibilidades, com IDs das provas e denominadores. |
| `resultados/sensibilidade.csv` | Recalcula a cobertura retirando anulações conhecidas, questões de foco misto ou 2026, sem editar a base. |
| `resultados/figuras/` | Quatro PNG: cobertura da ementa, tópicos recorrentes, série UEA e contraste temporal por etapa. |
| `tests/test_estudo.py` | Verifica integridade, pertinência do vínculo, lacunas versus zeros e preservação das etapas na comparação temporal. |
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

## Plano temporal e leitura dos indicadores

As faixas de calendário são **2017–2021**, **2022–2023**, **2024** e **2025–2026**. O contraste compara a primeira faixa com 2024–2026, por instituição × processo × etapa presentes nos dois lados. A transição 2022–2023 fica fora desse contraste. A sensibilidade sem 2026 usa 2024–2025. A série usa `ano_aplicacao`, preservando as edições deslocadas pela pandemia.

Os marcos do Novo Ensino Médio contextualizam essas faixas; suas fontes oficiais e regras de transição estão no relatório. Não há observação do currículo individual dos candidatos. A comparação é descritiva, com mudanças de ementa, composição e calendário explicitadas. A sensibilidade dos quatro tópicos comuns UEA resulta em **4/24 pares cobrados (16,7%) nos dois períodos**.

| Campo em `temporal.csv` | Significado |
| --- | --- |
| `nivel`, `instituicao`, `processo`, `etapa` | Estrato literal, painel dos mesmos sete estratos ou acervo inteiro. FUVEST dia 2 e dia 3 permanecem distintos. |
| `tipo`, `janela`, `inicio`, `fim` | Ano, período ou corte seriado; limites em anos de aplicação. Cortes PSC são aproximações de calendário, sem atribuição curricular. |
| `provas`, `provas_ids` | Quantidade e identificadores das provas que formam cada agregado. |
| `questoes_amazonicas`, `questoes_triadas`, `incidencia_percentual` | Questões regionais / itens do bloco examinado. O bloco é H/G ou Humanas, conforme a origem. |
| `provas_com_ementa_completa`, `topicos_previstos`, `topicos_cobrados`, `cobertura_percentual` | Subconjunto com triagem e programa regional integrais; cobertura por pares prova × tópico explícito. |
| `media_provas_percentual`, `media_estratos_percentual` | Incidência com peso igual por prova ou por estrato comum; diferem da razão global dos totais. |
| `diferenca_incidencia_pp_referencia`, `diferenca_cobertura_pp_referencia` | Diferença em pontos percentuais em relação a 2017–2021 no mesmo grupo. |

Proporção vazia significa denominador indisponível; zero exige um universo observado. As taxas são calculadas antes do arredondamento. `sensibilidade.csv` informa o universo de cada cenário: retirar questões mantém os programas originais, enquanto retirar 2026 também muda o conjunto de provas.

A conferência complementar confirmou 141/682 e registrou uma ressalva sem impacto nessa razão: um vínculo geral adicional de UEA 2026 Q05 a “2º Reinado” não corresponde ao objeto Pará/1823. O relatório identifica questão, item e página para revisão. As bases curadas foram preservadas.

O repositório anterior foi substituído por esta estrutura. O histórico permanece no Git; notas, protótipos, inventário institucional e módulo de anotação antigos foram preservados em arquivo local externo à pasta ativa.

O protocolo e o dicionário anteriores podem ser consultados no Git com `git show 3f044af^:docs/protocolo.md` e `git show 3f044af^:docs/dicionario-dados.md`. As regras e os campos atuais estão documentados acima e no relatório.

Autoria do projeto: **Matheus Garcia**, com pesquisa, curadoria e implementação assistidas por Codex.
