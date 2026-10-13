import { calculateTBScoreII, compareScores } from './score.mjs';

const form = document.querySelector('#score-form');
const output = document.querySelector('#result');
const reset = document.querySelector('#reset-result');

form.addEventListener('submit', (event) => {
  event.preventDefault();
  try {
    const data = Object.fromEntries(new FormData(form));
    const result = calculateTBScoreII(data);
    const followup = data.followup_score;
    let comparison = '';
    if (followup !== '') {
      const change = compareScores(Number(followup), result.score);
      comparison = change.percent_reduction === null
        ? 'Baseline score 0: percentage change is undefined.'
        : `From baseline ${followup}/8 to current ${result.score}/8: ${change.percent_reduction}% reduction. ${change.decreased_at_least_25_percent ? 'At least 25% reduction observed.' : 'Less than 25% reduction observed.'}`;
    }
    output.replaceChildren();
    const heading = document.createElement('h2');
    heading.textContent = `TBscore II: ${result.score}/8 — Severity class ${result.severity_class}`;
    output.append(heading);
    const description = document.createElement('p');
    description.textContent = 'Class I: 0–1 · Class II: 2–3 · Class III: 4–7 · Class IV: 8. A severity class is not an individual outcome probability or a treatment instruction.';
    output.append(description);
    const dl = document.createElement('dl');
    for (const [name, points] of Object.entries(result.components)) {
      const dt = document.createElement('dt');
      dt.textContent = name.replaceAll('_', ' ');
      const dd = document.createElement('dd');
      dd.textContent = `${points} point${points === 1 ? '' : 's'}`;
      dl.append(dt, dd);
    }
    output.append(dl);
    if (comparison) {
      const para = document.createElement('p');
      para.className = 'followup';
      para.textContent = comparison;
      output.append(para);
    }
    output.hidden = false;
  } catch (error) {
    output.replaceChildren();
    const message = document.createElement('p');
    message.className = 'error';
    message.textContent = error instanceof Error ? error.message : 'Invalid input';
    output.append(message);
    output.hidden = false;
  }
});

reset.addEventListener('click', () => {
  form.reset();
  output.replaceChildren();
  output.hidden = true;
  document.querySelector('#cough').focus();
});
