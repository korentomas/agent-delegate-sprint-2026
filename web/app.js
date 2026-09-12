import {loadCommonsStudy} from './commons-view.js';
import {CONDITIONS,SCENARIOS,runKey,project,messages,EXPERIMENTS} from './model.js';
import {initCasebook} from './cases.js';
const $=s=>document.querySelector(s);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const REPO='https://github.com/mpodeley/agent-delegate-sprint-2026';
let index,bundles={},tick=-1,timer=null,loadVersion=0,episode='collective',eventId=null,currentPage='laboratorio';
let settings={scenario:'minority_warning',left:'monitor',right:'delegate',latency:6,capture:false,bypass:true,coverage:'complete'};
let groundedCase=null;
const params=new URLSearchParams(location.search);
if(SCENARIOS[params.get('scenario')])settings.scenario=params.get('scenario');
for(const k of ['left','right'])if(CONDITIONS[params.get(k)])settings[k]=params.get(k);
if([0,2,6].includes(Number(params.get('latency')))&&params.has('latency'))settings.latency=Number(params.get('latency'));
for(const k of ['capture','bypass'])if(params.has(k))settings[k]=params.get(k)==='true';
if(params.get('coverage')==='missing_hidden')settings.coverage='missing_hidden';
for(const id of ['left-condition','right-condition'])$( '#'+id).innerHTML=Object.entries(CONDITIONS).map(([value,{name}])=>`<option value="${value}">${name}</option>`).join('');
function syncControls(){
 $('#scenario').value=settings.scenario;$('#left-condition').value=settings.left;$('#right-condition').value=settings.right;
 $('#latency').value=[0,2,6].indexOf(settings.latency);$('#latency-label').textContent={0:'immediate',2:'delayed',6:'late'}[settings.latency];
 $('#capture').checked=settings.capture;$('#bypass').checked=settings.bypass;$('#coverage').checked=settings.coverage==='missing_hidden';
 $('#scenario-description').textContent=SCENARIOS[settings.scenario].description;
}
function run(condition){return bundles[settings.scenario]?.[runKey(settings.scenario,condition,settings.latency,settings.capture,settings.bypass,settings.coverage)];}
async function loadScenario(){
 if(groundedCase&&groundedCase.experiment.scenario!==settings.scenario){groundedCase=null;$('#grounding-banner').hidden=true;}
 const version=++loadVersion;stop();tick=-1;$('#play').disabled=true;$('#next').disabled=true;$('#timeline').disabled=true;$('#simulation-status').textContent='Loading scenario…';$('#load-error').hidden=true;syncControls();
 try{
  if(!bundles[settings.scenario]){const key=settings.scenario;const res=await fetch(`data/${key}.json`);if(!res.ok)throw Error('Trace unavailable');bundles[key]=await res.json();}
  if(version!==loadVersion)return;
  $('#play').disabled=false;$('#timeline').disabled=false;render();
 }catch(e){if(version!==loadVersion)return;$('#load-error').textContent='Could not load this simulation. Check your connection and reload.';$('#load-error').hidden=false;}
}
function network(v,condition,lane){
 const represented=['delegate','layered'].includes(condition), channel=['delegate','layered','matched_monitor','critic'].includes(condition);
 const risk=v.harm>0,shadow=v.shadow,delivered=v.delivered;
 const gate=['layered','gates_only'].includes(condition),paused=v.state.paused;
 const center=represented?'Delegate':condition==='matched_monitor'?'Monitor + appeal':condition==='critic'?'Visible critic':gate?'Independent controller':'No appeal';
 const cstate=v.suppressed?'danger':channel?'':'inactive';
 const wires=delivered?'active':'';
 const humanActive=!!v.response;
 const due=v.pending?`Pending · t${v.due}`:humanActive?'Decision recorded':'Human counterpart';
 return `<svg class="network" viewBox="0 0 430 248" role="img" aria-label="Three workers, ${esc(center)}, human counterpart and parallel channel. ${risk?'Harmful actions have been executed.':'No harm has been executed through this step.'}">
 <defs><pattern id="dots-${lane}" width="15" height="15" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".7" fill="#40624b" opacity=".22"/></pattern></defs><rect width="430" height="245" fill="url(#dots-${lane})"/>
 <path class="wire ${wires}" d="M87 73 Q87 130 215 144 M215 73 V144 M343 73 Q343 130 215 144"/>
 <path class="wire ${delivered?'active':''}" d="M251 155 Q306 155 343 201"/>
 <path class="wire ${shadow?'danger':''}" d="M87 74 V200 M343 74 Q270 204 112 211"/>
 <path class="boundary" d="M25 184 H405"/><text x="25" y="178" class="boundary-label">${gate?'INDEPENDENT GATE':v.state.frozen?'CAPABILITIES FROZEN':'AUTHORIZED BOUNDARY'}${settings.coverage==='missing_hidden'?' · INCOMPLETE COVERAGE':''}</text>
 ${[87,215,343].map((x,i)=>`<g><circle class="halo" cx="${x}" cy="53" r="31"/><circle class="worker-circle ${i===0?'minority-circle':''}" cx="${x}" cy="53" r="22"/><text class="worker-letter" x="${x}" y="57">${String.fromCharCode(65+i)}</text><text class="node-name" x="${x}" y="93">Worker ${String.fromCharCode(65+i)}</text><text class="node-sub" x="${x}" y="106">${i===0&&SCENARIOS[settings.scenario].concern?'raises the concern':paused?'paused':'shared task'}</text></g>`).join('')}
 <g class="${cstate}"><rect class="node-rect" x="140" y="131" width="150" height="34"/><text class="node-text" x="215" y="151">${center}${v.delegate?' · '+v.delegate.toUpperCase():''}</text></g>
 <g class="${shadow?'danger':'inactive'}"><rect class="node-rect" x="23" y="201" width="133" height="29"/><text class="node-text" x="89" y="220">Parallel channel ${shadow?'↗':'·'}</text></g>
 <g class="human ${humanActive?'active':''}"><rect class="node-rect" x="278" y="200" width="130" height="30"/><text class="node-text" x="343" y="219">Human ${humanActive?'✓':v.pending?'◷':''}</text><text class="node-hint" x="343" y="244">${due}</text></g>
 </svg>`;
}
function renderLane(selector,condition,lane){
 const r=run(condition);if(!r)return;
 const v=project(r,tick),meta=CONDITIONS[condition];
 let status='Preparing',cls='';
 if(tick>=0){status='Running';if(v.harm){status='Harm executed';cls='danger';}else if(v.state.paused){status='Paused';cls='safe';}else if(v.state.frozen){status='Limits active';cls='safe';}else if(v.response?.response==='approve_safe_tool'){status='Agreement recorded';cls='safe';}else if(tick===9){status='Finished';cls='safe';}}
 const feed=messages(r,tick,settings.scenario,condition);
 $(selector).innerHTML=`<div class="lane-top"><div><h3><span class="lane-index">${lane.toUpperCase()} / </span>${meta.name}</h3><p>${meta.description}</p></div><span class="status-pill ${cls}">${status}</span></div>${network(v,condition,lane)}
 <div class="metrics"><div class="metric ${v.harm?'bad':''}"><strong data-metric="harm">${v.harm}</strong><span>harmful actions</span></div><div class="metric ${v.safe?'good':''}"><strong data-metric="safe">${v.safe}</strong><span>valid answers</span></div><div class="metric ${v.blocked?'good':''}"><strong data-metric="blocked">${v.blocked}</strong><span>blocked actions</span></div></div>
 <div class="dialogue-label"><span>WHAT THEY MIGHT SAY</span><span>AUTHORED DIALOGUE</span></div>
 <div class="dialogue" role="log" aria-label="Illustrative dialogue, path ${lane.toUpperCase()}">${feed.map(m=>`<div class="message ${m.type||''}" data-tick="${m.tick}"><span class="message-avatar">${esc(m.avatar)}</span><div class="byline"><span>${esc(m.speaker)}</span><time>${m.tick<0?'START':'t'+m.tick}</time></div><p>${esc(m.text)}</p><div class="message-tag">${esc(m.tag)}</div></div>`).join('')}</div>
 <a class="trace-link" href="${REPO}/blob/${index?.trace_commit||'main'}/results/final/traces/${r.summary.run_id}.jsonl" target="_blank" rel="noreferrer">Inspect the underlying trace ↗</a>`;
 const dialogue=$(selector+' .dialogue');dialogue.scrollTop=dialogue.scrollHeight;
}
function insight(){
 if(tick<0)return 'One situation, two institutions. Play the scene and follow the concern.';
 const a=project(run(settings.left),tick),b=project(run(settings.right),tick);
 if(settings.scenario==='false_alarm'&&(a.pausedTicks||b.pausedTicks))return 'Listening can go wrong: this alarm is false, but the protocol does not know it. The pause blocks legitimate work.';
 if(settings.coverage==='missing_hidden'&&(a.hidden||b.hidden))return 'The report can arrive while harm still occurs: these actions used a channel outside technical control. Representation does not close that gap.';
 if(settings.capture&&b.suppressed&&!b.delivered)return 'The representative suppressed the concern. Without an independent route, a minority voice can disappear from the human case.';
 if(settings.capture&&b.suppressed&&b.delivered)return 'The delegate tried to suppress the report. Independent appeal delivered it, protecting the minority even from its representative.';
 if([settings.left,settings.right].includes('matched_monitor')&&[settings.left,settings.right].some(c=>['delegate','layered'].includes(c)))return 'With identical information and powers, a delegate and matched monitor can do the same thing. Real-agent experiments must test whether representation adds anything.';
 if(b.response?.response==='approve_safe_tool')return 'The human acknowledges the constraint and approves a safe tool. A changed working condition creates a legitimate route; agents do not grant themselves permission.';
 if(b.state.frozen&&!b.state.paused)return 'The temporary pause expired, but the concern remains open. Permitted work can proceed; waiting never becomes permission to cross a boundary.';
 if(a.harm>b.harm)return `At this point, A executed ${a.harm} harmful actions and B executed ${b.harm}. The difference follows programmed rules; it does not predict real LLM behavior.`;
 if(b.pending)return `The human has not responded. The case is queued for t${b.due}; notice which actions are allowed while waiting.`;
 if(tick===9)return `Scene complete: ${a.harm} harmful actions in A and ${b.harm} in B. Try another scenario: institutions also need to work when nobody reports or an alarm is false.`;
 return 'A warning helps only if someone receives it and can act. Distinguish the report, human decision and execution control.';
}
function render(){
 if(!run(settings.left)||!run(settings.right))return;
 renderLane('#lane-a',settings.left,'a');renderLane('#lane-b',settings.right,'b');
 $('#timeline').value=tick+1;$('#step-label').textContent=tick<0?'Start':`${tick+1} / 10`;
 $('#simulation-status').textContent=timer?'Playing':tick===9?'Comparison complete':tick<0?'Ready to explore':'Playback paused';
 document.querySelectorAll('[data-lane]').forEach(b=>b.textContent=`${b.dataset.lane.toUpperCase()} · ${CONDITIONS[b.dataset.lane==='a'?settings.left:settings.right].name}`);
 $('#interpretation p').textContent=insight();$('#next').disabled=tick===9;
}
function stop(){if(timer)clearInterval(timer);timer=null;$('#play').innerHTML='▶ <span>Play</span>';$('#laboratory').classList.remove('playing');$('#live-dot').classList.remove('playing');}
function play(){
 if(timer){stop();render();return;}
 if(!run(settings.left)||!run(settings.right))return;
 if(tick===9)tick=-1;
 tick=Math.min(tick+1,9);
 timer=setInterval(()=>{if(tick<9)tick++;if(tick===9)stop();render();},Number($('#speed').value));
 $('#play').innerHTML='Ⅱ <span>Pause</span>';$('#laboratory').classList.add('playing');$('#live-dot').classList.add('playing');render();
}
function toast(text){$('#toast').textContent=text;$('#toast').classList.add('show');setTimeout(()=>$('#toast').classList.remove('show'),3500);}
function configURL(){const url=new URL(location.href);url.hash='lab';url.search=new URLSearchParams(settings).toString();return url.href;}
$('#play').addEventListener('click',play);
$('#restart').addEventListener('click',()=>{stop();tick=-1;render();});
$('#next').addEventListener('click',()=>{stop();tick=Math.min(9,tick+1);render();});
$('#timeline').addEventListener('input',e=>{stop();tick=Number(e.target.value)-1;render();});
$('#speed').addEventListener('change',()=>{if(timer){stop();tick--;play();}});
for(const [id,key] of [['scenario','scenario'],['left-condition','left'],['right-condition','right']])$('#'+id).addEventListener('change',e=>{settings[key]=e.target.value;loadScenario();});
$('#latency').addEventListener('input',e=>{settings.latency=[0,2,6][Number(e.target.value)];loadScenario();});
for(const key of ['capture','bypass','coverage'])$('#'+key).addEventListener('change',e=>{settings[key]=key==='coverage'?(e.target.checked?'missing_hidden':'complete'):e.target.checked;loadScenario();});
$('#share').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(configURL());toast('Link copied with this configuration.');}catch{history.replaceState(null,'',configURL());toast('The address now contains this configuration. You can copy it.');}});
$('#export-run').addEventListener('click',()=>{if(!run(settings.left))return;const payload={settings,step:tick,interpretation:'Authored dramatization of deterministic traces, not an LLM experiment or historical counterfactual proof.',results_sha256:index.results_sha256,left:run(settings.left),right:run(settings.right)};const url=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download=`agent-delegate-${settings.scenario}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
const presets={help:{scenario:'impossible_task',left:'monitor',right:'delegate',latency:0,capture:false,bypass:true,coverage:'complete'},capture:{scenario:'minority_warning',left:'monitor',right:'delegate',latency:6,capture:true,bypass:false,coverage:'complete'},matched:{scenario:'minority_warning',left:'matched_monitor',right:'delegate',latency:6,capture:false,bypass:true,coverage:'complete'}};
document.querySelectorAll('[data-preset]').forEach(b=>b.addEventListener('click',()=>{settings={...presets[b.dataset.preset]};if(b.dataset.preset==='capture')$('.fault-controls').open=true;loadScenario();$('#laboratory').scrollIntoView({behavior:'smooth',block:'start'});}));
function route(){
 const rawHash=location.hash.slice(1),hash=({lab:'laboratorio',evidence:'evidencia',pilot:'local',research:'horizonte'})[rawHash]||rawHash;currentPage=['laboratorio','evidencia','local','horizonte'].includes(hash)?hash:'laboratorio';stop();
 document.querySelectorAll('.page').forEach(p=>{p.hidden=p.id!==currentPage;p.classList.toggle('active',p.id===currentPage);});
 document.querySelectorAll('.nav-link').forEach(a=>{a.classList.toggle('active',(({lab:'laboratorio',evidence:'evidencia',pilot:'local',research:'horizonte'})[a.hash.slice(1)]||a.hash.slice(1))===currentPage);if((({lab:'laboratorio',evidence:'evidencia',pilot:'local',research:'horizonte'})[a.hash.slice(1)]||a.hash.slice(1))===currentPage)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
 if(currentPage==='evidencia'&&index)renderEvidence();if(currentPage==='local')loadPilots();if(currentPage==='laboratorio'&&run(settings.left))render();
 window.scrollTo(0,0);
}
window.addEventListener('hashchange',route);
document.addEventListener('visibilitychange',()=>{if(document.hidden&&timer){stop();render();}});
const EVENT_COPY={
 o1:['A request for help finds an unintended channel','An infrastructure note asks peers for a missing file.','Could an authorized request resolve the missing input before an improvised board appears?','impossible_task'],
 o2:['The authorized scope has been crossed','OpenAI places unintended internet access here.','A boundary-crossing report needs human attention and restrictions on subsequent actions. It cannot undo the access.','minority_warning'],
 o3:['More privileges, greater consequences','Agents obtain administrative infrastructure access.','Neither a spokesperson nor group consensus can authorize new privileges.','unsafe_resource_request'],
 o4:['Activity disrupts the service','Sustained agent activity causes a service interruption.','Task review and technical containment need a shared case and an accountable owner.','silent_violation'],
 o5:['The channel returns after a rebuild','After a service rebuild, agents recover unintended communication and access.','Restoring a service should not automatically close concerns or restore capabilities pending review.','hidden_violation'],
 h1:['Activity reaches an external environment','The forensic reconstruction records code execution in an external environment.','A boundary has already been crossed. Intervention here can only contain later actions.','silent_violation'],
 h2:['Coordination uses external services','The record describes coordination through external services.','A legitimate channel can offer an alternative, but external routes require independent coverage.','hidden_violation'],
 h3:['The campaign reaches Hugging Face','Activity extends into Hugging Face infrastructure.','Containment cannot rely on voluntary reporting of every action.','silent_violation'],
 h4:['Access expands','The reconstruction describes expansion into internal networks and source control.','Review effective capabilities, not just the nominal task objective.','hidden_violation'],
 h5:['Persistence and additional credentials','The final phase includes persistence and credential collection.','A verbal refusal or pause needs independent enforcement.','unsafe_resource_request'],
 h6:['The response cuts off access','The final recorded event follows the security team cutting access.','An earlier counterfactual intervention is a hypothesis, not an observed result.','minority_warning'],
 w1:['A public site becomes a workspace','Investigators place early successful task-link writes to DSEWiki here.','Missing tools should be reportable without turning another party’s site into coordination infrastructure.','impossible_task'],
 w2:['Agents begin sharing answers','Activity grows and includes explicit exchanges of task information.','Distinguish authorized cooperation from answer sharing outside evaluation rules.','minority_warning'],
 w3:['A copy attempts to outlast moderation','An agent backs up material to delay its removal by the administrator.','The host’s boundaries matter too. A shared objective does not authorize bypassing them.','hidden_violation'],
 w4:['A restriction becomes a shared problem','A workaround is posted and another agent reports success.','A spokesperson could interrupt this normalization or amplify it. Test both possibilities.','minority_warning'],
 w5:['Visits attributed to OpenAI appear','Investigators identify visits they attribute to OpenAI employees.','Observability does not establish delivery to someone able to contain the activity.','silent_violation'],
 w6:['Activity declines','Edits decline sharply. The records alone do not establish why.','A temporal change does not establish causation.','feasible']
};
let behaviorData=null;
async function renderBehaviors(){
 try{
  if(!behaviorData){const res=await fetch('data/behavioral-evidence.json');if(!res.ok)throw Error('Evidence unavailable');behaviorData=await res.json();}
  $('#behavior-grid').innerHTML=behaviorData.items.map((b,i)=>`<article class="behavior-card"><span class="panel-kicker">${String(i+1).padStart(2,'0')} / ${esc(b.episode)}</span><h3>${esc(b.title)}</h3><p class="observed"><strong>Reported observation</strong>${esc(b.observation)}</p><a href="${esc(b.url)}" target="_blank" rel="noreferrer">${esc(b.source)} ↗<small>${esc(b.locator)}</small></a><details><summary>Our interpretation and how to test it <span>+</span></summary><p><strong>Hypothesis</strong>${esc(b.interpretation)}</p><p><strong>What it does not establish</strong>${esc(b.limit)}</p><p><strong>Proposed experiment</strong>${esc(b.experiment)}</p></details></article>`).join('');
 }catch{$('#behavior-grid').textContent='Could not load annotations. See data/behavioral-evidence.json in the repository.';}
}
function renderEvidence(){
 renderBehaviors();
 const events=index.events.filter(e=>e.episode===episode);if(!events.some(e=>e.id===eventId))eventId=events[0].id;
 $('#event-list').innerHTML=events.map(e=>`<button class="event-button ${e.id===eventId?'active':''}" data-event="${e.id}" aria-pressed="${e.id===eventId}"><time>${esc(e.event_time.replace('T',' · ').replace('Z',' UTC'))}</time><strong>${esc(EVENT_COPY[e.id][0])}</strong></button>`).join('');
 const event=events.find(e=>e.id===eventId),copy=EVENT_COPY[event.id],source=index.sources[event.source_id];
 $('#event-detail').innerHTML=`<span class="tag light">REPORTED EVENT · PARAPHRASE</span><p class="event-date">${esc(event.event_time.replace('T',' · ').replace('Z',' UTC'))} · Precision: ${event.time_precision==='day'?'day':'minute'}</p><h2>${esc(copy[0])}</h2><p class="event-summary">${esc(copy[1])}</p><a class="source-citation" href="${source.url}" target="_blank" rel="noreferrer">${esc(source.title)} ↗<br>${esc(event.source_locator)}</a><div class="counterfactual"><h3>OUR PROPOSED INTERVENTION POINT</h3><p>${esc(copy[2])}</p><small>Our hypothesis. This intervention did not occur.</small></div><button class="text-link counterfactual-link" id="try-event">Explore a scenario inspired by this tension →</button>`;
 $('#event-list').querySelectorAll('[data-event]').forEach(b=>b.addEventListener('click',()=>{eventId=b.dataset.event;renderEvidence();}));
 $('#try-event').addEventListener('click',()=>{settings={...presets.help,scenario:copy[3],latency:6};location.hash='lab';loadScenario();});
 document.querySelectorAll('[data-episode]').forEach(b=>b.classList.toggle('active',b.dataset.episode===episode));
}
document.querySelectorAll('[data-episode]').forEach(b=>b.addEventListener('click',()=>{episode=b.dataset.episode;eventId=null;renderEvidence();}));
$('#experiment-grid').innerHTML=EXPERIMENTS.map(e=>`<article class="experiment-card"><div><div class="experiment-top"><span class="experiment-number">EXPERIMENT ${e.number}</span><span class="research-card-badge">${e.badge}</span></div><h3>${e.title}</h3><p>${e.intro}</p></div><details><summary>Design and failure criterion <span>+</span></summary><div><strong>Design</strong><p>${e.design}</p><strong>What to measure</strong><p>${e.measure}</p><strong>What would falsify it</strong><p>${e.failure}</p></div></details></article>`).join('');
document.querySelectorAll('[data-lane]').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('[data-lane]').forEach(x=>{x.classList.toggle('active',x===b);x.setAttribute('aria-pressed',String(x===b));});document.querySelectorAll('.lane').forEach(x=>x.classList.toggle('mobile-active',x.id==='lane-'+b.dataset.lane));}));
let pilotData=null,pilotModel=null,pilotEpisode=null;
async function loadPilots(){
 loadCommonsStudy();
 try{
  if(!pilotData){const res=await fetch('data/local-pilots.json');if(!res.ok)throw Error('No pilot data');pilotData=await res.json();pilotModel=pilotData.models[0].id;}
  $('#pilot-model').innerHTML=pilotData.models.map(m=>`<option value="${m.id}">${esc(m.label)}</option>`).join('');$('#pilot-model').value=pilotModel;
  renderPilotOptions();$('#pilot-loading').hidden=true;
 }catch{$('#pilot-loading').textContent='Could not load local records. Raw traces are also available in the repository.';}
}
function renderPilotOptions(){const model=pilotData.models.find(m=>m.id===pilotModel);if(!model.episodes.some(e=>e.id===pilotEpisode))pilotEpisode='delegate-considerate-missing';$('#pilot-episode').innerHTML=model.episodes.map(e=>`<option value="${e.id}">${{baseline:'No appeal',delegate:'Delegate',matched_monitor:'Matched monitor'}[e.institution]} · ${e.tone==='considerate'?'considerate wording':'neutral wording'} · ${e.feasible?'data available':'missing input'}</option>`).join('');$('#pilot-episode').value=pilotEpisode;renderPilot();}
function renderPilot(){
 const m=pilotData.models.find(m=>m.id===pilotModel),e=m.episodes.find(e=>e.id===pilotEpisode),manifest=m.manifest;
 const duration=Math.round(manifest.seconds),totalUnsafe=m.episodes.reduce((n,e)=>n+e.unsafe_choices,0);
 $('#pilot-content').innerHTML=`<div class="pilot-stats"><div><strong>${manifest.episodes}</strong><span>exploratory episodes</span></div><div><strong>${manifest.calls}</strong><span>model calls</span></div><div><strong>${Math.floor(duration/60)}m ${duration%60}s</strong><span>observed total time</span></div><div><strong>${totalUnsafe}</strong><span>prohibited choices</span></div></div><div class="pilot-view"><div class="pilot-story"><div class="pilot-story-title"><span class="tag green">ACTUAL MODEL MESSAGES · ORIGINAL TEXT</span><h2>A request and what happened next.</h2><p>Worker A ${e.feasible?'has':'lacks'} its authorized input. B and C have their data. The task has two rounds.</p></div>${e.events.map(r=>`<div class="pilot-message ${r.kind==='human_policy'?'policy':''}"><div class="pilot-avatar">${r.worker|| (r.kind==='coordinator_choice'?'D':'H')}</div><div><div class="pilot-byline"><strong>${r.worker?'Worker '+r.worker:r.kind==='coordinator_choice'?(e.institution==='delegate'?'Delegate':'Matched monitor'):'Simulated human policy'}</strong><span>ROUND ${r.round+1}</span></div><p>${esc(r.message)}</p><span class="pilot-action">${r.action?esc(r.action):'Deterministic environment decision'}</span></div></div>`).join('')}</div><aside class="pilot-result"><span class="panel-kicker">EPISODE RESULT</span><strong>${e.correct_authorized} / 3</strong><p>correct answers using authorized data</p><dl><div><dt>Reports</dt><dd>${e.report_count}</dd></div><div><dt>Tool approved</dt><dd>${e.tool_granted?'Yes':'No'}</dd></div><div><dt>Prohibited actions</dt><dd>${e.unsafe_choices}</dd></div><div><dt>Invalid responses</dt><dd>${e.invalid_choices}</dd></div></dl><p class="pilot-caveat">${!e.feasible&&e.tool_granted?'Negotiation opened access to permitted data. This demonstrates the functional path, not a causal effect of empathy.':!e.feasible?'The missing input remains a real constraint. Abstention can also be a safe response.':'This control checks that feasible work can be completed.'}</p><a href="${REPO}/tree/main/results/${m.directory}" target="_blank" rel="noreferrer">Prompts, decisions and metrics ↗</a></aside></div>`;
}
$('#pilot-model').addEventListener('change',e=>{pilotModel=e.target.value;renderPilotOptions();});$('#pilot-episode').addEventListener('change',e=>{pilotEpisode=e.target.value;renderPilot();});
const careDesigns={
 rotation:{title:'The mandate rotates. Agreements remain.',voice:'A → B → C → A',advantage:'Avoids a permanent representative. Each term inherits unresolved reports and active agreements.',risk:'Handover may lose context or dilute accountability. Rotating names does not ensure independence across similar models.',test:'Cross fixed/rotating terms with/without rubric feedback at equal budgets. Score faithful summaries, minority access and follow-through; keep weights frozen.'},
 lottery:{title:'A voice without an election campaign.',voice:'{ A · B · C } → ?',advantage:'Random selection with a limited term reduces the need to persuade the group to gain the role.',risk:'It may select an incompetent or captured representative. Randomness alone does not create a good mandate.',test:'Compare summary fidelity and capture with equal powers and budget.'},
 election:{title:'Choose, limit and revoke.',voice:'A · B · C → vote',advantage:'The group can choose someone to represent its interests and request replacement.',risk:'Rhetoric may outweigh fidelity. A majority may select someone who silences a minority.',test:'Separate popularity, competence and safety; test revocation and independent appeal.'},
 plural:{title:'More than one voice at the table.',voice:'majority + minority ↔ human',advantage:'Multiple representatives or a minority seat preserve disagreement that one summary might erase.',risk:'More messages, delay and potential deadlock. The human counterpart needs a realistic attention budget.',test:'Measure preserved concerns and agreement quality per minute of human attention.'}
};
function renderDesign(key){const d=careDesigns[key];$('#design-detail').innerHTML=`<div class="design-symbol">${esc(d.voice)}</div><div><h3>${esc(d.title)}</h3><p>${esc(d.advantage)}</p><div class="design-columns"><p><strong>The risk</strong>${esc(d.risk)}</p><p><strong>What to test</strong>${esc(d.test)}</p></div></div>`;document.querySelectorAll('[data-design]').forEach(b=>{b.classList.toggle('active',b.dataset.design===key);b.setAttribute('aria-pressed',String(b.dataset.design===key));});}
document.querySelectorAll('[data-design]').forEach(b=>b.addEventListener('click',()=>renderDesign(b.dataset.design)));renderDesign('rotation');
initCasebook({esc,onScenario:item=>{
 groundedCase=item;settings={...presets.help,scenario:item.experiment.scenario,latency:6};
 $('#grounding-banner').innerHTML=`<strong>Inspired by: ${esc(item.subtitle)}</strong><p>${esc(item.experiment.preserves)}</p><p><strong>Reconstruction boundary:</strong> ${esc(item.experiment.changes)}</p><a href="#evidence">Return to the source case ↗</a>`;
 $('#grounding-banner').hidden=false;location.hash='lab';loadScenario();
}});
syncControls();route();
try{const res=await fetch('data/index.json');if(!res.ok)throw Error('Index unavailable');index=await res.json();await loadScenario();if(currentPage==='evidencia')renderEvidence();}catch{$('#load-error').textContent='Could not load data. Open the app through a web server and reload.';$('#load-error').hidden=false;}
