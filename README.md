# Tb Score II Clinical Severity

> **Domain:** Infectious Disease Surveillance & Microbiology
> **Reference Guidelines & Standards:** `CLSI M100, EUCAST & CDC NHSN Clinical Standards`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

TBscore II Clinical Severity Index for Tuberculosis.
Calculates TBscore II from signs and symptoms to predict treatment failure and mortality in pulmonary TB.

Zero-dependency Python implementation with single and batch evaluation.
Author: Dr. Abu Suraih Sakhri
License: MIT

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Analytical Functions

- **`calculate_metrics()`**: Core domain algorithm for tb-score-ii-clinical-severity.
- **`process_single()`** — Evaluates a single case with v1/v2/v3 parameters.
- **`process_batch()`** — Processes CSV files with path traversal protection and input validation.
- **`main()`** — CLI entry point for tb_score_ii module.

### 🤖 Enterprise Agent Suite (`agents/`)

- **`SystemSupervisor`** — Multi-worker orchestrator with PHI guard validation.
- **`InvariantQCWorker`** — Primary metric threshold monitoring.
- **`SafetyEscalationWorker`** — Critical safety interlock detection.
- **`ProtocolConformanceWorker`** — Discordance and anomaly triage.
- **`AuditTrail`** — HMAC-SHA256 tamper-evident audit logging.
- **`PHIGuard`** — Zero-PHI outbound interceptor with regex pattern detection.

---

## 💻 Installation

```bash
pip install -r requirements.txt
```

---

## 💻 CLI Quickstart & Usage

### 1. Single Case Evaluation
```bash
python tb_score_ii.py single --v1 14.5 --v2 4.2 --v3 1.8
```

### 2. Batch CSV Processing
```bash
python tb_score_ii.py batch -i sample.csv -o results.csv
```

### 3. Enterprise Agent CLI
```bash
# Run audit evaluation
python cli.py audit --task-id TASK-001 --primary 28.5 --secondary 14.2

# Chat with supervisor
python cli.py chat "Explain TBscore II thresholds"

# Verify audit trail integrity
python cli.py verify-audit

# Batch process with agents
python cli.py batch -i sample.csv -o agent_results.csv

# Launch FastAPI server
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference (tb_score_ii.py)
- `--v1`: Primary parameter (float, default: 10.0)
- `--v2`: Secondary parameter (float, default: 5.0)
- `--v3`: Tertiary parameter (float, default: 2.0)
- `-i/--input`: Input CSV file path (required for batch)
- `-o/--output`: Output CSV file path (default: results.csv)

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `Patient_ID` | Patient identifier | Required |
| `v1` | Primary observation metric | Required |
| `v2` | Secondary observation metric | Required |
| `v3` | Tertiary observation metric | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Path Traversal Protection:** All file operations validate paths against allowed directories.
* **Input Sanitization:** CSV field names are sanitized to prevent injection.
* **Secure Defaults:** Audit keys are generated from `AUDIT_SECRET_KEY` env var with ephemeral fallback.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
docker build -t tb-score-ii-clinical-severity .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key tb-score-ii-clinical-severity
```

Or using docker-compose:

```bash
AUDIT_SECRET_KEY=your-secret-key docker-compose up
```

---

## 📁 Project Structure

```
tb-score-ii-clinical-severity/
├── agents/                  # Enterprise agent suite
│   ├── api.py              # FastAPI REST server
│   ├── base.py             # Security, PHI guard, audit trail
│   ├── models.py           # Pydantic data models
│   ├── supervisor.py       # Multi-worker orchestrator
│   ├── workers.py          # Specialized domain workers
│   ├── llm_factory.py      # LLM provider factory
│   ├── metrics.py          # Prometheus metrics
│   ├── learning.py         # Bayesian calibration engine
│   └── streamer.py         # WebSocket telemetry
├── tests/                  # Test suite
├── web/                    # Operations console (HTML)
├── tb_score_ii.py          # Core algorithm & CLI
├── cli.py                  # Enterprise agent CLI
├── enrichment.py           # Domain enrichment engines
├── simulator.py            # High-throughput simulator
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container build
├── docker-compose.yml      # Container orchestration
└── sample.csv              # Sample input data
```
