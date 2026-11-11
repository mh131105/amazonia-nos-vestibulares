# Dicionário de dados — versão 0.4.0

Arquivos tabulares em UTF-8, com quebra de linha LF fixa para preservar hashes entre plataformas. Datas são ISO 8601. Páginas são posições do PDF a partir de 1. Campos vazios no CSV e `null` no JSON indicam valor ausente ou não verificado; não significam zero. Listas e regiões geométricas dentro de CSV usam JSON. Booleanos do CSV de segmentação aparecem como `True`/`False`.

## Arquivos e chaves

| Arquivo | Unidade e chave | Origem e finalidade |
| --- | --- | --- |
| `data/registry/instituicoes.csv` | IES observada em 2024; `instituicao_id` | Cadastro nacional Inep filtrado por rede pública. Não é universo histórico reconciliado. |
| `data/registry/fontes_inventario.json` | Aquisição do cadastro e membros do ZIP; `fonte_id` | URL, data, ano, tamanho, CRC e hashes dos membros efetivamente obtidos. |
| `data/registry/triagem_ufam.json` | Notas documentais por aplicação e modalidade | Fontes, datas, evidências de programa, retificações, aplicações futuras e pendências UFAM. |
| `data/registry/triagem_demais.json` | Fontes, evidências e processos candidatos | Notas da pesquisa em UFRR, UEA, UERR, UEMA, UNEMAT e UEPG. |
| `data/registry/triagem-sul-sudeste-c3.json` e `triagem-ne-co-c3.json` | Fontes, processos/ramos e evidências | Triagem nacional C3, com adoção do programa, datas efetivas e alcance das leituras. |
| `data/registry/auditoria-datas-c3.json` | Verificação documental por aplicação | Datas confirmadas ou pendentes, retificações examinadas e ressalva de finalidade de gabarito. |
| `data/registry/contexto-normativo.json` | Versão de fonte normativa; `fonte_id` | Marcos S2–S6 arquivados por hash, separados dos documentos de aplicações de vestibular. |
| `data/registry/expansao-fuvest-c4.json` e `expansao-ufms-c4.json` | Aplicação, programa compartilhado e versões de documento | Datas efetivas, fases/dias, formatos, exposição por carreira e bases digitais. |
| `data/registry/auditoria-datas-c4.json` | Complemento temporal e finalidade de gabarito | Confirmações primárias, limites e cadeia documental; preserva a auditoria C3. |
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

`instituicoes-historico.csv` usa `registro_ano_id=instituicao_id@ano` para as 2.459 observações de 2017–2024. Em 2017–2022, `rede_codigo` fica vazio: `rede=publica_por_categoria` para 1/2/3 e `especial_a_verificar` para 7. A planilha/linha do dicionário e seu hash sustentam a regra por ano. `reconciliacao-instituicoes.csv` agrupa observações pelo código, mantendo nomes, siglas, categorias, UFs e fontes anuais. Não resolve identidades entre códigos distintos. `fila-triagem-institucional.csv` cobre os 334 códigos históricos; `parcial` significa que foram registrados processos, nunca investigação institucional concluída.

`codigo_inep` preserva o código original. `instituicao_id` usa o prefixo `inep_`. `ano_fonte=2024` limita a validade da observação; `historico_institucional_status=pendente` impede interpretar a fotografia como categoria válida em toda a década. `fonte_linha` conta o cabeçalho do CSV original como linha 1.

`rede_codigo=1` representa rede pública no dicionário oficial. `categoria_administrativa_codigo` conserva 1 (federal), 2 (estadual), 3 (municipal) ou 7 (especial). Categoria Especial conserva `esfera_administrativa=a_verificar`, mesmo incluída pela rede pública. Siglas não são chave histórica suficiente para reconciliar instituições.

Os estados de triagem seguem o protocolo: inclusão com recorrência, evidência insuficiente, lacuna documental e exclusões justificadas. `anos_previsao_historia/geografia` e `anos_programa_verificavel_historia/geografia` separam o número de anos positivos do alcance examinado. Uma lista vazia não comprova inexistência de programa. A condição de uma instituição na fotografia de 2024 não demonstra regularidade do seu processo seletivo.

O ciclo 3 conserva `ciencias_humanas_integradas` como atribuição conjunta oficial. `anos_previsao_integrada` não alimenta automaticamente as listas de História/Geografia. Há uma evidência integrada por aplicação, com disciplinas abrangidas e interpretação em campos próprios. Os registros de ramos ainda não desagregados são pistas de investigação, sem comprovar um processo único. Recorrência de programa não comprova ocorrência de questões.

