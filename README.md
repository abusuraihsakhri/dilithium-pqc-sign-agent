# Dilithium PQC Sign Agent

> **Domain:** Post-Quantum Cryptography & Zero-Knowledge Architecture
> **Reference Guidelines & Standards:** `NIST FIPS 203/204/205, NIST SP 800-90B & ISO/IEC Standards`

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

**Dilithium PQC Sign Agent** is an advanced analytical and computational platform implementing NIST FIPS 204 ML-DSA (Dilithium2/3/5) digital signature verification & rejection sampling. It provides a multi-worker evaluation engine with cryptographic audit trails and PHI outbound protection.

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **Deterministic Calculation Engine**: Strict compliance with standard reference formulations and thresholds.
- **Risk & Urgency Classification**: Multi-tier categorization with automated clinical/operational action recommendations.
- **Validation & Guardrails**: Rigorous input bounds checking and anomaly detection.
- **Multi-Worker Evaluation**: Invariant QC, Safety Escalation, and Protocol Conformance workers.
- **FastAPI REST API**: OpenAPI 3.1 endpoints for programmatic access.
- **Prometheus Telemetry**: Operational metrics export.

---

## 💻 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/dilithium-pqc-sign-agent.git
cd dilithium-pqc-sign-agent

# Install dependencies
pip install fastapi uvicorn pydantic pytest

# Set the audit secret key (required)
export AUDIT_SECRET_KEY="your-secure-audit-key-min-32-chars"
```

---

## 💻 CLI Quickstart & Usage

### 1. Guided Interactive Mode
```bash
python cli.py audit
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 3. Batch Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail
```bash
python cli.py verify-audit
```

### 5. Start API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
- `--task-id`: Unique task identifier (alphanumeric, underscores, hyphens only)
- `--target`: Target identifier (alphanumeric, underscores, hyphens only)
- `--primary`: Primary metric value (float)
- `--secondary`: Secondary metric value (float)
- `--critical`: Flag for critical priority
- `--status`: Status descriptor (e.g., NOMINAL, DISCORDANT)

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Unique task identifier | Required |
| `target_identifier` | Target entity identifier | Required |
| `primary_metric` | Primary measurement value | Required |
| `secondary_metric` | Secondary measurement value | Optional |
| `is_critical_flag` | Critical priority flag | Optional |
| `status_descriptor` | Status code descriptor | Optional |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition. Both chain linkage AND HMAC signatures are verified.
* **Secure Key Management:** Audit secret key must be provided via `AUDIT_SECRET_KEY` environment variable (minimum 32 characters). No hardcoded defaults.
* **Input Validation:** All identifiers are validated to prevent path traversal and injection attacks.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
# Set test audit key
export AUDIT_SECRET_KEY="test-audit-key-for-unit-tests-only-2026"

# Run tests
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
docker build -t dilithium-pqc-sign-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY="your-secure-audit-key" dilithium-pqc-sign-agent
```

---

## 📁 Project Structure

```
dilithium-pqc-sign-agent/
├── agents/                  # Core agent modules
│   ├── api.py              # FastAPI REST server
│   ├── base.py             # Security, PHI guard, audit trail
│   ├── learning.py         # Bayesian calibration engine
│   ├── llm_factory.py      # LLM provider factory
│   ├── metrics.py          # Prometheus metrics
│   ├── models.py           # Pydantic data models
│   ├── streamer.py         # WebSocket telemetry
│   ├── supervisor.py       # Supervisor orchestrator
│   └── workers.py          # Specialized worker agents
├── dilithium_sign/         # Dilithium signature modules
│   ├── agents.py           # PQC signature coordinator
│   ├── cli.py              # CLI for dilithium module
│   ├── engine.py           # Core algorithmic engine
│   ├── models.py           # Data models
│   └── server.py           # FastAPI server factory
├── tests/                  # Test suite
├── cli.py                  # Main CLI entry point
├── dilithium_sign_app.py   # Alternative entry point
├── enrichment.py           # Enrichment feature suite
├── simulator.py            # High-throughput simulator
├── Dockerfile              # Container definition
├── docker-compose.yml      # Docker Compose config
└── pyproject.toml          # Project metadata
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
