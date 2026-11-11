# Manual inicial de revisão e anotação

Versão 0.2.0, 11/11/2026. Aplica-se a História e Geografia pelo mesmo procedimento. A taxonomia inicial é uma proposta a avaliar no desenvolvimento, não um resultado de frequência. Matheus foi definido pelo usuário como anotador humano; essa definição não preenche nenhum rótulo.

## Unidade e fonte

A unidade é a **ocorrência de uma questão numa aplicação**. `ocorrencia_id` identifica a ocorrência; o número impresso, `documento_id`, SHA-256, páginas e regiões em pontos PDF permitem encontrá-la. `hash_texto_sha256` é somente um indício de equivalência textual: não incorpora mapas, charges ou alternativas gráficas.

Abra o original indicado em `data/registry/documentos.jsonl` e confira as regiões de `data/processed/questoes-texto.jsonl`. As coordenadas usam origem superior esquerda e unidades em pontos PDF. O CSV público contém metadados; o texto e o acervo permanecem locais.

## Ordem de revisão

1. Verifique número, disciplina, enunciado integral, alternativas na ordem original e continuidade entre colunas/páginas. O sinalizador A–E confirma apenas uma estrutura textual, não o sentido ou a completude visual.
2. Veja se há mapa, imagem, gráfico, tabela, legenda ou texto compartilhado indispensável. Não complete uma parte ausente com memória ou IA. Se estiver ilegível ou incompleta, registre a pendência.
3. Confira gabarito e anulações na fonte oficial da mesma versão de caderno. Uma alternativa encontrada automaticamente ainda precisa dessa conferência. Gabarito ausente não impede necessariamente análise temática, mas impede liberação para o banco educacional.
4. Classifique regionalidade com evidência que explique qual conhecimento é necessário para resolver o item. A ocorrência de uma palavra regional sozinha não decide a classe.
5. Registre recorte territorial, temas e operação cognitiva. Só relacione ao programa efetivamente vigente se esse documento estiver disponível; caso contrário, registre programa indisponível.
6. Identifique anotador e data. Discordância ou dúvida permanece em revisão. As verificações do Codex não podem ser assinadas como anotação humana.

## Regionalidade

| Valor | Regra comum às duas disciplinas |
| --- | --- |
| `regional_substantiva` | Conhecimento ou interpretação histórica/geográfica sobre a região é substantivo para a resolução. |
| `mencao_contextual` | A região aparece, mas a resolução depende de conteúdo geral. |
| `nao_regional` | Não se enquadra no recorte. |
| `ambiguo_revisar` | Faltam informações ou a fronteira conceitual exige revisão. |

Use `amazonas_estado`, `outros_territorios_amazonicos`, `amazonia_transregional` ou `a_revisar` para recorte territorial. Preserve lugares e períodos originais; limites atuais da Amazônia Legal não definem sozinhos a regionalidade histórica. Conteúdos maranhenses ou mato-grossenses não são automaticamente amazônicos.

## Temas e operações

Em História, os temas iniciais do protocolo incluem populações indígenas; colonização e políticas indigenistas; formação territorial; conflitos e movimentos sociais; escravidão e trabalho; borracha e urbanização; Estado e integração; cultura e patrimônio.

Em Geografia, as famílias iniciais incluem território e regionalização; relevo, solos e recursos; clima e hidrografia; biodiversidade e ambiente; populações e urbanização; economia, trabalho e redes; conflitos territoriais e políticas ambientais. Tópicos específicos serão refinados a partir dos programas e do manual de desenvolvimento. Registre múltiplos temas sem duplicar a ocorrência no total.

Registre a operação exigida: reconhecimento factual, interpretação de fonte, localização espacial/temporal, comparação, explicação de processos ou raciocínio causal. Essa anotação descreve demanda do item e não mede dificuldade empírica dos candidatos.

## Programa e revisão

Para o vínculo ao programa, use `explicito`, `abrangente`, `ambiguo` ou `nao_identificado`. `programa_indisponivel` é uma situação separada. A ausência de uma expressão literal não autoriza chamar o item de fora do edital. Uma lista de tópicos não observados nas provas disponíveis não é recomendação para abandonar seu estudo.

