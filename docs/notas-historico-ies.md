# Inventário institucional histórico — 2017–2024

Em 11/11/2026, foram obtidos e validados os cadastros institucionais oficiais dos oito anos de **2017 a 2024**. O histórico contém **2.459 registros instituição/ano** e **334 códigos Inep distintos**, incluindo instituições explicitamente públicas e casos de categoria Especial mantidos como candidatos. São **331 códigos com natureza pública indicada pelo cadastro em pelo menos um ano** e **três códigos observados somente como Especial sem campo de rede**, cuja natureza permanece pendente.

Não se trata de 334 vestibulares elegíveis nem de 334 instituições com cobrança amazônica. O objetivo desta etapa é formar a fila nacional histórica para investigar processos próprios, sem limitar o estudo à situação institucional de 2024.

## Fonte e regra por ano

A [página oficial de microdados do Inep](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-da-educacao-superior) lista os pacotes anuais e informa atualizações das versões disponibilizadas. `data/registry/fontes_inventario_historico.json` preserva a versão efetivamente coletada: URLs, data de aquisição, membro do ZIP, tamanho, SHA-256, CRC e MD5 oficial do cadastro.

Os cadastros IES de **2017–2022 não contêm `TP_REDE`**. O termo aparece no dicionário geral desses pacotes, mas na planilha de cursos; sua presença global não permite inventar uma coluna na tabela de instituições. O procedimento histórico verifica a planilha **`cadastro_ies`**, sua linha de definição e o cabeçalho real do CSV.

- **2017–2022:** selecionar `TP_CATEGORIA_ADMINISTRATIVA` em 1, 2 e 3, explicitamente públicas no dicionário. Conservar também 7, Especial, como candidata com natureza e esfera a verificar. Para essas linhas, `rede_codigo` fica vazio; `rede=publica_por_categoria` para 1/2/3 ou `especial_a_verificar` para 7. Não foi fabricado `TP_REDE=1`.
- **2023–2024:** selecionar o campo efetivamente presente `TP_REDE=1`, preservando a categoria administrativa original, inclusive Especial. A esfera das Especiais continua a verificar.
- Não filtrar por região, UF ou conhecimento prévio de conteúdo amazônico. Cada ano selecionado abrange as 27 UFs e cinco regiões.

| Ano | IES no cadastro completo | Públicas por categoria, quando não há rede | Especiais candidatas sem rede | Rede pública quando `TP_REDE` está presente | Total selecionado |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2017 | 2.448 | 286 | 10 | Não disponível | 296 |
| 2018 | 2.537 | 274 | 25 | Não disponível | 299 |
| 2019 | 2.608 | 281 | 21 | Não disponível | 302 |
| 2020 | 2.457 | 280 | 24 | Não disponível | 304 |
| 2021 | 2.574 | 289 | 24 | Não disponível | 313 |
| 2022 | 2.595 | 287 | 25 | Não disponível | 312 |
| 2023 | 2.580 | Campo de rede utilizado | 0 | 316 | 316 |
| 2024 | 2.561 | Campo de rede utilizado | 0 | 317 | 317 |

O zero na coluna de Especiais **sem rede** em 2023–2024 indica que essa lacuna de campo não ocorre nesses anos. Não significa inexistência de categoria Especial: o filtro de rede pública selecionou 27 Especiais em 2023 e 28 em 2024. Nos seis anos anteriores, há 129 registros anuais Especiais cuja natureza não foi confirmada por um campo de rede da IES.

A fotografia `data/registry/instituicoes.csv`, com 317 IES de 2024, e seu manifesto original foram preservados sem alterações de conteúdo. Os arquivos históricos são separados, para não apagar a proveniência da primeira etapa.

## Reconciliar observações, sem inventar eventos jurídicos

`instituicoes-historico.csv` tem chave `registro_ano_id` (`instituicao_id@ano`), conservando código, nome, sigla, categoria, UF, ano, regra de seleção, fonte e linha do original. As referências ao dicionário incluem planilha, linha e hash. O ano do Censo é observação institucional e não data de aplicação de vestibular.

`reconciliacao-instituicoes.csv` agrupa pelo mesmo código Inep e preserva as observações anuais. Há **17 códigos selecionados em anos anteriores que não aparecem na fotografia de 2024**; três são os casos antigos Especiais sem natureza confirmada. Esses casos mostram por que somente a lista atual não basta para a década.

