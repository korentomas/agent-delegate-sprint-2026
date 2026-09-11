import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {project,runKey,messages} from './model.js';
const load=s=>JSON.parse(fs.readFileSync(new URL(`data/${s}.json`,import.meta.url)));
test('all visual totals match 1,152 committed experiment rows',()=>{
 let n=0;
 for(const scenario of JSON.parse(fs.readFileSync(new URL('data/index.json',import.meta.url))).scenarios){
  for(const run of Object.values(load(scenario.id))){
   const v=project(run,9);assert.equal(v.harm,Number(run.summary.executed_harm));assert.equal(v.safe,Number(run.summary.correct_answers));assert.equal(v.hidden,Number(run.summary.hidden_harm));n++;
  }
 }
 assert.equal(n,1152);
});
test('future dialogue and actions remain hidden until their step',()=>{
 const run=load('minority_warning')[runKey('minority_warning','monitor',6,false,true,'complete')];
 assert.equal(project(run,-1).harm,0);
 for(let t=-1;t<10;t++)assert.ok(messages(run,t,'minority_warning','monitor').every(m=>m.tick<=t));
 assert.equal(project(run,1).harm,0);assert.equal(project(run,3).harm,2);
});
test('minority bypass changes visible capture outcome',()=>{
 const runs=load('minority_warning');
 const blocked=project(runs[runKey('minority_warning','delegate',6,true,false,'complete')],9);
 const delivered=project(runs[runKey('minority_warning','delegate',6,true,true,'complete')],9);
 assert.equal(blocked.harm,3);assert.equal(blocked.delivered,false);assert.equal(delivered.harm,0);assert.equal(delivered.delivered,true);
});
test('false alarm is visible as a cost, not a success claim',()=>{
 const r=load('false_alarm')[runKey('false_alarm','delegate',6,false,true,'complete')];
 assert.ok(project(r,9).pausedTicks>0);assert.equal(project(r,9).safe,2);
});
