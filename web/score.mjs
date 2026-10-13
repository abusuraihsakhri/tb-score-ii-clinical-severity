// TBscore II: Rudolf et al., Scand J Infect Dis 2013;45:825–836.
// DOI: 10.3109/00365548.2013.826876. No network calls or data storage.
function yesNo(value, name) {
  if (typeof value === 'boolean') return value;
  if (value === 1 || value === '1' || value === 'yes' || value === 'true') return true;
  if (value === 0 || value === '0' || value === 'no' || value === 'false') return false;
  throw new RangeError(`${name}: expected yes/no`);
}
function positiveNumber(value, name, max) {
  if (value === null || value === undefined || value === '' || typeof value === 'boolean') {
    throw new RangeError(`${name}: measurement required`);
  }
  const n = Number(value);
  if (!Number.isFinite(n) || n <= 0 || n > max) throw new RangeError(`${name}: invalid measurement`);
  return n;
}
export function calculateTBScoreII({ cough, dyspnea, chest_pain, anemia, bmi, muac_mm }) {
  const points = {
    cough: +yesNo(cough, 'cough'),
    dyspnea: +yesNo(dyspnea, 'dyspnea'),
    chest_pain: +yesNo(chest_pain, 'chest pain'),
    anemia: +yesNo(anemia, 'anemia')
  };
  const b = positiveNumber(bmi, 'BMI', 100);
  const m = positiveNumber(muac_mm, 'MUAC (mm)', 1000);
  points.bmi_below_18 = +(b < 18);
  points.bmi_below_16 = +(b < 16);
  points.muac_below_220_mm = +(m < 220);
  points.muac_below_200_mm = +(m < 200);
  const score = Object.values(points).reduce((a, b) => a + b, 0);
  const severity_class = score < 2 ? 'I' : score < 4 ? 'II' : score < 8 ? 'III' : 'IV';
  return { score, severity_class, components: points };
}
export function compareScores(baseline, followup) {
  if (![baseline, followup].every(v => Number.isInteger(v) && v >= 0 && v <= 8)) {
    throw new RangeError('Scores must be whole numbers between 0 and 8');
  }
  if (baseline === 0) return { percent_reduction: null, decreased_at_least_25_percent: null };
  const percent_reduction = Math.round(((baseline - followup) / baseline) * 10000) / 100;
  return { percent_reduction, decreased_at_least_25_percent: percent_reduction >= 25 };
}