## Tempo e aplicações

`data_aplicacao`, `ano_aplicacao`, `edicao`, `ano_ingresso` e `data_publicacao_edital` têm significados distintos. Os IDs do piloto conservam o nome da edição, por exemplo `ufam-psc2020-e3` corresponde à aplicação de **01/12/2019**; nunca derive o ano de análise do texto do ID.

`data_prevista` e situação `futura_na_data_de_corte` não são observações de aplicação. A prova futura PSC2027 E3 não tem ano de aplicação observado nem questões contadas no corte.

`aplicacao_ocorrida_data_exata_a_corrobora` identifica caderno/programa localizados com data exata ainda não sustentada. A data prevista não é promovida para `ano_aplicacao`; a grade marca `data_efetiva_pendente`. `banca` e `formato` preservam mudanças relevantes, como os conjuntos recentes Cebraspe/UERR. As fontes C2 estão em `expansao-ufam-c2.json` e `expansao-demais-c2.json`.

`periodo_calendario` segue as faixas `2017-2021`, `2022-2023`, `2024`, `2025-2026`. Esses rótulos descrevem calendário, não comprovam currículo escolar dos candidatos. `serie_alvo`, `ano_serie_alvo`, `coorte_alvo_esperada`, `fonte_do_corte`, `evidencia_implantacao_local`, `alinhamento_explicito_prova`, `regime_curricular_contexto` e `incerteza_classificacao` preservam o contexto e as lacunas. A E2/UFAM aplicada em 2026 se destinou a quem cursou a segunda série em 2025.

No C4, `fase` e `dia` separam eventos da segunda fase FUVEST, preservando a etapa. `estrutura_documentada` descreve quantidades e exposição por carreira; `variantes_documentadas` distingue presencial/digital sem criar outra aplicação por ordenação. `programa_documento_id` pode referenciar um programa mantido por outro dia da mesma edição; `aplicacoes_vinculadas` explicita o compartilhamento. `vigencia_confirmada=false` e `previsao_regional=pendente_vigencia_versao_programa` preservam a dúvida do manual2021, nominalmente posterior às provas. A previsão lida fica em `previsao_regional_documento`; ela não comprova adoção pré-prova.

## Documentos e extrações

`sha256`/`documento_sha256` se referem aos bytes do original; não são hashes de um texto corrigido. Os arquivos locais são preservados por conteúdo. A fonte pode publicar outra versão no mesmo URL: recuperação sem `--atualizar` recusa bytes diferentes dos conhecidos. Aquisição explícita de nova versão preserva histórico e originais anteriores.

`redistribuicao_autorizada=null` não autoriza publicar o PDF. `condicoes_uso` informa condição observada ou pendência; não é licença do código nem de todos os dados.

`extracao_automatica=false` conserva original e hash sem solicitar extração de conteúdo pessoal/financeiro fora da evidência necessária. A cobertura mostra `nao_solicitada_preservacao_original`. Não é falha de OCR nem exclusão do acervo. `documento_id_evidencia_data` e `fonte_data_sha256` ligam a confirmação administrativa ao original e à aplicação; emissão ou pagamento não datam a prova.

`motor_utilizado` distingue `poppler_bbox_layout` e `pypdf_layout_alternativo`. `falha_motor_primario` preserva o erro que motivou a alternativa. `artefato_poppler_valido=false` identifica que o XML primário não deve ser usado como extração válida. `coordenadas_disponiveis=false` indica ausência de caixas nesse motor; páginas e original continuam localizáveis.

O ciclo 2 acrescenta `pdftohtml_fragmentos_alternativo`: caixas nativas de fragmentos, com `granularidade_coordenadas=fragmento_textual`. O campo compatível `palavras` nas linhas contém unidades geométricas inteiras, não caixas inventadas para cada palavra do fragmento. `controles_xml_substituidos` conta controles ilegais substituídos por U+FFFD na camada de parse; o XML bruto não é reescrito. A flag do XML primário também é falsa quando ele exigiu esse saneamento para leitura. `transporte=curl_tls_sistema` documenta o uso da cadeia TLS validada pelo curl do sistema; não há opção de desativar certificados.

`caracteres_substituicao` conta U+FFFD; não conta todos os erros de extração. `paginas_texto_insuficiente` sinaliza menos de dez palavras, sem distinguir sozinho imagem, página em branco ou falha. `revisar_codificacao`, `revisar_ocr_ou_pagina_visual` e `texto_extraido_nao_revisado` são estados técnicos, não aprovação do conteúdo.

