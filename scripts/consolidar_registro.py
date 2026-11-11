#!/usr/bin/env python3
"""Consolida as notas documentais em tabelas de processos, aplicações e evidências."""

import csv
import json
import hashlib
from collections import defaultdict
from datetime import date
from pathlib import Path

if __package__:
    from .pipeline import ROOT, REGISTRY, read_jsonl, read_csv, write_csv, write_jsonl
    from .triagem_nacional import integrar, documentos_selecionados
    from .expansao_documental import integrar as integrar_expansoes
    from .auditoria_temporal import integrar as integrar_auditoria_temporal
else:
    from pipeline import ROOT, REGISTRY, read_jsonl, read_csv, write_csv, write_jsonl
    from triagem_nacional import integrar, documentos_selecionados
    from expansao_documental import integrar as integrar_expansoes
    from auditoria_temporal import integrar as integrar_auditoria_temporal

ALIASES = {
    'ufam_psc_2019_e3': 'ufam-psc2020-e3',
    'ufam_psc_2024_e3': 'ufam-psc2025-e3',
    'ufam_psc_2025_e3': 'ufam-psc2026-e3',
    'ufam_psc_2026_e2': 'ufam-psc2026-e2',
}
PROCESS_ALIASES = {'ufrr_pi': 'ufrr-integral'}


def packed(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def period(year):
    if year <= 2021:
        return '2017-2021'
    if year <= 2023:
        return '2022-2023'
    return '2024' if year == 2024 else '2025-2026'


def load_audit_c3(registry):
    path = registry / 'auditoria-datas-c3.json'
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}


def audited_application(item, verification):
    """Sobrepõe evidência C3 sem reescrever as fontes de triagem C2."""
    if not verification:
        return item
    result = dict(item)
    temporal = dict(item['evidencia_data'])
    temporal.update(fonte_cronograma=temporal['url'],
                    localizacao_cronograma=temporal.get('localizacao'),
                    fonte_auditoria_data='data/registry/auditoria-datas-c3.json',
                    resultado_auditoria_data=verification['resultado'],
                    fonte_corrobora=packed(verification.get('fonte_corrobora', [])))
    actual = verification.get('data_aplicacao_confirmada')
    if actual:
        if (verification.get('fonte_tipo') != 'noticia_institucional_pos_evento'
                or verification.get('resultado') != 'confirmada_por_noticia_institucional_pos_evento'):
            raise ValueError('Data C3 sem confirmação primária de realização')
        if item.get('data_aplicacao') not in (None, actual):
            raise ValueError('Data C3 diverge da data efetiva já registrada')
        result.update(data_aplicacao=actual, situacao='aplicada_data_corrobora_por_fonte_primaria')
        temporal.update(url=verification['fonte_url'], localizacao=verification['seção/página'],
                        natureza=verification['resultado'])
    result['evidencia_data'] = temporal
    return result


def integrar_auditoria_c3(registry, applications, evidence, processes, expected, *, audit=None):
    """Acrescenta vínculos e finalidade; não salva arquivos nem resolve pendências."""
    audit = load_audit_c3(registry) if audit is None else audit
    by_application = {row['aplicacao_id']: row for row in applications}
    pairs = {(row['aplicacao_id'], row['url_origem']): row for row in expected}
    additions = [(row, [row['aplicacao_id']], 'retificacao')
                 for row in audit.get('retificacoes_adicionais', [])]
    additions += [(row, row['aplicacoes'], 'comunicado')
                  for row in audit.get('comunicados_adicionais', [])]
    for source, application_ids, kind in additions:
        for application_id in application_ids:
            app = by_application.get(application_id)
            if app is None:
                raise ValueError('Documento da auditoria C3 sem aplicação')
            url = source['fonte_url']
            pair = application_id, url
            if pair not in pairs:
                suffix = '-' + hashlib.sha256(url.encode()).hexdigest()[:8] if kind == 'retificacao' else ''
                row = {'documento_id': application_id + '-' + kind + suffix,
                       'aplicacao_id': application_id, 'instituicao_sigla': app['instituicao_sigla'],
                       'processo_id': app['processo_id'], 'tipo': kind,
                       'publicador': 'COMPEC/UFAM', 'url_origem': url,
                       'fonte_url': source['fonte_indice'], 'origem_oficial': True,
                       'condicoes_uso': 'nao_verificadas', 'redistribuicao_autorizada': None,
                       'escopo_coleta': 'auditoria_documental_ciclo3',
                       'transporte': 'curl_tls_sistema',
                       'observacao': source.get('resultado', 'Reabertura de entrega de identidade; sem alteração identificada do programa ou dia de prova.')}
                expected.append(row)
                pairs[pair] = row
            if source.get('sha256'):
                pairs[pair]['sha256_auditado'] = source['sha256']
    by_id = {row['documento_id']: row for row in expected}
    for finding in audit.get('auditoria_gabaritos', []):
        row = by_id.get(finding['documento_id'])
        if row is None or row['url_origem'] != finding['url_arquivo']:
            raise ValueError('Gabarito auditado C3 ausente ou com URL divergente')
        row.update(finalidade_documental=finding['resultado'],
                   sha256_finalidade_documental=finding['sha256_arquivo'],
                   sha256_auditado=finding['sha256_arquivo'],
                   fonte_auditoria_finalidade='data/registry/auditoria-datas-c3.json')
    if len({row['documento_id'] for row in expected}) != len(expected):
        raise ValueError('Documento duplicado na auditoria C3')
    return expected


