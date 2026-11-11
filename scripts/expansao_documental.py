"""Incorpora aplicações e documentos C4 sem pressupor questões ou equivalência."""

import json
from datetime import date

REALIZACAO = {'relatorio_institucional_pos_aplicacao', 'capa_da_prova',
              'capa_prova_aplicada', 'noticia_institucional_pos_aplicacao',
              'noticia_pos_aplicacao', 'gabarito_pos_aplicacao',
              'gabarito_oficial_pos_aplicacao'}


def packed(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def audited_hash(document):
    expected, audited = document.get('sha256_esperado'), document.get('sha256_auditado')
    if expected and audited and expected != audited:
        raise ValueError('Documento C4 contém hashes de referência divergentes')
    return audited or expected


def check_hash(previous, current):
    old, new = audited_hash(previous), audited_hash(current)
    if old and new and old != new:
        raise ValueError('Documento C4 conflita com hash já preservado')


def integrar(registry, institutions, applications, evidence, processes, expected):
    by_app = {row['aplicacao_id']: row for row in applications}
    by_process = {row['processo_id']: row for row in processes}
    by_doc = {row['documento_id']: row for row in expected}
    by_evidence = {row['evidencia_id']: row for row in evidence}
    for path in sorted(registry.glob('expansao-*-c4.json')):
        source = json.loads(path.read_text(encoding='utf-8'))
        app_ids = {item['aplicacao_id'] for item in source.get('aplicacoes', [])}
        top_documents = {}
        source_documents = {}
        for item in source.get('aplicacoes', []):
            for doc in item.get('documentos', []):
                doc.setdefault('aplicacao_id', item['aplicacao_id'])
                if doc.get('documento_id'):
                    source_documents.setdefault(doc['documento_id'], doc)
        for doc in source.get('documentos', []):
            if doc.get('aplicacao_id') not in app_ids:
                raise ValueError('Documento C4 sem aplicação identificada no registro de origem')
            top_documents.setdefault(doc['aplicacao_id'], []).append(doc)
            if doc.get('documento_id'):
                source_documents.setdefault(doc['documento_id'], doc)
        shared_ids = {shared['documento_id'] for shared in source.get('programas_compartilhados', [])}
        for shared in source.get('programas_compartilhados', []):
            known = by_doc.get(shared['documento_id']) or source_documents.get(shared['documento_id'])
            if known is None:
                raise ValueError('Programa compartilhado C4 sem documento prévio identificado')
            if (known.get('url_origem') or known.get('url')) != shared['url']:
                raise ValueError('Programa compartilhado C4 diverge da fonte já preservada')
            check_hash(known, shared)
            known['referencia_programa_compartilhado'] = shared
            for field in ['fonte_adocao', 'origem_documentada', 'paginas_pdf', 'paginas_impressas']:
                if field in shared:
                    known[field] = shared[field]
            if audited_hash(shared):
                known['sha256_auditado'] = audited_hash(shared)
        for item in source.get('aplicacoes', []):
            key, process_id = item['aplicacao_id'], item['processo_id']
            if process_id not in by_process:
                raise ValueError('Expansão sem processo documentado')
            actual, forecast = item.get('data_aplicacao'), item.get('data_aplicacao_prevista')
            # Validar o calendário antes de comparar as representações ISO.
            if actual:
                date.fromisoformat(actual)
            if forecast:
                date.fromisoformat(forecast)
            if actual and not '2017-01-01' <= actual <= '2026-11-11':
                if item.get('situacao') != 'excluido_fora_janela':
                    raise ValueError('Aplicação fora da janela sem exclusão explícita')
                continue
            if not actual and (not forecast or forecast <= '2026-11-11'):
                raise ValueError('Expansão temporal sem data efetiva ou futuro documentado')
            temporal = item.get('evidencia_data') or {}
            if not temporal.get('url') or not temporal.get('natureza'):
                raise ValueError('Aplicação C4 sem evidência temporal identificada')
            if actual and temporal['natureza'] not in REALIZACAO:
                raise ValueError('Data C4 sem natureza primária de realização reconhecida')
            row = by_app.get(key)
            if row:
                if row['processo_id'] != process_id or row.get('data_aplicacao') != actual:
                    raise ValueError('Expansão diverge da identidade ou data já registrada')
            else:
                sigla = item['instituicao_sigla']
                year = date.fromisoformat(actual).year if actual else None
                row = {'aplicacao_id': key, 'instituicao_id': institutions[sigla],
                       'instituicao_sigla': sigla, 'processo_id': process_id,
                       'etapa': item['etapa'], 'edicao': item['edicao'],
                       'ano_ingresso': item.get('ano_ingresso'), 'data_aplicacao': actual,
                       'ano_aplicacao': year, 'data_prevista': forecast,
                       'situacao': item['situacao'],
                       'periodo_calendario': ('2017-2021' if year <= 2021 else '2022-2023' if year <= 2023
                                              else '2024' if year == 2024 else '2025-2026') if year else None,
                       'fonte_data': temporal['url'], 'localizacao_data': temporal.get('localizacao'),
                       'qualidade_evidencia_data': temporal['natureza'],
                       'regime_curricular_contexto': 'nao_validado_localmente',
                       'alinhamento_explicito_prova': 'nao_verificado',
                       'origem_anotacao': 'triagem_assistida_por_ia', 'revisao_humana': 'pendente'}
                applications.append(row)
                by_app[key] = row
            for field in ['fase', 'dia', 'banca', 'formato', 'programa_documento_id', 'limites',
                          'modalidade_aplicacao', 'turno', 'fonte_data_id']:
                if field in item:
                    row[field] = item[field]
            row['fonte_expansao'] = 'data/registry/' + path.name
            row['estrutura_documentada'] = packed(item.get('estrutura', {}))
            row['fonte_data_corrobora'] = packed(item.get('fonte_data_corrobora', []))
            if 'variantes' in item:
                row['variantes_documentadas'] = packed(item['variantes'])
            stages = json.loads(by_process[process_id]['etapas'])
            if item['etapa'] not in stages:
                stages.append(item['etapa'])
                by_process[process_id]['etapas'] = packed(stages)
            for program in item.get('programa', []):
                discipline = program['disciplina']
                if discipline not in {'historia', 'geografia', 'ciencias_humanas_integradas'}:
                    raise ValueError('Disciplina C4 não reconhecida')
                evidence_id = key + '-' + discipline
                program_id = item.get('programa_documento_id')
                program_doc = by_doc.get(program_id) or source_documents.get(program_id)
                if program_doc:
                    if program['fonte_url'] != (program_doc.get('url_origem') or program_doc.get('url')):
                        raise ValueError('Programa C4 diverge da fonte do documento compartilhado')
                    links = set(program_doc.get('aplicacoes_vinculadas', []))
                    links.update([key, program_doc['aplicacao_id']])
                    program_doc['aplicacoes_vinculadas'] = sorted(links)
                prior = by_evidence.get(evidence_id)
                if prior and (prior.get('fonte_url') != program['fonte_url'] or
                              prior.get('documento_id_programa') != program_id):
                    raise ValueError('Evidência C4 conflita com fonte de programa já preservada')
                if not prior:
                    added = {'evidencia_id': evidence_id, 'aplicacao_id': key,
                                     'processo_id': process_id, 'disciplina': discipline,
                                     'previsao_regional': program['previsao_regional'],
                                     'previsao_regional_documento': program.get('previsao_regional_documento', program['previsao_regional']),
                                     'vigencia_confirmada': program.get('vigencia_confirmada', True),
                                     'paginas_pdf': packed(program.get('paginas_pdf', [])),
                                     'paginas_impressas': packed(program.get('paginas_impressas', [])),
                                     'secao': program.get('localizacao'), 'trecho_curto': program.get('trecho_curto'),
                                     'fonte_url': program['fonte_url'],
                                     'documento_id_programa': program_id,
                                     'fonte_registro': 'data/registry/' + path.name,
                                     'origem_anotacao': 'triagem_assistida_por_ia', 'revisao_humana': 'pendente'}
                    evidence.append(added)
                    by_evidence[evidence_id] = added
                suffix = 'integrada' if discipline == 'ciencias_humanas_integradas' else discipline
                fields = ['anos_programa_verificavel_' + suffix]
                if program['previsao_regional'] == 'substantiva':
                    fields.append('anos_previsao_' + suffix)
                if actual and program.get('paginas_pdf') and program.get('vigencia_confirmada', True):
                    for field in fields:
                        values = set(json.loads(by_process[process_id].get(field) or '[]'))
                        values.add(date.fromisoformat(actual).year)
                        by_process[process_id][field] = packed(sorted(values))
            for doc in [*item.get('documentos', []), *top_documents.get(key, [])]:
                if doc.get('aplicacao_id', key) != key:
                    raise ValueError('Documento C4 vinculado a outra aplicação')
                doc_id = doc.get('documento_id') or key + '-' + doc['tipo'].replace('_', '-')
                request = {**doc, 'documento_id': doc_id, 'aplicacao_id': key,
                           'instituicao_sigla': item['instituicao_sigla'], 'processo_id': process_id,
                           'tipo': doc['tipo'], 'publicador': doc['publicador'], 'url_origem': doc['url'],
                           'fonte_url': doc.get('fonte_url') or item['fonte_landing'], 'origem_oficial': doc['origem_oficial'],
                           'condicoes_uso': doc.get('condicoes_uso', 'nao_verificadas'),
                           'redistribuicao_autorizada': doc.get('redistribuicao_autorizada'),
                           'escopo_coleta': doc.get('escopo_coleta', 'expansao_documental_ciclo4'),
                           'transporte': doc.get('transporte', 'urllib'), 'observacao': doc.get('observacao')}
                if audited_hash(doc):
                    request['sha256_auditado'] = audited_hash(doc)
                if 'bases_digitais' not in request and 'bases_digital' in request:
                    request['bases_digitais'] = request['bases_digital']
                old = by_doc.get(doc_id)
                if old and old['url_origem'] != request['url_origem']:
                    raise ValueError('Documento C4 conflita com identidade já preservada')
                if old and old['aplicacao_id'] != key:
                    if doc_id not in shared_ids or doc['tipo'] not in {'programa', 'edital_programa'}:
                        raise ValueError('Documento C4 conflita com identidade já preservada')
                    check_hash(old, request)
                    old['aplicacoes_vinculadas'] = sorted(set(
                        old.get('aplicacoes_vinculadas', []) + [old['aplicacao_id'], key]))
                    continue
                if old:
                    check_hash(old, request)
                    old.update(request)
                else:
                    expected.append(request)
                    by_doc[doc_id] = request
    for app in applications:
        program_id = app.get('programa_documento_id')
        if program_id:
            if program_id not in by_doc:
                raise ValueError('Aplicação C4 referencia programa não inventariado')
            program = by_doc[program_id]
            app['programa_vigencia_confirmada'] = program.get('referencia_programa_compartilhado', {}).get('vigencia_confirmada', True)
            program['aplicacoes_vinculadas'] = sorted(set(
                program.get('aplicacoes_vinculadas', []) + [program['aplicacao_id'], app['aplicacao_id']]))

