# Estado do estudo e continuidade

Ciclo 1 — 11/11/2026. Classificação: **progresso**, com alterações de dados, código, evidências e documentação. A meta do estudo permanece ativa; este ciclo não conclui o projeto nem o levantamento nacional.

## Entrega verificada do ciclo

Foi implantado um procedimento único para História e Geografia: inventário nacional inicial → triagem → coleta → extração por página → segmentação por layout → vínculo a gabaritos → fila de revisão → relatório de cobertura.

- 317 IES da rede pública no cadastro Inep de 2024, nas 27 UFs e cinco regiões; 28 têm categoria Especial e esfera a verificar.
- 18 processos em sete IES registrados na triagem inicial; 22 evidências disciplinares de programa.
- Nove aplicações identificadas no registro, incluindo uma futura no corte. Seis têm cadernos coletados e segmentados; as outras não são tratadas como ausência de cobrança.
- 24 PDFs oficiais coletados, com hashes, origem e extração registrada. Esse conjunto inclui a evidência de uma aplicação futura, não suas questões.
- 84 ocorrências, 42 de cada disciplina; 83 com estrutura textual A–E e uma com alternativas gráficas pendentes.
- 84 vínculos a gabaritos oficiais: 83 alternativas publicadas e uma anulação, UFAM PSC2026 E2, questão 27. Conferência de versão e revisão humana pendentes.
- Fila de revisão com 84 linhas sem rótulos humanos, acompanhada de manual. Nenhuma linha vazia é contada como referência humana.
- Relatórios e tabelas reconstruídos a partir dos registros, com manifesto de hashes.

As verificações incluem integridade dos originais e extrações, chaves e relações, datas, faixas de questões, alternativas, reconstrução da leitura por colunas, preservação de anulações, recuperação de arquivos ausentes e rejeição de atualizações silenciosas. Os testes usam exclusivamente dados sintéticos temporários. O procedimento também foi reexecutado no acervo real e os artefatos determinísticos foram comparados por hash.

## Pendências diante do protocolo completo

| Entrega | Estado e critério restante |
| --- | --- |
| Protocolo e decisões | Escopo atualizado e original preservado. Referências normativas S2–S6 e histórico de implementação local ainda precisam de auditoria com URLs verificáveis. |
| Inventário nacional | Fotografia 2024 concluída; reconciliar 2017–2023, criações/alterações 2025–2026, categoria Especial e fontes históricas/e-MEC. |
| Seleção de processos | Triagem inicial, com evidências e lacunas; investigar a maior parte das IES e demonstrar o alcance da busca antes de qualquer alegação de censo. |
| Cobertura documental | Piloto verificado; completar todas as aplicações dos processos elegíveis na década. A grade anual contém células de investigação, não provas presumidas. |
| Extração | PDFs digitais e duas organizações institucionais experimentadas; corrigir caracteres danificados com fonte visual e validar OCR em documentos escaneados reais. |
| Itens e tópicos | Segmentação inicial concluída; conferir texto, figuras, alternativas, gabaritos, equivalências e tópicos integrais dos programas. |
| Referência humana | Ainda não existe; revisar a fila e obter anotações identificadas. Meta de pelo menos 200 itens quando o corpus permitir. |
| Avaliação da IA | Pendente: baseline, partições por prova/grupos equivalentes, teste humano congelado, prompts versionados, métricas e erros. Orçamento de API não definido. |
| Análise substantiva | Pendente: incidência, temas, vínculo ao programa, demandas, contraste 2017–2021 versus 2024–2026 e sensibilidades. Os relatórios atuais são de implantação e cobertura. |
| Relatório público | Rascunho legível e reproduzível no repositório local. Publicação externa, séries finais, figuras e conclusões dependem dos dados e revisões. |
| Exportação educacional | Nenhum item liberado; exige completude, gabarito verificado, revisão e condições de uso compatíveis. |

## Próxima ação

1. Importar e reconciliar os cadastros nacionais históricos, preservando o inventário de 2024 como fotografia com fonte e ano próprios.
2. Expandir aplicações e documentos do PSC/UFAM em todas as etapas e anos; obter o terceiro ano de programa da UFRR e resolver as pendências documentais UEA/UERR por alternativas públicas autorizadas.
3. Auditar mais processos fora da Região Norte, seguindo a fila nacional; não restringir a investigação aos casos encontrados neste piloto.
4. Revisar os itens piloto e registrar anotações humanas. Preparar agrupamento de equivalências e teste antes dos ajustes finais da classificação.
5. Só depois calcular indicadores com denominadores íntegros e comparar a IA à referência humana.

## Retomada

Leia este arquivo, `docs/decisoes.md` e os dois relatórios em `reports/`. Execute a verificação e os testes do README. Confira `git status` antes de modificar dados; rótulos humanos preenchidos devem ser preservados. O acervo local está ignorado no Git e pode ser recuperado pelos comandos documentados, sujeito à disponibilidade e à identidade dos arquivos oficiais.
