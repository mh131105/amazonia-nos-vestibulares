# Dicionário de dados — versão 0.1.0

Arquivos tabulares em UTF-8, com quebra de linha LF fixa para preservar hashes entre plataformas. Datas são ISO 8601. Páginas são posições do PDF a partir de 1. Campos vazios no CSV e `null` no JSON indicam valor ausente ou não verificado; não significam zero. Listas e regiões geométricas dentro de CSV usam JSON. Booleanos do CSV de segmentação aparecem como `True`/`False`.

## Arquivos e chaves

| Arquivo | Unidade e chave | Origem e finalidade |
| --- | --- | --- |
| `data/registry/instituicoes.csv` | IES observada em 2024; `instituicao_id` | Cadastro nacional Inep filtrado por rede pública. Não é universo histórico reconciliado. |
| `data/registry/fontes_inventario.json` | Aquisição do cadastro e membros do ZIP; `fonte_id` | URL, data, ano, tamanho, CRC e hashes dos membros efetivamente obtidos. |
| `data/registry/triagem_ufam.json` | Notas documentais por aplicação e modalidade | Fontes, datas, evidências de programa, retificações, aplicações futuras e pendências UFAM. |
| `data/registry/triagem_demais.json` | Fontes, evidências e processos candidatos | Notas da pesquisa em UFRR, UEA, UERR, UEMA, UNEMAT e UEPG. |
| `data/registry/processos.csv` | Processo; `processo_id` | Consolidação de decisões com instituição, anos de programa por disciplina e alcance limitado às fontes examinadas. |
| `data/registry/aplicacoes.csv` | Aplicação; `aplicacao_id` | Datas, edição, ingresso, etapa, contexto curricular e evidência temporal. |
| `data/registry/evidencias-programa.csv` | Evidência disciplinar; `evidencia_id` | Páginas e fontes da triagem; não é transcrição integral dos tópicos nem vínculo questão–programa. |
| `data/registry/cobertura-anual.csv` | Célula de investigação processo × etapa × ano | Pendências e aplicações identificadas. Não afirma que houve prova em cada célula nem esgota múltiplas aplicações. |
| `data/registry/documentos-esperados.jsonl` | Documento selecionado no piloto; `documento_id` | Solicitações explícitas de coleta e fontes oficiais conhecidas. Não é a lista de todos os documentos esperados na década. |
| `data/registry/documentos.jsonl` | Versão selecionada de documento; `documento_id` | Estado da coleta, URL final, origem, hash, tamanho, data, caminho local e condições de uso. |
| `data/registry/aquisicoes.jsonl` | Evento de aquisição | Histórico acrescentado de sucessos, falhas e divergências. Não deduplicar como se cada linha fosse um documento novo. |
| `data/registry/extracoes.jsonl` | Extração vigente; `documento_id` | Hash do original, motor, versão, falhas, páginas, indicadores de texto e hashes dos artefatos. |
| `data/registry/regras-segmentacao.json` | Configuração de layout por caderno | Hash do PDF, margens, leitura em duas colunas, marcadores e faixas disciplinares. |
| `data/registry/segmentacoes.jsonl` | Execução por caderno; `documento_id` | Hashes do PDF, páginas extraídas e regras; contagens estruturais e pendências. |
| `data/processed/questoes.csv` | Ocorrência; `ocorrencia_id` | Metadados públicos dos itens; referências geométricas e estado estrutural. |
| `data/processed/questoes-texto.jsonl` | Ocorrência; `ocorrencia_id` | Texto bruto, alternativas e linhas de origem. Local e ignorado no Git. |
| `data/processed/gabaritos.csv` | Vínculo oficial por ocorrência; `ocorrencia_id` | Alternativa/anulação extraída do documento oficial correspondente; revisão humana pendente. |
| `data/annotation/fila.csv` | Ocorrência a revisar; `ocorrencia_id` | Referências para o trabalho humano, sem sugestão de regionalidade. |
| `data/annotation/rotulos-humanos.csv` | Anotação humana em preparação; `ocorrencia_id` | Campos inicialmente vazios. Só autor, data e evidência preenchidos permitem começar a auditar uma anotação. |
| `reports/manifesto-cobertura.json` | Instantâneo do relatório inicial | Hashes das entradas e saídas; não é congelamento do corpus analítico ou do teste humano. |

## Instituições e seleção

`codigo_inep` preserva o código original. `instituicao_id` usa o prefixo `inep_`. `ano_fonte=2024` limita a validade da observação; `historico_institucional_status=pendente` impede interpretar a fotografia como categoria válida em toda a década. `fonte_linha` conta o cabeçalho do CSV original como linha 1.

`rede_codigo=1` representa rede pública no dicionário oficial. `categoria_administrativa_codigo` conserva 1 (federal), 2 (estadual), 3 (municipal) ou 7 (especial). Categoria Especial conserva `esfera_administrativa=a_verificar`, mesmo incluída pela rede pública. Siglas não são chave histórica suficiente para reconciliar instituições.

