/** Regressões do acervo congelado: expectativas conferidas nos CSVs da pesquisa. */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { summarize } from '../dashboard/model.js';

const data = JSON.parse(readFileSync(new URL('../dashboard/dataset.json', import.meta.url), 'utf8'));

test('cobertura global usa a razão dos totais, com 43 programas comparáveis', () => {
  const result = summarize(data);
  assert.equal(result.questions.length, 196);
  assert.equal(result.exams.length, 70);
  assert.equal(result.coverage.examCount, 43);
  assert.equal(result.coverage.covered, 141);
  assert.equal(result.coverage.expected, 682);
  assert.equal(result.coverage.percent, 100 * 141 / 682);

  const rates = result.coverage.byExam.filter(exam => exam.percent !== null);
  const unweightedMean = rates.reduce((sum, exam) => sum + exam.percent, 0) / rates.length;
  assert.notEqual(result.coverage.percent, unweightedMean);
});

test('ausência de denominador no Enem difere do zero observado na UEA', () => {
  const enem = summarize(data, { institution: 'Inep' });
  assert.equal(enem.questions.length, 17);
  assert.equal(enem.exams.length, 9);
  assert.equal(enem.coverage.examCount, 0);
  assert.equal(enem.coverage.percent, null);
  assert.ok(enem.coverage.byExam.every(exam => exam.expected === null && exam.covered === null));

  const uea = summarize(data, {
    institution: 'UEA', stage: '2ª fase — Humanas', from: 2026, to: 2026,
  });
  assert.deepEqual(uea.exams.map(exam => exam.id), ['uea-vest2026-ce']);
  assert.equal(uea.questions.length, 3);
  assert.equal(uea.coverage.examCount, 1);
  assert.equal(uea.coverage.covered, 0);
  assert.equal(uea.coverage.expected, 14);
  assert.equal(uea.coverage.percent, 0);
});

test('filtros preservam prova sem questões e distinguem ano sem prova', () => {
  // A edição PSC 2019 foi aplicada em 2018: o filtro usa aplicação, não edição.
  const psc = summarize(data, {
    institution: 'UFAM', stage: 'PSC — 3ª etapa', from: 2018, to: 2018,
  });
  assert.deepEqual(psc.exams.map(exam => exam.id), ['ufam-psc2019-e3']);
  assert.equal(psc.questions.length, 0);
  assert.equal(psc.coverage.examCount, 1);
  assert.equal(psc.coverage.expected, 4);
  assert.equal(psc.coverage.covered, 0);
  assert.equal(psc.coverage.percent, 0);

  const gap = summarize(data, { institution: 'UEA', from: 2020, to: 2020 });
  assert.equal(gap.exams.length, 0);
  assert.equal(gap.questions.length, 0);
  assert.equal(gap.coverage.percent, null);
  assert.equal(gap.yearly[0].exams, 0);
  assert.equal(gap.yearly[0].coveragePercent, null);
});

test('etiquetas de História e Geografia podem se sobrepor sem duplicar questões', () => {
  const history = summarize(data, { area: 'História' });
  const geography = summarize(data, { area: 'Geografia' });
  const historyIds = new Set(history.questions.map(question => question.id));
  const geographyIds = new Set(geography.questions.map(question => question.id));

  assert.equal(history.questions.length, 92);
  assert.equal(historyIds.size, 92);
  assert.equal(geography.questions.length, 129);
  assert.equal(geographyIds.size, 129);
  assert.equal([...historyIds].filter(id => geographyIds.has(id)).length, 25);
  assert.equal(new Set([...historyIds, ...geographyIds]).size, 196);
  assert.equal(history.exams.length, 70);
  assert.equal(geography.exams.length, 70);
  assert.equal(history.coverage.covered, 75);
  assert.equal(history.coverage.expected, 410);
  assert.equal(geography.coverage.covered, 66);
  assert.equal(geography.coverage.expected, 272);
});
