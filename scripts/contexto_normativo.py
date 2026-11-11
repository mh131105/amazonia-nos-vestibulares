#!/usr/bin/env python3
"""Preserva os atos de contexto sem inventar aplicações de vestibular para eles."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time

if __package__:
    from .pipeline import ROOT, MAX_BYTES, USER_AGENT, append_jsonl, fetch_pdf_curl, now, sha256
else:
    from pipeline import ROOT, MAX_BYTES, USER_AGENT, append_jsonl, fetch_pdf_curl, now, sha256


def collect(root=ROOT, *, offline=False, update=False):
    if offline and update:
        raise ValueError('Modo offline não permite atualização de fontes')
    root = Path(root)
    path = root / 'data/registry/contexto-normativo.json'
    registry = json.loads(path.read_text(encoding='utf-8'))
    # Auditar todo o cache antes de qualquer aquisição ou alteração do manifesto.
    for source in registry['fontes']:
        cached = root / source['caminho_local'] if source.get('caminho_local') else None
        if cached and cached.exists():
            if sha256(cached) != source.get('sha256'):
                raise ValueError(f'Original normativo local alterado: {source["fonte_id"]}')
        elif offline:
            raise ValueError(f'Fonte normativa ausente para reprodução offline: '
                             f'{source["fonte_id"]} ({source.get("caminho_local", "sem caminho local")})')
    for source in registry['fontes']:
        known = source.get('sha256')
        cached = root / source['caminho_local'] if source.get('caminho_local') else None
        if cached and cached.exists():
            if not update:
                continue
        if offline:
            raise ValueError(f'Fonte normativa ausente para reprodução offline: {source["fonte_id"]}')
        time.sleep(1)
        if source['formato'] == 'pdf':
            content, final, mime = fetch_pdf_curl(source['url'])
        else:
            with tempfile.TemporaryDirectory(prefix='amazonia-contexto-') as temp:
                destination = Path(temp) / 'pagina.html'
                result = subprocess.run(['curl', '--fail', '--silent', '--show-error', '--location',
                                         '--proto', '=https', '--proto-redir', '=https', '--max-time', '30',
                                         '--max-filesize', str(MAX_BYTES), '--user-agent', USER_AGENT,
                                         '--output', str(destination), '--write-out', '%{json}', source['url']],
                                        check=True, capture_output=True, timeout=35)
                metadata = json.loads(result.stdout)
                content, final, mime = destination.read_bytes(), metadata['url_effective'], metadata.get('content_type')
                if len(content) > MAX_BYTES:
                    raise ValueError('Documento normativo excede limite configurado')
                text = content.decode('utf-8', errors='replace')
                if any(marker not in text for marker in source['marcadores_obrigatorios']):
                    raise ValueError('A resposta não contém o ato esperado; não preservar página de erro como norma')
        digest = hashlib.sha256(content).hexdigest()
        local = (cached if known == digest and cached else
                 root / 'data/raw/contexto' / (digest + '.' + source['formato']))
        local.parent.mkdir(parents=True, exist_ok=True)
        if not local.exists():
            with local.open('xb') as stream:
                stream.write(content)
        elif sha256(local) != digest:
            raise ValueError('Original de contexto alterado')
        if known and digest != known and not update:
            append_jsonl(root / 'data/registry/aquisicoes-contexto.jsonl', {
                'fonte_id': source['fonte_id'], 'em': now(), 'status': 'divergencia_versao',
                'sha256_esperado': known, 'sha256_recebido': digest, 'caminho_nova_versao': str(local.relative_to(root))})
            raise ValueError('Fonte normativa mudou; versão anterior preservada, atualização explícita necessária')
        if known == digest and not update:
            append_jsonl(root / 'data/registry/aquisicoes-contexto.jsonl', {
                'fonte_id': source['fonte_id'], 'em': now(), 'status': 'cache_recuperado',
                'sha256': digest, 'url_origem': source['url'], 'url_final': final})
            continue
        source.update(sha256=digest, tamanho_bytes=len(content), url_final=final, mime=mime,
                      coletado_em=now(), caminho_local=str(local.relative_to(root)), status='coletado')
        append_jsonl(root / 'data/registry/aquisicoes-contexto.jsonl', {
            'fonte_id': source['fonte_id'], 'em': source['coletado_em'], 'status': 'coletado',
            'sha256': digest, 'sha256_anterior': known, 'url_origem': source['url'], 'url_final': final})
        temporary = path.with_suffix(path.suffix + '.tmp')
        temporary.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        temporary.replace(path)
    print(f'Contexto normativo: {len(registry["fontes"])} fontes preservadas e verificadas.')
    return registry


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--offline', action='store_true')
    mode.add_argument('--atualizar', action='store_true')
    args = parser.parse_args()
    collect(offline=args.offline, update=args.atualizar)
