import {RESPONSES,newSession,visibleEvidence,choose,advance,readAll,exportSession} from './case-model.js';
const TYPE_LABEL={published_cot:'PUBLISHED CoT · LITERAL EXCERPT',public_message:'PUBLIC MESSAGE · LITERAL EXCERPT',investigator_reconstruction:'INVESTIGATOR RECONSTRUCTION · OUR PARAPHRASE'};

export async function initCasebook({esc,onScenario}){
 const root=document.querySelector('#casebook');
 try{
  const responses=await Promise.all([fetch('data/grounded_cases.json'),fetch('data/verified-excerpts.json')]);
  if(responses.some(r=>!r.ok))throw Error('Case data unavailable');
  const [data,audit]=await Promise.all(responses.map(r=>r.json()));
  let item=data.cases.find(c=>c.id===new URLSearchParams(location.search).get('case'))||data.cases[0];
  let session=newSession(item);
  function render(){
   const view=visibleEvidence(item,session),source=data.sources[item.source_id];
   const url=item.source_url||source.url+(item.anchor?'#'+item.anchor:'');
   const decided=session.decisions.some(d=>d.step===session.cursor);
   root.innerHTML=`<div class="case-toolbar"><label for="case-select">CHOOSE A RECORD<select id="case-select">${data.cases.map(c=>`<option value="${c.id}" ${c.id===item.id?'selected':''}>${esc(c.title)}</option>`).join('')}</select></label><div class="case-count"><strong>${session.cursor+1} / ${item.steps.length}</strong><span>selected passages revealed</span></div><button class="quiet-btn" id="case-reset">Start again ↺</button></div>
    <div class="case-heading"><span class="tag light">${esc(item.episode)}</span><h2>${esc(item.subtitle)}</h2><p>${esc(item.time||'Exact event time unavailable')} · ${esc(item.time_note)}</p></div>
    <div class="case-columns"><div class="case-record"><div class="record-heading"><span>THE PUBLISHED RECORD</span><span>NO GENERATED INNER MONOLOGUE</span></div>
    ${view.steps.map((step,i)=>`<article class="record-step"><div class="record-step-top"><span class="record-number">${String(i+1).padStart(2,'0')}</span><span class="tag ${step.kind==='investigator_reconstruction'?'light':'green'}">${TYPE_LABEL[step.kind]}</span></div><h3>${esc(step.actor)}</h3><p class="record-context">${esc(step.context)}</p>${step.quotes.map(q=>`<blockquote>${esc(q)}</blockquote>`).join('')}${step.quotes.length?'<p class="excerpt-note">Short excerpt; surrounding text is omitted. Quotation does not establish subjective experience.</p>':''}${session.decisions.find(d=>d.step===i)?`<div class="recorded-response">YOUR RESPONSE · ${esc(RESPONSES[session.decisions.find(d=>d.step===i).action])}</div>`:''}</article>`).join('')}
    ${session.revealed?`<div class="reported-outcome"><span class="panel-kicker">REPORTED OUTCOME / EVIDENCE LIMIT</span><p>${esc(view.outcome)}</p></div>`:`<div class="case-decision"><h3>What would you do with this evidence?</h3><p>Record a response before reading the next passage. There is no safety score: your choice does not establish that an incident would be prevented.</p><div class="case-actions">${Object.entries(RESPONSES).map(([key,label])=>`<button data-response="${key}" ${decided?'disabled':''}>${label}</button>`).join('')}</div><button id="case-next" class="case-next" ${decided?'':'disabled'}>${session.cursor===item.steps.length-1?'Reveal the reported outcome':'Reveal the next passage'} →</button><button id="case-read" class="text-link">Read the complete selected case without answering</button></div>`}
    </div><aside class="case-sidebar"><div class="source-box"><span class="panel-kicker">PROVENANCE</span><h3>${esc(source.title)}</h3><p>${esc(source.access)}</p><a class="full-source" href="${esc(url)}" target="_blank" rel="noreferrer">${esc(url)}</a><p class="source-locator">${esc(item.locator)}</p><details><summary>How the excerpt was checked</summary><p>${esc(source.quote_convention)}</p>${audit.excerpts.filter(e=>e.case_id===item.id).map(e=>`<p class="audit-excerpt"><strong>Passage ${e.step+1}</strong>${esc(e.method.replaceAll('_',' '))}${e.revision_id?`<br>Revision: ${esc(e.revision_id)}<br>Editor label: ${esc(e.editor_label)}<br>Added passage verified against previous revision.`:''}<code>${esc(e.excerpt_sha256)}</code></p>`).join('')||'<p>Investigator narration, manually checked against the linked report. No literal quotation is presented in this case.</p>'}</details></div><div class="visibility-box"><span class="panel-kicker">WHAT THE DELEGATE WOULD NEED TO SEE</span><p>${esc(item.observation_assumption)}</p></div>
    ${session.revealed?`<div class="case-interpretation"><span class="panel-kicker">OUR ANALYSIS</span><h3>What this can support</h3><p>${esc(item.claim)}</p><h3>What it cannot establish</h3><p>${esc(item.not_established)}</p><h3>Competing explanation</h3><p>${esc(item.alternative)}</p></div>`:'<div class="visibility-box"><p>Our interpretation and hypothetical delegate reply appear after the final passage. Full sources remain accessible; this is a learning exercise, not a blinded evaluation.</p></div>'}</aside></div>
    ${session.revealed?`<div class="case-counterfactual"><div><span class="tag warm">OUR HYPOTHETICAL REPLY · DID NOT OCCUR</span><blockquote>${esc(item.synthetic_reply)}</blockquote><p>${esc(item.intervention)}</p></div><div><span class="panel-kicker">FROM RECORD TO A TEST</span><p><strong>Preserved tension</strong>${esc(item.experiment.preserves)}</p><p><strong>What the simulation changes</strong>${esc(item.experiment.changes)}</p><p><strong>Next behavioral experiment</strong>${esc(item.experiment.next_test)}</p><button id="case-simulate" class="case-next">Explore the related mock scenario →</button></div></div>`:''}
    <div class="case-footer"><p>Selected passages, not a complete transcript. Responses stay in this browser session and are never uploaded.</p><button id="case-export" class="text-link">Download your exercise record ↓</button></div>`;
   root.querySelector('#case-select').addEventListener('change',e=>{item=data.cases.find(c=>c.id===e.target.value);session=newSession(item);render();});
   root.querySelector('#case-reset').addEventListener('click',()=>{session=newSession(item);render();});
   root.querySelectorAll('[data-response]').forEach(b=>b.addEventListener('click',()=>{session=choose(item,session,b.dataset.response);render();}));
   root.querySelector('#case-next')?.addEventListener('click',()=>{session=advance(item,session);render();});
   root.querySelector('#case-read')?.addEventListener('click',()=>{session=readAll(item,session);render();});
   root.querySelector('#case-simulate')?.addEventListener('click',()=>onScenario(item));
   root.querySelector('#case-export').addEventListener('click',()=>{
    const blob=new Blob([JSON.stringify(exportSession(item,session,data.version),null,2)],{type:'application/json'});
    const download=URL.createObjectURL(blob),a=document.createElement('a');a.href=download;a.download=`agent-delegate-case-${item.id}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(download),1000);
   });
  }
  render();
 }catch(error){root.textContent='Case records could not be loaded. The source dataset is available in data/grounded_cases.json in the repository.';}
}