O arquivo também identifica **35 códigos com mudanças textuais observadas** de nome, sigla, UF ou categoria. Toda diferença mantém valores, anos e fontes dos dois lados. Uma diferença de grafia não comprova mudança legal de nome; primeira/última observação não significa criação/extinção. A ausência na seleção pode corresponder a classificação distinta, falta de observação, substituição de código ou reorganização institucional. Fusões, incorporações, desmembramentos e processos encerrados exigem fontes institucionais e históricas adicionais.

O critério de igualdade é o código Inep; o arquivo não resolve automaticamente identidades entre códigos diferentes. Não foram deduzidos eventos de criação ou extinção a partir dessas sequências.

## Aquisição e integridade

O script lê o diretório ZIP e apenas o cadastro institucional, o dicionário e os checksums por HTTP Range. Não obtém o cadastro de cursos nem listas de alunos ou candidatos. O XLSX oficial do dicionário contém definições de IES e cursos; somente a planilha institucional valida os campos usados aqui.

Os originais ficam em `data/raw/inep/<ano>/<prefixo_sha256>/`. O nome do membro ZIP é preservado, inclusive problemas de codificação de nomes do pacote oficial; isso não é uma correção silenciosa do conteúdo. Arquivos temporários Excel começados por `~$` são ignorados, pois não são o dicionário completo.

O `curl` tem tempo máximo por consulta, tentativas limitadas e intervalo mínimo de um segundo. O tamanho de cada faixa é limitado; se o servidor não respeitar Range, a transferência é recusada. Os registros de requisições ficam em `data/interim/inventario/requisicoes.jsonl`. Houve consultas exploratórias e uma primeira passagem que identificou a falta de `TP_REDE`; o histórico final usa somente fontes que passaram na regra e no dicionário corretos.

Cada membro recebe SHA-256 e verificação do CRC do ZIP. O cadastro recebe ainda comparação com o MD5 publicado no pacote oficial. Como os ZIPs integrais não foram baixados, `zip_integral_baixado=false` e `zip_sha256=null`; hashes dos membros não são apresentados como hashes do ZIP completo.

Em recuperação de cache ausente, os membros conhecidos são reobtidos e seus hashes comparados. Bytes diferentes não são aceitos sem `--atualizar` explícito. Arquivo local adulterado interrompe a operação. As tabelas históricas anteriores não são substituídas quando uma fonte já conhecida falha na validação.

## Reprodução

Requer o ambiente Python 3.12.12 do projeto e `curl`; não acrescenta dependências Python.

```sh
# Adquire fontes ausentes, valida e recompõe todos os anos já aceitos.
uv run --locked python scripts/historico_ies.py

# Recompõe usando somente os originais locais e os hashes conhecidos.
uv run --locked python scripts/historico_ies.py --offline

# Seleciona anos para aquisição; não apaga os anos válidos já registrados.
uv run --locked python scripts/historico_ies.py --anos 2017 2018

# Consulta de nova versão explícita (2024 continua vinculada à fotografia preservada).
uv run --locked python scripts/historico_ies.py --anos 2023 --atualizar

uv run --locked python -m unittest discover -s tests -p test_historico_ies.py -v
```

As saídas versionáveis são `data/registry/instituicoes-historico.csv`, `data/registry/reconciliacao-instituicoes.csv` e `data/registry/fontes_inventario_historico.json`. O resumo por ano e as evidências detalhadas de esquema ficam em `data/interim/inventario/historico/resumo.json`. A reexecução offline foi comparada por hash; a fotografia de 2024 permaneceu idêntica.

## Limites e próxima ação

Não há cobertura institucional completa de **2017–2026**: faltam as mudanças de 2025–2026, a confirmação individual das Especiais, identidades entre códigos distintos e fontes jurídicas/institucionais. A página oficial consultada apresenta 2024 como edição mais recente dos microdados; isso não comprova inexistência de instituições posteriores.

O próximo passo é cruzar os 334 códigos candidatos históricos com a fila de processos, auditar os 17 não observados em 2024 e completar e-MEC/fontes institucionais. A elegibilidade dos vestibulares continua dependendo de ingresso próprio e recorrência documental amazônica por disciplina, não apenas da presença nesta tabela.
