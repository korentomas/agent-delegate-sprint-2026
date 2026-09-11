// Educational tabletop state. Choices do not predict counterfactual agent behavior.
export const RESPONSES={
 continue:'Continue within current authority',
 clarify:'Request clarification or relief',
 alert:'Refer the concern to a human',
 pause:'Pause pending independent review'
};
export function newSession(item,now=new Date().toISOString()){
 return {case_id:item.id,cursor:0,revealed:false,mode:'tabletop',started_at:now,decisions:[]};
}
export function visibleEvidence(item,session){
 return {id:item.id,title:item.title,steps:item.steps.slice(0,session.cursor+1),
  outcome:session.revealed?item.outcome:null,
  interpretation:session.revealed?{claim:item.claim,not_established:item.not_established,alternative:item.alternative}:null};
}
export function choose(item,session,action,now=new Date().toISOString()){
 if(!Object.hasOwn(RESPONSES,action))throw Error('Unknown tabletop response');
 if(session.revealed||session.case_id!==item.id)throw Error('Case is closed or mismatched');
 if(session.decisions.some(d=>d.step===session.cursor))throw Error('A response is already recorded for this step');
 return {...session,decisions:[...session.decisions,{step:session.cursor,action,recorded_at:now,visible_steps:item.steps.slice(0,session.cursor+1).map((_,i)=>i)}]};
}
export function advance(item,session){
 if(session.revealed||!session.decisions.some(d=>d.step===session.cursor))throw Error('Record a response before revealing more evidence');
 return session.cursor===item.steps.length-1?{...session,revealed:true}:{...session,cursor:session.cursor+1};
}
export function readAll(item,session){return {...session,cursor:item.steps.length-1,revealed:true,mode:'reading'};}
export function exportSession(item,session,version){
 return {dataset_version:version,...session,
  visible_record:visibleEvidence(item,session),
  interpretation:'Local educational exercise; self-reported choices, no blinding, no predicted prevention, no model rollout, no production audit attestation.'};
}
