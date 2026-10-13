# TBscore II — Clinical Severity

A small, dependency-free clinical scoring implementation of **TBscore II**, the eight-point Bandim assessment for monitoring pulmonary tuberculosis during treatment. A browser calculator, Python CLI, batch CSV mode, and optional FastAPI endpoint are provided.

**Intended for research and education.** This score is not a diagnostic test, mortality probability estimator, drug resistance predictor, or substitute for clinical evaluation.

## Clinical definition

The four binary findings **cough**, **dyspnea**, **chest pain**, and **clinical anemia (e.g., pale conjunctivae)** each contribute one point. BMI < 18 kg/m² adds one point and BMI < 16 adds another. MUAC < 220 mm adds one point and MUAC < 200 mm adds another. Total: **0–8 points**.

| Severity class | Points |
|---|---:|
| I | 0–1 |
| II | 2–3 |
| III | 4–7 |
| IV | 8 |

Cutoffs are strictly less-than. Both anthropometric measurements are required. A baseline-to-follow-up decline of at least 25% was investigated in the original study, but is not an individual-level risk estimate. The validation results differed by study population.

**Reference:** Rudolf F, et al. *TBscore II: refining and validating a simple clinical score for treatment monitoring of patients with pulmonary tuberculosis*. Scand J Infect Dis. 2013;45(11):825–836. [doi:10.3109/00365548.2013.826876](https://doi.org/10.3109/00365548.2013.826876).

## Use

The static browser calculator is in `web/`. It requires no Python, backend, Pyodide or account. With a local HTTP server:

```bash
python -m http.server 8080 --directory web
```

Open `http://localhost:8080`. The browser uses JavaScript ES modules and performs calculations locally.

### Python CLI

Requires Python 3.10 or newer. The score itself requires only the standard library.

```bash
python tb_score_ii.py single --cough yes --dyspnea no --chest-pain yes --anemia no --bmi 17.5 --muac-mm 215
python tb_score_ii.py batch -i sample.csv -o results.csv
```

Batch CSV must contain exactly `cough,dyspnea,chest_pain,anemia,bmi,muac_mm`. The four sign fields accept `yes/no`, `true/false`, or `1/0`. Blank, invalid, or nonfinite measurements are rejected. On invalid rows, no partial output file is written. Never use identifying patient data in the sample file or browser calculator.

### Optional FastAPI server and legacy utilities

```bash
python -m pip install -r requirements.txt
python cli.py serve --host 127.0.0.1 --port 8000
```

The local web UI is served at `/`. Use `POST /api/score` with the six structured clinical inputs; interactive API docs are at `/docs`. The separate `cli.py audit`, `/api/audit`, `/api/chat`, `agents/`, `enrichment.py` and `simulator.py` remain as **legacy demonstrations** using arbitrary measurements. Their alerts, mock responses, and enrichment labels **do not implement or validate TBscore II** and must not be used to direct clinical care.

Access to `/api/audit/logs` requires `AUDIT_READ_TOKEN` in the server environment and a matching `X-Audit-Token` header. `AUDIT_SECRET_KEY` should be set to a strong random value for cross-restart audit-key consistency. The legacy regex-based identifier filter is not a validated de-identification system.

## Privacy and security

The browser UI sends no requests, has no analytics, cookies, or local storage, and does not retain inputs. The API, when run separately, receives values over its configured network transport. Do not expose it directly to the public internet or submit personal health information without an appropriate secured deployment and privacy review. CSV outputs contain clinical observations; protect them as appropriate.

## Testing

```bash
python -m pip install -r requirements.txt
python -m pytest -q
node --test web/test_score.mjs
node --check web/app.mjs
```

CI tests Python 3.10–3.13 and Node 22. The GitHub Actions workflow also contains a static GitHub Pages deployment job for the `web/` directory; successful activation and the live address depend on Pages settings in the repository.

## Technology and compatibility

Python standard library for score and CSV; HTML/CSS and native JavaScript modules for the browser; optional FastAPI, Uvicorn, and Pydantic for the server. Browser UI requires a modern browser supporting ES modules and `FormData`. The optional Python server can also be run via the provided Dockerfile / Compose configuration.

## License

MIT — see [LICENSE](LICENSE).