def expand(registry, institutions, applications, evidence, processes):
    existing = {r['aplicacao_id'] for r in applications}
    process_by_id = {r['processo_id']: r for r in processes}
    expected_path = registry / 'documentos-esperados.jsonl'
    expected = read_jsonl(expected_path)
    audit = load_audit_c3(registry)
    verifications = {row['aplicacao_id']: row for row in audit.get('verificacoes', [])}
    if len(verifications) != len(audit.get('verificacoes', [])):
        raise ValueError('Aplicação repetida na auditoria C3')
    doc_pairs = {(r['aplicacao_id'], r['url_origem']) for r in expected}
    for path in sorted(registry.glob('expansao-*-c2.json')):
        source = json.loads(path.read_text(encoding='utf-8'))
        for original in source.get('aplicacoes', []):
            item = audited_application(original, verifications.get(original['aplicacao_id']))
            key, process_id = item['aplicacao_id'], item['processo_id']
            if key in existing:
                raise ValueError(f'Aplicação repetida na expansão: {key}')
            if process_id not in process_by_id:
                raise ValueError('Expansão sem processo previamente inventariado')
            actual = item.get('data_aplicacao')
            forecast = item.get('data_aplicacao_prevista')
            if not actual and not forecast:
                continue  # Pista sem data continua na fonte de triagem, sem aplicação temporal.
            day = date.fromisoformat(actual) if actual else None
            if day and not date(2017, 1, 1) <= day <= date(2026, 11, 11):
                raise ValueError('Aplicação fora da janela na expansão')
            temporal = item['evidencia_data']
            applications.append({
                'aplicacao_id': key, 'instituicao_id': institutions[item['instituicao_sigla']],
                'instituicao_sigla': item['instituicao_sigla'], 'processo_id': process_id,
                'etapa': item['etapa'], 'edicao': item['edicao'], 'ano_ingresso': item.get('ano_ingresso'),
                'banca': item.get('banca'), 'formato': item.get('formato'),
                'data_publicacao_edital': item.get('data_publicacao_edital'),
                'data_aplicacao': actual, 'ano_aplicacao': day.year if day else None,
                'data_prevista': forecast, 'situacao': item['situacao'],
                'periodo_calendario': period(day.year) if day else None,
                'fonte_data': temporal['url'], 'localizacao_data': temporal.get('localizacao'),
                'qualidade_evidencia_data': temporal.get('natureza'),
                'fonte_corrobora': temporal.get('fonte_corrobora'),
                'fonte_cronograma': temporal.get('fonte_cronograma'),
                'localizacao_cronograma': temporal.get('localizacao_cronograma'),
                'fonte_auditoria_data': temporal.get('fonte_auditoria_data'),
                'resultado_auditoria_data': temporal.get('resultado_auditoria_data'),
                'serie_alvo': item.get('serie_alvo'), 'ano_serie_alvo': item.get('ano_serie_alvo'),
                'regime_curricular_contexto': 'nao_validado_localmente',
                'alinhamento_explicito_prova': 'nao_verificado',
                'origem_anotacao': 'triagem_assistida_por_ia', 'revisao_humana': 'pendente'})
            existing.add(key)
            for program in item.get('programa', []):
                discipline = program['disciplina']
                positive = program['previsao_regional'] in {'substantiva', 'previsao_regional_verificada'}
                evidence.append({'evidencia_id': key + '-' + discipline, 'aplicacao_id': key,
                                 'processo_id': process_id, 'disciplina': discipline,
                                 'previsao_regional': program['previsao_regional'],
                                 'paginas_pdf': packed(program['paginas_pdf']),
                                 'paginas_impressas': packed(program['paginas_impressas']) if program.get('paginas_impressas') else None,
                                 'secao': program['localizacao'], 'trecho_curto': program.get('trecho_curto'),
                                 'fonte_url': program['fonte_url'], 'origem_anotacao': 'triagem_assistida_por_ia',
                                 'revisao_humana': 'pendente'})
                process = process_by_id[process_id]
                if day:
                    for field in ['anos_programa_verificavel_' + discipline] + (['anos_previsao_' + discipline] if positive else []):
                        values = set(json.loads(process.get(field) or '[]'))
                        values.add(day.year)
                        process[field] = packed(sorted(values))
            for doc in item.get('documentos', []):
                pair = key, doc['url']
                if pair in doc_pairs:
                    known = next(r for r in expected if (r['aplicacao_id'], r['url_origem']) == pair)
                    known['publicador'] = doc.get('publicador', item.get('banca') or item['instituicao_sigla'])
                    continue
                kind = doc['tipo']
                suffix = hashlib.sha256(doc['url'].encode()).hexdigest()[:8] if kind.startswith('retificacao') else None
                doc_id = key + '-' + kind.replace('_', '-') + ('-' + suffix if suffix else '')
                expected.append({'documento_id': doc_id, 'aplicacao_id': key,
                                 'instituicao_sigla': item['instituicao_sigla'], 'processo_id': process_id,
                                 'tipo': kind, 'publicador': doc.get('publicador', item.get('banca') or item['instituicao_sigla']),
                                 'url_origem': doc['url'], 'fonte_url': item['fonte_landing'],
                                 'origem_oficial': doc.get('origem_oficial', True),
                                 'condicoes_uso': 'nao_verificadas', 'redistribuicao_autorizada': None,
                                 'escopo_coleta': 'expansao_documental_ciclo2',
                                 'transporte': 'curl_tls_sistema' if 'antigocompec.ufam.edu.br' in doc['url'] else 'urllib',
                                 'observacao': doc.get('observacao', doc.get('titulo', 'Conferência do documento e retificações pendente.'))})
                doc_pairs.add(pair)
    integrar_auditoria_c3(registry, applications, evidence, processes, expected, audit=audit)
    for process in processes:
        if process['estado_triagem'].startswith('excluido'):
            continue
        enough = [d for d in ['historia', 'geografia'] if len(json.loads(process.get('anos_previsao_' + d) or '[]')) >= 3]
        if enough:
            process['estado_triagem'] = 'incluido_recorrencia_confirmada'
            process['motivo_e_pendencias'] = 'Recorrência de três anos por disciplina no processo: ' + ', '.join(enough) + '. Etapas, banca, vigência dos documentos e revisão humana devem permanecer identificadas; cobertura da década não concluída.'
    if len({r['documento_id'] for r in expected}) != len(expected):
        raise ValueError('Documento duplicado na expansão')
    for doc in expected:
        if 'antigocompec.ufam.edu.br' in doc['url_origem']:
            doc['transporte'] = 'curl_tls_sistema'
    return expected


