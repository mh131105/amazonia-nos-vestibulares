"""Exporta os CSVs curados para o dashboard e prepara dist/ para publicação."""
import json
from pathlib import Path
import shutil

from limpeza import ler_csv

ROOT = Path(__file__).resolve().parents[1]
META = {
    'title': 'História e Geografia da Amazônia nos vestibulares',
    'startYear': 2017,
    'endYear': 2026,
    'cutoff': '2026-11-11',
    'curation': 'IA (Codex)',
}


def lista(valor):
    return [item for item in valor.split('|') if item]


def montar_dataset(root=ROOT):
    """Converte campos e tipos sem alterar as decisões de curadoria."""
    questoes = ler_csv(root / 'dados/curado/questoes.csv')
    provas = ler_csv(root / 'dados/provas.csv')
    topicos = ler_csv(root / 'dados/topicos.csv')
    ementas = ler_csv(root / 'dados/ementas.csv')
    fontes = ler_csv(root / 'dados/fontes.csv')
    tipos = {'ementa': 'Programa', 'prova': 'Prova', 'gabarito': 'Gabarito'}
    return {
        'meta': META.copy(),
        'questions': [{
            'id': q['questao_id'], 'examId': q['prova_id'],
            'institution': q['instituicao'], 'year': int(q['ano_aplicacao']),
            'edition': q['edicao'], 'stage': q['etapa'],
            'area': q['disciplina'], 'originalArea': q['disciplina_origem'],
            'number': q['numero'], 'statement': q['enunciado'],
            'options': [{'label': letra, 'text': q[f'alternativa_{letra.lower()}']}
                        for letra in 'ABCDE' if q[f'alternativa_{letra.lower()}']],
            'answer': q['gabarito'] or None,
            'topicIds': lista(q['topicos_ids']), 'primaryTopicId': q['topico_id'],
            'syllabusItemIds': lista(q['ementa_itens']),
            'syllabusLinkType': q['tipo_vinculo_ementa'],
            'regionalFocus': q['foco_regional'], 'justification': q['justificativa'],
            'pdfPages': [int(p) for p in lista(q['paginas_pdf'])],
            'sourceId': q['fonte_prova_id'], 'url': q['url_prova'],
            'visual': q['recurso_visual'] == 'sim', 'observation': q['observacao'],
        } for q in questoes],
        'exams': [{
            'id': p['prova_id'], 'institution': p['instituicao'],
            'process': p['processo'], 'edition': p['edicao'],
            'year': int(p['ano_aplicacao']), 'date': p['data_aplicacao'] or None,
            'stage': p['etapa'], 'sourceId': p['fonte_prova_id'],
            'syllabusSourceIds': lista(p['fonte_ementa_id']),
            'screenedCount': int(p['questoes_triadas']),
            'screenedComplete': p['triagem_completa'] == 'sim',
            'regionalSyllabusComplete': p['ementa_regional_completa'] == 'sim',
            'observation': p['observacao'],
        } for p in provas],
        'topics': [{
            'id': t['topico_id'], 'area': t['disciplina'],
            'content': t['conteudo'], 'label': t['topico'],
            'definition': t['definicao'],
        } for t in topicos],
        'syllabus': [{
            'id': e['ementa_item_id'], 'examId': e['prova_id'],
            'area': e['disciplina'], 'text': e['texto_oficial'],
            'topicIds': lista(e['topicos_ids']), 'sourceId': e['fonte_id'],
            'url': e['url'], 'pages': [int(p) for p in lista(e['paginas_pdf'])],
            'scope': e['escopo'], 'observation': e['observacao'],
        } for e in ementas],
        'sources': [{
            'id': f['fonte_id'], 'institution': f['instituicao'], 'type': f['tipo'],
            'title': f"{f['instituicao']} — {tipos[f['tipo']]}",
            'url': f['url'], 'officialUrl': f['url_publicacao'] or None,
            'origin': f['origem'], 'sha256': f['sha256'] or None,
            'observation': f['observacao'],
        } for f in fontes],
    }


def preparar(root=ROOT):
    dataset = montar_dataset(root)
    origem = root / 'dashboard'
    (origem / 'dataset.json').write_text(
        json.dumps(dataset, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    destino = root / 'dist'
    if destino.exists():
        shutil.rmtree(destino)
    shutil.copytree(origem, destino,
                    ignore=shutil.ignore_patterns('README.md', 'preview.png'))
    print(f"Dashboard: {len(dataset['questions'])} questões; "
          f"{len(dataset['exams'])} provas. Publicação preparada em dist/.")
    return dataset


if __name__ == '__main__':
    preparar()