`data/registry/evidencias-programa.csv` registra somente evidências iniciais de triagem, não a transcrição integral dos programas nem vínculos de cada questão. As páginas são posições do PDF, contadas a partir de 1; páginas impressas podem divergir.

## Desenvolvimento, teste e métricas

O piloto atual serve para desenvolver e revisar a extração. **Não há teste humano congelado nem rótulos humanos nesta versão.** A fila gerada contém campos vazios para anotação; não deve ser contada como referência humana pronta.

Antes dos ajustes finais de prompts, formar referência humana (meta de pelo menos 200 itens quando o corpus permitir), agrupar conteúdos equivalentes e separar provas/edições inteiras. Itens equivalentes, inclusive com imagens diferentes ou alternativas reordenadas, não podem atravessar desenvolvimento e teste. A validação dos grupos exige mais que o hash textual.

Congelar IDs, rótulos, manual, partições, versões e hashes do teste antes de avaliá-lo. Registrar mudanças posteriores em outra versão. Definir as palavras-chave do método simples no desenvolvimento; não ajustá-las olhando o teste.

Somente depois calcular precisão, revocação, F1, suporte, matriz de confusão, erros e abstenções. Não usar rótulos do Codex como referência humana nem concordância entre modelos como substituto. Sem referência, as métricas são indisponíveis, nunca zero ou 100% por conveniência.

## Fila de trabalho

Execute `uv run python scripts/preparar_revisao.py`. O comando gera `data/annotation/fila.csv` e cria as linhas ainda ausentes em `data/annotation/rotulos-humanos.csv`, preservando o preenchimento já existente. A fila aponta para os textos locais; o arquivo de rótulos começa sem qualquer resposta ou assinatura humana.

Preencha primeiro integridade e dependência visual. A regionalidade só deve entrar nos indicadores quando houver evidência e revisão suficientes para o subconjunto analítico correspondente. Um item com anulação oficial integra a cobrança aplicada; a versão para pontuação o exclui do numerador e do denominador.

## Caderno local para Matheus

O arquivo `data/annotation/revisao/index.html` apresenta as 300 questões do acervo atual, por aplicação e disciplina. Ele usa imagens recortadas fielmente do PDF, acompanhadas de página, coluna, link para o documento completo e opção de ampliar. O texto extraído aparece fechado em uma seção complementar. Gabaritos e sugestões de regionalidade não são mostrados.

1. Abra o caderno no navegador. Se for necessário recriá-lo, execute `uv run --locked python scripts/gerar_revisao.py` com o acervo presente.
2. Confira a fonte visual, registre integridade, regionalidade e uma justificativa curta. Avalie o enunciado sem presumir uma tendência de mudança curricular. A opção de caso ambíguo permanece disponível.
3. Use **Salvar minha anotação** em cada item. Navegar sem salvar exige confirmação. As anotações ficam no armazenamento do navegador e não são enviadas a um serviço externo.
4. Use **Exportar anotações** periodicamente para guardar o JSON. **Carregar anotações** permite restaurar esse arquivo se as ocorrências e hashes continuarem válidos; uma atualização do caderno também recupera registros compatíveis do mesmo navegador.
5. Incorpore o arquivo exportado com `uv run --locked python scripts/importar_anotacoes.py /caminho/para/arquivo.json`. O importador valida os campos, a identidade configurada, a data com fuso e o hash do PDF antes de modificar o CSV. Alterações em anotações já preenchidas exigem `--substituir`; o CSV anterior e um evento de importação são preservados.

O JSON declara a origem humana e registra ações de quem preencheu o formulário; não é autenticação independente da pessoa. O Codex não deve preencher o caderno real se passando por Matheus. Os testes de preenchimento usam somente uma página fictícia separada e diretórios temporários.

Ainda não há teste humano congelado ou sugestão de partição atribuída pela interface. A anotação de integridade e regionalidade inicia a referência; a auditoria, os grupos equivalentes e as partições continuam etapas próprias. Temas, operação e notas podem ser preenchidos no caderno; revisão de gabarito e vínculo ao programa usam a fonte e o CSV em etapa separada.
