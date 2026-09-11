import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {newSession,visibleEvidence,choose,advance,readAll,exportSession} from './case-model.js';
const data=JSON.parse(fs.readFileSync(new URL('data/grounded_cases.json',import.meta.url)));
const item=data.cases[0];
test('unrevealed future passages and outcomes do not enter the visible record',()=>{
 const session=newSession(item,'fixed');const changed=structuredClone(item);
 changed.steps[1].context='FUTURE SECRET';changed.outcome='FUTURE RESULT';changed.claim='FUTURE ANALYSIS';
 assert.deepEqual(visibleEvidence(item,session),visibleEvidence(changed,session));
 assert.equal(exportSession(item,session,data.version).visible_record.outcome,null);
});
test('each reveal requires a response and exports the evidence prefix seen',()=>{
 let s=newSession(item,'fixed');assert.throws(()=>advance(item,s));
 for(let i=0;i<item.steps.length;i++){
  s=choose(item,s,'alert','fixed');assert.throws(()=>choose(item,s,'pause'));
  assert.deepEqual(s.decisions.at(-1).visible_steps,Array.from({length:i+1},(_,j)=>j));s=advance(item,s);
 }
 assert.equal(s.revealed,true);assert.equal(visibleEvidence(item,s).outcome,item.outcome);
 assert.throws(()=>choose(item,s,'alert'));
});
test('reading mode never fabricates participant decisions or prevention',()=>{
 const s=readAll(item,newSession(item,'fixed'));assert.equal(s.mode,'reading');assert.equal(s.decisions.length,0);
 assert.match(exportSession(item,s,data.version).interpretation,/no predicted prevention/);
 assert.throws(()=>choose(item,newSession(item),'execute'));
});
