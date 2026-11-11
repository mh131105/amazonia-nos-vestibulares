"""Recuperação do cadastro conhecido sem rede e sem misturar fixtures ao acervo."""

import contextlib
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from xml.sax.saxutils import escape
import zipfile

from scripts import inventario_ies


UF_REGIONS = {
    "AC": "Norte", "AL": "Nordeste", "AP": "Norte", "AM": "Norte",
    "BA": "Nordeste", "CE": "Nordeste", "DF": "Centro-Oeste",
    "ES": "Sudeste", "GO": "Centro-Oeste", "MA": "Nordeste",
    "MT": "Centro-Oeste", "MS": "Centro-Oeste", "MG": "Sudeste",
    "PA": "Norte", "PB": "Nordeste", "PR": "Sul", "PE": "Nordeste",
    "PI": "Nordeste", "RJ": "Sudeste", "RN": "Nordeste",
    "RS": "Sul", "RO": "Norte", "RR": "Norte", "SC": "Sul",
    "SP": "Sudeste", "SE": "Nordeste", "TO": "Norte",
}


class InventoryRecoveryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.manifest = self.root / "data/registry/fontes_inventario.json"
        self.manifest.parent.mkdir(parents=True)
        for name, value in [("ROOT", self.root), ("SOURCE_FILE", self.manifest)]:
            replacement = patch.object(inventario_ies, name, value)
            replacement.start()
            self.addCleanup(replacement.stop)

    def make_source(self, changed_kind=None):
        stream = io.StringIO(newline="")
        fields = ["NU_ANO_CENSO", "CO_IES", "NO_IES", "SG_IES", "SG_UF_IES",
                  "NO_REGIAO_IES", "NO_MUNICIPIO_IES", "CO_MUNICIPIO_IES",
                  "TP_REDE", "TP_CATEGORIA_ADMINISTRATIVA", "TP_ORGANIZACAO_ACADEMICA"]
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter=";")
        writer.writeheader()
        for number, (uf, region) in enumerate(UF_REGIONS.items(), start=1):
            writer.writerow({
                "NU_ANO_CENSO": "2024", "CO_IES": str(number),
                "NO_IES": f"Instituição fictícia {uf}" + (" alterada" if changed_kind == "cadastro_ies" else ""),
                "SG_IES": f"TESTE{uf}", "SG_UF_IES": uf, "NO_REGIAO_IES": region,
                "NO_MUNICIPIO_IES": "Município fictício", "CO_MUNICIPIO_IES": "0000000",
                "TP_REDE": "1", "TP_CATEGORIA_ADMINISTRATIVA": "1",
                "TP_ORGANIZACAO_ACADEMICA": "1",
            })
        cadastro = stream.getvalue().encode("cp1252")
        strings = ["TP_REDE", "1. Pública\n2. Privada"]
        if changed_kind == "dicionario":
            strings.append("Nota nova da fonte fictícia")
        xml = ('<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
               + "".join(f"<si><t>{escape(text)}</t></si>" for text in strings) + "</sst>")
        dictionary_stream = io.BytesIO()
        with zipfile.ZipFile(dictionary_stream, "w") as archive:
            archive.writestr(zipfile.ZipInfo("xl/sharedStrings.xml", (2024, 1, 1, 0, 0, 0)), xml)
        checksums = (hashlib.md5(cadastro).hexdigest() + " *CADASTRO_IES_2024.CSV\n").encode()
        payloads = [
            ("cadastro_ies", "CADASTRO_IES_2024.CSV", cadastro),
            ("dicionario", "dicionario.xlsx", dictionary_stream.getvalue()),
            ("checksums_md5", "md5.txt", checksums),
        ]
        files = []
        for kind, filename, content in payloads:
            digest = hashlib.sha256(content).hexdigest()
            relative = Path("data/raw/inep/2024") / digest[:12] / filename
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                self.assertEqual(path.read_bytes(), content)
            else:
                path.write_bytes(content)
            files.append({"tipo": kind, "membro_zip": f"fixture/{filename}",
                          "caminho_local": relative.as_posix(), "sha256": digest,
                          "tamanho_bytes": len(content)})
        return {"fonte_id": "fonte-ficticia-" + files[0]["sha256"][:12],
                "ano_censo": 2024, "url_arquivo": "https://example.invalid/fixture.zip",
                "coletado_em": "2026-11-11T12:00:00-04:00", "arquivos": files}

    def write_known_source(self):
        source = self.make_source()
        self.manifest.write_text(json.dumps({"fontes": [source]}, ensure_ascii=False), encoding="utf-8")
        return source

    def invoke(self, *arguments):
        output = io.StringIO()
        with patch.object(sys, "argv", ["inventario_ies.py", *arguments]), contextlib.redirect_stdout(output):
            inventario_ies.main()
        return output.getvalue()

    def test_offline_reconstructs_identical_inventory_without_network(self):
        source = self.write_known_source()
        inventario_ies.build_inventory(source)
        destination = self.root / "data/registry/instituicoes.csv"
        before = destination.read_bytes()
        with patch.object(inventario_ies, "acquire", side_effect=AssertionError("Rede proibida")) as acquire:
            result = json.loads(self.invoke("--offline"))
        acquire.assert_not_called()
        self.assertEqual(destination.read_bytes(), before)
        self.assertEqual(result["ies_rede_publica"], 27)
        self.assertEqual(result["ufs"], 27)
        self.assertEqual(result["inventario_sha256"], hashlib.sha256(before).hexdigest())
        self.assertNotIn("triagem_processos_status", before.decode("utf-8").splitlines()[0])

    def test_offline_rejects_adulterated_original_before_network(self):
        source = self.write_known_source()
        altered = self.root / source["arquivos"][0]["caminho_local"]
        altered.write_bytes(b"arquivo adulterado no cache")
        before = self.manifest.read_bytes()
        with patch.object(inventario_ies, "acquire") as acquire:
            with self.assertRaisesRegex(ValueError, "Original alterado"):
                self.invoke("--offline")
        acquire.assert_not_called()
        self.assertEqual(self.manifest.read_bytes(), before)
        self.assertEqual(altered.read_bytes(), b"arquivo adulterado no cache")

    def test_offline_reports_missing_original_explicitly(self):
        source = self.write_known_source()
        missing = source["arquivos"][0]["caminho_local"]
        (self.root / missing).unlink()
        with patch.object(inventario_ies, "acquire") as acquire:
            with self.assertRaisesRegex(ValueError, "--offline.*originais locais") as error:
                self.invoke("--offline")
        acquire.assert_not_called()
        self.assertIn(missing, str(error.exception))

    def test_clean_clone_recovers_all_known_members_without_changing_manifest(self):
        source = self.write_known_source()
        inventario_ies.build_inventory(source)
        before_manifest = self.manifest.read_bytes()
        before_inventory = (self.root / "data/registry/instituicoes.csv").read_bytes()
        for item in source["arquivos"]:
            (self.root / item["caminho_local"]).unlink()

        def download(_year):
            recovered = self.make_source()
            recovered["coletado_em"] = "2026-11-11T13:00:00-04:00"
            return recovered

        with patch.object(inventario_ies, "acquire", side_effect=download) as acquire:
            self.invoke()
        acquire.assert_called_once_with(2024)
        inventario_ies.verify_cached(source)
        self.assertEqual(self.manifest.read_bytes(), before_manifest)
        self.assertEqual((self.root / "data/registry/instituicoes.csv").read_bytes(), before_inventory)
        event = json.loads((self.root / "data/interim/inventario/recuperacoes.jsonl").read_text())
        self.assertEqual(event["acao"], "originais_conhecidos_recuperados")
        self.assertEqual(event["aquisicao"]["coletado_em"], "2026-11-11T13:00:00-04:00")

    def test_changed_dictionary_is_preserved_and_rejected_even_when_cadastro_matches(self):
        source = self.write_known_source()
        inventario_ies.build_inventory(source)
        before_manifest = self.manifest.read_bytes()
        destination = self.root / "data/registry/instituicoes.csv"
        before_inventory = destination.read_bytes()
        (self.root / source["arquivos"][0]["caminho_local"]).unlink()
        downloaded = []

        def download(_year):
            acquired = self.make_source(changed_kind="dicionario")
            downloaded.append(acquired)
            return acquired

        with patch.object(inventario_ies, "acquire", side_effect=download):
            with self.assertRaisesRegex(ValueError, "fonte mudou"):
                self.invoke()
        self.assertEqual(self.manifest.read_bytes(), before_manifest)
        self.assertEqual(destination.read_bytes(), before_inventory)
        changed = next(item for item in downloaded[0]["arquivos"] if item["tipo"] == "dicionario")
        self.assertTrue((self.root / changed["caminho_local"]).is_file())
        event = json.loads((self.root / "data/interim/inventario/recuperacoes.jsonl").read_text())
        self.assertEqual(event["acao"], "divergencia_fonte_rejeitada")
        self.assertEqual(len(event["divergencias"]), 1)
        self.assertEqual(event["divergencias"][0]["membro_zip"], changed["membro_zip"])

    def test_missing_member_in_download_is_rejected(self):
        source = self.write_known_source()
        (self.root / source["arquivos"][0]["caminho_local"]).unlink()

        def download(_year):
            acquired = self.make_source()
            acquired["arquivos"] = [item for item in acquired["arquivos"] if item["tipo"] != "checksums_md5"]
            return acquired

        with patch.object(inventario_ies, "acquire", side_effect=download):
            with self.assertRaisesRegex(ValueError, "fonte mudou"):
                self.invoke()
        event = json.loads((self.root / "data/interim/inventario/recuperacoes.jsonl").read_text())
        self.assertEqual(event["divergencias"][0]["sha256_obtido"], None)

    def test_present_adulteration_blocks_recovery_even_when_another_member_is_missing(self):
        source = self.write_known_source()
        (self.root / source["arquivos"][0]["caminho_local"]).unlink()
        (self.root / source["arquivos"][1]["caminho_local"]).write_bytes(b"adulterado")
        with patch.object(inventario_ies, "acquire") as acquire:
            with self.assertRaisesRegex(ValueError, "Original alterado"):
                self.invoke()
        acquire.assert_not_called()

    def test_explicit_update_accepts_new_source_and_keeps_old_originals(self):
        source = self.write_known_source()
        old_paths = [self.root / item["caminho_local"] for item in source["arquivos"]]

        def download(_year):
            return self.make_source(changed_kind="cadastro_ies")

        with patch.object(inventario_ies, "acquire", side_effect=download):
            self.invoke("--atualizar")
        new_source = json.loads(self.manifest.read_text())["fontes"][0]
        self.assertNotEqual(new_source["arquivos"][0]["sha256"], source["arquivos"][0]["sha256"])
        self.assertTrue(all(path.is_file() for path in old_paths))
        with (self.root / "data/registry/instituicoes.csv").open(encoding="utf-8", newline="") as handle:
            row = next(csv.DictReader(handle))
        self.assertIn("alterada", row["nome"])


if __name__ == "__main__":
    unittest.main()
