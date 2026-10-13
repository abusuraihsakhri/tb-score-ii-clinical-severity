import test from 'node:test';
import assert from 'node:assert/strict';
import { calculateTBScoreII, compareScores } from './score.mjs';

const base = { cough: 'no', dyspnea: 'no', chest_pain: 'no', anemia: 'no', bmi: 18, muac_mm: 220 };
const score = updates => calculateTBScoreII({ ...base, ...updates });

test('published BMI and MUAC strict boundaries', () => {
  for (const [bmi, points] of [[15.99,2],[16,1],[17.99,1],[18,0]]) {
    assert.equal(score({bmi}).score, points);
  }
  for (const [muac_mm, points] of [[199.99,2],[200,1],[219.99,1],[220,0]]) {
    assert.equal(score({muac_mm}).score, points);
  }
});
test('all severity bands and maximum 8', () => {
  for (const [updates, expectedScore, severity] of [
    [{},0,'I'], [{cough:'yes'},1,'I'],
    [{cough:'yes',dyspnea:'yes'},2,'II'],
    [{cough:'yes',dyspnea:'yes',anemia:'yes'},3,'II'],
    [{bmi:15,muac_mm:199},4,'III'],
    [{bmi:15,muac_mm:199,cough:'yes',dyspnea:'yes',chest_pain:'yes'},7,'III'],
    [{bmi:15,muac_mm:199,cough:'yes',dyspnea:'yes',chest_pain:'yes',anemia:'yes'},8,'IV']
  ]) {
    const result=score(updates);
    assert.equal(result.score, expectedScore);
    assert.equal(result.severity_class, severity);
    assert.equal(Object.values(result.components).reduce((a,b)=>a+b,0),expectedScore);
  }
});
test('invalid values never silently score zero', () => {
  for (const updates of [
    {cough:''}, {cough:'unknown'}, {bmi:''}, {bmi:'nan'},
    {bmi:'Infinity'}, {bmi:-1}, {muac_mm:null},
    {muac_mm:0}, {muac_mm:Infinity}
  ]) assert.throws(()=>score(updates),RangeError);
});
test('follow-up thresholds and zero baseline', () => {
  assert.deepEqual(compareScores(8,6),{percent_reduction:25,decreased_at_least_25_percent:true});
  assert.equal(compareScores(4,4).decreased_at_least_25_percent,false);
  assert.equal(compareScores(0,0).percent_reduction,null);
  assert.throws(()=>compareScores(9,0),RangeError);
});
