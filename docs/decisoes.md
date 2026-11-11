# Registro de decisões

## D001 — 11/11/2026 — História e Geografia, procedimento único

A missão mais recente do usuário inclui **História e Geografia da Amazônia**. O usuário confirmou: “a ideia é história E geografia da amazonia, mas o procedimento é um só”. Essa decisão amplia o alvo substantivo das seções 1, 2, 3, 7, 9 e 13 do protocolo original, que tratavam Geografia como complemento de História. O original permanece preservado em `protocolo-original.txt`.

As duas disciplinas seguem o mesmo inventário, coleta, extração, classificação, revisão e análise. `disciplina` é um atributo dos itens e das evidências de programa, não uma bifurcação da infraestrutura.

- Cada disciplina conserva suas próprias questões regionais e seu denominador completo.
- Resultados conjuntos contam ocorrências distintas, sem duplicar itens interdisciplinares.
- A regra de três anos de previsão substantiva será verificada por processo e disciplina; não se somam evidências de disciplinas diferentes para confirmar recorrência em uma delas.
- As quatro categorias de regionalidade se aplicam ao conhecimento histórico ou geográfico substantivo necessário à resolução. Uma menção à Amazônia não é suficiente.
- Amazonas (estado), Amazônia e relações transregionais são atributos distintos.
- A janela de aplicações, os cortes temporais e as exigências de rastreabilidade, referência humana e direitos permanecem os do protocolo.

## D002 — 11/11/2026 — Primeiro ciclo verificável

Entrega: inventário nacional inicial de IES públicas com fonte e ano explícitos; triagem documental inicial; coleta de documentos oficiais; extração por página; segmentação piloto verificável; relatório de cobertura reproduzível.

Aceite: originais com SHA-256, URLs e data de coleta; dados sem fontes inventadas; separação entre evidência observada e inferência; comandos documentados; verificações de integridade executadas. A coleta piloto não substitui o levantamento nacional e não autoriza conclusões de incidência antes da revisão e dos denominadores completos.

## D003 — 11/11/2026 — Custos e anotação

Não executar chamadas pagas de IA sem orçamento definido. Classificações feitas pelo Codex são assistência de IA, nunca referência humana. Métricas contra humanos permanecem indisponíveis até existir anotação humana identificada e conjuntos separados por prova e conteúdo equivalente. Ausência de anotação não será convertida em F1 zero nem em concordância perfeita.

## D004 — 11/11/2026 — Originais e reprodução

Originais, extrações com enunciados e imagens permanecem locais e ignorados no Git enquanto não houver condição de redistribuição verificada. Metadados, hashes, fontes, código e resultados de cobertura podem ser versionados. Um comando de coleta recupera os originais oficiais quando disponíveis; o cache evita baixar novamente um arquivo íntegro.

O ambiente inicial usa Python 3.12.12 e Poppler. OCR ausente ou texto insuficiente gera pendência explícita; o programa não inventa texto. O relatório inicial mede cobertura e integridade documental, sem afirmar resultados temáticos ainda não validados.

## D005 — 11/11/2026 — Falha real de extração e versão das fontes

O Poppler 26.04.0 abortou em PDFs oficiais recentes da UFAM. Foi acrescentado pypdf 7.0.1, fixado no lockfile, como motor alternativo. A saída e o erro do motor primário são preservados e o motor efetivamente utilizado aparece no manifesto. As extrações alternativas não afirmam ter coordenadas. Permanecem caracteres U+FFFD em editais; renderização legível não é justificativa para inventar a transcrição.

Uma recuperação de acervo em cópia sem PDFs deve obter os hashes conhecidos. Se a fonte publicar bytes diferentes no mesmo URL, o procedimento preserva a divergência e recusa a atualização silenciosa. Atualizações aceitas exigem `--atualizar` explícito; regras de segmentação e análises vinculadas à versão anterior precisam ser reexaminadas.

A revisão independente também corrigiu duas referências: páginas de programa da UEPG antes associadas ao manual de incorporação e a paginação UEMA, cuja página impressa 66 corresponde à posição 98 no PDF de 213 páginas. A fonte programática passa a ter identificador explícito; páginas impressas e físicas ficam em campos distintos.

## D006 — 11/11/2026 — Gabarito normalizado e anulação

Os gabaritos foram vinculados por `ocorrencia_id` em tabela própria, sem duplicar uma resposta em campos provisórios da segmentação. O piloto encontrou uma anulação oficial, PSC2026 E2/UFAM questão 27, que permanece com alternativa vazia. Isso não exclui a questão do indicador de cobrança aplicada.

As seis páginas relevantes de gabarito foram inspecionadas pelo Codex; isso é conferência assistida por IA. A revisão humana e a confirmação das versões de caderno permanecem pendentes. O banco educacional continua sem itens liberados.
