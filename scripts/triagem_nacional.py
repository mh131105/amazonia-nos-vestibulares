"""Integra as duas triagens nacionais C3 sem transformar pistas em aplicações.

Não lê ou grava CSVs. O consolidado chama ``integrar`` antes de gravar suas
listas; as solicitações de programas são obtidas separadamente, sem rede.
"""

import json
import re
import unicodedata
from datetime import date
from pathlib import Path


ARQUIVOS = ('triagem-sul-sudeste-c3.json', 'triagem-ne-co-c3.json')
DISCIPLINAS = ('historia', 'geografia', 'ciencias_humanas_integradas')
DATAS_PRIMARIAS = {'noticia_pos_aplicacao', 'gabarito_pos_aplicacao',
                   'indice_provas_pos_aplicacao', 'prova', 'gabarito_oficial'}
POSITIVAS = {'substantiva', 'previsao_regional_verificada',
             'amazonia_explicita_geografia_relacoes_transfronteiricas'}
# Estas etapas são documentadas nas triagens; não se deduz etapa do ano/curso.
ETAPAS_DATADAS = {'usp-fuvest': ('1_fase_conhecimentos_gerais', 'f1'),
                  'uel-vestibular': ('1_fase_conhecimentos_gerais', 'f1'),
                  'ufms-vestibular': ('objetiva_redacao', 'unica')}
ETAPAS_PROCESSOS = {
    'usp-fuvest': ['1_fase_conhecimentos_gerais', '2_fase_discursiva'],
    'uel-vestibular': ['1_fase_conhecimentos_gerais', '2_fase',
                       'habilidades_especificas_quando_exigidas'],
    'ufms-vestibular': ['objetiva_redacao'],
}
ESTADOS = {
    'elegibilidade_documental_geografia_tres_anos': 'candidato_evidencia_insuficiente',
    'pendente_recorte_amazonico': 'candidato_evidencia_insuficiente',
    'pendente_programa_incorporado': 'pendente_por_lacuna_documental',
    'pendente_acesso_documental': 'pendente_por_lacuna_documental',
}


