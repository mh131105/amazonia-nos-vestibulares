# História e Geografia da Amazônia nos vestibulares públicos

Estudo documental da previsão nos programas e da cobrança nas provas de processos próprios de ingresso na graduação de IES públicas brasileiras. História e Geografia seguem **um único procedimento**, com a disciplina registrada em cada item e com denominadores separados.

Recorte: aplicações de **01/01/2017 a 11/11/2026**, no horário de Manaus. O ano de 2026 é parcial. A comparação temporal em torno do Novo Ensino Médio é observacional, sem atribuição causal à reforma.

## Estado e resultados disponíveis

- Inventário inicial: **317 IES da rede pública no Censo 2024**, nas 27 UFs e cinco regiões. O histórico institucional da década está pendente.
- Triagem inicial: **18 processos em sete IES**, com fontes, decisões e lacunas. O levantamento nacional de processos permanece aberto.
- Piloto: **24 PDFs oficiais**, incluindo editais, retificações, manuais, provas e gabaritos. São **seis cadernos** UFAM/UFRR com **84 questões segmentadas: 42 de História e 42 de Geografia**.
- Os itens têm origem por documento, hash, página e região do PDF. **Ainda não há incidência regional calculada, referência humana, avaliação da IA ou banco educacional liberado.**

Leia o [relatório inicial](reports/relatorio-inicial.md), a [cobertura documental](reports/cobertura-inicial.md) e o [estado do projeto](docs/estado.md). O [manifesto](reports/manifesto-cobertura.json) identifica as entradas e saídas desta versão.

## Procedimento e reprodução

Ambiente fixado: **Python 3.12.12**, dependências em `uv.lock`. O extrator usa **Poppler** (`pdftotext`, testado na versão 26.04.0) e **pypdf 7.0.1** como alternativa para falhas reais. A aquisição do cadastro Inep usa `curl` e leitura parcial do ZIP. O OCR ainda não foi validado neste ambiente.

### 1. Reconstruir relatórios dos registros versionados

Depois de preparar o ambiente com `uv sync --locked`:

```sh
uv run --locked python scripts/pipeline.py verificar --somente-metadados
uv run --locked python scripts/pipeline.py relatorio
```

Esses comandos usam os registros versionados e dispensam PDFs, rede e chamadas de IA. Não recriam a extração sem os originais. `reports/manifesto-cobertura.json` permite conferir os hashes das entradas e saídas.

### 2. Obter originais e reconstruir o piloto

Requer fontes oficiais disponíveis e Poppler instalado. Execute na raiz do projeto:

```sh
uv run --locked python scripts/inventario_ies.py
uv run --locked python scripts/consolidar_registro.py
uv run --locked python scripts/pipeline.py coletar
uv run --locked python scripts/pipeline.py extrair
uv run --locked python scripts/segmentar.py
uv run --locked python scripts/gabaritos.py
uv run --locked python scripts/preparar_revisao.py
uv run --locked python scripts/pipeline.py verificar
uv run --locked python scripts/pipeline.py relatorio
```

A coleta reaproveita arquivos íntegros, limita frequência e tentativas e registra falhas. Em uma cópia sem o acervo local, recupera os bytes conhecidos; se o URL retornar outra versão, preserva a divergência e recusa a substituição silenciosa. Para consultar e aceitar uma atualização explicitamente, use `--atualizar` nos comandos de inventário ou coleta. Novos conteúdos são preservados por hash; regras de segmentação vinculadas a outro hash exigem revisão.

Com originais presentes, `uv run --locked python scripts/inventario_ies.py --offline` reconstrói o cadastro sem rede. Reexecutar a preparação da fila preserva os rótulos humanos já preenchidos.

### 3. Reclassificar com IA

Essa etapa ainda não está implementada. Depende de referência humana, partições por prova e grupos equivalentes, teste congelado, orçamento e avaliação contra um método simples por palavras-chave. Não foram feitas chamadas pagas de API de modelos pelo pipeline. Custos da assistência no aplicativo não foram quantificados.

## Verificação

```sh
uv run --locked python -m unittest discover -s tests -v
git diff --check
```

Os testes protegem integridade dos originais, mudanças de versão, limites de coleta, identificação de páginas e coordenadas, leitura de colunas, alternativas incompletas e reprodução. Fixtures sintéticas ficam somente nos testes e nunca entram no corpus histórico.

## Documentação e dados

- [Protocolo](docs/protocolo.md), [decisões posteriores](docs/decisoes.md) e [texto original preservado](docs/protocolo-original.txt).
- [Inventário nacional e pendências históricas](docs/notas-inventario.md).
- [Notas da triagem documental](docs/notas-triagem-demais.md) e [dicionário de dados](docs/dicionario-dados.md).
- [Manual de revisão e anotação](docs/manual-anotacao.md).
- Registros em `data/registry/`; metadados dos itens e gabaritos em `data/processed/`; fila de revisão em `data/annotation/`.

Originais, extrações com enunciados e imagens permanecem locais e ignorados no Git enquanto não houver condição de redistribuição demonstrada. Metadados, código e resultados de cobertura são versionados. Não há licença geral aplicada aos materiais de terceiros.

Autoria do projeto: **Matheus Garcia**. Inventário, pesquisa documental, código e verificações iniciais preparados com assistência do **Codex**. Essa assistência não constitui anotação humana independente.
