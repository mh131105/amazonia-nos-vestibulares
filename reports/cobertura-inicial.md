# Cobertura documental inicial

Documentos previstos no piloto: **24**. Coletados: **24**. Com extração registrada: **24**.

Essas contagens descrevem somente os documentos selecionados para testar o procedimento. Não medem cobertura nacional, edições esperadas na década, incidência regional ou dificuldade das questões.

| Documento | Tipo | Coleta | Páginas | Extração |
| --- | --- | --- | --- | --- |
| ufam-psc2020-e3-edital | edital | coletado | 26 | texto_extraido_nao_revisado |
| ufam-psc2020-e3-prova | prova | coletado | 20 | revisar_ocr_ou_pagina_visual |
| ufam-psc2020-e3-gabarito-definitivo | gabarito_definitivo | coletado | 1 | texto_extraido_nao_revisado |
| ufam-psc2025-e3-edital | edital | coletado | 31 | revisar_codificacao |
| ufam-psc2025-e3-prova | prova | coletado | 20 | revisar_ocr_ou_pagina_visual |
| ufam-psc2025-e3-gabarito-definitivo | gabarito_definitivo | coletado | 1 | texto_extraido_nao_revisado |
| ufam-psc2026-e3-edital | edital | coletado | 31 | revisar_codificacao |
| ufam-psc2026-e3-prova | prova | coletado | 20 | revisar_ocr_ou_pagina_visual |
| ufam-psc2026-e3-gabarito-definitivo | gabarito_definitivo | coletado | 1 | texto_extraido_nao_revisado |
| ufam-psc2026-e2-edital | edital | coletado | 20 | revisar_codificacao |
| ufam-psc2026-e2-prova | prova | coletado | 16 | revisar_ocr_ou_pagina_visual |
| ufam-psc2026-e2-gabarito-definitivo | gabarito_definitivo | coletado | 1 | texto_extraido_nao_revisado |
| ufrr-vestibular2026-pi-manual | manual | coletado | 54 | revisar_ocr_ou_pagina_visual |
| ufrr-vestibular2026-pi-prova | prova | coletado | 32 | texto_extraido_nao_revisado |
| ufrr-vestibular2026-pi-gabarito-definitivo | gabarito_definitivo | coletado | 4 | texto_extraido_nao_revisado |
| ufam-psc2020-e3-retificacao-01 | retificacao_01 | coletado | 2 | texto_extraido_nao_revisado |
| ufam-psc2020-e3-retificacao-02 | retificacao_02 | coletado | 2 | texto_extraido_nao_revisado |
| ufam-psc2025-e3-retificacao-01 | retificacao_01 | coletado | 1 | texto_extraido_nao_revisado |
| ufam-psc2026-e3-retificacao-01 | retificacao_01 | coletado | 1 | texto_extraido_nao_revisado |
| ufam-psc2026-e2-retificacao-01 | retificacao_01 | coletado | 2 | texto_extraido_nao_revisado |
| ufam-psc2027-e3-edital-consolidado | edital_consolidado | coletado | 31 | texto_extraido_nao_revisado |
| ufrr-vestibular2025-pi-manual | manual | coletado | 61 | revisar_ocr_ou_pagina_visual |
| ufrr-vestibular2025-pi-prova | prova | coletado | 31 | texto_extraido_nao_revisado |
| ufrr-vestibular2025-pi-gabarito-definitivo | gabarito_definitivo | coletado | 6 | texto_extraido_nao_revisado |

A tabela CSV inclui os URLs e os hashes dos originais. `texto_extraido_nao_revisado` não significa seção disciplinar completa: a conferência de itens, imagens, gabaritos e retificações é uma etapa própria.

Páginas com menos de dez palavras são sinalizadas para inspeção visual/OCR; podem ser páginas de imagens ou em branco. O sinalizador não diagnostica sozinho um PDF digitalizado.

Não há referência humana anotada nem avaliação da IA nesta versão. Não foram executadas chamadas pagas de IA.

Reprodução: `uv run python scripts/pipeline.py relatorio`. A geração usa somente os registros locais; não requer rede ou IA.