def _json(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def _id(value):
    ascii_text = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', ascii_text.lower()).strip('-')


def _discipline(value):
    return _id(value).replace('-', '_')


def _inputs(registry):
    for filename in ARQUIVOS:
        path = Path(registry) / filename
        if path.exists():
            data = json.loads(path.read_text(encoding='utf-8'))
            yield filename, data, {s['fonte_id']: s for s in data['fontes']}


def _official(source):
    return bool(source and source.get('origem_oficial') is True and source.get('url'))


def _read_program(source, pages):
    status = source.get('status_acesso', '') if source else ''
    return (_official(source) and bool(pages) and
            ('lido' in status or 'consultado' in status or 'inspecionado' in status))


def _regional(value, verifiable):
    if not verifiable:
        return 'pendente_fonte_documental'
    if value is True or isinstance(value, str) and value in POSITIVAS:
        return 'substantiva'
    if value is False:
        return 'nao_identificada_no_programa_examinado'
    if value == 'recorte_amazonico_nao_demonstrado_nesta_fonte':
        return 'nao_demonstrada_na_fonte_examinada'
    return value or 'pendente_por_lacuna_documental'


def _event(item, process_id, sources):
    actual = item.get('data_aplicacao')
    source = sources.get(item.get('fonte_data_id'))
    if not actual or not _official(source) or source.get('tipo') not in DATAS_PRIMARIAS:
        return None
    # A data não basta quando falta vínculo inequívoco de edição e etapa.
    edition = str(item.get('edicao', ''))
    match = re.fullmatch(r'(?:Vestibular )?(20\d{2})', edition)
    if process_id not in ETAPAS_DATADAS or not match:
        return None
    day = date.fromisoformat(actual)
    if not date(2017, 1, 1) <= day <= date(2026, 11, 11):
        raise ValueError('Aplicação nacional fora da janela')
    if item.get('ano_aplicacao_verificado') != day.year:
        raise ValueError('Ano verificado diverge da data de aplicação')
    stage, suffix = ETAPAS_DATADAS[process_id]
    return {'aplicacao_id': f'{process_id}{match[1]}-{suffix}', 'etapa': stage,
            'edicao': edition, 'ano_ingresso': int(match[1]), 'data_aplicacao': actual,
            'ano_aplicacao': day.year, 'fonte_data': source['url'],
            'fonte_data_id': _id(item['fonte_data_id']),
            'fonte_data_id_origem': item['fonte_data_id'],
            'qualidade_evidencia_data': source['tipo']}


def integrar(registry, institutions, applications, evidence, processes):
    """Muta as listas do consolidado; somente datas primárias geram aplicações.

    Anos são derivados das evidências vinculadas às aplicações, nunca dos
    resumos da triagem. Humanidades integradas têm uma série própria.
    """
    process_index = {r['processo_id']: r for r in processes}
    application_index = {r['aplicacao_id']: r for r in applications}
    evidence_ids = {r['evidencia_id'] for r in evidence}
    touched = set()
    for filename, data, sources in _inputs(registry):
        for item in data['processos']:
            key = _id(item['processo_id'])
            sigla = item['instituicao_sigla'].upper()
            if sigla not in institutions:
                raise ValueError(f'Instituição nacional não cadastrada: {sigla}')
            references = [sources[s] for s in item.get('fonte_ids', []) if s in sources]
            if key not in process_index:
                row = {'processo_id': key, 'instituicao_id': institutions[sigla],
                       'instituicao_sigla': sigla, 'nome': item['nome'],
                       'etapas': _json(ETAPAS_PROCESSOS.get(key, item.get('etapas', []))),
                       'etapas_origem': _json(item.get('etapas', [])),
                       'estado_triagem': ESTADOS.get(item['estado_triagem'], item['estado_triagem']),
                       'estado_triagem_origem': item['estado_triagem'],
                       'fonte_registro': f'data/registry/{filename}',
                       'fonte_url': references[0]['url'] if references else None,
                       'fontes_ids_origem': _json(item.get('fonte_ids', [])),
                       'fontes_urls': _json([s['url'] for s in references]),
                       'motivo_e_pendencias': item.get('motivo'),
                       'alcance_triagem': item.get('alcance'), 'revisao_humana': 'pendente',
                       'situacao_identificacao_processo': 'processo_documentado_parcialmente'}
                if key in {'ufmt-ead', 'ufmt-proinq', 'ufrgs-concurso-vestibular'}:
                    row['situacao_identificacao_processo'] = 'pista_sem_desenho_confirmado'
                processes.append(row)
                process_index[key] = row
            touched.add(key)
        for item in data['evidencias']:
            key, process_id = _id(item['evidencia_id']), _id(item['processo_id'])
            if process_id not in process_index:
                raise ValueError(f'Evidência nacional sem processo: {process_id}')
            if key in evidence_ids:
                continue
            discipline = _discipline(item['disciplina'])
            if discipline not in DISCIPLINAS:
                raise ValueError(f'Disciplina nacional não reconhecida: {discipline}')
            program = sources.get(item.get('fonte_programa_id'))
            adoption = sources.get(item.get('fonte_vigencia_id'))
            pages = item.get('paginas_pdf', [])
            if any(type(p) is not int or p < 1 for p in pages):
                raise ValueError('Página física deve ser inteira e 1-based')
            verifiable = _read_program(program, pages) and _official(adoption)
            event = _event(item, process_id, sources)
            application_id = event['aplicacao_id'] if event else None
            if event and application_id not in application_index:
                process = process_index[process_id]
                year = event['ano_aplicacao']
                row = {**event, 'processo_id': process_id,
                       'instituicao_id': process['instituicao_id'],
                       'instituicao_sigla': process['instituicao_sigla'],
                       'data_prevista': None, 'situacao': 'aplicacao_identificada_documentos_parciais',
                       'periodo_calendario': ('2017-2021' if year <= 2021 else
                                            '2022-2023' if year <= 2023 else
                                            '2024' if year == 2024 else '2025-2026'),
                       'localizacao_data': item.get('localizacao_data') or
                                            ('Gabarito, página física 1' if
                                             event['qualidade_evidencia_data'] == 'gabarito_pos_aplicacao'
                                             else 'Fonte primária pós-aplicação indicada na triagem C3'),
                       'formato': ('presencial_e_online_variantes_nao_conferidas' if
                                   process_id == 'ufms-vestibular' else 'nao_conferido'),
                       'variantes_conferidas': False, 'cadernos_identificados': None,
                       'regime_curricular_contexto': 'nao_validado_localmente',
                       'alinhamento_explicito_prova': 'nao_verificado',
                       'origem_anotacao': 'triagem_assistida_por_ia',
                       'fonte_registro': f'data/registry/{filename}', 'revisao_humana': 'pendente'}
                applications.append(row)
                application_index[application_id] = row
            row = {'evidencia_id': key, 'aplicacao_id': application_id, 'processo_id': process_id,
                   'evidencia_id_origem': item['evidencia_id'],
                   'disciplina': discipline, 'edicao': item.get('edicao'),
                   'previsao_regional': _regional(item.get('previsao_regional'), verifiable),
                   'previsao_regional_origem': item.get('previsao_regional'),
                   'programa_verificavel': verifiable, 'paginas_pdf': _json(pages),
                   'paginas_impressas': _json(item.get('paginas_impressas', [])),
                   'secao': item.get('secao'), 'trecho_curto': item.get('evidencia_curta'),
                   'fonte_programa_id': _id(item['fonte_programa_id']),
                   'fonte_programa_id_origem': item['fonte_programa_id'],
                   'fonte_url': program['url'] if program else None,
                   'fonte_vigencia_id': _id(item['fonte_vigencia_id']) if item.get('fonte_vigencia_id') else None,
                   'fonte_vigencia_id_origem': item.get('fonte_vigencia_id'),
                   'fonte_vigencia_url': adoption['url'] if adoption else None,
                   'fonte_data_id': _id(item['fonte_data_id']) if item.get('fonte_data_id') else None,
                   'fonte_data_id_origem': item.get('fonte_data_id'),
                   'fonte_data_url': sources.get(item.get('fonte_data_id'), {}).get('url'),
                   'data_aplicacao': event['data_aplicacao'] if event else None,
                   'data_aplicacao_declarada_na_triagem': item.get('data_aplicacao'),
                   'limites': item.get('limites'), 'fonte_registro': f'data/registry/{filename}',
                   'disciplinas_abrangidas': _json(item.get('disciplinas_abrangidas', [])),
                   'interpretacao_historica_geografica': item.get('interpretacao_historica_geografica'),
                   'origem_anotacao': 'triagem_assistida_por_ia', 'revisao_humana': 'pendente'}
            evidence.append(row)
            evidence_ids.add(key)
    for process_id in touched:
        row = process_index[process_id]
        for discipline in DISCIPLINAS:
            verified, positive = set(), set()
            for record in evidence:
                app = application_index.get(record.get('aplicacao_id'))
                if (record.get('processo_id') != process_id or record.get('disciplina') != discipline
                        or record.get('programa_verificavel') not in (True, 'True', 'true') or not app):
                    continue
                year = app['ano_aplicacao']
                verified.add(year)
                if record['previsao_regional'] == 'substantiva':
                    positive.add(year)
            suffix = 'integrada' if discipline == 'ciencias_humanas_integradas' else discipline
            row['anos_programa_verificavel_' + suffix] = _json(sorted(verified))
            row['anos_previsao_' + suffix] = _json(sorted(positive))
        separate = [d for d in ('historia', 'geografia')
                    if len(json.loads(row['anos_previsao_' + d])) >= 3]
        row['recorrencia_integrada_confirmada'] = len(json.loads(row['anos_previsao_integrada'])) >= 3
        if separate:
            row['estado_triagem'] = 'incluido_recorrencia_confirmada'


def documentos_selecionados(registry, applications):
    """Solicita só programas positivos ligados a eventos reais; nenhum caderno."""
    applications = {a['aplicacao_id']: a for a in applications if a.get('data_aplicacao')}
    selected = {}
    for _, data, sources in _inputs(registry):
        for item in data['evidencias']:
            process_id = _id(item['processo_id'])
            program = sources.get(item.get('fonte_programa_id'))
            adoption = sources.get(item.get('fonte_vigencia_id'))
            verifiable = _read_program(program, item.get('paginas_pdf')) and _official(adoption)
            if _regional(item.get('previsao_regional'), verifiable) != 'substantiva':
                continue
            event = _event(item, process_id, sources)
            if not event or event['aplicacao_id'] not in applications:
                continue
            app = applications[event['aplicacao_id']]
            if app['processo_id'] != process_id or app['data_aplicacao'] != event['data_aplicacao']:
                raise ValueError('Vínculo do programa diverge da aplicação consolidada')
            document_id = event['aplicacao_id'] + '-programa'
            # A URL canônica consta do acervo anual; o espelho tem TLS expirado.
            canonical = sources.get(item['fonte_programa_id'] + '_canonico')
            origin = canonical if _official(canonical) else program
            selected[document_id] = {
                'documento_id': document_id, 'aplicacao_id': event['aplicacao_id'],
                'instituicao_sigla': app['instituicao_sigla'], 'processo_id': process_id,
                'tipo': 'programa', 'publicador': program['publicador'],
                'url_origem': origin['url'], 'fonte_url': adoption['url'], 'origem_oficial': True,
                'fonte_programa_id_origem': item['fonte_programa_id'],
                'fonte_vigencia_id_origem': item['fonte_vigencia_id'],
                'fonte_programa_url_observada': program['url'],
                'paginas_pdf': item['paginas_pdf'],
                'condicoes_uso': 'nao_verificadas', 'redistribuicao_autorizada': None,
                'escopo_coleta': 'triagem_nacional_ciclo3', 'transporte': 'urllib',
                'observacao': ('Programa positivo; páginas físicas: ' + _json(item['paginas_pdf']) +
                               '. Coleta documental não identifica caderno ou valida questão.')}
    return [selected[key] for key in sorted(selected)]
