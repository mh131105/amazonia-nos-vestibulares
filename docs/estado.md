# Estado do estudo e continuidade

Ciclo 2 — 11/11/2026. Classificação do ciclo anterior: **progresso**, verificado no commit `e853054`. Este ciclo também produz **progresso**; o estudo permanece ativo e incompleto.

## Entrega deste ciclo

- Inventário histórico oficial de 2017–2024: **2.459 observações anuais, 334 códigos públicos ou Especiais candidatos**, dos quais 331 têm indicação pública em algum ano. A fotografia inicial de 2024, com 317 IES, foi preservada.
- Fila nacional de 334 códigos: sete IES com triagem parcial e as demais ainda sem triagem de processos. Nenhuma IES foi declarada esgotada por ter um processo examinado.
- **121 vínculos documentais, correspondentes a 120 PDFs oficiais distintos**, com hash, origem e extração; **26 aplicações identificadas**, incluindo uma futura no corte e oito com data exata ainda pendente.
- **23 cadernos e 300 ocorrências**, 150 de História e 150 de Geografia. São 299 estruturas textuais A–E e um caso de alternativas gráficas ainda pendente.
- **300 vínculos de gabarito**: 290 alternativas publicadas e dez anulações. A revisão humana e a conferência de versões continuam pendentes.
- Matheus foi definido pelo usuário como anotador. O caderno local de revisão reúne 300 itens e 372 regiões de origem, sem gabaritos ou predições de regionalidade. A fila real continua sem rótulos humanos.
- **90 testes** passaram. Foram verificados hashes, relações, origem de caixas geométricas, importação de anotações e preservação das versões. O teste interativo usa somente uma página fictícia e não preenche os dados reais.

O acervo atual inclui UFAM, UFRR e UERR. UERR alcançou três anos de previsão regional no processo (2022, 2025 e 2026). UFRR continua com dois anos confirmados: fontes históricas oficiais estão indisponíveis e não foram substituídas por espelhos não autenticados.

## Achados que afetam a comparação

PSC2021 E1/E2 ocorreu em 06/03/2022 para séries cursadas em 2020; PSC2022 E1/E2 ocorreu em 23/10/2022 para séries de 2021. Uma célula anual admite múltiplas aplicações. Ano letivo, edição, ingresso e data de aplicação permanecem separados.

A ampliação encontrou Geografia regional nas etapas 1/2 anteriores a 2024 e programas sem previsão amazônica explícita em seções examinadas. Esses achados documentais não são incidência de questões nem efeito da reforma. As oito datas pendentes não entram como datas observadas no contraste.

UERR mudou de banca e de organização das disciplinas. Banca e formato são preservados no registro. Os 17 códigos históricos não encontrados em 2024 e os 35 com diferenças textuais não são automaticamente instituições extintas ou mudanças jurídicas comprovadas.

## Revisão por Matheus

Abra `data/annotation/revisao/index.html` ou o servidor local do README. Confira o PDF, salve suas anotações e exporte o JSON para guardar cópia. `scripts/importar_anotacoes.py` valida e incorpora o arquivo, preservando versões anteriores. Não há anotação humana inferida a partir da configuração do nome.

A anotação é necessária para a referência humana e a avaliação, mas ainda há trabalho documental independente. Não existe teste humano congelado, baseline avaliado ou métricas de IA. Nenhum indicador de incidência foi publicado nem item liberado ao banco educacional.

## Pendências do protocolo completo

1. Completar mudanças institucionais 2025–2026, e-MEC/fontes históricas, natureza dos Especiais e vínculos jurídicos entre códigos.
2. Triar os processos dos demais códigos da fila nacional e ampliar casos fora da Região Norte. As leituras de UEMA, UNEMAT e UEPG são parciais; não excluem instituições inteiras.
3. Corroborar oito datas efetivas e auditar as retificações já coletadas; completar todas as etapas e aplicações da década, incluindo anos sem previsão regional.
4. Resolver UFRR/UEA/UERR antigos por alternativas oficiais autorizadas, sem contornar controles de acesso.
5. Auditar as referências normativas S2–S6 com URLs e implementação local; calendário escolar não prova alteração simultânea nas provas.
6. Validar OCR em PDFs digitalizados reais e revisar enunciados, figuras, alternativas, gabaritos e textos compartilhados.
7. Completar tópicos de programa, taxonomia e equivalência de conteúdos. Obter referência humana, partições por prova/grupo e teste congelado antes dos ajustes finais.
8. Avaliar extração, detecção, temas e vínculos contra humanos e método simples. Orçamento de API permanece indefinido; o pipeline não fez chamadas pagas de modelos.
9. Calcular indicadores com denominadores íntegros, contraste temporal e sensibilidades. Publicação externa, relatório final e exportação educacional dependem das revisões, cobertura e direitos.

## Próxima ação

Matheus pode começar a anotação no caderno. Em paralelo, o próximo ciclo documental deve corroborar as datas pendentes, auditar retificações e avançar na fila nacional, especialmente os códigos históricos ausentes em 2024 e os processos fora do Norte. A falta de rótulos humanos não deve interromper esse trabalho independente.

## Retomada e reprodução

Leia as decisões, os relatórios atuais e `reports/verificacao-ciclo2.json`. Os comandos estão no README. `reports/verificacao-ciclo1.json` é evidência histórica da versão do commit `e853054`, não uma validação do manifesto atual. Confira `git status` e preserve anotações preenchidas antes de qualquer modificação.