def main():
    registry = ROOT / REGISTRY
    ufam = json.loads((registry / 'triagem_ufam.json').read_text(encoding='utf-8'))
    other = json.loads((registry / 'triagem_demais.json').read_text(encoding='utf-8'))
    with (registry / 'instituicoes.csv').open(encoding='utf-8', newline='') as stream:
        institutions = {row['sigla'].upper(): row['instituicao_id'] for row in csv.DictReader(stream)}
    sources = {row['fonte_id']: row for row in other['fontes']}
    applications, evidence, processes = [], [], []
    by_discipline = defaultdict(set)
    program_years = defaultdict(set)
    for item in ufam['aplicacoes']:
        application_id = ALIASES[item['aplicacao_id']]
        day = date.fromisoformat(item['data_aplicacao'])
        assert date(2017, 1, 1) <= day <= date(2026, 11, 11)
        applications.append({
            'aplicacao_id': application_id, 'alias_triagem': item['aplicacao_id'],
            'instituicao_id': institutions['UFAM'], 'instituicao_sigla': 'UFAM',
            'processo_id': 'ufam-psc', 'etapa': item['etapa'], 'edicao': item['edicao'],
            'ano_ingresso': item['ano_ingresso'], 'data_aplicacao': item['data_aplicacao'],
            'data_publicacao_edital': item['data_publicacao_edital'],
            'ano_aplicacao': day.year, 'data_prevista': None, 'situacao': item['situacao'],
            'periodo_calendario': period(day.year), 'fonte_data': item['evidencia_data']['url'],
            'localizacao_data': item['evidencia_data']['localizacao'],
            'qualidade_evidencia_data': item['evidencia_data'].get('natureza', 'capa_da_prova'),
            'fonte_corrobora': item['evidencia_data'].get('fonte_corrobora'),
            'serie_alvo': item.get('serie_alvo', item['etapa']),
            'ano_serie_alvo': item.get('ano_serie_alvo'),
            'regime_curricular_contexto': 'nao_validado_localmente',
            'alinhamento_explicito_prova': 'nao_verificado',
            'origem_anotacao': 'triagem_assistida_por_ia', 'revisao_humana': 'pendente'})
        for program in item['programa']:
            discipline = program['disciplina']
            program_years[discipline].add(day.year)
            if program['previsao_regional'] == 'substantiva':
                by_discipline[discipline].add(day.year)
            evidence.append({
                'evidencia_id': application_id + '-' + discipline, 'aplicacao_id': application_id,
                'processo_id': 'ufam-psc', 'disciplina': discipline,
                'previsao_regional': program['previsao_regional'], 'paginas_pdf': packed(program['paginas_pdf']),
                'secao': program['localizacao'], 'trecho_curto': program.get('trecho'),
                'fonte_url': next(d['url'] for d in item['documentos'] if d['tipo'] == 'edital_programa'),
                'origem_anotacao': 'triagem_assistida_por_ia', 'revisao_humana': 'pendente'})
    processes.append({
        'processo_id': 'ufam-psc', 'instituicao_id': institutions['UFAM'], 'instituicao_sigla': 'UFAM',
        'nome': 'Processo Seletivo Contínuo', 'etapas': packed(['1', '2', '3']),
        'estado_triagem': 'incluido_recorrencia_confirmada',
        'fonte_registro': 'data/registry/triagem_ufam.json',
        'fonte_url': ufam['aplicacoes'][0]['fonte_landing'],
        'localizacao_fonte': 'Editais anexos e evidências por aplicação na triagem UFAM',
        'anos_previsao_historia': packed(sorted(by_discipline['historia'])),
        'anos_previsao_geografia': packed(sorted(by_discipline['geografia'])),
        'anos_programa_verificavel_historia': packed(sorted(program_years['historia'])),
        'anos_programa_verificavel_geografia': packed(sorted(program_years['geografia'])),
        'motivo_e_pendencias': 'Três anos por disciplina no processo. Etapas separadas nas análises; Geografia E3 tem somente dois anos positivos observados. Completar aplicações, revisão e histórico institucional.',
        'revisao_humana': 'pendente'})
    future = ufam['aplicacoes_futuras_na_data_de_corte'][0]
    applications.append({
        'aplicacao_id': 'ufam-psc2027-e3', 'instituicao_id': institutions['UFAM'], 'instituicao_sigla': 'UFAM',
        'processo_id': 'ufam-psc', 'etapa': '3', 'edicao': future['edicao'],
        'ano_ingresso': future['ano_ingresso'], 'data_aplicacao': None, 'ano_aplicacao': None,
        'data_prevista': future['data_aplicacao_prevista'], 'situacao': future['situacao'],
        'periodo_calendario': None, 'fonte_data': future['edital_consolidado'],
        'localizacao_data': future['localizacao_data'], 'qualidade_evidencia_data': 'cronograma_futuro',
        'regime_curricular_contexto': 'nao_validado_localmente', 'alinhamento_explicito_prova': 'nao_verificado',
        'origem_anotacao': 'triagem_assistida_por_ia', 'revisao_humana': 'pendente'})
    for item in ufam['outros_processos_a_inventariar']:
        processes.append({
            'processo_id': 'ufam-' + item['processo'].lower(), 'instituicao_id': institutions['UFAM'],
            'instituicao_sigla': 'UFAM', 'nome': item.get('nome', item['processo']),
            'etapas': '[]', 'estado_triagem': item['estado'],
            'fonte_registro': 'data/registry/triagem_ufam.json', 'fonte_url': item['fonte'],
            'localizacao_fonte': item['localizacao'],
            'motivo_e_pendencias': item.get('pendencia', item.get('motivo')), 'revisao_humana': 'pendente'})
    for item in other['processos']:
        process_id = PROCESS_ALIASES.get(item['processo_id'], item['processo_id'].replace('_', '-'))
        reference = sources[item['fontes_ids'][0]] if item['fontes_ids'] else None
        row = {'processo_id': process_id, 'instituicao_id': institutions[item['instituicao_sigla']],
               'instituicao_sigla': item['instituicao_sigla'], 'nome': item['processo_nome'],
               'etapas': packed(item['etapas']), 'estado_triagem': item['status'],
               'fonte_registro': 'data/registry/triagem_demais.json',
               'fonte_url': reference['url'] if reference else None,
               'localizacao_fonte': packed(item['evidencias_ids']),
               'motivo_e_pendencias': ' '.join(item['lacunas']), 'revisao_humana': 'pendente'}
        for discipline in ['historia', 'geografia']:
            years = item['anos_aplicacao_com_programa_regional_verificado'] if discipline in item['disciplinas_com_previsao_regional'] else []
            row['anos_previsao_' + discipline] = packed(years)
            row['anos_programa_verificavel_' + discipline] = packed(item['anos_aplicacao_com_programa_verificavel'])
        processes.append(row)
    evidence_to_process = {
        'ufrr_programa_2025': ('ufrr-integral', 'ufrr-vestibular2025-pi', 'UFRR', 'unica', 2025),
        'ufrr_programa_2026': ('ufrr-integral', 'ufrr-vestibular2026-pi', 'UFRR', 'unica', 2026),
        'uerr_programa_2023': ('uerr-vestibular', 'uerr-vestibular2023', 'UERR', 'unica', 2023),
        'uema_paes_2026_exame_programa': ('uema-paes', 'uema-paes2026', 'UEMA', 'unica', 2026),
    }
    for item in other['evidencias']:
        mapping = evidence_to_process.get(item['evidencia_id'])
        extra_processes = {'uea_sis_programa_2020': 'uea-sis',
                           'unemat_programa_candidato_2026': 'unemat-vestibular',
                           'uepg_programa_2024_exame': 'uepg-vestibular'}
        process_id, application_id = (mapping[0], mapping[1]) if mapping else (extra_processes.get(item['evidencia_id']), None)
        if mapping and item.get('data_aplicacao'):
            _, _, sigla, stage, entrance = mapping
            day = date.fromisoformat(item['data_aplicacao'])
            source = sources[item['fontes_data_ids'][-1]]
            applications.append({
                'aplicacao_id': application_id, 'instituicao_id': institutions[sigla], 'instituicao_sigla': sigla,
                'processo_id': process_id, 'etapa': stage, 'edicao': item['edicao'], 'ano_ingresso': entrance,
                'data_aplicacao': item['data_aplicacao'], 'ano_aplicacao': day.year,
                'situacao': 'aplicacao_identificada_documentos_parciais', 'periodo_calendario': period(day.year),
                'fonte_data': source['url'], 'localizacao_data': 'Publicação institucional referenciada na triagem',
                'qualidade_evidencia_data': item['situacao_data'],
                'regime_curricular_contexto': 'nao_validado_localmente',
                'alinhamento_explicito_prova': 'nao_verificado',
                'origem_anotacao': 'triagem_assistida_por_ia', 'revisao_humana': 'pendente'})
        for program in item['disciplinas']:
            reference = sources[item['fonte_programa_id']]
            evidence.append({
                'evidencia_id': item['evidencia_id'] + '-' + program['disciplina'],
                'aplicacao_id': application_id, 'processo_id': process_id,
                'disciplina': program['disciplina'], 'previsao_regional': item['elegibilidade_ano'],
                'paginas_pdf': packed(program['paginas_pdf']),
                'paginas_impressas': packed(program['paginas_impressas']) if program.get('paginas_impressas') else None,
                'secao': program['secao'],
                'trecho_curto': program.get('trecho_curto'), 'fonte_url': reference['url'],
                'origem_anotacao': 'triagem_assistida_por_ia', 'revisao_humana': 'pendente'})
    expected = expand(registry, institutions, applications, evidence, processes)
    integrar(registry, institutions, applications, evidence, processes)
    selected_ids = {row['documento_id']: row for row in expected}
    for row in documentos_selecionados(registry, applications):
        known = selected_ids.get(row['documento_id'])
        if known and (known['url_origem'] != row['url_origem'] or known['aplicacao_id'] != row['aplicacao_id']):
            raise ValueError('Solicitação nacional mudou; investigar antes de substituir')
        if not known:
            expected.append(row)
            selected_ids[row['documento_id']] = row
    integrar_expansoes(registry, institutions, applications, evidence, processes, expected)
    integrar_auditoria_temporal(registry, applications, evidence, processes, expected)
    for label, rows, key in [('processos', processes, 'processo_id'), ('aplicacoes', applications, 'aplicacao_id'), ('evidencias-programa', evidence, 'evidencia_id')]:
        if label == 'aplicacoes':
            for row in rows:
                row.update(coorte_alvo_esperada=None,
                           fonte_do_corte='protocolo_secao_6_2_classificacao_por_calendario' if row.get('data_aplicacao') else None,
                           evidencia_implantacao_local=None,
                           incerteza_classificacao='Implantação local e trajetória escolar dos candidatos ainda não verificadas.')
        assert len({r[key] for r in rows}) == len(rows), f'IDs duplicados em {label}'
        fields = list(dict.fromkeys(field for row in rows for field in row))
        write_csv(registry / f'{label}.csv', sorted(rows, key=lambda r: r[key]), fields)
    grid = []
    by_cell = defaultdict(list)
    for app in applications:
        year = app.get('ano_aplicacao') or int(app['data_prevista'][:4])
        by_cell[(app['processo_id'], app['etapa'], year)].append(app)
    for process in processes:
        if process['estado_triagem'].startswith('excluido'):
            continue
        stages = json.loads(process['etapas'])
        if process['processo_id'] in ['ufrr-integral', 'uerr-vestibular', 'uema-paes']:
            stages = ['unica']
        for stage in stages or ['a_verificar']:
            for year in range(2017, 2027):
                apps = by_cell[(process['processo_id'], stage, year)]
                status = 'a_verificar'
                if apps:
                    status = 'aplicacao_identificada' if any(a.get('data_aplicacao') for a in apps) else (
                        'futura_no_corte' if all(a['situacao'] == 'futura_na_data_de_corte' for a in apps) else 'data_efetiva_pendente')
                grid.append({'processo_id': process['processo_id'], 'etapa': stage, 'ano_calendario': year,
                             'estado_investigacao': status, 'aplicacoes_ids': packed([a['aplicacao_id'] for a in apps]),
                             'observacao': 'Grade de investigação; não afirma que houve aplicação em célula pendente nem esgota múltiplas aplicações no ano.'})
    write_csv(registry / 'cobertura-anual.csv', grid, ['processo_id', 'etapa', 'ano_calendario', 'estado_investigacao', 'aplicacoes_ids', 'observacao'])
    history = read_csv(registry / 'instituicoes-historico.csv')
    if history:
        latest = {}
        for row in sorted(history, key=lambda r: int(r['ano_fonte'])):
            latest[row['instituicao_id']] = row
        queue = []
        for institution_id, row in sorted(latest.items()):
            found = [p['processo_id'] for p in processes if p['instituicao_id'] == institution_id]
            queue.append({'instituicao_id': institution_id, 'codigo_inep': row['codigo_inep'],
                          'nome_ultima_observacao': row['nome'], 'sigla_ultima_observacao': row['sigla'],
                          'uf_ultima_observacao': row['uf'], 'regiao_ultima_observacao': row['regiao'],
                          'ultimo_ano_observado': row['ano_fonte'], 'natureza_ultima_observacao': row['rede'],
                          'fonte_ultima_observacao': row['fonte_id'],
                          'processos_registrados': packed(found),
                          'triagem_status': 'parcial' if found else 'nao_iniciada',
                          'triagem_completa': False,
                          'observacao': 'Código histórico candidato; não equivale a instituição atual ou vestibular elegível. Natureza, vínculos e processos exigem auditoria.'})
        write_csv(registry / 'fila-triagem-institucional.csv', queue, list(queue[0]))
    app_ids = {r['aplicacao_id'] for r in applications}
    assert all(r['aplicacao_id'] in app_ids for r in expected), 'Documento sem aplicação'
    write_jsonl(registry / 'documentos-esperados.jsonl', expected)
    print(f'Registro: {len(processes)} processos, {len(applications)} aplicações identificadas (inclui futura), {len(evidence)} evidências disciplinares.')
    print('A grade anual contém pendências explícitas; não é denominador de provas efetivamente realizadas.')


if __name__ == '__main__':
    main()
