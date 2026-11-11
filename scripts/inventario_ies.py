#!/usr/bin/env python3
"""Gera o inventário nacional a partir do cadastro oficial de IES do Inep.

Usa somente a biblioteca padrão e curl. Lê membros do ZIP por HTTP Range;
nunca baixa o cadastro de cursos para produzir o inventário de instituições.
"""

import argparse
from collections import Counter
import csv
from datetime import datetime
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import time
from xml.etree import ElementTree
import zipfile
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
PAGE = "https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-da-educacao-superior"
SOURCE_FILE = ROOT / "data/registry/fontes_inventario.json"
CATEGORIES = {
    "1": ("Pública Federal", "federal"),
    "2": ("Pública Estadual", "estadual"),
    "3": ("Pública Municipal", "municipal"),
    "7": ("Especial", "a_verificar"),
}


def curl(url, *options):
    time.sleep(1)
    command = [
        "curl", "--fail", "--silent", "--show-error", "--location",
        "--max-time", "45", "--retry", "2", "--retry-delay", "1",
        "--retry-all-errors", "--retry-max-time", "120", *options, url,
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    log = ROOT / "data/interim/inventario/requisicoes.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "instante": datetime.now(ZoneInfo("America/Manaus")).isoformat(timespec="seconds"),
            "url": url, "opcoes": list(options), "codigo_saida_curl": result.returncode,
            "bytes_recebidos": len(result.stdout),
            "diagnostico_curl": result.stderr.decode(errors="replace"),
        }, ensure_ascii=False) + "\n")
    result.check_returncode()
    return result.stdout


class RemoteZip(io.RawIOBase):
    """Arquivo seekable com leituras limitadas às faixas requisitadas."""

    def __init__(self, url, length):
        self.url, self.length, self.position = url, length, 0
        self.bytes_received, self.requests = 0, 0

    def seekable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=0):
        origins = {0: 0, 1: self.position, 2: self.length}
        self.position = origins[whence] + offset
        if not 0 <= self.position <= self.length:
            raise ValueError("Posição fora do ZIP")
        return self.position

    def read(self, size=-1):
        end = self.length if size < 0 else min(self.length, self.position + size)
        wanted = end - self.position
        if wanted <= 0:
            return b""
        # Impede que a ausência de suporte a Range baixe o ZIP completo.
        content = curl(self.url, "--range", f"{self.position}-{end - 1}",
                       "--max-filesize", str(wanted))
        if len(content) != wanted:
            raise ValueError("Servidor não respeitou a faixa solicitada")
        self.position = end
        self.bytes_received += len(content)
        self.requests += 1
        return content


def preserve(content, filename, year):
    digest = hashlib.sha256(content).hexdigest()
    path = ROOT / "data/raw/inep" / str(year) / digest[:12] / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != content:
        raise ValueError(f"Colisão ou original alterado: {path}")
    if not path.exists():
        path.write_bytes(content)
    return {"caminho_local": path.relative_to(ROOT).as_posix(),
            "sha256": digest, "tamanho_bytes": len(content)}


def acquire(year):
    url = f"https://download.inep.gov.br/microdados/microdados_censo_da_educacao_superior_{year}.zip"
    headers = curl(url, "--head", "--write-out", "\nURL_FINAL:%{url_effective}").decode()
    lengths = re.findall(r"(?im)^Content-Length:\s*(\d+)", headers)
    if not lengths:
        raise ValueError("Servidor não informou tamanho do ZIP")
    length = int(lengths[-1])
    remote = RemoteZip(url, length)
    files = []
    with zipfile.ZipFile(remote) as archive:
        for info in archive.infolist():
            basename = Path(info.filename).name
            is_ies = re.fullmatch(r"MICRODADOS_(?:CADASTRO|ED_SUP)_IES_\d{4}\.CSV", basename, re.I)
            is_dictionary = basename.lower().endswith(".xlsx") and "dicion" in basename.lower()
            is_md5 = basename.lower().startswith("md5_") and "/dados/" in info.filename.lower()
            if not (is_ies or is_dictionary or is_md5):
                continue
            content = archive.read(info)  # zipfile também verifica o CRC do membro.
            record = preserve(content, basename, year)
            record.update({"membro_zip": info.filename, "crc32_zip": f"{info.CRC:08x}",
                           "tipo": "cadastro_ies" if is_ies else "dicionario" if is_dictionary else "checksums_md5"})
            files.append(record)
    ies = [item for item in files if item["tipo"] == "cadastro_ies"]
    if len(ies) != 1:
        raise ValueError("Esperado exatamente um cadastro de IES no ZIP")
    md5_records = [item for item in files if item["tipo"] == "checksums_md5"]
    if md5_records:
        text = (ROOT / md5_records[0]["caminho_local"]).read_text(encoding="ascii")
        matches = re.findall(r"(?im)^([a-f0-9]{32})\s+\*?[^\n]*IES[^\n]*", text)
        calculated = hashlib.md5((ROOT / ies[0]["caminho_local"]).read_bytes()).hexdigest()
        if len(matches) != 1 or calculated != matches[0]:
            raise ValueError("MD5 do cadastro não confere com o checksum oficial")
        ies[0]["md5_oficial_verificado"] = calculated
    return {
        "fonte_id": f"inep_ces_{year}_{ies[0]['sha256'][:12]}", "ano_censo": year,
        "instituicao_publicadora": "Inep", "pagina_origem": PAGE, "url_arquivo": url,
        "url_final": headers.split("URL_FINAL:")[-1].strip(),
        "coletado_em": datetime.now(ZoneInfo("America/Manaus")).isoformat(timespec="seconds"),
        "zip_tamanho_bytes": length,
        "zip_etag": re.findall(r"(?im)^ETag:\s*(.+)", headers)[-1].strip(),
        "zip_last_modified": re.findall(r"(?im)^Last-Modified:\s*(.+)", headers)[-1].strip(),
        "zip_sha256": None, "zip_integral_baixado": False,
        "metodo_aquisicao": "HTTP Range dos membros selecionados; CRC ZIP e MD5 oficial do cadastro verificados",
        "requisicoes_range": remote.requests, "bytes_range_recebidos": remote.bytes_received,
        "arquivos": files,
    }


