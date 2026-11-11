#!/usr/bin/env python3
"""Monta caderno local de revisão com regiões fiéis do PDF, sem rótulos sugeridos."""

import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path

from pipeline import ROOT, read_csv, read_jsonl, sha256, verify

VERSION = '0.1.0'
DPI = 120


def generate(root=ROOT, *, only=None):
    root = Path(root)
    verify(root)
    public = read_csv(root / 'data/processed/questoes.csv')
    texts = {r['ocorrencia_id']: r for r in read_jsonl(root / 'data/processed/questoes-texto.jsonl')}
    documents = {r['documento_id']: r for r in read_jsonl(root / 'data/registry/documentos.jsonl')}
    applications = {r['aplicacao_id']: r for r in read_csv(root / 'data/registry/aplicacoes.csv')}
    config = json.loads((root / 'data/annotation/configuracao.json').read_text(encoding='utf-8'))
    items = []
    image_manifest = []
    output = root / 'data/annotation/revisao'
    images = output / 'imagens'
    images.mkdir(parents=True, exist_ok=True)
    previous_images = {}
    if (output / 'manifesto.json').exists():
        previous_images = {r['arquivo']: r['imagem_sha256'] for r in json.loads((output / 'manifesto.json').read_text())['imagens']}
    renderer = subprocess.run(['pdftoppm', '-v'], check=True, capture_output=True, text=True)
    render_version = (renderer.stdout + renderer.stderr).splitlines()[0]
    for question in public:
        if only and question['aplicacao_id'] not in only:
            continue
        raw = texts[question['ocorrencia_id']]
        doc = documents[question['documento_id']]
        if raw['documento_sha256'] != doc['sha256']:
            raise ValueError('Texto de outra versão de original')
        app = applications[question['aplicacao_id']]
        views = []
        for region in json.loads(question['regioes_origem']):
            box = region['bbox_regiao']
            scale = DPI / 72
            x, y = max(0, math.floor(box[0] * scale)), max(0, math.floor((box[1] - 2) * scale))
            width = math.ceil(box[2] * scale) - x
            height = math.ceil(min(region['altura_pagina'], box[3] + 1) * scale) - y
            if width <= 0 or height <= 0:
                raise ValueError('Região visual inválida')
            key_data = [doc['sha256'], region['pagina'], x, y, width, height, DPI, render_version]
            key = hashlib.sha256(json.dumps(key_data).encode()).hexdigest()[:24]
            destination = images / f'{key}.png'
            relative_image = f'imagens/{destination.name}'
            if destination.exists() and relative_image in previous_images and sha256(destination) != previous_images[relative_image]:
                raise ValueError('Imagem derivada alterada; investigar antes de montar revisão humana')
            if not destination.exists():
                subprocess.run(['pdftoppm', '-f', str(region['pagina']), '-l', str(region['pagina']),
                                '-r', str(DPI), '-x', str(x), '-y', str(y), '-W', str(width), '-H', str(height),
                                '-png', '-singlefile', str(root / doc['caminho_local']), str(destination.with_suffix(''))],
                               check=True, capture_output=True, timeout=60)
            view = {'arquivo': f'imagens/{destination.name}', 'pagina': region['pagina'], 'coluna': region['coluna']}
            views.append(view)
            image_manifest.append({**view, 'ocorrencia_id': question['ocorrencia_id'], 'documento_sha256': doc['sha256'],
                                   'regiao_pontos_pdf': box, 'recorte_pixels': [x, y, width, height],
                                   'imagem_sha256': sha256(destination)})
        items.append({'id': question['ocorrencia_id'], 'documento_sha256': doc['sha256'],
                      'aplicacao_id': question['aplicacao_id'], 'disciplina': question['disciplina'],
                      'numero': question['numero_questao'], 'edicao': app['edicao'], 'data': app['data_aplicacao'] or '',
                      'data_prevista': app.get('data_prevista') or '',
                      'instituicao': question['instituicao_sigla'], 'url': doc['url_origem'],
                      'imagens': views, 'texto_extraido': raw['texto_bruto_segmentado']})
    if not items:
        raise ValueError('Nenhuma questão selecionada')
    items.sort(key=lambda r: (r['data'] or r['data_prevista'], r['aplicacao_id'], int(r['numero'])))
    package_id = hashlib.sha256(json.dumps(items, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    package = {'versao': VERSION, 'pacote_id': package_id, 'anotador_previsto': config['anotador_previsto'], 'itens': items}
    template = (root / 'templates/revisao.html').read_text(encoding='utf-8')
    # Texto original nunca é interpretado como HTML ou código, mesmo contendo </script>.
    payload = json.dumps(package, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    (output / 'index.html').write_text(template.replace('__PACOTE_JSON__', payload), encoding='utf-8')
    local_manifest = {'pacote_id': package_id, 'versao_gerador': VERSION, 'renderizador': render_version,
                      'dpi': DPI, 'imagens': image_manifest, 'index_sha256': sha256(output / 'index.html')}
    (output / 'manifesto.json').write_text(json.dumps(local_manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    public_manifest = {'pacote_id': package_id, 'versao_gerador': VERSION, 'anotador_previsto': config['anotador_previsto'],
                       'ocorrencias_ids': [r['id'] for r in items], 'quantidade': len(items),
                       'artefato_local': 'data/annotation/revisao/index.html', 'revisao_humana': 'a_realizar',
                       'contem_sugestoes_regionalidade': False, 'contem_gabaritos': False}
    (root / 'data/registry/pacote-revisao.json').write_text(json.dumps(public_manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Caderno local: {len(items)} itens, {len(image_manifest)} regiões de origem. {output / "index.html"}')
    return public_manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--somente', nargs='+', help='IDs de aplicações para um lote menor')
    args = parser.parse_args()
    generate(only=set(args.somente) if args.somente else None)
