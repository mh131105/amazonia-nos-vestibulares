"""Contratos históricos com fontes sintéticas temporárias; nunca alimentam o corpus."""

import contextlib
import csv
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from xml.sax.saxutils import escape

from scripts import historico_ies as history
from scripts import inventario_ies as base

UF_REGIONS = {
    'AC': 'Norte', 'AL': 'Nordeste', 'AP': 'Norte', 'AM': 'Norte', 'BA': 'Nordeste',
    'CE': 'Nordeste', 'DF': 'Centro-Oeste', 'ES': 'Sudeste', 'GO': 'Centro-Oeste',
    'MA': 'Nordeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste', 'MG': 'Sudeste',
    'PA': 'Norte', 'PB': 'Nordeste', 'PR': 'Sul', 'PE': 'Nordeste', 'PI': 'Nordeste',
    'RJ': 'Sudeste', 'RN': 'Nordeste', 'RS': 'Sul', 'RO': 'Norte', 'RR': 'Norte',
    'SC': 'Sul', 'SP': 'Sudeste', 'SE': 'Nordeste', 'TO': 'Norte',
}


class HistoricalInventoryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for module in [history, base]:
            replacement = patch.object(module, 'ROOT', self.root)
            replacement.start()
            self.addCleanup(replacement.stop)
        self.registry = self.root / 'data/registry'
        self.registry.mkdir(parents=True)
        self.snapshot = self.registry / 'instituicoes.csv'
        self.snapshot.write_bytes(b'fotografia 2024 preservada\n')

    def source(self, year, *, name='Instituição sintética', extra_public=False, network_field=True):
        fields = ['NU_ANO_CENSO', 'CO_IES', 'NO_IES', 'SG_IES', 'SG_UF_IES',
                  'NO_REGIAO_IES', 'NO_MUNICIPIO_IES', 'CO_MUNICIPIO_IES',
                  'TP_REDE', 'TP_CATEGORIA_ADMINISTRATIVA', 'TP_ORGANIZACAO_ACADEMICA']
        stream = io.StringIO(newline='')
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter=';', lineterminator='\n')
        writer.writeheader()
        for number, (uf, region) in enumerate(UF_REGIONS.items(), 1):
            writer.writerow({'NU_ANO_CENSO': year, 'CO_IES': number, 'NO_IES': f'{name} {uf}',
                             'SG_IES': f'TESTE{uf}', 'SG_UF_IES': uf, 'NO_REGIAO_IES': region,
                             'NO_MUNICIPIO_IES': 'Município sintético', 'CO_MUNICIPIO_IES': '0000000',
                             'TP_REDE': '1', 'TP_CATEGORIA_ADMINISTRATIVA': '7' if number == 1 else '1',
                             'TP_ORGANIZACAO_ACADEMICA': '1'})
        if extra_public:
            writer.writerow({'NU_ANO_CENSO': year, 'CO_IES': 999, 'NO_IES': 'IES antiga sintética',
                             'SG_IES': 'ANTIGA', 'SG_UF_IES': 'AM', 'NO_REGIAO_IES': 'Norte',
                             'NO_MUNICIPIO_IES': 'Município sintético', 'CO_MUNICIPIO_IES': '0000000',
                             'TP_REDE': '1', 'TP_CATEGORIA_ADMINISTRATIVA': '1', 'TP_ORGANIZACAO_ACADEMICA': '1'})
        writer.writerow({'NU_ANO_CENSO': year, 'CO_IES': 888, 'NO_IES': 'Privada sintética',
                         'TP_REDE': '2', 'TP_CATEGORIA_ADMINISTRATIVA': '4'})
        if not network_field:
            parsed = list(csv.DictReader(io.StringIO(stream.getvalue()), delimiter=';'))
            stream = io.StringIO(newline='')
            writer = csv.DictWriter(stream, fieldnames=[f for f in fields if f != 'TP_REDE'], delimiter=';', lineterminator='\n')
            writer.writeheader()
            writer.writerows({k: v for k, v in row.items() if k != 'TP_REDE'} for row in parsed)
        dictionary = io.BytesIO()
        strings = ['TP_REDE', '1. Pública\n2. Privada', 'TP_CATEGORIA_ADMINISTRATIVA',
                   '1. Pública Federal\n2. Pública Estadual\n3. Pública Municipal\n4. Privada\n7. Especial']
        with zipfile.ZipFile(dictionary, 'w') as book:
            book.writestr(zipfile.ZipInfo('xl/sharedStrings.xml', (2024, 1, 1, 0, 0, 0)),
                          '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                          + ''.join(f'<si><t>{escape(text)}</t></si>' for text in strings) + '</sst>')
            book.writestr(zipfile.ZipInfo('xl/workbook.xml', (2024, 1, 1, 0, 0, 0)),
                          '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                          'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                          '<sheets><sheet name="cadastro_ies" sheetId="1" r:id="rId1"/></sheets></workbook>')
            book.writestr(zipfile.ZipInfo('xl/_rels/workbook.xml.rels', (2024, 1, 1, 0, 0, 0)),
                          '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                          '<Relationship Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>')
            book.writestr(zipfile.ZipInfo('xl/worksheets/sheet1.xml', (2024, 1, 1, 0, 0, 0)),
                          '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
                          '<row r="24"><c r="B24" t="s"><v>2</v></c><c r="F24" t="s"><v>3</v></c></row>'
                          + ('<row r="25"><c r="B25" t="s"><v>0</v></c><c r="F25" t="s"><v>1</v></c></row>' if network_field else '')
                          + '</sheetData></worksheet>')
        files = []
        for kind, filename, content in [('cadastro_ies', f'IES_{year}.CSV', stream.getvalue().encode('cp1252')),
                                        ('dicionario', 'dicionario.xlsx', dictionary.getvalue())]:
            digest = hashlib.sha256(content).hexdigest()
            relative = Path(f'data/raw/inep/{year}/{digest[:12]}') / filename
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            files.append({'tipo': kind, 'caminho_local': str(relative), 'membro_zip': f'fixture/{filename}',
                          'sha256': digest, 'tamanho_bytes': len(content)})
        return {'fonte_id': f'fonte-sintetica-{year}-{files[0]["sha256"][:8]}',
                'ano_censo': year, 'url_arquivo': f'https://example.invalid/{year}.zip', 'arquivos': files}

    def manifest(self, sources):
        path = self.registry / 'fontes_inventario_historico.json'
        path.write_text(json.dumps({'versao': '0.1.0', 'fontes': sources, 'pendencias_por_ano': []}), encoding='utf-8')
        return path

    def invoke(self, *args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return history.main(list(args))

    def test_alternate_destination_preserves_snapshot_and_special_category(self):
        source = self.source(2017)
        before = self.snapshot.read_bytes()
        output = self.root / 'data/interim/history.csv'
        summary = base.build_inventory(source, destination=output)
        self.assertEqual(self.snapshot.read_bytes(), before)
        self.assertEqual(summary['ies_rede_publica'], 27)
        with output.open(encoding='utf-8', newline='') as stream:
            rows = list(csv.DictReader(stream))
        self.assertNotIn('888', [row['codigo_inep'] for row in rows])
        self.assertEqual(rows[0]['categoria_administrativa_codigo'], '7')
        self.assertEqual(rows[0]['esfera_administrativa'], 'a_verificar')

    def test_union_retains_institution_not_observed_in_later_snapshot(self):
        source17 = self.source(2017, extra_public=True)
        source18 = self.source(2018)
        summary = history.build_history([source17, source18])
        self.assertEqual(summary['registros_instituicao_ano'], 55)
        self.assertEqual(summary['instituicoes_distintas_publicas_ou_especiais'], 28)
        with (self.registry / 'reconciliacao-instituicoes.csv').open(encoding='utf-8', newline='') as stream:
            old = next(row for row in csv.DictReader(stream) if row['codigo_inep'] == '999')
        self.assertEqual(json.loads(old['anos_observados_selecao_institucional']), [2017])
        self.assertEqual(json.loads(old['anos_cobertos_sem_observacao_selecao']), [2018])
        self.assertIn('não comprovam criação, extinção', old['limite_interpretacao'])

    def test_name_changes_keep_both_years_and_sources_without_claiming_legal_event(self):
        history.build_history([self.source(2017, name='Nome sintético A'),
                               self.source(2019, name='Nome sintético B')])
        with (self.registry / 'reconciliacao-instituicoes.csv').open(encoding='utf-8', newline='') as stream:
            row = next(csv.DictReader(stream))
        changes = json.loads(row['mudancas_textuais_observadas'])
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0]['campo'], 'nome')
        self.assertEqual(changes[0]['ano_anterior'], 2017)
        self.assertEqual(changes[0]['ano_posterior'], 2019)
        self.assertTrue(changes[0]['intervalo_com_lacuna'])
        self.assertNotEqual(changes[0]['fonte_anterior'], changes[0]['fonte_posterior'])

    def test_missing_network_field_never_fabricates_public_network_for_special_category(self):
        summary = history.build_history([self.source(2017, network_field=False)])
        self.assertEqual(summary['registros_especiais_sem_campo_rede'], 1)
        self.assertEqual(summary['registros_publicos_confirmados_pelo_cadastro'], 26)
        with (self.registry / 'instituicoes-historico.csv').open(encoding='utf-8', newline='') as stream:
            rows = list(csv.DictReader(stream))
        special = next(row for row in rows if row['categoria_administrativa_codigo'] == '7')
        self.assertEqual(special['rede_codigo'], '')
        self.assertEqual(special['rede'], 'especial_a_verificar')
        self.assertIn('TP_REDE ausente', special['criterio_selecao_ano'])
        self.assertEqual(rows[1]['rede'], 'publica_por_categoria')

    def test_duplicate_year_and_institution_is_rejected(self):
        row = {'instituicao_id': 'inep_1', 'codigo_inep': '1', 'ano_fonte': '2017'}
        with self.assertRaisesRegex(ValueError, 'repetida no mesmo ano'):
            history.reconcile([row, dict(row)], [2017])

    def test_dictionary_term_outside_ies_sheet_cannot_validate_network_field(self):
        source = self.source(2017, network_field=False)
        cadastro = next(item for item in source['arquivos'] if item['tipo'] == 'cadastro_ies')
        path = self.root / cadastro['caminho_local']
        with path.open(encoding='cp1252', newline='') as stream:
            reader = csv.DictReader(stream, delimiter=';')
            fields = reader.fieldnames + ['TP_REDE']
            rows = [{**row, 'TP_REDE': '1'} for row in reader]
        with path.open('w', encoding='cp1252', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, delimiter=';')
            writer.writeheader()
            writer.writerows(rows)
        # SharedStrings contém TP_REDE, mas a planilha cadastro_ies não o define.
        with self.assertRaisesRegex(ValueError, 'sem mapeamento correspondente na planilha cadastro_ies'):
            history.dictionary_evidence(source)

    def test_offline_reexecution_is_identical_and_does_not_acquire(self):
        self.manifest([self.source(2017), self.source(2018)])
        self.invoke('--anos', '2017', '2018', '--offline')
        outputs = [self.registry / name for name in ['instituicoes-historico.csv', 'reconciliacao-instituicoes.csv',
                                                     'fontes_inventario_historico.json']]
        before = [p.read_bytes() for p in outputs]
        with patch.object(base, 'acquire', side_effect=AssertionError('Rede proibida')) as acquire:
            self.invoke('--anos', '2017', '2018', '--offline')
        acquire.assert_not_called()
        self.assertEqual([p.read_bytes() for p in outputs], before)

    def test_adulterated_known_source_preserves_previous_historical_tables(self):
        source = self.source(2017)
        manifest = self.manifest([source])
        self.invoke('--anos', '2017', '--offline')
        output = self.registry / 'instituicoes-historico.csv'
        before = output.read_bytes()
        (self.root / source['arquivos'][0]['caminho_local']).write_bytes(b'arquivo adulterado')
        with patch.object(base, 'acquire') as acquire:
            with self.assertRaisesRegex(ValueError, 'tabelas históricas anteriores preservadas'):
                self.invoke('--anos', '2017', '--offline')
        acquire.assert_not_called()
        self.assertEqual(output.read_bytes(), before)
        self.assertEqual(json.loads(manifest.read_text())['fontes'], [source])

    def test_source_failure_does_not_erase_other_valid_annual_source(self):
        source18 = self.source(2018)
        self.manifest([source18])
        with patch.object(base, 'acquire', side_effect=OSError('Falha temporária sintética')):
            result = self.invoke('--anos', '2017')
        self.assertEqual(result, 1)
        data = json.loads((self.registry / 'fontes_inventario_historico.json').read_text())
        self.assertEqual([s['ano_censo'] for s in data['fontes']], [2018])
        self.assertEqual(data['pendencias_por_ano'][0]['ano_censo'], 2017)
        with (self.registry / 'instituicoes-historico.csv').open(encoding='utf-8', newline='') as stream:
            self.assertEqual({row['ano_fonte'] for row in csv.DictReader(stream)}, {'2018'})


if __name__ == '__main__':
    unittest.main()
