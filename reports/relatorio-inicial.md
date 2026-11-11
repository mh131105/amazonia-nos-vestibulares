# História e Geografia da Amazônia nos vestibulares públicos

Relatório de implantação documental — versão 0.1.0. Referência: 11/11/2026, Manaus.

## Resumo

O inventário inicial reúne **317 IES da rede pública no Censo 2024**. A triagem inicial registra **18 processos** de **7 IES**. O piloto segmentou **84 ocorrências** em **6 cadernos**, sendo **42 de História** e **42 de Geografia**.

Essas quantidades descrevem o trabalho documental e os itens extraídos. Ainda não respondem qual é a incidência regional, o que mudou nas provas ou como a IA se compara a humanos. O estudo e o inventário histórico permanecem em andamento.

## Pergunta e seleção

O estudo investiga a previsão nos programas e a cobrança substantiva de conhecimentos históricos e geográficos da Amazônia. As disciplinas usam o mesmo procedimento e denominadores próprios. A motivação sobre procura e dificuldade é uma hipótese; os documentos não demonstram demanda comercial nem dificuldade empírica.

A fotografia nacional de 2024 não substitui o histórico de 2017–2026. Ela inclui instituições de todas as regiões, sem filtro geográfico:

| Região da sede | IES públicas em 2024 |
| --- | ---: |
| Centro-Oeste | 27 |
| Nordeste | 66 |
| Norte | 24 |
| Sudeste | 166 |
| Sul | 34 |

Fonte: [microdados oficiais do Inep](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-da-educacao-superior). `data/registry/fontes_inventario.json` identifica membro, coleta e hashes. As 28 instituições de categoria Especial foram conservadas pelo campo de rede pública e exigem verificação da esfera administrativa.

## Evidências iniciais de programa

O PSC/UFAM atende ao limiar documental de três anos no processo para cada disciplina, pelas evidências atualmente localizadas. História aparece em 2019, 2024, 2025 e 2026; Geografia em 2024, 2025 e 2026. O terceiro ano de Geografia inclui a etapa 2: isso não demonstra três anos de previsão na etapa 3. Fontes, páginas, retificações e revisão pendente estão nas tabelas de processos e evidências.

Na UFRR, há dois anos de programa regional verificados (aplicações 2024 e 2025): caso auxiliar para o limiar de dois anos, ainda candidato ao corpus principal. UERR possui evidência em 2022. UEA apresenta pendências de calendário e acesso. As leituras iniciais de UEMA e UEPG não confirmaram previsão amazônica substantiva nas edições examinadas; a UNEMAT exige autenticação documental. Nenhum desses achados exclui automaticamente uma instituição inteira ou toda a década.

Essas decisões são triagem assistida por IA, com revisão humana pendente. `evidencias-programa.csv` contém pistas documentais, não o inventário integral de tópicos nem vínculos de cada questão ao programa.

## Acervo e integridade

| Aplicação do piloto | Data efetiva registrada | Etapa | História | Geografia |
| --- | --- | --- | ---: | ---: |
| ufam-psc2020-e3 | 2019-12-01 | 3 | 6 | 6 |
| ufam-psc2025-e3 | 2024-11-24 | 3 | 6 | 6 |
| ufrr-vestibular2025-pi | 2024-11-24 | unica | 9 | 9 |
| ufam-psc2026-e3 | 2025-11-30 | 3 | 6 | 6 |
| ufrr-vestibular2026-pi | 2025-11-30 | unica | 9 | 9 |
| ufam-psc2026-e2 | 2026-06-14 | 2 | 6 | 6 |

**83/84** itens apresentam a estrutura textual A–E. Os demais exigem revisão de alternativas gráficas ou segmentação. Essa conferência estrutural não garante integridade de enunciados, imagens, legendas ou textos compartilhados. Todos os itens do piloto mantêm `apto_denominador_validado=false`.

