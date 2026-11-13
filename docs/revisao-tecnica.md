# Revisão técnica e evidências do projeto

Revisão de 12/11/2026, a partir do commit `ff3c1f3`. Escopo: apresentação pública, reprodução do congelamento 2017–11/11/2026, integridade e evidências de uso de IA. A revisão foi executada com assistência de agentes no Codex; não constitui uma nova anotação humana das questões.

[README](../README.md) · [Relatório analítico](../resultados/relatorio.md) · [Dashboard](https://amazonia.mhvps.site/)

## Resultado da revisão

Não foi encontrado bloqueador da reprodução dos resultados publicados. A contagem permanece em **196 questões**, **70 provas** e **141/682 pares prova × tópico cobrados**, em **43 provas comparáveis**. As correções de engenharia não modificam os dados curados, a taxonomia, os cálculos ou o design do dashboard.

A reprodução computacional é verificável. A qualidade semântica da seleção, das etiquetas e dos vínculos ainda requer avaliação contra uma referência humana. O projeto demonstra uma análise assistida por IA e um produto publicado; não demonstra um classificador validado ou um agente operando no dashboard.

## Achados e tratamento

| Prioridade | Achado demonstrado | Correção ou situação |
| --- | --- | --- |
| Bloqueadores | Nenhum identificado no congelamento publicado. | A execução documentada reconstruiu as saídas. Isso não certifica a correção semântica de todos os registros. |
| Melhoria relevante | `assert` fazia a validação de entrada desaparecer em `python -O`; um hash conflitante era aceito em teste. | [limpeza.py](../scripts/limpeza.py) e [analise.py](../scripts/analise.py) usam `ValueError` explícito. Os testes executam também com `-O`. |
| Melhoria relevante | A limpeza aceitava ID de questão vazio e PDF diferente do cadastrado para a prova, quando URL/hash combinavam com esse outro PDF. | A limpeza exige ID preenchido e a mesma fonte da prova. Casos fictícios protegem ambas as rejeições. Não foram observadas essas falhas no acervo publicado. |
| Melhoria relevante | Com uma questão duplicada, a análise falhava depois de sobrescrever quatro CSVs e deixava o relatório anterior. | IDs, identidade prova/número e reconciliação da triagem passam por validação antes da gravação. O teste confirma que a rejeição da duplicata conserva as saídas anteriores. |
| Melhoria relevante | A cópia incremental para `dist/` conservava assets removidos da origem. | [preparar_dashboard.py](../scripts/preparar_dashboard.py) reconstrói a saída gerada. Um teste remove um asset de origem e confirma sua retirada do build seguinte. |
| Melhoria relevante | O modelo JavaScript não tinha regressões persistentes para os denominadores. | [test_dashboard.mjs](../tests/test_dashboard.mjs) cobre razão global, zero/ausência, filtros, provas sem questões e etiquetas interdisciplinares. |
| Melhoria relevante | A apresentação não separava suficientemente assistência de IA, inferência reproduzível e validação humana. | O README e esta revisão registram o papel da IA, os metadados ausentes e o que não foi medido. |
| Melhoria relevante | As verificações dependiam de execução manual. | [GitHub Actions](../.github/workflows/verificar.yml) executa testes e compara as saídas regeneradas com o Git em pushes e pull requests. |
| Ajuste opcional | Aumentar frameworks, bibliotecas de agentes ou ferramentas de automação. | Não implementado: o dashboard estático e o pipeline atual não exigem essas tecnologias. |

## Verificações executadas

A primeira execução ocorreu em cópia temporária do commit de referência, antes das correções. A repetição após as correções confirmou os mesmos resultados. Nenhuma nova chamada de IA participou da reprodução.

| Verificação | Resultado |
| --- | --- |
| Limpeza → análise → preparação do dashboard | Oito arquivos idênticos byte a byte: CSV curado, relatório, cinco tabelas e JSON do dashboard. |
| Quatro figuras | PNGs idênticos byte a byte e por pixels, com Matplotlib **3.10.8**. |
| Testes Python | **6 testes aprovados**, em execução normal e com `-O`. |
| Testes JavaScript | **4 testes aprovados**. |
| Cobertura independente | **141/682**; História **75/410** e Geografia **66/272**. |
| Auditoria numérica pontual | **70 linhas** de cobertura e **198 linhas** temporais conferidas; **505 recortes** comparados ao modelo JavaScript, sem divergências. |
| Duplicatas no congelamento | **0** IDs, hashes de texto limpo ou pares prova/número repetidos. |
| Sensibilidades | Sem anuladas **138/682**; somente foco central **132/682**; central sem anuladas **129/682**; sem 2026 **131/621**. |

Ambiente local da revisão: **Python 3.14.4**, **Node.js 25.9.0**, **Matplotlib 3.10.8**. O workflow usa Python 3.10 e Node.js 22. Os testes JavaScript fixam expectativas do acervo congelado: uma ampliação deliberada da base exige revisar essas expectativas junto aos resultados.

Para refazer as verificações computacionais:

```sh
python3 -m unittest discover -s tests -v
python3 -O -m unittest discover -s tests -v
node --test tests/test_dashboard.mjs
python3 scripts/limpeza.py
python3 scripts/analise.py
python3 scripts/preparar_dashboard.py
git diff --exit-code -- dados/curado/questoes.csv resultados dashboard/dataset.json
```

As instruções de instalação do Matplotlib e geração das figuras estão no [README](../README.md#reproduzir). As verificações aritméticas não substituem a conferência dos PDFs, do significado dos textos ou da pertinência das classificações.

## Uso de IA e qualidade da curadoria

| Camada | Evidência disponível | Limite da evidência |
| --- | --- | --- |
| Desenvolvimento assistido | Código Python/JavaScript, histórico Git, assistência declarada do Codex e prompts dos assets no [README da interface](../dashboard/README.md). | Os prompts visuais não documentam os prompts de classificação das questões. |
| Seleção e classificação | Os **196 registros** em [questoes.jsonl](../dados/brutos/questoes.jsonl) têm `curadoria=IA (Codex)`, justificativa, fonte, hash e páginas; [triagem.csv](../dados/brutos/triagem.csv) registra inclusão/exclusão de **1.401 itens**. | As decisões estão congeladas; os scripts não refazem a inferência que as produziu. |
| Extração | Todos os registros apontam para o PDF; **64** conservam também `texto_extraido_original` e `tratamento_texto`. | **132** não conservam esses dois campos. Não há extração textual integral versionada para todo o banco. |
| Modelo e execução | A ferramenta está identificada como Codex. | Modelo exato, versão, prompts analíticos por execução, parâmetros, tokens, duração e custo não foram registrados. Não é possível reconstruí-los com confiança retroativamente. |
| Revisão humana | Matheus foi indicado como anotador previsto no registro histórico. | Não há anotações humanas preenchidas ou conjunto de referência validado na evidência examinada. |
| Avaliação | Testes estruturais, reconciliação de totais, reprodução e casos semânticos sinalizados. | Precisão, recall, F1, concordância entre anotadores e taxa de erro da IA **não medidos**. |
| Impacto | Dashboard público, arquivos acessíveis e comandos verificáveis. | Uso por estudantes, aprendizagem, horas economizadas e retorno financeiro **não medidos**. |

O planejamento histórico de anotação pode ser consultado com `git show 3f044af^:data/annotation/configuracao.json`. Ele registra a anotação como ainda não recebida. A planilha histórica tinha 312 candidatos da fase anterior, com campos humanos vazios; ela não é uma validação do banco atual de 196 questões.

Não foram criados prompts retroativos nem resultados de avaliação para preencher essas lacunas. Em uma futura rodada, registrar modelo, prompt, saída, fonte e revisão por item permitiria comparar versões. Para medir a qualidade do banco congelado, é necessária uma avaliação contra referência humana, sem exigir nova inferência. Registrar esses metadados permitiria reproduzir futuras classificações; os agregados atuais já são reproduzíveis.

## Coerência analítica e Novo Ensino Médio

O denominador principal conta tópicos regionais explícitos **por prova comparável**, com repetição interna removida. O numerador exige vínculo ao item pertinente e interseção de etiquetas. Assim, 141/682 não é a fração de tópicos únicos do catálogo, a média simples por prova, a extensão do programa ou uma previsão da próxima prova.

A série usa ano de aplicação, preserva fases/etapas e mantém provas sem questões elegíveis. Ausência de programa comparável é diferente de cobertura zero. Edições, atrasos de calendário, formatos e cobertura documental impedem tratar todos os processos como amostras equivalentes.

Os cortes do Novo Ensino Médio são contextuais. O relatório distingue cronograma normativo, implementação escolar, matriz de exame e trajetória de candidatos. A primeira fase UEA passa de **19/96** para **26/72** entre 2017–2021 e 2024–2026; a segunda passa de **23/96** para **15/72**. Sem 2026, a segunda fica em **12/48**, e a aparência de queda desaparece. Isso sustenta uma descrição por estrato, não uma conclusão causal sobre a reforma.

Os marcos foram conferidos nas fontes primárias ligadas na [seção temporal](../resultados/relatorio.md#5-o-que-mudou-no-tempo-em-torno-do-novo-ensino-médio): Portaria MEC 521/2021, art. 4º; Lei 14.945/2024, art. 5º, II; DCNEM 2/2024, arts. 39 e 42; Edital Enem 52/2025, item 3.1. Sem respostas de candidatos ou medida de demanda cognitiva, a base não permite concluir que as provas ficaram mais difíceis.

## Correspondência com a vaga

Referência consultada em 12/11/2026: [Programa de Estágio GenAI — iFood, anúncio oficial](https://job-boards.greenhouse.io/ifoodcarreiras/jobs/8901054002). O anúncio apresenta **AI Engineer** e **AI Builder**. A leitura abaixo prioriza AI Builder e descreve este projeto, sem presumir outras experiências do autor.

| Competência relevante | Evidência do projeto | Situação |
| --- | --- | --- |
| Construção de uma solução e dashboard funcional | [Interface](../dashboard/), [hospedagem](../.openai/hosting.json), filtros, fontes, exportação CSV e [produto publicado](https://amazonia.mhvps.site/). | **Demonstrada**: entrega acessível com dados, cálculo e navegação. Adoção por usuários não medida. |
| Análise de dados com IA | Curadoria declarada nos [registros brutos](../dados/brutos/questoes.jsonl), normalização, [análise](../scripts/analise.py), sensibilidades e relatório. | **Demonstrada com limites**: assistência de IA e resultados reproduzíveis; qualidade semântica ainda não medida. |
| Desenvolvimento assistido por IA | Python e JavaScript implementados com assistência do Codex; histórico e documentação das decisões. | **Demonstrada como processo declarado**; não implica treinamento ou integração de LLM no produto. |
| Automação de processo | [Coletor](../scraping/coletar.py), limpeza, geração de tabelas/JSON e [verificação contínua](../.github/workflows/verificar.yml). | **Demonstrada para tarefas determinísticas**. Não há uso de n8n/Make/Zapier nem economia de horas medida. |
| Prompt engineering avançado e orquestração de agentes | Há atribuição da curadoria a agentes e prompts de assets. | **Evidência insuficiente** de experimentos analíticos controlados ou de um orquestrador reproduzível. |
| Desenvolvimento de APIs e integração de IA | O navegador lê `dataset.json`; não há backend ou serviço de inferência. | **Fora do escopo implementado**. Publicar JSON estático não demonstra desenvolvimento de uma API de IA. |
| Resultado de negócio mensurável | Banco, indicadores e dashboard verificáveis. | **Evidência insuficiente** de benefício para usuários; contagens do acervo não medem impacto. |
| Engenharia de modelos/LLMs, relacionada a AI Engineer | Código testado e pipeline de dados. | **Parcial para software; fora do escopo para modelos**: não há treinamento, fine-tuning, avaliação de LLM ou serviço de inferência. |

A candidatura pode apoiar-se na entrega de ponta a ponta e na capacidade de delimitar o que foi verificado. Adicionar uma tecnologia apenas para reproduzir palavras do anúncio não melhora essa evidência.

## Pendências reais, por importância

1. **Validar a curadoria semântica.** Revisar inclusão/exclusão, taxonomia e vínculos contra uma referência humana documentada. Começar pelos casos conhecidos abaixo não produz, sozinho, uma estimativa imparcial de acurácia; uma avaliação da qualidade requer também amostragem definida, incluindo exclusões.
2. **Resolver as divergências registradas, com histórico da decisão.** `uea-2026-ce-q05` associa Pará/1823 a um item adicional sobre o Segundo Reinado; esse vínculo é inadequado. Sua retirada simulada não altera **141/682** nem **0/14**, por ter escopo geral. Outros **12 itens regionais, em 13 relações questão–item**, têm vínculo sem etiqueta compartilhada: explicam **240/849** por vínculo versus **228/849** com interseção. Isso não é uma taxa de erro da IA. Os dados foram preservados; o [relatório](../resultados/relatorio.md#6-robustez-e-conferência-dos-indicadores) e [itens-ementa.csv](../resultados/itens-ementa.csv) permitem a revisão dirigida.
3. **Completar lacunas documentais antes de ampliar alegações.** Programas UEA 2017 e PSC 2018 E1/E2 pendentes; **16 questões** sem item localizado; **149/151 referências** com hash. Um documento pode atender mais de uma prova, portanto referências pendentes e programas pendentes não têm a mesma contagem. A janela de 2026 permanece parcial.
4. **Completar os dados necessários a correção automática, se essa função for construída.** Há **129 gabaritos vazios**, incluindo oito discursivos, e **111 questões com recurso visual**. Uma objetiva apresenta alternativas como climogramas no PDF (`uea2017-geral-q28`); não são alternativas textuais perdidas silenciosamente. Há também **111 questões sem data diária**, com ano de aplicação preservado.
5. **Medir impacto apenas quando houver uso.** Definir tarefa e linha de base antes de alegar economia de tempo ou melhora educacional. Não é pendência para publicar esta análise descritiva, mas limita as afirmações sobre resultado de negócio.

Não há bloqueador de código remanescente identificado nesta revisão. As pendências de curadoria impedem tratar o banco como referência validada para avaliação automática de IA ou correção de estudantes.

## Apresentação para o portfólio

> Desenvolvi, com assistência do Codex, um projeto de análise de História e Geografia da Amazônia em vestibulares públicos. O repositório reúne 196 questões rastreáveis às fontes, um pipeline reproduzível em Python e um dashboard publicado em JavaScript. Nas 43 provas com programas comparáveis, identifiquei cobrança de 141 dos 682 pares prova × tópico previstos. Documentei os limites da curadoria por IA, as lacunas e as comparações temporais, sem atribuir causalidade ao Novo Ensino Médio ou medir dificuldade sem dados de candidatos.

## Perguntas técnicas para o autor

- Por que o denominador é 682 pares prova × tópico, e não 53 tópicos? Em que difere da média dos percentuais por prova?
- Como uma prova pode ter três questões e cobertura regional explícita de 0/14?
- O que a limpeza faz e quais decisões semânticas ela não refaz? Onde está a origem de uma questão?
- Por que 92 questões com História e 129 com Geografia não somam o tamanho do banco?
- Como você distingue zero observado, programa ausente e ausência de aplicação em um ano?
- Por que comparar os mesmos estratos e retirar 2026 muda a leitura temporal? O que faltaria para estudar dificuldade ou efeito curricular?
- O que o hash de um PDF garante? Por que ele não garante que a classificação está correta?
- Quais decisões você tomou, quais tarefas delegou ao Codex e como revisaria um erro sem apagar sua proveniência?
- Como montaria uma referência humana e uma avaliação que incluísse tanto questões selecionadas quanto excluídas?
- Que necessidade justificaria colocar um modelo de IA, uma API ou uma ferramenta de agentes em execução neste produto?
