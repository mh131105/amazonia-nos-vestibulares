# Inventário nacional inicial de instituições

Em 11/11/2026, foi importado o cadastro de IES do Censo da Educação Superior **2024**, publicado pelo Inep. Trata-se de uma fotografia institucional desse ano, que inicia a busca nacional; não é um censo de processos de vestibular elegíveis nem comprova a natureza de cada instituição durante toda a janela 2017–2026.

O arquivo [instituicoes.csv](../data/registry/instituicoes.csv) contém **317 instituições da rede pública**, com IDs únicos, das **27 UFs e das cinco regiões**. Ele registra a fotografia institucional de 2024. O andamento da triagem dos processos é registrado separadamente em [processos.csv](../data/registry/processos.csv), sem ser reescrito pela importação do cadastro; a reconciliação do histórico institucional permanece pendente.

| Região da sede no cadastro | IES da rede pública em 2024 |
| --- | ---: |
| Centro-Oeste | 27 |
| Nordeste | 66 |
| Norte | 24 |
| Sudeste | 166 |
| Sul | 34 |
| Total | 317 |

## Seleção e a categoria Especial

O filtro é **`TP_REDE = 1`**, cuja descrição no dicionário oficial é “Pública”. Filtrar somente `TP_CATEGORIA_ADMINISTRATIVA` em 1, 2 e 3 perderia 28 instituições que o próprio cadastro classifica simultaneamente como rede pública e categoria **7 — Especial**.

| Categoria administrativa original | Registros selecionados |
| --- | ---: |
| 1 — Pública Federal | 122 |
| 2 — Pública Estadual | 139 |
| 3 — Pública Municipal | 28 |
| 7 — Especial | 28 |
| Total | 317 |

As categorias foram preservadas. A esfera administrativa das 28 especiais fica **`a_verificar`**, sem converter automaticamente seu código para municipal. A [divulgação oficial do Inep](https://www.gov.br/inep/pt-br/centrais-de-conteudo/noticias/censo-da-educacao-superior/inep-divulga-resultado-do-censo-superior-2024) apresenta o mesmo total de 317 públicas, agregado em 122 federais, 139 estaduais e 56 municipais. Essa diferença de apresentação exige leitura dos campos e verificação individual; não autoriza apagar casos especiais do inventário.

O cadastro completo observado tem 2.561 IES. A seleção não usa UF, região ou presença prévia de conteúdo amazônico. Instituições fora da Região Norte também serão triadas por processo de ingresso, com o mesmo procedimento para História e Geografia e com a disciplina registrada separadamente.

## Origem, aquisição e integridade

- [Página oficial dos microdados do Censo da Educação Superior](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-da-educacao-superior).
- [ZIP oficial de 2024](https://download.inep.gov.br/microdados/microdados_censo_da_educacao_superior_2024.zip).
- Membro utilizado: `microdados_censo_da_educacao_superior_2024/dados/MICRODADOS_ED_SUP_IES_2024.CSV`.
- Encoding original: Windows-1252; separador original: ponto e vírgula. A exportação do inventário é UTF-8 e CSV com vírgulas.
- O dicionário XLSX e o arquivo de checksums oficiais foram coletados junto com o cadastro. Os originais ficam em `data/raw/inep/2024/<prefixo_sha256>/`, preservados por conteúdo.
- O MD5 do cadastro confere com o checksum oficial: `dbe25e67857aa68b12beaeffa194f53f`. O arquivo de checksums usa o nome anterior `MICRODADOS_CADASTRO_IES_2024.csv`; a igualdade foi conferida pelo conteúdo.
- [fontes_inventario.json](../data/registry/fontes_inventario.json) registra a URL, o membro do ZIP, a hora de coleta em Manaus, os tamanhos, SHA-256 e CRC de cada membro, ETag e Last-Modified do ZIP.

O ZIP tem 456.807.449 bytes. A aquisição lê somente o diretório ZIP e os membros necessários por **HTTP Range**, sem baixar o cadastro de cursos. O manifesto declara `zip_integral_baixado: false` e `zip_sha256: null`: os hashes dos membros não são apresentados como se fossem o hash do pacote integral. A leitura via `zipfile` verifica o CRC e o cadastro recebe a verificação adicional do MD5 oficial.

Cada consulta usa limite de 45 segundos, até duas novas tentativas e intervalo mínimo de um segundo entre requisições lógicas. Se o servidor ignorar Range, o limite de tamanho impede a transferência do pacote completo. O cache local evita consultas na reprodução e cada nova aquisição preserva os membros pelo hash. As consultas registram saídas e falhas do curl em `data/interim/inventario/requisicoes.jsonl`.

Quando o manifesto conhecido existe, mas os originais estão ausentes em um clone limpo, o comando padrão tenta recuperá-los. Todos os membros selecionados — cadastro, dicionário e checksums — precisam conferir com os SHA-256 conhecidos. Uma divergência preserva os novos originais e o evento em `data/interim/inventario/recuperacoes.jsonl`, mas rejeita a substituição do manifesto e do inventário. `--atualizar` aceita explicitamente uma nova aquisição. Um original local adulterado interrompe a operação antes de qualquer acesso à rede.

## Reprodução

Usa o ambiente Python 3.12.12 fixado pelo projeto e `curl`; este script não usa pacotes Python externos. Os comandos abaixo usam `uv` para respeitar o ambiente do repositório.

```sh
# Primeira aquisição ou recuperação de clone limpo, conferindo a versão conhecida.
uv run python scripts/inventario_ies.py

# Reconstrução sem acesso à rede, com conferência de SHA-256 dos originais.
uv run python scripts/inventario_ies.py --offline

# Nova consulta explícita à mesma fonte. Novos conteúdos recebem outro diretório por hash.
uv run python scripts/inventario_ies.py --atualizar
```

Sem os originais locais, a reprodução exige a aquisição oficial; `--offline` informa claramente os caminhos ausentes. O manifesto conhecido permanece intacto quando a recuperação confirma seus hashes, preservando a data da aquisição histórica; a nova tentativa fica no registro de recuperação. Os CSVs de instituições e os metadados são versionáveis; a disponibilidade pública dos demais materiais do projeto deve ser decidida por suas condições de uso.

O comando verifica unicidade dos IDs, ano da fonte, presença das cinco regiões e 27 UFs, mapeamento do dicionário e integridade dos originais. O resumo de execução fica em `data/interim/inventario/resumo_2024.json`. `fonte_linha` é a linha do CSV original, contando o cabeçalho como linha 1; `fonte_membro_zip` identifica o arquivo dentro do pacote.

## Pendências de cobertura

1. Importar e reconciliar os cadastros históricos de 2017–2023, preservando mudanças de nomes, siglas, categoria, IDs e processos encerrados. Os cadastros anuais desse período estão listados na página oficial, mas ainda não foram importados.
2. Complementar as lacunas de 2025–2026 e o histórico com e-MEC e fontes institucionais. A página consultada listava 2024 como edição mais recente dos microdados; isso não prova inexistência de instituições criadas depois.
3. Verificar individualmente a esfera e a natureza das instituições de categoria Especial.
4. Para cada IES, identificar processos próprios ativos ou históricos e registrar evidências de previsão regional por disciplina, etapa e ano de aplicação.
5. Confirmar recorrência e cobertura documental antes de declarar processos elegíveis. Estar neste cadastro significa entrar na fila de investigação, sem inferir que a instituição cobre Amazônia em suas provas.

Não foram coletados registros de alunos, candidatos ou desempenho individual. O próximo avanço do inventário é a reconciliação histórica e a triagem documental dos processos de ingresso das 317 instituições.
