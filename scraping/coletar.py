"""Baixa os documentos oficiais de dados/fontes.csv e, opcionalmente, extrai texto."""
import argparse
import csv
import hashlib
from pathlib import Path
import subprocess
import tempfile
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def coletar(root=ROOT, extrair=False):
    pasta = root / 'acervo'
    pasta.mkdir(exist_ok=True)
    fontes = list(csv.DictReader((root / 'dados/fontes.csv').open(encoding='utf-8')))
    falhas, conferidas, pendentes = [], 0, 0
    for fonte in fontes:
        digest = fonte['sha256']
        if not digest:
            pendentes += 1
            print(f"PENDENTE {fonte['fonte_id']}: arquivo da edição não recuperado; consultar a URL registrada.")
            continue
        destino = pasta / f"{digest or fonte['fonte_id']}.pdf"
        try:
            if urlparse(fonte['url']).scheme != 'https':
                raise ValueError('A fonte deve usar HTTPS')
            if not destino.exists():
                with tempfile.TemporaryDirectory(dir=pasta) as tmp:
                    candidato = Path(tmp) / 'documento.pdf'
                    subprocess.run(['curl', '--fail', '--location', '--retry', '2',
                                    '--connect-timeout', '20', '--max-time', '180',
                                    '--proto', '=https', '--proto-redir', '=https',
                                    '--silent', '--show-error', '--output', str(candidato),
                                    fonte['url']], check=True)
                    conteudo = candidato.read_bytes()
                    if digest and hashlib.sha256(conteudo).hexdigest() != digest:
                        raise ValueError('A fonte mudou: SHA-256 diferente do documento estudado')
                    if not conteudo.startswith(b'%PDF-'):
                        raise ValueError('O documento recebido não é PDF')
                    candidato.replace(destino)
            elif digest and hashlib.sha256(destino.read_bytes()).hexdigest() != digest:
                raise ValueError('Arquivo local corrompido; preserve-o antes de baixar novamente')
            if extrair:
                subprocess.run(['pdftotext', '-layout', str(destino),
                                str(destino.with_suffix('.txt'))], check=True)
            conferidas += 1
            print(f"OK {fonte['fonte_id']}" + ('' if digest else ' (sem hash histórico para comparação)'))
        except (ValueError, OSError, subprocess.CalledProcessError) as erro:
            falhas.append(f"{fonte['fonte_id']}: {erro}")
    if falhas:
        raise SystemExit('\n'.join(falhas))
    print(f'{conferidas} referências conferidas; {pendentes} pendentes. Arquivos em {pasta}.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--extrair', action='store_true', help='Requer pdftotext (Poppler).')
    coletar(extrair=parser.parse_args().extrair)