Registros de gabarito vinculados: **84**. A extração de resposta oficial não é validação humana do item. Anulações permanecem identificadas; não são descartadas da cobrança aplicada.

Originais são preservados por SHA-256. Extrações bruta e normalizada ficam em camadas separadas, com página e coordenadas quando disponíveis. Falhas reais do Poppler acionam pypdf e são registradas; há caracteres danificados em editais recentes e páginas visuais sinalizadas. Os materiais experimentados têm camada digital; processamento de documentos escaneados e OCR ainda exige validação própria.

O edital PSC2027 E3 registra aplicação futura em 29/11/2026, depois do corte. Não entra no corpus de questões desta versão. Ausência de caderno em um processo não vira zero questões. A grade `cobertura-anual.csv` registra investigação pendente, sem afirmar que houve prova em cada célula.

Na UFRR, PI e PSS-E3 compartilham caderno, mas o subconjunto para pontuação PSS é diferente. O piloto representa PI e não duplica o mesmo documento como outra observação agregada.

## Comparação temporal planejada

| Estrato com questões segmentadas | 2017–2021: cadernos | 2022–2023: cadernos | 2024: cadernos | 2025–2026: cadernos | Contraste de incidência |
| --- | ---: | ---: | ---: | ---: | --- |
| UFAM / ufam-psc / 2 | Sem caderno segmentado | Sem caderno segmentado | Sem caderno segmentado | 1 | Não calculado |
| UFAM / ufam-psc / 3 | 1 | Sem caderno segmentado | 1 | 1 | Não calculado |
| UFRR / ufrr-integral / unica | Sem caderno segmentado | Sem caderno segmentado | 1 | 1 | Não calculado |

O contraste obrigatório será 2017–2021 versus 2024–2026, com 2022–2023 fora desse contraste e posterior separado em 2024 e 2025–2026. O piloto UFAM E3 contém cadernos dos dois lados, mas ainda não tem classificações regionais e denominadores validados. Os outros estratos não simulam uma comparação pareada inexistente. Não foi estimado efeito causal da reforma.

Sensibilidades pendentes: limiar de dois anos, exclusão de 2026 (2017–2025, nove anos), painel comparável versus acervo total, itens interdisciplinares e versão válida para pontuação. Ainda não há indicador final a submeter a essas sensibilidades.

## Avaliação da IA

Linhas com autor, data e regionalidade preenchidos na fila: **0**. O preenchimento da fila é uma etapa de trabalho e ainda requer auditoria; linhas vazias não são anotações. Não existe teste humano congelado, baseline avaliado ou métricas de extração/classificação nesta versão. F1, precisão, revocação e custo comparativo permanecem indisponíveis.

As investigações e inspeções do Codex foram identificadas como assistência de IA. O pipeline não fez chamadas pagas de API de modelos; custos da assistência no aplicativo não foram quantificados. A metodologia futura está em `docs/manual-anotacao.md`.

## Limitações e reuso

Faltam reconciliação institucional histórica, triagem da maior parte das IES, cobertura da década, OCR validado, revisão dos itens, grupos de equivalência, tópicos completos, classificação, avaliação humana e análise substantiva. Não há exportação liberada para o banco educacional. Direitos dos originais e imagens ainda precisam ser examinados por documento.

Os metadados e referências estão preparados para continuidade. Originais, imagens e enunciados permanecem locais enquanto não houver condição de redistribuição demonstrada; o Git conserva código, metadados e relatório.

## Reprodução

Use a sequência do README. `uv run python scripts/pipeline.py relatorio` reconstrói este relatório sem rede ou IA a partir dos registros versionados. `reports/manifesto-cobertura.json` registra hashes das entradas e saídas. A obtenção e nova extração dos originais são modos separados, dependentes da disponibilidade das fontes oficiais.

Próxima entrega: expandir o inventário histórico e as aplicações dos processos; revisar os itens do piloto e formar referência humana antes de avaliar ou ajustar o classificador.
