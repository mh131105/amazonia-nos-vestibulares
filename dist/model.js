/** Summarize the curated corpus without changing its records. */
export function summarize(data, filters = {}) {
  const institution = filters.institution ?? 'all';
  const stage = filters.stage ?? 'all';
  const area = filters.area ?? 'all';
  const from = Number(filters.from ?? data.meta.startYear);
  const to = Number(filters.to ?? data.meta.endYear);
  if (!Number.isInteger(from) || !Number.isInteger(to) || from > to) {
    throw new RangeError('Intervalo de anos inválido.');
  }
  if (!['all', 'História', 'Geografia'].includes(area)) {
    throw new RangeError('Disciplina inválida.');
  }

  const topics = data.topics.filter(t => area === 'all' || t.area === area);
  const topicIds = new Set(topics.map(t => t.id));
  // Keep exams with no selected questions: they can still supply a denominator.
  const exams = data.exams.filter(e =>
    e.year >= from && e.year <= to &&
    (institution === 'all' || e.institution === institution) &&
    (stage === 'all' || e.stage === stage));
  const examIds = new Set(exams.map(e => e.id));
  const questions = data.questions.filter(q => examIds.has(q.examId) &&
    q.topicIds.some(id => topicIds.has(id)));
  const questionsByExam = new Map(exams.map(e => [e.id, []]));
  for (const q of questions) questionsByExam.get(q.examId).push(q);

  const regionalItems = new Map();
  const expectedByExam = new Map(exams.map(e => [e.id, new Set()]));
  for (const item of data.syllabus) {
    if (!examIds.has(item.examId) || item.scope !== 'regional explícito') continue;
    regionalItems.set(item.id, item);
    for (const id of item.topicIds) {
      if (topicIds.has(id)) expectedByExam.get(item.examId).add(id);
    }
  }

  const coverageByExam = new Map();
  for (const exam of exams) {
    const expected = expectedByExam.get(exam.id);
    const comparable = exam.screenedComplete && exam.regionalSyllabusComplete && expected.size > 0;
    const covered = new Set();
    if (comparable) {
      for (const q of questionsByExam.get(exam.id)) {
        for (const itemId of q.syllabusItemIds) {
          const item = regionalItems.get(itemId);
          if (!item || item.examId !== exam.id) continue;
          // A shared topic elsewhere in the programme is not a semantic link.
          for (const id of item.topicIds) {
            if (topicIds.has(id) && q.topicIds.includes(id)) covered.add(id);
          }
        }
      }
    }
    coverageByExam.set(exam.id, {comparable, expected, covered});
  }

  function coverageFor(selectedExams) {
    let expected = 0, covered = 0, examCount = 0;
    const byExam = selectedExams.map(exam => {
      const c = coverageByExam.get(exam.id);
      if (!c.comparable) {
        return {examId: exam.id, expected: null, covered: null, percent: null};
      }
      expected += c.expected.size;
      covered += c.covered.size;
      examCount++;
      return {examId: exam.id, expected: c.expected.size, covered: c.covered.size,
        percent: 100 * c.covered.size / c.expected.size};
    });
    return {expected, covered, examCount, percent: expected ? 100 * covered / expected : null, byExam};
  }

  const topicRanking = topics.map(t => {
    const matching = questions.filter(q => q.topicIds.includes(t.id));
    return {id: t.id, label: t.label, area: t.area, content: t.content,
      count: matching.length,
      primaryCount: matching.filter(q => q.primaryTopicId === t.id).length,
      examCount: new Set(matching.map(q => q.examId)).size,
      expectedExamCount: exams.filter(e => {
        const c = coverageByExam.get(e.id);
        return c.comparable && c.expected.has(t.id);
      }).length,
      coveredExamCount: exams.filter(e => {
        const c = coverageByExam.get(e.id);
        return c.comparable && c.covered.has(t.id);
      }).length};
  }).sort((a, b) => b.count - a.count || b.primaryCount - a.primaryCount ||
    a.label.localeCompare(b.label, 'pt-BR'));

  const yearly = [];
  for (let year = from; year <= to; year++) {
    const selected = exams.filter(e => e.year === year);
    const c = coverageFor(selected);
    yearly.push({year, questions: questions.filter(q => q.year === year).length,
      exams: selected.length, covered: c.covered, expected: c.expected,
      coveragePercent: c.percent});
  }
  const institutions = [...new Set(exams.map(e => e.institution))].sort().map(institution => {
    const selected = exams.filter(e => e.institution === institution);
    const c = coverageFor(selected);
    return {institution, questions: questions.filter(q => q.institution === institution).length,
      exams: selected.length, covered: c.covered, expected: c.expected,
      coveragePercent: c.percent, comparables: c.examCount};
  });

  return {exams, questions, coverage: coverageFor(exams), topicRanking, yearly, institutions};
}
