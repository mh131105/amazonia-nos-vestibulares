"""Aplica a auditoria C4 preservando suas fontes e as decisões anteriores."""

import json
from datetime import date


def packed(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def integrar(registry, applications, evidence, processes, expected):
    path = registry / 'auditoria-datas-c4.json'
    if not path.exists():
        return
    audit = json.loads(path.read_text(encoding='utf-8'))
    by_app = {row['aplicacao_id']: row for row in applications}
    by_doc = {row['documento_id']: row for row in expected}
    by_process = {row['processo_id']: row for row in processes}
    verified_ids = set()
    for check in audit['verificacoes']:
        actual = check.get('data_aplicacao_confirmada')
        if not actual:
            continue
        if (check['fonte_tipo'] != 'historico_administrativo_pos_evento'
                or check['resultado'] != 'confirmada_por_historico_administrativo_pos_evento'
                or not check.get('sha256_arquivo') or not check.get('evidencia_curta') or not check.get('pagina_pdf')):
            raise ValueError('Auditoria C4 sem relato primário explícito de realização')
        app = by_app[check['aplicacao_id']]
        if app.get('data_aplicacao') not in (None, '', actual):
            raise ValueError('Auditoria C4 conflita com data efetiva já registrada')
        day = date.fromisoformat(actual)
        if not date(2017, 1, 1) <= day <= date(2026, 11, 11):
            raise ValueError('Data auditada C4 fora da janela')
        app.update(data_aplicacao=actual, ano_aplicacao=day.year,
                   periodo_calendario='2017-2021' if day.year <= 2021 else '2022-2023' if day.year <= 2023 else '2024' if day.year == 2024 else '2025-2026',
                   fonte_data_anterior=app.get('fonte_data_anterior') or app['fonte_data'], fonte_data=check['fonte_url'],
                   localizacao_data=check['seção/página'], qualidade_evidencia_data=check['resultado'],
                   fonte_auditoria_data='data/registry/auditoria-datas-c4.json',
                   resultado_auditoria_data=check['resultado'], fonte_data_sha256=check['sha256_arquivo'],
                   fonte_corrobora=packed(check.get('fonte_corrobora', [])),
                   situacao='aplicada_data_corrobora_por_fonte_primaria')
        verified_ids.add(app['aplicacao_id'])
        for item in evidence:
            if item.get('aplicacao_id') != app['aplicacao_id']:
                continue
            discipline = item['disciplina']
            if discipline not in {'historia', 'geografia'}:
                continue
            fields = ['anos_programa_verificavel_' + discipline]
            if item['previsao_regional'] in {'substantiva', 'previsao_regional_verificada'}:
                fields.append('anos_previsao_' + discipline)
            for field in fields:
                process = by_process[app['processo_id']]
                values = set(json.loads(process.get(field) or '[]'))
                values.add(day.year)
                process[field] = packed(sorted(values))
    additions = []
    for source in audit.get('fontes_data_adicionais', []):
        for app_id in source['aplicacoes_ids']:
            if app_id not in verified_ids:
                raise ValueError('Evidência administrativa sem data confirmada correspondente')
            doc_id = app_id + '-historico-aplicacao-setembro2023'
            by_app[app_id]['documento_id_evidencia_data'] = doc_id
            additions.append({**source, 'documento_id': doc_id, 'aplicacao_id': app_id})
    additions.extend(row for row in audit.get('documentos_adicionais', [])
                     if row.get('preservacao_sugerida') == 'local_ignorada_no_git')
    for source in additions:
        app = by_app[source['aplicacao_id']]
        row = {'documento_id': source['documento_id'], 'aplicacao_id': app['aplicacao_id'],
               'instituicao_sigla': app['instituicao_sigla'], 'processo_id': app['processo_id'],
               'tipo': source['tipo'], 'publicador': source['publicador'],
               'url_origem': source['url_origem'], 'fonte_url': source['fonte_url'],
               'sha256_auditado': source['sha256_auditado'], 'origem_oficial': True,
               'condicoes_uso': 'nao_verificadas', 'redistribuicao_autorizada': None,
               'escopo_coleta': 'auditoria_documental_ciclo4', 'extracao_automatica': False,
               'observacao': 'Preservação local do original; somente evidência institucional do certame nos metadados. Identificações pessoais e dados financeiros fora da evidência não são transcritos.'}
        old = by_doc.get(row['documento_id'])
        if old:
            if old['url_origem'] != row['url_origem'] or old.get('sha256_auditado') not in (None, row['sha256_auditado']):
                raise ValueError('Documento auditado C4 conflita com versão preservada')
            old.update(row)
        else:
            expected.append(row)
            by_doc[row['documento_id']] = row
    for check in audit.get('auditoria_gabaritos', []):
        row = by_doc[check['documento_id']]
        if (row['url_origem'] != check['url_arquivo'] or row.get('sha256_auditado') != check['sha256_arquivo']
                or check.get('mesmos_bytes_c3') is not True):
            raise ValueError('Finalidade C4 não corresponde ao original auditado C3')
        row.update(finalidade_documental=check['resultado'],
                   fonte_auditoria_finalidade='data/registry/auditoria-datas-c4.json',
                   fonte_corrobora_finalidade=check['fonte_indice_edoc'])