def verify_cached(source, *, allow_missing=False):
    missing = []
    for item in source["arquivos"]:
        path = ROOT / item["caminho_local"]
        if not path.exists():
            missing.append(item["caminho_local"])
            continue
        content = path.read_bytes()
        if hashlib.sha256(content).hexdigest() != item["sha256"]:
            raise ValueError(f"Original alterado: {item['caminho_local']}")
    if missing and not allow_missing:
        raise ValueError("Original ausente no cache: " + ", ".join(missing))
    return missing


def record_recovery(action, known, acquired, *, differences=None):
    log = ROOT / "data/interim/inventario/recuperacoes.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "instante": datetime.now(ZoneInfo("America/Manaus")).isoformat(timespec="seconds"),
        "acao": action, "fonte_id_conhecida": known["fonte_id"],
        "aquisicao": acquired, "divergencias": differences or [],
    }
    with log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def recover_known_source(source):
    """Reobtém membros ausentes sem substituir a versão conhecida do manifesto."""
    acquired = acquire(source["ano_censo"])
    verify_cached(acquired)
    previous = {item["membro_zip"]: item for item in source["arquivos"]}
    received = {item["membro_zip"]: item for item in acquired["arquivos"]}
    if len(previous) != len(source["arquivos"]) or len(received) != len(acquired["arquivos"]):
        raise ValueError("Membros ZIP duplicados no manifesto do inventário")
    differences = [
        {"membro_zip": member, "sha256_conhecido": previous.get(member, {}).get("sha256"),
         "sha256_obtido": received.get(member, {}).get("sha256")}
        for member in sorted(previous.keys() | received.keys())
        if previous.get(member, {}).get("sha256") != received.get(member, {}).get("sha256")
    ]
    if differences:
        record_recovery("divergencia_fonte_rejeitada", source, acquired, differences=differences)
        raise ValueError(
            "A fonte mudou em relação ao manifesto conhecido. Novos originais foram preservados "
            "e a divergência registrada em data/interim/inventario/recuperacoes.jsonl; "
            "o inventário e o manifesto anteriores foram mantidos. "
            "Use --atualizar somente para aceitar explicitamente uma nova versão."
        )
    # Os hashes conferem, inclusive para dicionário e checksums. Restaura também
    # um caminho antigo do cache, caso a organização local tenha sido alterada.
    for member, item in previous.items():
        destination = ROOT / item["caminho_local"]
        if not destination.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            content = (ROOT / received[member]["caminho_local"]).read_bytes()
            with destination.open("xb") as handle:
                handle.write(content)
    verify_cached(source)
    record_recovery("originais_conhecidos_recuperados", source, acquired)


def validate_dictionary(source):
    dictionary = next(item for item in source["arquivos"] if item["tipo"] == "dicionario")
    with zipfile.ZipFile(ROOT / dictionary["caminho_local"]) as book:
        xml = ElementTree.fromstring(book.read("xl/sharedStrings.xml"))
        ns = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        strings = ["".join(node.itertext()) for node in xml.findall("s:si", ns)]
    if "TP_REDE" not in strings or not any("1. Pública\n2. Privada" == text for text in strings):
        raise ValueError("Dicionário não confirma o mapeamento de TP_REDE")


