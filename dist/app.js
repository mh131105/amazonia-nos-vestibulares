import {summarize} from './model.js';

const $ = id => document.getElementById(id);
const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const number = value => new Intl.NumberFormat('pt-BR').format(value);
const plural = (n,one,many=one+'s') => `${number(n)} ${n===1?one:many}`;
const percent = value => value === null ? '—' : `${new Intl.NumberFormat('pt-BR',{minimumFractionDigits:1,maximumFractionDigits:1}).format(value)}%`;
const icon = name => `<svg class="icon" aria-hidden="true"><use href="#i-${name}"/></svg>`;
const names = {UEA:'UEA',UFAM:'UFAM · PSC',Inep:'Enem · Inep',USP:'FUVEST · USP',UERR:'UERR',UFRR:'UFRR'};
const shortNames = {UEA:'UEA',UFAM:'UFAM',Inep:'Enem',USP:'FUVEST',UERR:'UERR',UFRR:'UFRR'};
const normalize = value => String(value).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('pt-BR');
const safeURL = value => {try {const url = new URL(value); return ['https:','http:'].includes(url.protocol) ? url.href : '';} catch {return '';}};
const pageURL = (url,pages) => `${safeURL(url)}${safeURL(url) && pages?.length ? `#page=${pages[0]}` : ''}`;
const defaults = {institution:'all',from:2017,to:2026,area:'all',stage:'all'};
const filters = {...defaults};
let data, view, topicById, sourceById;
let selectedTopic = null, search = '', page = 1, showAllTopics = false;
const pageSize = 10;
let toastTimer;