Os estados de triagem seguem o protocolo: inclusão com recorrência, evidência insuficiente, lacuna documental e exclusões justificadas. `anos_previsao_historia/geografia` e `anos_programa_verificavel_historia/geografia` separam o número de anos positivos do alcance examinado. Uma lista vazia não comprova inexistência de programa. A condição de uma instituição na fotografia de 2024 não demonstra regularidade do seu processo seletivo.

## Tempo e aplicações

`data_aplicacao`, `ano_aplicacao`, `edicao`, `ano_ingresso` e `data_publicacao_edital` têm significados distintos. Os IDs do piloto conservam o nome da edição, por exemplo `ufam-psc2020-e3` corresponde à aplicação de **01/12/2019**; nunca derive o ano de análise do texto do ID.

`data_prevista` e situação `futura_na_data_de_corte` não são observações de aplicação. A prova futura PSC2027 E3 não tem ano de aplicação observado nem questões contadas no corte.

`periodo_calendario` segue as faixas `2017-2021`, `2022-2023`, `2024`, `2025-2026`. Esses rótulos descrevem calendário, não comprovam currículo escolar dos candidatos. `serie_alvo`, `ano_serie_alvo`, `coorte_alvo_esperada`, `fonte_do_corte`, `evidencia_implantacao_local`, `alinhamento_explicito_prova`, `regime_curricular_contexto` e `incerteza_classificacao` preservam o contexto e as lacunas. A E2/UFAM aplicada em 2026 se destinou a quem cursou a segunda série em 2025.

## Documentos e extrações

`sha256`/`documento_sha256` se referem aos bytes do original; não são hashes de um texto corrigido. Os arquivos locais são preservados por conteúdo. A fonte pode publicar outra versão no mesmo URL: recuperação sem `--atualizar` recusa bytes diferentes dos conhecidos. Aquisição explícita de nova versão preserva histórico e originais anteriores.

`redistribuicao_autorizada=null` não autoriza publicar o PDF. `condicoes_uso` informa condição observada ou pendência; não é licença do código nem de todos os dados.

`motor_utilizado` distingue `poppler_bbox_layout` e `pypdf_layout_alternativo`. `falha_motor_primario` preserva o erro que motivou a alternativa. `artefato_poppler_valido=false` identifica que o XML primário não deve ser usado como extração válida. `coordenadas_disponiveis=false` indica ausência de caixas nesse motor; páginas e original continuam localizáveis.

`caracteres_substituicao` conta U+FFFD; não conta todos os erros de extração. `paginas_texto_insuficiente` sinaliza menos de dez palavras, sem distinguir sozinho imagem, página em branco ou falha. `revisar_codificacao`, `revisar_ocr_ou_pagina_visual` e `texto_extraido_nao_revisado` são estados técnicos, não aprovação do conteúdo.

`texto_bruto`, `texto_normalizado` e `texto_corrigido_humano` são camadas distintas. A normalização inicial apenas compacta espaços horizontais; não restaura letras nem muda o sentido. OCR não foi executado nem validado no piloto.

## Questões, respostas e anotações

`ocorrencia_id` é a chave para juntar itens, gabaritos e fila humana. `disciplina` vale `historia` ou `geografia` no piloto. A seção original define essa disciplina; uma classificação futura de interdisciplinaridade não pode duplicar o item no agregado.

`regioes_origem` contém página, coluna, caixa da região e do texto, largura e altura da página. As coordenadas são pontos PDF, com origem superior esquerda, e preservam acesso ao espaço visual entre linhas. O texto sozinho não preserva uma figura.

`alternativas_textuais_completas=True` significa marcadores A–E únicos, em ordem, com texto extraído. `status_estrutural` também considera marcadores de questão, tamanho de texto e caracteres danificados. Nenhum desses campos equivale à revisão humana. `dependencia_visual=a_verificar`, `integridade_revisada_humano=False` e `apto_denominador_validado=False` permanecem em todos os itens desta versão.

`hash_texto_sha256` compacta espaços do texto e sugere possíveis repetições. `conteudo_equivalente_id` permanece vazio: equivalência requer conferência de imagens, textos, alternativas e versões. Essa distinção é necessária para evitar vazamento entre desenvolvimento e teste.

Em `gabaritos.csv`, `estado_oficial=alternativa_publicada` conserva a letra em `alternativa_oficial`; `estado_oficial=anulada` exige letra vazia. Documento, hash, página, seção e URL permitem conferir a origem. `vinculo_versao_caderno` e `revisao_humana` continuam pendentes. A fonte oficial não foi substituída por uma resolução do modelo.

`regionalidade` usa as quatro classes do protocolo. Nesta versão não há rótulos preenchidos. `origem_segmentacao=regra_automatica_de_layout` não é anotação humana. O manual define os campos de tema, território, demanda cognitiva e vínculo ao programa que serão usados na revisão.
