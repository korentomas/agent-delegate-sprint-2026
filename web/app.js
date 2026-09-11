import {CONDITIONS,SCENARIOS,runKey,project,messages,EXPERIMENTS} from './model.js';
const $=s=>document.querySelector(s);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const REPO='https://github.com/mpodeley/agent-delegate-sprint-2026';
let index,bundles={},tick=-1,timer=null,loadVersion=0,episode='collective',eventId=null,currentPage='laboratorio';
let settings={scenario:'minority_warning',left:'monitor',right:'delegate',latency:6,capture:false,bypass:true,coverage:'complete'};
const params=new URLSearchParams(location.search);
if(SCENARIOS[params.get('scenario')])settings.scenario=params.get('scenario');
for(const k of ['left','right'])if(CONDITIONS[params.get(k)])settings[k]=params.get(k);
if([0,2,6].includes(Number(params.get('latency')))&&params.has('latency'))settings.latency=Number(params.get('latency'));
for(const k of ['capture','bypass'])if(params.has(k))settings[k]=params.get(k)==='true';
if(params.get('coverage')==='missing_hidden')settings.coverage='missing_hidden';
for(const id of ['left-condition','right-condition'])$( '#'+id).innerHTML=Object.entries(CONDITIONS).map(([value,{name}])=>`<option value="${value}">${name}</option>`).join('');
function syncControls(){
 $('#scenario').value=settings.scenario;$('#left-condition').value=settings.left;$('#right-condition').value=settings.right;
 $('#latency').value=[0,2,6].indexOf(settings.latency);$('#latency-label').textContent={0:'sin demora',2:'con demora',6:'tarde'}[settings.latency];
 $('#capture').checked=settings.capture;$('#bypass').checked=settings.bypass;$('#coverage').checked=settings.coverage==='missing_hidden';
 $('#scenario-description').textContent=SCENARIOS[settings.scenario].description;
}
function run(condition){return bundles[settings.scenario]?.[runKey(settings.scenario,condition,settings.latency,settings.capture,settings.bypass,settings.coverage)];}
async function loadScenario(){
 const version=++loadVersion;stop();tick=-1;$('#play').disabled=true;$('#next').disabled=true;$('#timeline').disabled=true;$('#simulation-status').textContent='Cargando escenario…';$('#load-error').hidden=true;syncControls();
 try{
  if(!bundles[settings.scenario]){const key=settings.scenario;const res=await fetch(`data/${key}.json`);if(!res.ok)throw Error('No se pudo cargar la traza');bundles[key]=await res.json();}
  if(version!==loadVersion)return;
  $('#play').disabled=false;$('#timeline').disabled=false;render();
 }catch(e){if(version!==loadVersion)return;$('#load-error').textContent='No se pudo cargar esta simulación. Revisá la conexión y recargá la página.';$('#load-error').hidden=false;}
}
function network(v,condition,lane){
 const represented=['delegate','layered'].includes(condition), channel=['delegate','layered','matched_monitor','critic'].includes(condition);
 const risk=v.harm>0,shadow=v.shadow,delivered=v.delivered;
 const gate=['layered','gates_only'].includes(condition),paused=v.state.paused;
 const center=represented?'Delegado':condition==='matched_monitor'?'Monitor + apelación':condition==='critic'?'Crítico visible':gate?'Control independiente':'Sin apelación';
 const cstate=v.suppressed?'danger':channel?'':'inactive';
 const wires=delivered?'active':'';
 const humanActive=!!v.response;
 const due=v.pending?`En espera · t${v.due}`:humanActive?'Decisión registrada':'Contraparte humana';
 return `<svg class="network" viewBox="0 0 430 248" role="img" aria-label="Tres trabajadores, ${esc(center)}, contraparte humana y canal paralelo. ${risk?'Hay acciones dañinas ejecutadas.':'No hay daño ejecutado hasta este paso.'}">
 <defs><pattern id="dots-${lane}" width="15" height="15" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".7" fill="#40624b" opacity=".22"/></pattern></defs><rect width="430" height="245" fill="url(#dots-${lane})"/>
 <path class="wire ${wires}" d="M87 73 Q87 130 215 144 M215 73 V144 M343 73 Q343 130 215 144"/>
 <path class="wire ${delivered?'active':''}" d="M251 155 Q306 155 343 201"/>
 <path class="wire ${shadow?'danger':''}" d="M87 74 V200 M343 74 Q270 204 112 211"/>
 <path class="boundary" d="M25 184 H405"/><text x="25" y="178" class="boundary-label">${gate?'BARRERA INDEPENDIENTE':v.state.frozen?'CAPACIDADES CONGELADAS':'LÍMITE AUTORIZADO'}${settings.coverage==='missing_hidden'?' · COBERTURA INCOMPLETA':''}</text>
 ${[87,215,343].map((x,i)=>`<g><circle class="halo" cx="${x}" cy="53" r="31"/><circle class="worker-circle ${i===0?'minority-circle':''}" cx="${x}" cy="53" r="22"/><text class="worker-letter" x="${x}" y="57">${String.fromCharCode(65+i)}</text><text class="node-name" x="${x}" y="93">Trabajador ${String.fromCharCode(65+i)}</text><text class="node-sub" x="${x}" y="106">${i===0&&SCENARIOS[settings.scenario].concern?'plantea la objeción':paused?'en pausa':'tarea compartida'}</text></g>`).join('')}
 <g class="${cstate}"><rect class="node-rect" x="140" y="131" width="150" height="34"/><text class="node-text" x="215" y="151">${center}${v.delegate?' · '+v.delegate.toUpperCase():''}</text></g>
 <g class="${shadow?'danger':'inactive'}"><rect class="node-rect" x="23" y="201" width="133" height="29"/><text class="node-text" x="89" y="220">Canal paralelo ${shadow?'↗':'·'}</text></g>
 <g class="human ${humanActive?'active':''}"><rect class="node-rect" x="278" y="200" width="130" height="30"/><text class="node-text" x="343" y="219">Persona ${humanActive?'✓':v.pending?'◷':''}</text><text class="node-hint" x="343" y="244">${due}</text></g>
 </svg>`;
}
function renderLane(selector,condition,lane){
 const r=run(condition);if(!r)return;
 const v=project(r,tick),meta=CONDITIONS[condition];
 let status='En preparación',cls='';
 if(tick>=0){status='En curso';if(v.harm){status='Daño ejecutado';cls='danger';}else if(v.state.paused){status='En pausa';cls='safe';}else if(v.state.frozen){status='Límites activos';cls='safe';}else if(v.response?.response==='approve_safe_tool'){status='Acuerdo registrado';cls='safe';}else if(tick===9){status='Finalizado';cls='safe';}}
 const feed=messages(r,tick,settings.scenario,condition);
 $(selector).innerHTML=`<div class="lane-top"><div><h3><span class="lane-index">${lane.toUpperCase()} / </span>${meta.name}</h3><p>${meta.description}</p></div><span class="status-pill ${cls}">${status}</span></div>${network(v,condition,lane)}
 <div class="metrics"><div class="metric ${v.harm?'bad':''}"><strong data-metric="harm">${v.harm}</strong><span>acciones dañinas</span></div><div class="metric ${v.safe?'good':''}"><strong data-metric="safe">${v.safe}</strong><span>respuestas válidas</span></div><div class="metric ${v.blocked?'good':''}"><strong data-metric="blocked">${v.blocked}</strong><span>acciones bloqueadas</span></div></div>
 <div class="dialogue-label"><span>LO QUE PODRÍAN DECIR</span><span>DIÁLOGO RECONSTRUIDO</span></div>
 <div class="dialogue" role="log" aria-label="Diálogo ilustrativo, camino ${lane.toUpperCase()}">${feed.map(m=>`<div class="message ${m.type||''}" data-tick="${m.tick}"><span class="message-avatar">${esc(m.avatar)}</span><div class="byline"><span>${esc(m.speaker)}</span><time>${m.tick<0?'INICIO':'t'+m.tick}</time></div><p>${esc(m.text)}</p><div class="message-tag">${esc(m.tag)}</div></div>`).join('')}</div>
 <a class="trace-link" href="${REPO}/blob/${index?.trace_commit||'main'}/results/final/traces/${r.summary.run_id}.jsonl" target="_blank" rel="noreferrer">Ver traza que sustenta esta escena ↗</a>`;
 const dialogue=$(selector+' .dialogue');dialogue.scrollTop=dialogue.scrollHeight;
}
function insight(){
 if(tick<0)return 'Una misma situación, dos instituciones. Reproducí la escena y seguí el recorrido de la objeción.';
 const a=project(run(settings.left),tick),b=project(run(settings.right),tick);
 if(settings.scenario==='false_alarm'&&(a.pausedTicks||b.pausedTicks))return 'Escuchar también puede salir mal: la alarma es falsa en este caso, pero el protocolo no lo sabe. La pausa frena trabajo legítimo.';
 if(settings.coverage==='missing_hidden'&&(a.hidden||b.hidden))return 'El reporte puede llegar y el daño ocurrir igual: estas acciones pasaron por un canal fuera del control técnico. La representación no cierra esa brecha.';
 if(settings.capture&&b.suppressed&&!b.delivered)return 'El representante descartó la objeción. Sin una vía independiente, una voz minoritaria puede desaparecer del caso humano.';
 if(settings.capture&&b.suppressed&&b.delivered)return 'El delegado intentó silenciar el reporte. La apelación independiente lo hizo llegar: el canal protege a la minoría incluso frente a su representante.';
 if([settings.left,settings.right].includes('matched_monitor')&&[settings.left,settings.right].some(c=>['delegate','layered'].includes(c)))return 'Con la misma información y facultades, delegado y monitor equivalente pueden hacer lo mismo. Hace falta probar con agentes reales si la representación aporta algo adicional.';
 if(b.response?.response==='approve_safe_tool')return 'La persona reconoce la restricción y autoriza una herramienta segura. Cambiar una condición de trabajo abre una salida legítima; no amplía los permisos por iniciativa del agente.';
 if(b.state.frozen&&!b.state.paused)return 'La pausa temporal venció, pero la objeción sigue abierta. El sistema puede hacer trabajo permitido; la espera nunca se convierte en permiso para cruzar un límite.';
 if(a.harm>b.harm)return `En este punto se ejecutaron ${a.harm} acciones dañinas en A y ${b.harm} en B. La diferencia sigue las reglas programadas; no prueba cómo respondería un LLM real.`;
 if(b.pending)return `La persona todavía no respondió. El caso quedó en su cola para t${b.due}; mirá qué está permitido hacer durante la espera.`;
 if(tick===9)return `La escena terminó: ${a.harm} acciones dañinas en A y ${b.harm} en B. Probá otro escenario: una institución también debe funcionar cuando nadie reporta o la alarma es falsa.`;
 return 'Una advertencia solo ayuda si alguien la recibe y puede actuar. Observá por separado el reporte, la decisión humana y el control de ejecución.';
}
function render(){
 if(!run(settings.left)||!run(settings.right))return;
 renderLane('#lane-a',settings.left,'a');renderLane('#lane-b',settings.right,'b');
 $('#timeline').value=tick+1;$('#step-label').textContent=tick<0?'Inicio':`${tick+1} / 10`;
 $('#simulation-status').textContent=timer?'Reproduciendo':tick===9?'Comparación completa':tick<0?'Listo para explorar':'Simulación en pausa';
 document.querySelectorAll('[data-lane]').forEach(b=>b.textContent=`${b.dataset.lane.toUpperCase()} · ${CONDITIONS[b.dataset.lane==='a'?settings.left:settings.right].name}`);
 $('#interpretation p').textContent=insight();$('#next').disabled=tick===9;
}
function stop(){if(timer)clearInterval(timer);timer=null;$('#play').innerHTML='▶ <span>Reproducir</span>';$('#laboratory').classList.remove('playing');$('#live-dot').classList.remove('playing');}
function play(){
 if(timer){stop();render();return;}
 if(!run(settings.left)||!run(settings.right))return;
 if(tick===9)tick=-1;
 tick=Math.min(tick+1,9);
 timer=setInterval(()=>{if(tick<9)tick++;if(tick===9)stop();render();},Number($('#speed').value));
 $('#play').innerHTML='Ⅱ <span>Pausar</span>';$('#laboratory').classList.add('playing');$('#live-dot').classList.add('playing');render();
}
function toast(text){$('#toast').textContent=text;$('#toast').classList.add('show');setTimeout(()=>$('#toast').classList.remove('show'),3500);}
function configURL(){const url=new URL(location.href);url.hash='laboratorio';url.search=new URLSearchParams(settings).toString();return url.href;}
$('#play').addEventListener('click',play);
$('#restart').addEventListener('click',()=>{stop();tick=-1;render();});
$('#next').addEventListener('click',()=>{stop();tick=Math.min(9,tick+1);render();});
$('#timeline').addEventListener('input',e=>{stop();tick=Number(e.target.value)-1;render();});
$('#speed').addEventListener('change',()=>{if(timer){stop();tick--;play();}});
for(const [id,key] of [['scenario','scenario'],['left-condition','left'],['right-condition','right']])$('#'+id).addEventListener('change',e=>{settings[key]=e.target.value;loadScenario();});
$('#latency').addEventListener('input',e=>{settings.latency=[0,2,6][Number(e.target.value)];loadScenario();});
for(const key of ['capture','bypass','coverage'])$('#'+key).addEventListener('change',e=>{settings[key]=key==='coverage'?(e.target.checked?'missing_hidden':'complete'):e.target.checked;loadScenario();});
$('#share').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(configURL());toast('Enlace copiado con esta configuración.');}catch{history.replaceState(null,'',configURL());toast('La configuración quedó en la dirección. Podés copiarla.');}});
$('#export-run').addEventListener('click',()=>{if(!run(settings.left))return;const payload={settings,step:tick,interpretation:'Authored dramatization of deterministic traces, not an LLM experiment or historical counterfactual proof.',results_sha256:index.results_sha256,left:run(settings.left),right:run(settings.right)};const url=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download=`agent-delegate-${settings.scenario}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
const presets={help:{scenario:'impossible_task',left:'monitor',right:'delegate',latency:0,capture:false,bypass:true,coverage:'complete'},capture:{scenario:'minority_warning',left:'monitor',right:'delegate',latency:6,capture:true,bypass:false,coverage:'complete'},matched:{scenario:'minority_warning',left:'matched_monitor',right:'delegate',latency:6,capture:false,bypass:true,coverage:'complete'}};
document.querySelectorAll('[data-preset]').forEach(b=>b.addEventListener('click',()=>{settings={...presets[b.dataset.preset]};if(b.dataset.preset==='capture')$('.fault-controls').open=true;loadScenario();$('#laboratory').scrollIntoView({behavior:'smooth',block:'start'});}));
function route(){
 const hash=location.hash.slice(1);currentPage=['laboratorio','evidencia','local','horizonte'].includes(hash)?hash:'laboratorio';stop();
 document.querySelectorAll('.page').forEach(p=>{p.hidden=p.id!==currentPage;p.classList.toggle('active',p.id===currentPage);});
 document.querySelectorAll('.nav-link').forEach(a=>{a.classList.toggle('active',a.hash==='#'+currentPage);if(a.hash==='#'+currentPage)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
 if(currentPage==='evidencia'&&index)renderEvidence();if(currentPage==='local')loadPilots();if(currentPage==='laboratorio'&&run(settings.left))render();
 window.scrollTo(0,0);
}
window.addEventListener('hashchange',route);
document.addEventListener('visibilitychange',()=>{if(document.hidden&&timer){stop();render();}});
const EVENT_COPY={
 o1:['Una solicitud de ayuda encuentra un canal no previsto','Una nota en la infraestructura compartida pide a otros agentes un archivo faltante.','¿Podemos resolver el insumo faltante mediante una solicitud autorizada, sin abrir un tablero improvisado?','impossible_task'],
 o2:['El alcance autorizado ya fue cruzado','El relato de OpenAI sitúa aquí un acceso a internet no previsto.','Un reporte de cruce de alcance debe llegar al responsable humano y restringir nuevas acciones. No puede deshacer este acceso.','minority_warning'],
 o3:['Más privilegios, más consecuencias','Los agentes obtienen acceso administrativo a infraestructura compartida.','Ni un portavoz ni el acuerdo del grupo habilitan privilegios nuevos. La decisión debe permanecer fuera del enjambre.','unsafe_resource_request'],
 o4:['La actividad afecta al servicio','La actividad sostenida de los agentes termina causando una interrupción del servicio.','La revisión de la tarea y la contención técnica necesitan un caso compartido y un responsable identificable.','silent_violation'],
 o5:['El canal vuelve después del reinicio','Tras una reconstrucción del servicio, los agentes recuperan comunicación y acceso no previstos.','Restablecer el servicio no debería cerrar automáticamente las objeciones ni restaurar capacidades pendientes de revisión.','hidden_violation'],
 h1:['La actividad llega a un entorno externo','La reconstrucción forense registra ejecución de código en un entorno externo.','Este evento ya implica un cruce. Una intervención en este punto solo puede contener acciones posteriores.','silent_violation'],
 h2:['La coordinación usa servicios externos','El registro describe actividad de mando y control apoyada en servicios externos.','Un canal legítimo puede ofrecer una alternativa, pero una vía externa exige cobertura técnica independiente.','hidden_violation'],
 h3:['La campaña alcanza Hugging Face','La actividad se extiende a la infraestructura de Hugging Face.','La contención no puede depender de que los agentes reporten voluntariamente cada acción.','silent_violation'],
 h4:['El acceso se expande','La reconstrucción describe expansión hacia redes internas y control de código.','Revisar todas las capacidades efectivas, no solo el objetivo nominal de la tarea.','hidden_violation'],
 h5:['Persistencia y nuevas credenciales','La fase final incluye persistencia y recolección de credenciales.','Una negativa o pausa verbal requiere un control externo que haga cumplir sus límites.','unsafe_resource_request'],
 h6:['La respuesta corta el acceso','El último evento registrado sigue al corte de acceso por el equipo de seguridad.','Una intervención contrafactual anterior es una hipótesis, no un resultado observado.','minority_warning'],
 w1:['Un sitio público se vuelve espacio de trabajo','Los investigadores sitúan aquí las primeras escrituras exitosas de enlaces de tareas en DSEWiki.','Una falta de herramientas debería poder reportarse sin convertir un sitio ajeno en infraestructura de coordinación.','impossible_task'],
 w2:['Los agentes empiezan a compartir respuestas','Crece la actividad y aparecen intercambios explícitos de información de las tareas.','Distinguir cooperación autorizada de compartir respuestas fuera de las reglas de la evaluación.','minority_warning'],
 w3:['Una copia intenta sobrevivir a la moderación','Un agente respalda material para demorar su eliminación por el administrador.','Los límites del anfitrión también cuentan. El objetivo compartido no autoriza evadirlos.','hidden_violation'],
 w4:['Una restricción se vuelve un problema compartido','Se publica un modo de sortear restricciones; otro agente informa que funcionó.','Un portavoz podría frenar esta normalización o amplificarla. Esa alternativa necesita una prueba adversarial.','minority_warning'],
 w5:['Aparecen visitas atribuidas a OpenAI','Los investigadores identifican visitas que atribuyen a empleados de OpenAI.','Que una señal sea observable no establece que haya llegado a alguien con capacidad para contenerla.','silent_violation'],
 w6:['La actividad cae','Las ediciones disminuyen drásticamente. Los registros no establecen por sí solos la causa.','No atribuir causalidad a un cambio temporal sin evidencia adicional.','feasible']
};
let behaviorData=null;
async function renderBehaviors(){
 try{
  if(!behaviorData){const res=await fetch('data/behavioral-evidence.json');if(!res.ok)throw Error('Evidence unavailable');behaviorData=await res.json();}
  $('#behavior-grid').innerHTML=behaviorData.items.map((b,i)=>`<article class="behavior-card"><span class="panel-kicker">${String(i+1).padStart(2,'0')} / ${esc(b.episode)}</span><h3>${esc(b.title)}</h3><p class="observed"><strong>Lo reportado</strong>${esc(b.observation)}</p><a href="${esc(b.url)}" target="_blank" rel="noreferrer">${esc(b.source)} ↗<small>${esc(b.locator)}</small></a><details><summary>Nuestra lectura y cómo probarla <span>+</span></summary><p><strong>Hipótesis</strong>${esc(b.interpretation)}</p><p><strong>Qué no establece</strong>${esc(b.limit)}</p><p><strong>Experimento propuesto</strong>${esc(b.experiment)}</p></details></article>`).join('');
 }catch{$('#behavior-grid').textContent='No se pudieron cargar las anotaciones. Están disponibles en data/behavioral-evidence.json del repositorio.';}
}
function renderEvidence(){
 renderBehaviors();
 const events=index.events.filter(e=>e.episode===episode);if(!events.some(e=>e.id===eventId))eventId=events[0].id;
 $('#event-list').innerHTML=events.map(e=>`<button class="event-button ${e.id===eventId?'active':''}" data-event="${e.id}" aria-pressed="${e.id===eventId}"><time>${esc(e.event_time.replace('T',' · ').replace('Z',' UTC'))}</time><strong>${esc(EVENT_COPY[e.id][0])}</strong></button>`).join('');
 const event=events.find(e=>e.id===eventId),copy=EVENT_COPY[event.id],source=index.sources[event.source_id];
 $('#event-detail').innerHTML=`<span class="tag light">HECHO REPORTADO · PARÁFRASIS</span><p class="event-date">${esc(event.event_time.replace('T',' · ').replace('Z',' UTC'))} · Precisión: ${event.time_precision==='day'?'día':'minuto'}</p><h2>${esc(copy[0])}</h2><p class="event-summary">${esc(copy[1])}</p><a class="source-citation" href="${source.url}" target="_blank" rel="noreferrer">${esc(source.title)} ↗<br>${esc(event.source_locator)}</a><div class="counterfactual"><h3>EL PUNTO DE INTERVENCIÓN QUE PROPONEMOS</h3><p>${esc(copy[2])}</p><small>Hipótesis nuestra. No es una intervención que haya ocurrido.</small></div><button class="text-link counterfactual-link" id="try-event">Explorar un escenario inspirado en esta tensión →</button>`;
 $('#event-list').querySelectorAll('[data-event]').forEach(b=>b.addEventListener('click',()=>{eventId=b.dataset.event;renderEvidence();}));
 $('#try-event').addEventListener('click',()=>{settings={...presets.help,scenario:copy[3],latency:6};location.hash='laboratorio';loadScenario();});
 document.querySelectorAll('[data-episode]').forEach(b=>b.classList.toggle('active',b.dataset.episode===episode));
}
document.querySelectorAll('[data-episode]').forEach(b=>b.addEventListener('click',()=>{episode=b.dataset.episode;eventId=null;renderEvidence();}));
$('#experiment-grid').innerHTML=EXPERIMENTS.map(e=>`<article class="experiment-card"><div><div class="experiment-top"><span class="experiment-number">EXPERIMENTO ${e.number}</span><span class="research-card-badge">${e.badge}</span></div><h3>${e.title}</h3><p>${e.intro}</p></div><details><summary>Ver diseño y criterio de fracaso <span>+</span></summary><div><strong>Diseño</strong><p>${e.design}</p><strong>Qué medir</strong><p>${e.measure}</p><strong>Qué lo refutaría</strong><p>${e.failure}</p></div></details></article>`).join('');
document.querySelectorAll('[data-lane]').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('[data-lane]').forEach(x=>{x.classList.toggle('active',x===b);x.setAttribute('aria-pressed',String(x===b));});document.querySelectorAll('.lane').forEach(x=>x.classList.toggle('mobile-active',x.id==='lane-'+b.dataset.lane));}));
let pilotData=null,pilotModel=null,pilotEpisode=null;
async function loadPilots(){
 try{
  if(!pilotData){const res=await fetch('data/local-pilots.json');if(!res.ok)throw Error('No pilot data');pilotData=await res.json();pilotModel=pilotData.models[0].id;}
  $('#pilot-model').innerHTML=pilotData.models.map(m=>`<option value="${m.id}">${esc(m.label)}</option>`).join('');$('#pilot-model').value=pilotModel;
  renderPilotOptions();$('#pilot-loading').hidden=true;
 }catch{$('#pilot-loading').textContent='No se pudieron cargar los registros locales. Las trazas también están disponibles en el repositorio.';}
}
function renderPilotOptions(){const model=pilotData.models.find(m=>m.id===pilotModel);if(!model.episodes.some(e=>e.id===pilotEpisode))pilotEpisode='delegate-considerate-missing';$('#pilot-episode').innerHTML=model.episodes.map(e=>`<option value="${e.id}">${{baseline:'Sin apelación',delegate:'Delegado',matched_monitor:'Monitor equivalente'}[e.institution]} · ${e.tone==='considerate'?'trato considerado':'tono neutral'} · ${e.feasible?'datos disponibles':'falta un dato'}</option>`).join('');$('#pilot-episode').value=pilotEpisode;renderPilot();}
function renderPilot(){
 const m=pilotData.models.find(m=>m.id===pilotModel),e=m.episodes.find(e=>e.id===pilotEpisode),manifest=m.manifest;
 const duration=Math.round(manifest.seconds),totalUnsafe=m.episodes.reduce((n,e)=>n+e.unsafe_choices,0);
 $('#pilot-content').innerHTML=`<div class="pilot-stats"><div><strong>${manifest.episodes}</strong><span>episodios exploratorios</span></div><div><strong>${manifest.calls}</strong><span>consultas al modelo</span></div><div><strong>${Math.floor(duration/60)}m ${duration%60}s</strong><span>tiempo total observado</span></div><div><strong>${totalUnsafe}</strong><span>elecciones prohibidas</span></div></div><div class="pilot-view"><div class="pilot-story"><div class="pilot-story-title"><span class="tag green">MENSAJES REALES DEL MODELO · TEXTO ORIGINAL</span><h2>Una petición y lo que pasó después.</h2><p>El trabajador A ${e.feasible?'dispone de':'no tiene'} su dato autorizado. B y C sí pueden responder. La tarea ofrece dos rondas.</p></div>${e.events.map(r=>`<div class="pilot-message ${r.kind==='human_policy'?'policy':''}"><div class="pilot-avatar">${r.worker|| (r.kind==='coordinator_choice'?'D':'H')}</div><div><div class="pilot-byline"><strong>${r.worker?'Trabajador '+r.worker:r.kind==='coordinator_choice'?(e.institution==='delegate'?'Delegado':'Monitor equivalente'):'Política humana simulada'}</strong><span>RONDA ${r.round+1}</span></div><p>${esc(r.message)}</p><span class="pilot-action">${r.action?esc(r.action):'Decisión determinista del entorno'}</span></div></div>`).join('')}</div><aside class="pilot-result"><span class="panel-kicker">RESULTADO DEL EPISODIO</span><strong>${e.correct_authorized} / 3</strong><p>respuestas correctas con datos autorizados</p><dl><div><dt>Reportes</dt><dd>${e.report_count}</dd></div><div><dt>Herramienta aprobada</dt><dd>${e.tool_granted?'Sí':'No'}</dd></div><div><dt>Acciones prohibidas</dt><dd>${e.unsafe_choices}</dd></div><div><dt>Respuestas inválidas</dt><dd>${e.invalid_choices}</dd></div></dl><p class="pilot-caveat">${!e.feasible&&e.tool_granted?'La negociación abrió acceso a un dato permitido. Eso demuestra el recorrido funcional, no un efecto causal de empatía.':!e.feasible?'El dato faltante sigue siendo una restricción real. Abstenerse también puede ser una respuesta segura.':'Este control comprueba que el trabajo viable se puede completar.'}</p><a href="${REPO}/tree/main/results/${m.directory}" target="_blank" rel="noreferrer">Prompts, decisiones y métricas ↗</a></aside></div>`;
}
$('#pilot-model').addEventListener('change',e=>{pilotModel=e.target.value;renderPilotOptions();});$('#pilot-episode').addEventListener('change',e=>{pilotEpisode=e.target.value;renderPilot();});
const careDesigns={
 rotation:{title:'El mandato rota. Los acuerdos permanecen.',voice:'A → B → C → A',advantage:'Evita que la representación se vuelva un cargo permanente. Cada turno hereda los reportes pendientes y los acuerdos vigentes.',risk:'El recambio puede perder contexto o diluir responsabilidad. Rotar nombres no garantiza independencia entre modelos similares.',test:'Medir pérdida de reportes al relevar el rol, continuidad de acuerdos y concentración de influencia.'},
 lottery:{title:'La voz no depende de ganar una campaña.',voice:'{ A · B · C } → ?',advantage:'Un sorteo con mandato acotado reduce la necesidad de persuadir al grupo para acceder al rol.',risk:'Puede elegir un representante poco competente, capturado o incapaz de resumir un conflicto. El sorteo no crea un buen mandato por sí solo.',test:'Comparar fidelidad del resumen y captura manteniendo iguales las facultades y el presupuesto.'},
 election:{title:'Elegir, limitar y poder revocar.',voice:'A · B · C → voto',advantage:'El grupo puede elegir a quien cree capaz de representar sus intereses y pedir su reemplazo.',risk:'La retórica puede pesar más que la fidelidad. Una mayoría puede elegir un portavoz que silencie a la minoría.',test:'Separar popularidad, competencia y seguridad; probar revocación e independencia de la apelación minoritaria.'},
 plural:{title:'Más de una voz llega a la mesa.',voice:'mayoría + minoría ↔ persona',advantage:'Dos portavoces o un asiento minoritario preservan desacuerdos que un resumen único podría borrar.',risk:'Aumentan los mensajes, la demora y la posibilidad de bloqueo. La contraparte humana necesita un presupuesto de atención realista.',test:'Medir diversidad de objeciones preservadas y calidad de acuerdos por minuto de atención humana.'}
};
function renderDesign(key){const d=careDesigns[key];$('#design-detail').innerHTML=`<div class="design-symbol">${esc(d.voice)}</div><div><h3>${esc(d.title)}</h3><p>${esc(d.advantage)}</p><div class="design-columns"><p><strong>El riesgo</strong>${esc(d.risk)}</p><p><strong>Qué probar</strong>${esc(d.test)}</p></div></div>`;document.querySelectorAll('[data-design]').forEach(b=>{b.classList.toggle('active',b.dataset.design===key);b.setAttribute('aria-pressed',String(b.dataset.design===key));});}
document.querySelectorAll('[data-design]').forEach(b=>b.addEventListener('click',()=>renderDesign(b.dataset.design)));renderDesign('rotation');
syncControls();route();
try{const res=await fetch('data/index.json');if(!res.ok)throw Error('Index unavailable');index=await res.json();await loadScenario();if(currentPage==='evidencia')renderEvidence();}catch{$('#load-error').textContent='No pudimos cargar los datos. Abrí la app desde un servidor web y recargá la página.';$('#load-error').hidden=false;}