function toast(message){$('toast').textContent=message;$('toast').classList.add('visible');clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('toast').classList.remove('visible'),3000);}
function renderOptions(){
  for(const id of ['from','to']) $(''+id).innerHTML=Array.from({length:10},(_,i)=>`<option value="${2017+i}">${2017+i}</option>`).join('');
  const params=new URLSearchParams(location.search);
  for(const key of ['institution','area','stage']) if(params.has(key)) filters[key]=params.get(key);
  for(const key of ['from','to']) if(params.has(key)) filters[key]=Number(params.get(key));
  if(!Object.hasOwn(names,filters.institution)) filters.institution='all';
  if(!['all','História','Geografia'].includes(filters.area)) filters.area='all';
  for(const key of ['from','to']) if(!Number.isInteger(filters[key]) || filters[key]<2017 || filters[key]>2026) filters[key]=defaults[key];
  if(filters.from>filters.to) [filters.from,filters.to]=[filters.to,filters.from];
  for(const key of ['institution','from','to','area']) $(key).value=filters[key];
  populateStages();
  if(params.has('topic') && topicById.has(params.get('topic'))) selectedTopic=params.get('topic');
  search=params.get('q')||'';$('question-search').value=search;
}
function populateStages(){
  const stages=[...new Set(data.exams.filter(e=>filters.institution==='all'||e.institution===filters.institution).map(e=>e.stage))].sort((a,b)=>a.localeCompare(b,'pt-BR'));
  if(!stages.includes(filters.stage)) filters.stage='all';
  $('stage').innerHTML='<option value="all">Todas as fases</option>'+stages.map(s=>`<option value="${escape(s)}">${escape(s)}</option>`).join('');
  $('stage').value=filters.stage;
}
function updateURL(){
  const params=new URLSearchParams();
  for(const key of Object.keys(defaults)) if(filters[key]!==defaults[key]) params.set(key,String(filters[key]));
  if(selectedTopic) params.set('topic',selectedTopic);
  if(search) params.set('q',search);
  history.replaceState(null,'',`${location.pathname}${params.size?'?'+params.toString():''}${location.hash}`);
}
function refresh(){
  view=summarize(data,filters);page=1;
  if(selectedTopic && !view.topicRanking.some(t=>t.id===selectedTopic)) selectedTopic=null;
  $('metric-questions').textContent=number(view.questions.length);
  $('metric-exams').textContent=number(view.exams.length);
  $('metric-topics').textContent=number(view.topicRanking.filter(t=>t.count>0).length);
  $('metric-coverage').textContent=percent(view.coverage.percent);
  $('metric-questions-note').textContent='Questões únicas no recorte';
  const withQuestions=new Set(view.questions.map(q=>q.examId)).size;
  $('metric-exams-note').textContent=`${number(withQuestions)} com questões amazônicas`;
  $('metric-topics-note').textContent=`Do catálogo de ${view.topicRanking.length} tópicos`;
  $('metric-coverage-note').textContent=view.coverage.percent===null ? 'Sem base comparável no recorte' : `${number(view.coverage.covered)} de ${number(view.coverage.expected)} · ${plural(view.coverage.examCount,'prova')}`;
  $('filter-context').textContent=`${filters.from===filters.to?filters.from:filters.from+'–'+filters.to} · ${filters.institution==='all'?view.institutions.length+' origens':names[filters.institution]}${filters.area!=='all'?' · '+filters.area:''}${filters.stage!=='all'?' · '+filters.stage:''}`;
  $('reset-filters').disabled=Object.keys(defaults).every(k=>filters[k]===defaults[k])&&!selectedTopic&&!search;
  renderAnnual();renderOrigins();renderTopics();renderCoverage();renderBank();updateURL();
  $('panorama').setAttribute('aria-busy','false');
}
function renderAnnual(){
  const max=Math.max(5,...view.yearly.map(y=>y.questions));
  const step=max>12?Math.ceil(max/4/5)*5:Math.max(1,Math.ceil(max/4));
  const ceiling=step*4;
  const ticks=Array.from({length:5},(_,i)=>Math.round(ceiling*(4-i)/4));
  $('annual-count').textContent=`${view.yearly.length} ${view.yearly.length===1?'ano':'anos'}`;
  $('annual-chart').innerHTML=`<div class="chart-y-axis" aria-hidden="true">${ticks.map(n=>`<span>${n}</span>`).join('')}</div>`+view.yearly.map(y=>{
    const qs=view.questions.filter(q=>q.year===y.year);
    const h=qs.filter(q=>q.area==='História').length,g=qs.filter(q=>q.area==='Geografia').length;
    return `<button class="year-bar-button" data-year="${y.year}" aria-label="${y.year}: ${plural(y.questions,'questão','questões')}, ${plural(y.exams,'prova')}. ${h} de História e ${g} de Geografia pela disciplina principal. Filtrar este ano."><span class="bar-space">${y.questions?`<span class="bar-stack" style="height:${100*y.questions/ceiling}%"><span class="bar-history" style="height:${100*h/y.questions}%"></span><span class="bar-geography" style="height:${100*g/y.questions}%"></span></span>`:`<span class="bar-empty"></span>`}</span><span class="bar-year">${y.year}</span><span class="chart-tooltip"><strong>${y.year}</strong>${y.exams?`${plural(y.questions,'questão','questões')} · ${plural(y.exams,'prova')}`:'Sem prova no recorte'}<br>${h} História · ${g} Geografia</span></button>`;
  }).join('');
}
function renderOrigins(){
  const rows=[...view.institutions].sort((a,b)=>b.questions-a.questions);
  const max=Math.max(1,...rows.map(r=>r.questions));
  $('origin-chart').innerHTML=rows.length?rows.map(r=>`<button class="origin-row" data-institution="${escape(r.institution)}" aria-pressed="${filters.institution===r.institution}" aria-label="${escape(names[r.institution])}: ${plural(r.questions,'questão','questões')} em ${plural(r.exams,'prova')}. Filtrar origem."><span class="origin-name">${escape(shortNames[r.institution])}</span><span class="origin-track"><span class="origin-fill" style="width:${100*r.questions/max}%"></span></span><span class="origin-value">${r.questions}</span></button>`).join(''):'<div class="empty-state">Nenhuma prova neste recorte.</div>';
}
function renderTopics(){
  const rows=showAllTopics?view.topicRanking:view.topicRanking.filter(t=>t.count>0).slice(0,8);
  const max=Math.max(1,...rows.map(t=>t.count));
  $('toggle-topics').innerHTML=`${showAllTopics?'Ver menos':'Ver todos'}${icon('arrow')}`;
  $('toggle-topics').setAttribute('aria-expanded',String(showAllTopics));
  $('topic-chart').innerHTML=rows.length?rows.map((t,i)=>`<button class="topic-row" data-topic="${t.id}" aria-pressed="${selectedTopic===t.id}" aria-label="Consultar ${escape(t.label)}, ${t.count} questões"><span class="topic-index">${String(i+1).padStart(2,'0')}</span><span class="topic-main"><span class="topic-name">${escape(t.label)}</span><span class="topic-track"><span class="topic-fill" style="width:${100*t.count/max}%"></span></span></span><span class="topic-value">${t.count}</span></button>`).join(''):'<div class="empty-state"><strong>Nenhuma questão neste recorte</strong>Os programas podem prever conteúdos mesmo sem questões identificadas.</div>';
}
function renderCoverage(){
  const rows=[...view.institutions].sort((a,b)=>b.expected-a.expected);
  $('coverage-chart').innerHTML=rows.length?rows.map(r=>`<div class="coverage-row ${r.coveragePercent===null?'unavailable':''}"><div class="coverage-row-top"><span>${escape(names[r.institution])}</span><strong>${percent(r.coveragePercent)}</strong></div><div class="coverage-track">${r.coveragePercent!==null?`<span class="coverage-fill" style="width:${r.coveragePercent}%"></span>`:''}</div><div class="coverage-caption">${r.coveragePercent===null?'Sem base comparável':`${r.covered} de ${r.expected} pares prova × tópico · ${plural(r.comparables,'prova')}`}</div></div>`).join(''):'<div class="empty-state">Nenhuma prova neste recorte.</div>';
}
function bankQuestions(){
  const words=normalize(search).trim().split(/\s+/).filter(Boolean);
  const rows=view.questions.filter(q=>(!selectedTopic||q.topicIds.includes(selectedTopic))&&(!words.length||words.every(word=>normalize([q.statement,q.number,q.year,q.edition,q.area,names[q.institution],q.stage,...q.topicIds.map(id=>topicById.get(id).label)].join(' ')).includes(word))));
  const sort=$('sort-questions').value;
  return rows.sort((a,b)=>(sort==='institution'?names[a.institution].localeCompare(names[b.institution],'pt-BR'):0)||(sort==='oldest'?a.year-b.year:b.year-a.year)||a.number.localeCompare(b.number,'pt-BR',{numeric:true})||a.id.localeCompare(b.id));
}
function renderBank(){
  const rows=bankQuestions();const pages=Math.max(1,Math.ceil(rows.length/pageSize));page=Math.min(page,pages);
  const start=(page-1)*pageSize;
  $('bank-count').textContent=number(rows.length);
  $('bank-filter').hidden=!selectedTopic;
  $('bank-filter').innerHTML=selectedTopic?`<button class="topic-chip" id="clear-topic">${escape(topicById.get(selectedTopic).label)}${icon('close')}<span class="visually-hidden">Remover tópico selecionado</span></button>`:'';
  $('questions-body').innerHTML=rows.length?rows.slice(start,start+pageSize).map(q=>{
    const topic=topicById.get(q.primaryTopicId);
    return `<tr><td><span class="question-title"><span class="question-number">${/^\d+$/.test(q.number)?'Q. ':''}${escape(q.number)}</span>${escape(topic.label)}</span><span class="question-subtitle">${escape(topic.content)} · ${escape(q.area)}</span></td><td><span class="question-institution">${escape(names[q.institution])}</span><span class="question-stage">${escape(q.stage)}</span></td><td>${q.year}</td><td><button class="question-open" data-question="${escape(q.id)}" aria-label="Abrir questão ${escape(q.number)} de ${escape(shortNames[q.institution])}, aplicação ${q.year}">${icon('arrow')}</button></td></tr>`;
  }).join(''):'<tr><td colspan="4"><div class="empty-state"><strong>Nenhuma questão encontrada</strong>Tente outro termo ou remova os filtros do banco.</div></td></tr>';
  $('pagination-label').textContent=rows.length?`${start+1}–${Math.min(start+pageSize,rows.length)} de ${plural(rows.length,'questão','questões')}`:'0 questões';
  $('page-label').textContent=`${page} / ${pages}`;
  $('previous-page').disabled=page===1;$('next-page').disabled=page>=pages;
}
function openDialog(kicker,body){
  $('dialog-kicker').textContent=kicker;$('dialog-body').innerHTML=body;
  $('detail-dialog').showModal();$('dialog-body').scrollTop=0;document.body.style.overflow='hidden';
}
function sourceLink(url,label,pages=[]){const href=pageURL(url,pages);return href?`<a class="inline-link" href="${escape(href)}" target="_blank" rel="noopener noreferrer">${escape(label)} ↗</a>`:'<span>Documento não recuperado</span>';}
function openQuestion(id){
  const q=data.questions.find(q=>q.id===id);if(!q)return;
  const topic=topicById.get(q.primaryTopicId),source=sourceById.get(q.sourceId);
  const links=q.syllabusItemIds.map(id=>data.syllabus.find(s=>s.id===id)).filter(Boolean);
  const correction=q.id==='uea-2026-ce-q05';
  const body=`<h2 id="dialog-title">${escape(shortNames[q.institution])} · Questão ${escape(q.number)}</h2><div class="meta-line"><span class="meta-tag">Aplicação ${q.year}</span><span class="meta-tag">${escape(q.stage)}</span><span class="meta-tag blue">${escape(q.area)}</span>${q.answer==='ANULADA'?'<span class="meta-tag">Anulada</span>':''}</div><p>Edição: ${escape(q.edition)}.</p><div class="meta-line">${q.topicIds.map(id=>`<span class="meta-tag ${id===q.primaryTopicId?'blue':''}">${escape(topicById.get(id).label)}${id===q.primaryTopicId?' · principal':''}</span>`).join('')}</div>${q.visual?`<div class="notice">Esta questão usa imagem, mapa ou gráfico. Consulte ${q.pdfPages.length===1?'a página':'as páginas'} ${q.pdfPages.join(', ')} no PDF da prova.</div>`:''}<div class="question-statement">${escape(q.statement)}</div>${q.options.length?`<ol class="options-list">${q.options.map(o=>`<li><span class="option-letter">${o.label}</span><span>${escape(o.text)}</span></li>`).join('')}</ol>`:''}<div class="dialog-actions"><a class="button button-dark" href="${escape(pageURL(q.url,q.pdfPages))}" target="_blank" rel="noopener noreferrer">${icon('file')}Abrir prova · p. ${q.pdfPages.join(', ')}${icon('external')}</a></div><details class="source-details"><summary>Gabarito e dados de origem</summary><p><strong>Gabarito:</strong> ${q.answer===null?'Não incorporado ao banco':q.answer==='ANULADA'?'Questão anulada':escape(q.answer)}.</p><p><strong>Fonte:</strong> ${escape(source?.origin==='oficial'?'Publicação institucional':'Cópia pública identificada de prova oficial')}. ${source?.officialUrl?sourceLink(source.officialUrl,'Publicação institucional'):''}</p><p><strong>Identificador:</strong> ${escape(q.id)}</p><p><strong>SHA-256 do documento:</strong> ${escape(source?.sha256||'Não registrado')}</p>${q.observation?`<p>${escape(q.observation)}</p>`:''}</details><h3>Correspondência com o programa</h3><p>${escape(topic.content)}. Vínculo ${q.syllabusLinkType==='não localizado'?'não localizado':q.syllabusLinkType} na curadoria.</p>${links.length?links.map(item=>`<article class="syllabus-item"><div class="meta-line"><span class="meta-tag">${item.scope==='regional explícito'?'Regional explícito':'Cláusula geral'}</span><span>Programa · p. ${item.pages.join(', ')}</span></div><p>${escape(item.text)}</p>${correction&&item.id.endsWith('historia-027')?'<div class="notice review">Vínculo em revisão: este item trata do Segundo Reinado; a questão se refere ao Pará em 1823. Esse vínculo geral não entra no cálculo da cobertura regional.</div>':''}${sourceLink(item.url,'Consultar programa',item.pages)}</article>`).join(''):'<div class="notice">Nenhum vínculo programático foi localizado para esta questão. Isso não demonstra que ela esteja fora do edital.</div>'}<details class="source-details"><summary>Critério de inclusão no estudo</summary><p>${escape(q.justification)}</p><p>Foco regional ${q.regionalFocus==='central'?'central':'substantivo em contexto misto'}. Classificação assistida por IA.</p></details>`;
  openDialog('BANCO DE QUESTÕES',body);
}
function openMethod(){
  openDialog('SOBRE OS DADOS',`<h2 id="dialog-title">Como ler este estudo</h2><p>Reunimos questões de História e Geografia da Amazônia e os programas das provas para comparar o conteúdo previsto com a cobrança identificada.</p><div class="method-facts"><div class="method-fact"><strong>196</strong><span>questões amazônicas</span></div><div class="method-fact"><strong>70</strong><span>provas examinadas</span></div><div class="method-fact"><strong>53</strong><span>tópicos no catálogo</span></div></div><h3>O recorte</h3><p>Aplicações de 1º de janeiro de 2017 a 11 de novembro de 2026. O núcleo reúne UEA Vestibular/Macro e UFAM PSC; o complemento inclui Enem regular impresso, segunda fase FUVEST e duas edições de UERR e UFRR. O levantamento não é um censo de todas as instituições brasileiras.</p><h3>O que significa 20,7%</h3><p>Nas 43 provas com triagem completa e programa regional integral, identificamos cobrança de 141 dos 682 pares prova × tópico previstos. Um tópico previsto em cinco provas conta cinco vezes. A razão soma os tópicos cobrados e os previstos; ela não é uma média dos percentuais por prova.</p><p>Os conteúdos vêm das ementas. Padronizamos os nomes e desdobramentos em disciplina, conteúdo e tópico, preservando a redação original. Para contar uma cobrança, exigimos uma questão ligada ao item pertinente do programa e ao tópico correspondente.</p><h3>Questões e tópicos</h3><p>Cada questão tem um tópico principal e pode ter tópicos secundários. Por isso, as frequências por tópico não somam o total de questões. História e Geografia selecionam qualquer tópico da área: há 25 questões com ambas as disciplinas. O gráfico anual usa a disciplina principal, contando cada questão uma vez.</p><p>A busca e o tópico selecionado afetam o banco de questões. Os filtros de origem, aplicação, disciplina e etapa atualizam todos os indicadores. As oito provas sem questões amazônicas continuam no cadastro.</p><h3>Zeros e lacunas</h3><p>“—” significa que não há base comparável para a cobertura. Enem e FUVEST possuem vínculos programáticos amplos e ficam fora dessa proporção regional explícita. Zero significa que observamos a previsão regional, mas não encontramos cobrança vinculada aos seus tópicos. UEA 2026 Humanas, por exemplo, tem três questões regionais amparadas por cláusulas gerais e cobertura de 0/14 no recorte explícito.</p><p>O programa UEA 2017 e dois editais PSC 2018 permanecem pendentes. Quatro provas PSC de primeira etapa recentes não apresentam previsão regional explícita registrada. As questões anuladas permanecem porque apareceram nos cadernos.</p><h3>Datas e fontes</h3><p>Ano de aplicação, edição e ingresso são distintos. UEA 2020 e Enem 2020 ocorreram em 2021; duas edições UEA ocorreram em 2022. Os detalhes conservam a edição e as páginas dos PDFs. As fontes distinguem publicações institucionais de cópias públicas identificadas.</p><h3>Autoria e curadoria</h3><p>Projeto de Matheus Garcia, com pesquisa, classificação e implementação assistidas por Codex. Uma associação geral de UEA 2026 Q05 ao Segundo Reinado está em revisão e aparece sinalizada nos detalhes; ela não modifica o indicador regional explícito.</p><div class="dialog-actions"><a class="button button-outline" href="dataset.json" download="amazonia-nas-provas.json">${icon('download')}Baixar base completa · JSON</a></div>`);
}
function openPrograms(){
  const coverageByExam=new Map(view.coverage.byExam.map(c=>[c.examId,c]));
  openDialog('CONTEÚDOS E EMENTAS',`<h2 id="dialog-title">Previsão e cobrança por prova</h2><p>O recorte atual reúne ${plural(view.exams.length,'prova')}. ${view.coverage.examCount} fornecem denominador para a cobertura regional. Os valores contam tópicos padronizados em cada prova.</p><div class="table-scroll"><table class="programs-table"><thead><tr><th>Prova e aplicação</th><th>Cobrados / previstos</th><th>Cobertura</th><th>Programa</th></tr></thead><tbody>${[...view.exams].sort((a,b)=>b.year-a.year||a.id.localeCompare(b.id)).map(e=>{
    const c=coverageByExam.get(e.id);const sources=e.syllabusSourceIds.map(id=>sourceById.get(id)).filter(Boolean);
    return `<tr><td>${escape(names[e.institution])} · ${e.year}<small>${escape(e.stage)}<br>Edição ${escape(e.edition)}</small></td><td>${c.percent===null?'—':`${c.covered} / ${c.expected}`}</td><td>${percent(c.percent)}</td><td>${sources.length?sources.map(s=>s.sha256?sourceLink(s.url,'Abrir PDF'):'Pendente').join('<br>'):'Não recuperado'}</td></tr>`;
  }).join('')}</tbody></table></div>`);
}
function renderSources(query=''){
  const words=normalize(query).trim().split(/\s+/).filter(Boolean);
  const rows=data.sources.filter(s=>words.every(word=>normalize([s.id,s.title,s.institution,s.type,s.origin].join(' ')).includes(word)));
  $('source-list').innerHTML=rows.map(s=>{
    const years=data.exams.filter(e=>e.sourceId===s.id||e.syllabusSourceIds.includes(s.id)).map(e=>e.year);
    const yearLabel=years.length?` · ${Math.min(...years)}${Math.min(...years)!==Math.max(...years)?'–'+Math.max(...years):''}`:'';
    return `<article class="source-card"><strong>${escape(s.title)}${yearLabel}</strong><p>${s.origin==='oficial'?'Publicação institucional':'Cópia pública identificada'} · ${s.sha256?'Arquivo recuperado e identificado por hash':'Arquivo pendente de recuperação'}</p>${sourceLink(s.url,'Documento consultado')}${s.officialUrl&&s.officialUrl!==s.url?sourceLink(s.officialUrl,'Publicação institucional'):''}</article>`;
  }).join('')||'<div class="empty-state">Nenhuma fonte com esse termo.</div>';
}
function openSources(){
  openDialog('FONTES CONSULTADAS',`<h2 id="dialog-title">Documentos de origem</h2><p>${data.sources.length} referências de provas, programas e gabaritos. Os detalhes de cada questão indicam o documento e a página utilizados.</p><label><span class="visually-hidden">Pesquisar fontes</span><input class="source-search" id="source-search" type="search" placeholder="Buscar por instituição, ano ou tipo de documento"></label><div id="source-list"></div>`);
  renderSources();$('source-search').addEventListener('input',e=>renderSources(e.target.value));
}
function download(){
  const rows=bankQuestions();if(!rows.length){toast('O recorte não tem questões para exportar.');return;}
  const headers=['questao_id','instituicao','ano_aplicacao','edicao','fase_etapa','numero','disciplina_principal','conteudo','topico_principal','topicos','enunciado','alternativa_a','alternativa_b','alternativa_c','alternativa_d','alternativa_e','gabarito','vinculo_ementa','url_prova','paginas_pdf'];
  const cell=value=>`"${String(value??'').replace(/"/g,'""')}"`;
  const lines=rows.map(q=>[q.id,names[q.institution],q.year,q.edition,q.stage,q.number,q.area,topicById.get(q.primaryTopicId).content,topicById.get(q.primaryTopicId).label,q.topicIds.map(id=>topicById.get(id).label).join(' | '),q.statement,...['A','B','C','D','E'].map(l=>q.options.find(o=>o.label===l)?.text||''),q.answer,q.syllabusLinkType,q.url,q.pdfPages.join('|')].map(cell).join(';'));
  const blob=new Blob(['\ufeff'+headers.map(cell).join(';')+'\r\n'+lines.join('\r\n')+'\r\n'],{type:'text/csv;charset=utf-8;'});
  const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=`amazonia-questoes-${filters.from}-${filters.to}.csv`;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);toast(`${plural(rows.length,'questão','questões')} ${rows.length===1?'exportada':'exportadas'}.`);
}
function scrollToBank(){document.getElementById('questoes').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});$('bank-title').focus({preventScroll:true});}
function closeMenu(returnFocus=false){const wasOpen=$('sidebar').classList.contains('open');$('sidebar').classList.remove('open');$('menu-toggle').setAttribute('aria-expanded','false');if(wasOpen&&returnFocus)$('menu-toggle').focus();}
function setupEvents(){
  $('filters').addEventListener('submit',e=>e.preventDefault());
  $('filters').addEventListener('change',e=>{
    if(!Object.hasOwn(filters,e.target.name))return;
    filters[e.target.name]=['from','to'].includes(e.target.name)?Number(e.target.value):e.target.value;
    if(filters.from>filters.to){if(e.target.name==='from')filters.to=filters.from;else filters.from=filters.to;$('from').value=filters.from;$('to').value=filters.to;}
    if(e.target.name==='institution')populateStages();
    refresh();
  });
  $('reset-filters').addEventListener('click',()=>{Object.assign(filters,defaults);selectedTopic=null;search='';$('question-search').value='';for(const key of ['institution','from','to','area'])$(key).value=filters[key];populateStages();refresh();});
  $('question-search').addEventListener('input',e=>{search=e.target.value;page=1;renderBank();updateURL();$('reset-filters').disabled=false;});
  $('sort-questions').addEventListener('change',()=>{page=1;renderBank();});
  $('toggle-topics').addEventListener('click',()=>{showAllTopics=!showAllTopics;renderTopics();});
  $('previous-page').addEventListener('click',()=>{if(page>1){page--;renderBank();}});
  $('next-page').addEventListener('click',()=>{page++;renderBank();});
  $('download-button').addEventListener('click',download);
  $('share-button').addEventListener('click',async()=>{updateURL();const fallback=setTimeout(()=>toast('Copie o endereço desta página para compartilhar o recorte.'),1200);try{await navigator.clipboard.writeText(location.href);clearTimeout(fallback);toast('Link do recorte copiado.');}catch{clearTimeout(fallback);toast('Copie o endereço desta página para compartilhar o recorte.');}});
  $('menu-toggle').addEventListener('click',()=>{$('sidebar').classList.toggle('open');$('menu-toggle').setAttribute('aria-expanded',String($('sidebar').classList.contains('open')));});
  document.addEventListener('click',e=>{
    const open=e.target.closest('[data-open]');if(open){closeMenu(true);({method:openMethod,programs:openPrograms,sources:openSources}[open.dataset.open])();return;}
    const question=e.target.closest('[data-question]');if(question){openQuestion(question.dataset.question);return;}
    const institution=e.target.closest('[data-institution]');if(institution){filters.institution=institution.dataset.institution;$('institution').value=filters.institution;populateStages();refresh();document.querySelector(`[data-institution="${filters.institution}"]`)?.focus({preventScroll:true});return;}
    const year=e.target.closest('[data-year]');if(year){filters.from=filters.to=Number(year.dataset.year);$('from').value=filters.from;$('to').value=filters.to;refresh();document.querySelector(`[data-year="${filters.from}"]`)?.focus({preventScroll:true});return;}
    const topic=e.target.closest('[data-topic]');if(topic){selectedTopic=selectedTopic===topic.dataset.topic?null:topic.dataset.topic;page=1;renderTopics();renderBank();updateURL();$('reset-filters').disabled=false;scrollToBank();return;}
    if(e.target.closest('#clear-topic')){selectedTopic=null;page=1;renderTopics();renderBank();updateURL();$('bank-title').focus({preventScroll:true});return;}
    const nav=e.target.closest('[data-nav]');if(nav){document.querySelectorAll('[data-nav]').forEach(n=>n.classList.toggle('active',n===nav));closeMenu();$(nav.dataset.nav).focus({preventScroll:true});}
    if($('sidebar').classList.contains('open')&&!e.target.closest('#sidebar')&&!e.target.closest('#menu-toggle'))closeMenu();
  });
  $('close-dialog').addEventListener('click',()=>$('detail-dialog').close());
  $('detail-dialog').addEventListener('close',()=>{document.body.style.overflow='';});
  $('detail-dialog').addEventListener('click',e=>{if(e.target===$('detail-dialog')){const r=e.target.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)e.target.close();}});
  document.addEventListener('keydown',e=>{if(e.key==='Escape')closeMenu(true);});
  const observer=new IntersectionObserver(entries=>{for(const entry of entries)if(entry.isIntersecting){document.querySelectorAll('[data-nav]').forEach(n=>n.classList.toggle('active',n.dataset.nav===entry.target.id));}},{rootMargin:'-10% 0px -65% 0px',threshold:0});
  for(const id of ['panorama','conteudos','questoes'])observer.observe($(id));
}
async function start(){
  try{
    const response=await fetch('dataset.json');if(!response.ok)throw new Error(`HTTP ${response.status}`);data=await response.json();
    topicById=new Map(data.topics.map(t=>[t.id,t]));sourceById=new Map(data.sources.map(s=>[s.id,s]));
    renderOptions();setupEvents();refresh();
  }catch(error){$('panorama').setAttribute('aria-busy','false');$('loading-error').hidden=false;$('loading-error').textContent='Não foi possível carregar os dados. Recarregue a página ou confira se abriu o dashboard por um servidor HTTP.';console.error('Falha ao carregar o acervo:',error);}
}
start();
