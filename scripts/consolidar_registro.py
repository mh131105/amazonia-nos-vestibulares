#!/usr/bin/env python3
"""Consolida as notas documentais em tabelas de processos, aplicações e evidências."""

import csv
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

from pipeline import ROOT, REGISTRY, read_jsonl, write_csv

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
                    status = 'aplicacao_identificada' if any(a.get('data_aplicacao') for a in apps) else 'futura_no_corte'
                grid.append({'processo_id': process['processo_id'], 'etapa': stage, 'ano_calendario': year,
                             'estado_investigacao': status, 'aplicacoes_ids': packed([a['aplicacao_id'] for a in apps]),
                             'observacao': 'Grade de investigação; não afirma que houve aplicação em célula pendente nem esgota múltiplas aplicações no ano.'})
    write_csv(registry / 'cobertura-anual.csv', grid, ['processo_id', 'etapa', 'ano_calendario', 'estado_investigacao', 'aplicacoes_ids', 'observacao'])
    expected = read_jsonl(registry / 'documentos-esperados.jsonl')
    app_ids = {r['aplicacao_id'] for r in applications}
    assert all(r['aplicacao_id'] in app_ids for r in expected), 'Documento sem aplicação'
    print(f'Registro: {len(processes)} processos, {len(applications)} aplicações identificadas (inclui futura), {len(evidence)} evidências disciplinares.')
    print('A grade anual contém pendências explícitas; não é denominador de provas efetivamente realizadas.')


if __name__ == '__main__':
    main()