`texto_bruto`, `texto_normalizado` e `texto_corrigido_humano` são camadas distintas. A normalização inicial apenas compacta espaços horizontais; não restaura letras nem muda o sentido. OCR não foi executado nem validado no piloto.

## Questões, respostas e anotações

`ocorrencia_id` é a chave para juntar itens, gabaritos e fila humana. `disciplina` vale `historia` ou `geografia` no piloto. A seção original define essa disciplina; uma classificação futura de interdisciplinaridade não pode duplicar o item no agregado.

`numero_questao` conserva o identificador impresso, inclusive G01/H01 nas discursivas. O ID inclui esse código, evitando colisão entre disciplinas com o mesmo ordinal. `tipo_resposta` distingue `objetiva_multipla_escolha` e `discursiva`. Nesta última, `alternativas_textuais_completas` fica vazio e `subitens_rotulos_detectados` registra letras sem criar novas ocorrências. A estrutura textual não substitui conferência visual/humana.

`regioes_origem` contém página, coluna, caixa da região e do texto, largura e altura da página. As coordenadas são pontos PDF, com origem superior esquerda, e preservam acesso ao espaço visual entre linhas. O texto sozinho não preserva uma figura.

`alternativas_textuais_completas=True` significa marcadores A–E únicos, em ordem, com texto extraído. `status_estrutural` também considera marcadores de questão, tamanho de texto e caracteres danificados. Nenhum desses campos equivale à revisão humana. `dependencia_visual=a_verificar`, `integridade_revisada_humano=False` e `apto_denominador_validado=False` permanecem em todos os itens desta versão.

`hash_texto_sha256` compacta espaços do texto e sugere possíveis repetições. `conteudo_equivalente_id` permanece vazio: equivalência requer conferência de imagens, textos, alternativas e versões. Essa distinção é necessária para evitar vazamento entre desenvolvimento e teste.

Em `gabaritos.csv`, `estado_oficial=alternativa_publicada` conserva a letra em `alternativa_oficial`; `estado_oficial=anulada` exige letra vazia. Documento, hash, página, seção e URL permitem conferir a origem. `vinculo_versao_caderno` e `revisao_humana` continuam pendentes. A fonte oficial não foi substituída por uma resolução do modelo.

`finalidade_documental=definitivo_indicado_no_indice_sem_confirmacao_no_arquivo` preserva a divergência entre o rótulo do índice oficial e o conteúdo do PDF PSC2019 E2. As letras continuam publicadas; a finalidade para pontuação exige confirmação. O valor não classifica o documento como preliminar. `sha256_auditado`, quando presente no registro esperado, fixa os bytes examinados pela auditoria; a verificação recusa outra versão.

A auditoria C4 sobrepõe, sem apagar a fonte C3, `finalidade_documental=definitivo_corrobora_repositorio_e_pos_recursos` para os mesmos bytes. Isso corrobora a finalidade institucional e mantém revisão humana pendente. Em discursivas, `estado_oficial=orientacao_discursiva_publicada` indica referência oficial com código e páginas, sem letra de alternativa ou declaração de resposta única. `paginas_pdf` conserva continuações; G05/FUVEST2024, pp.31–32, depende de hash verificado. Fonte ausente permanece `nao_identificado`, sem resposta fabricada.

`regionalidade` usa as quatro classes do protocolo. Nesta versão não há rótulos preenchidos. `origem_segmentacao=regra_automatica_de_layout` não é anotação humana. O manual define os campos de tema, território, demanda cognitiva e vínculo ao programa que serão usados na revisão.

`configuracao.json` registra Matheus como anotador previsto. `pacote-revisao.json` contém o identificador do caderno e seus IDs, sem enunciados, gabaritos ou sugestões. As imagens e o HTML completos ficam locais em `data/annotation/revisao/`, ignorados no Git. A importação do JSON exportado preserva CSVs anteriores em `data/annotation/historico/` e registra hashes/IDs em `importacoes.jsonl`. Uma declaração de origem humana não é autenticação independente; preencher o nome automaticamente na interface não preenche a classificação.

`integridade_alternativas=nao_se_aplica_discursiva` é aceito somente em questão discursiva. Matheus registra a conferência no formulário. As linhas existentes são preservadas, e novas questões recebem apenas linhas vazias.