def build_inventory(source):
    verify_cached(source)
    validate_dictionary(source)
    cadastro = next(item for item in source["arquivos"] if item["tipo"] == "cadastro_ies")
    path = ROOT / cadastro["caminho_local"]
    with path.open(encoding="cp1252", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        rows = [(number, row) for number, row in enumerate(reader, start=2)]
    selected = []
    for number, row in rows:
        if row["TP_REDE"] != "1":
            continue
        code = row["TP_CATEGORIA_ADMINISTRATIVA"]
        if code not in CATEGORIES:
            raise ValueError(f"Categoria pública ainda não mapeada: {code}")
        label, sphere = CATEGORIES[code]
        if int(row["NU_ANO_CENSO"]) != source["ano_censo"]:
            raise ValueError("Ano do cadastro diverge do ano da fonte")
        selected.append({
            "instituicao_id": f"inep_{row['CO_IES']}", "codigo_inep": row["CO_IES"],
            "nome": row["NO_IES"], "sigla": row["SG_IES"],
            "uf": row["SG_UF_IES"], "regiao": row["NO_REGIAO_IES"],
            "municipio": row["NO_MUNICIPIO_IES"], "codigo_municipio": row["CO_MUNICIPIO_IES"],
            "rede_codigo": row["TP_REDE"], "rede": "publica",
            "categoria_administrativa_codigo": code, "categoria_administrativa": label,
            "esfera_administrativa": sphere,
            "organizacao_academica_codigo": row["TP_ORGANIZACAO_ACADEMICA"],
            "ano_fonte": row["NU_ANO_CENSO"], "fonte_id": source["fonte_id"],
            "fonte_url": source["url_arquivo"], "fonte_membro_zip": cadastro["membro_zip"],
            "fonte_linha": number,
            "historico_institucional_status": "pendente",
            "observacoes": "Categoria Especial; verificar esfera e natureza jurídica individualmente." if code == "7" else "Natureza observada apenas no ano da fonte; vigência histórica pendente.",
        })
    selected.sort(key=lambda row: int(row["codigo_inep"]))
    ids = [row["instituicao_id"] for row in selected]
    if len(ids) != len(set(ids)):
        raise ValueError("CO_IES duplicado no inventário")
    if len({row["uf"] for row in selected}) != 27 or len({row["regiao"] for row in selected}) != 5:
        raise ValueError("Inventário não abrange as 27 UFs e cinco regiões")
    destination = ROOT / "data/registry/instituicoes.csv"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(selected[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(selected)
    summary = {
        "ano_fonte": source["ano_censo"], "linhas_cadastro_total": len(rows),
        "ies_rede_publica": len(selected), "ids_unicos": len(set(ids)),
        "ufs": 27, "regioes": dict(sorted(Counter(row["regiao"] for row in selected).items())),
        "categorias": dict(sorted(Counter(row["categoria_administrativa"] for row in selected).items())),
        "criterio": "TP_REDE = 1; categorias originais preservadas, inclusive 7 (Especial)",
        "cobertura_historica_completa": False,
        "inventario_sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
    }
    output = ROOT / f"data/interim/inventario/resumo_{source['ano_censo']}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ano", type=int, default=2024)
    parser.add_argument("--offline", action="store_true", help="Usa somente originais já coletados e verificados")
    parser.add_argument("--atualizar", action="store_true", help="Consulta novamente a fonte e preserva novos originais por hash")
    args = parser.parse_args()
    if args.offline and args.atualizar:
        parser.error("--offline e --atualizar são incompatíveis")
    if SOURCE_FILE.exists() and not args.atualizar:
        source = json.loads(SOURCE_FILE.read_text(encoding="utf-8"))["fontes"][0]
        if source["ano_censo"] != args.ano:
            parser.error("Ano em cache diferente; use --atualizar para outra edição")
        missing = verify_cached(source, allow_missing=True)
        if missing:
            if args.offline:
                raise ValueError(
                    "Reprodução --offline exige os originais locais; ausentes: "
                    + ", ".join(missing)
                    + ". Execute sem --offline para tentar recuperá-los e conferir os hashes conhecidos."
                )
            recover_known_source(source)
    elif args.offline:
        parser.error("Manifesto ausente para reprodução offline")
    else:
        source = acquire(args.ano)
        SOURCE_FILE.parent.mkdir(parents=True, exist_ok=True)
        SOURCE_FILE.write_text(json.dumps({"fontes": [source]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(build_inventory(source), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"ERRO: {error}", file=sys.stderr)
        sys.exit(2)
