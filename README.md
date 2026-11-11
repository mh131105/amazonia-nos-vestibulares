# História e Geografia da Amazônia nos vestibulares públicos

Estudo documental da previsão nos programas e da cobrança nas provas de processos próprios de ingresso na graduação de IES públicas brasileiras. História e Geografia seguem **um único procedimento**, com a disciplina registrada em cada item e com denominadores separados.

Recorte: aplicações de **01/01/2017 a 11/11/2026**, no horário de Manaus. O ano de 2026 é parcial. A comparação temporal em torno do Novo Ensino Médio é observacional, sem atribuição causal à reforma.

## Estado e resultados disponíveis

- Inventário histórico: **2.459 observações anuais em 2017–2024**, reunindo **334 códigos públicos ou Especiais candidatos**. A fotografia de 2024, com 317 IES da rede pública, permanece preservada. Mudanças de 2025–2026 e reconciliação jurídica estão pendentes.
- Triagem: **39 registros de processos ou ramos em 24 IES**, com fontes, decisões e lacunas nas cinco regiões. Ramos ainda não desagregados não equivalem a processos únicos comprovados. O levantamento nacional permanece aberto.
- Questões: **312 ocorrências, 156 de História e 156 de Geografia**. São 300 objetivas de 23 cadernos UFAM/UFRR/UERR e 12 discursivas da compilação FUVEST2024. Subitens e versões por carreira não multiplicam as ocorrências.
- Acervo de vestibulares: **231 vínculos documentais e 225 PDFs oficiais distintos**, com **62 eventos registrados**. Os cinco marcos normativos ficam em registro separado. Quatro vínculos administrativos/de recursos preservam originais e metadados, sem extração textual automática.
- FUVEST: 32 eventos das fases comuns em 2017–2026, com versões e programas compartilhados. A primeira fase de ingresso 2027 ocorreu em 01/11/2026 e está incluída; sua segunda fase permanece futura. UFMS: variantes presencial/digital preservadas, sem converter blocos integrados em História exclusiva.
- As auditorias confirmaram cinco datas UFAM; três E3 continuam pendentes. A finalidade do gabarito PSC2019 E2 foi corroborada por cadeia institucional e pós-recursos, mantendo as mesmas letras e anulações. Revisão humana e versão de caderno permanecem pendentes.
- Os itens têm origem por documento, hash, página e região do PDF. **Ainda não há incidência regional calculada, referência humana, avaliação da IA ou banco educacional liberado.**

Leia o [relatório inicial](reports/relatorio-inicial.md), a [cobertura documental](reports/cobertura-inicial.md) e o [estado do projeto](docs/estado.md). O [manifesto](reports/manifesto-cobertura.json) identifica as entradas e saídas desta versão.

## Procedimento e reprodução

Ambiente fixado: **Python 3.12.12**, dependências em `uv.lock`. O extrator usa **Poppler** (`pdftotext`, testado na versão 26.04.0) e **pypdf 7.0.1** como alternativa para falhas reais. A aquisição Inep usa `curl` e leitura parcial do ZIP. PDFs do arquivo legado UFAM usam a cadeia TLS do sistema pelo `curl`, sem desativar certificados. `pdftohtml` preserva coordenadas de fragmentos nos PDFs que fazem o extrator principal falhar. O OCR ainda não foi validado neste ambiente.

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
uv run --locked python scripts/historico_ies.py
uv run --locked python scripts/contexto_normativo.py
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

Os cinco marcos S2–S6 ficam em acervo separado, sem aplicações fictícias de vestibular. `uv run --locked python scripts/contexto_normativo.py --offline` confere os originais arquivados; os cortes temporais e as limitações estão no [contexto temporal](docs/contexto-temporal.md).

### 3. Reclassificar com IA

Essa etapa ainda não está implementada. Depende de referência humana, partições por prova e grupos equivalentes, teste congelado, orçamento e avaliação contra um método simples por palavras-chave. Não foram feitas chamadas pagas de API de modelos pelo pipeline. Custos da assistência no aplicativo não foram quantificados.

## Revisão por Matheus

O [caderno local de revisão](data/annotation/revisao/index.html) reúne as questões por prova e disciplina com imagens da fonte. Ele não mostra gabaritos nem sugestões de regionalidade. Nas discursivas, as alternativas são não aplicáveis; mantenha os subitens na mesma questão. Abra o arquivo no navegador, salve suas decisões e use **Exportar anotações** para guardar uma cópia. As datas não corroboradas aparecem como pendentes.

```sh
# Recriar o caderno a partir do acervo local
uv run --locked python scripts/gerar_revisao.py

# Incorporar um arquivo exportado por você
uv run --locked python scripts/importar_anotacoes.py /caminho/para/anotacoes-amazonia.json
```

A importação confere ocorrência, versão do PDF, autor, data, evidência e campos obrigatórios. Correções de anotações existentes exigem `--substituir` e preservam a versão anterior. Gerar o caderno não cria rótulos humanos. Para servir apenas o caderno local: `uv run --locked python -m http.server 8765 --bind 127.0.0.1 --directory data/annotation/revisao`.

## Verificação

```sh
uv run --locked python -m unittest discover -s tests -v
git diff --check
```

Os testes protegem integridade dos originais, mudanças de versão, limites de coleta, identificação de páginas e coordenadas, leitura de colunas, alternativas incompletas e reprodução. Fixtures sintéticas ficam somente nos testes e nunca entram no corpus histórico.

## Documentação e dados

- [Protocolo](docs/protocolo.md), [decisões posteriores](docs/decisoes.md) e [texto original preservado](docs/protocolo-original.txt).
- [Inventário nacional inicial](docs/notas-inventario.md) e [cadastros históricos 2017–2024](docs/notas-historico-ies.md).
- [Notas da triagem documental](docs/notas-triagem-demais.md) e [dicionário de dados](docs/dicionario-dados.md).
- Ampliação C3: [Sul/Sudeste](docs/notas-triagem-sul-sudeste-c3.md), [Nordeste/Centro-Oeste](docs/notas-triagem-ne-co-c3.md) e [auditoria temporal UFAM](docs/notas-datas-ciclo3.md).
- Ampliação C4: [FUVEST](docs/notas-fuvest-ciclo4.md), [UFMS](docs/notas-ufms-ciclo4.md) e [datas e gabarito UFAM](docs/notas-datas-ciclo4.md).
- [Manual de revisão e anotação](docs/manual-anotacao.md).
- Registros em `data/registry/`; metadados dos itens e gabaritos em `data/processed/`; fila de revisão em `data/annotation/`.

Originais, extrações com enunciados e imagens permanecem locais e ignorados no Git enquanto não houver condição de redistribuição demonstrada. Metadados, código e resultados de cobertura são versionados. Não há licença geral aplicada aos materiais de terceiros.

Autoria do projeto: **Matheus Garcia**. Inventário, pesquisa documental, código e verificações iniciais preparados com assistência do **Codex**. Essa assistência não constitui anotação humana independente.
