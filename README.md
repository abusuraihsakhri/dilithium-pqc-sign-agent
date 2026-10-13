# Dilithium PQC Sign Agent

Python tooling for **ML-DSA (FIPS 204) file signatures**, plus separate experimental threshold-based audit utilities.

The ML-DSA operations use [pqcrypto 1.0.0](https://pypi.org/project/pqcrypto/), not the project's legacy numeric scoring engine. The cryptographic dependency has **not been independently certified or audited as part of this project**. Do not assume FIPS 140 validation, NIST conformance certification, or production key-management readiness.

## What works

- **ML-DSA-44, ML-DSA-65, ML-DSA-87:** generate keypairs, sign exact file bytes, and verify file signatures from a CLI.
- **Operational audit CLI/API:** evaluate three clearly project-specific rules: primary metric > 25, secondary metric > 12 or a critical flag, and descriptors containing a configured alert keyword. These rules **do not verify cryptographic signatures or establish FIPS compliance**.
- **Local browser demo:** open [web/index.html](web/index.html) directly. The standalone HTML/JavaScript demo applies the same operational rules without network requests, produces a JSON report, and **does not generate any cryptographic signatures or HMAC audit records**.
- **HMAC-SHA256 audit chain:** the Python supervisor signs and verifies its **in-memory** operational audit entries; these entries are lost when the process restarts.
- **FastAPI:** authenticated numeric audit, chat mock, metrics summary and audit-log inspection. Chat mode is a deterministic mock, not an LLM integration.

## Install

Requires Python 3.10+.

```bash
git clone https://github.com/abusuraihsakhri/dilithium-pqc-sign-agent.git
cd dilithium-pqc-sign-agent
python -m pip install -e ".[api,dev]"
```

### Cryptographic file signing (no audit secret required)

```bash
python cli.py keygen --algorithm ml-dsa-44 --public-out public.key --secret-out private.secret.key
python cli.py sign --algorithm ml-dsa-44 --secret-key private.secret.key --message-file sample.csv --signature-out sample.sig
python cli.py verify --algorithm ml-dsa-44 --public-key public.key --message-file sample.csv --signature-file sample.sig
```

The signer creates new binary files without overwriting existing files. On POSIX systems files are created with mode `0600`; restrict access to the private key and store it securely. Verification prints `VALID` or `INVALID` and exits with status 0 or 1. Message bytes and any UTF-8 `--context` string (maximum 255 bytes) must match exactly.

**Do not commit private keys, send them to an API, or expose them in a browser.** The repository does not implement hardware-backed key storage, key rotation, or certificate issuance.

### Operational audit CLI

Set a random unique secret (minimum 32 characters); this authenticates audit-chain entries, not ML-DSA signatures.

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
python cli.py batch -i sample.csv -o results.csv
python cli.py verify-audit
```

The `verify-audit` command only checks the current Python process's in-memory chain; a new invocation has no access to a previous process's entries. See `tests/` for tamper-detection tests.

### API

```bash
export API_BEARER_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
python cli.py serve --host 127.0.0.1 --port 8000
```

`GET /health` is public. All other API endpoints require `Authorization: Bearer <API_BEARER_TOKEN>`; when the token is absent, requests fail closed. API documentation is available at `/docs` locally. Keep server access limited to trusted networks, use HTTPS behind a reverse proxy when deployed, and do not accept private keys through the audit interface.

Alternatively, Docker Compose requires both environment variables. It binds port 8000 to localhost by default.

## Privacy and limitations

- The offline browser demo does not transmit input data and uses no external fonts or services. It is an **illustrative audit-rule demonstrator**, not a security control.
- The Python API records per-process operational data in memory. Its regex-based identifier checks cannot guarantee detection or redaction of all personal health information.
- There is no production authentication/authorization layer beyond the configured bearer token, no persistent audit storage, and no verified certificate or interoperability test-vector suite.
- GitHub Pages can only host the static browser demo, **not** the Python FastAPI service or native `pqcrypto` implementation. A live Pages deployment has not been verified.

## Development and tests

```bash
python -m pip install -e ".[api,dev]"
python -m pytest -q
python -m compileall -q agents dilithium_sign
node --check web/app.js
node --test tests/web.test.cjs
```

CI tests Python 3.10, 3.11, and 3.12 plus the standalone browser rules. Browser demo targets current desktop and mobile browsers supporting modern JavaScript and local downloads.

## Standards and license

ML-DSA is defined by [NIST FIPS 204](https://csrc.nist.gov/pubs/fips/204/final). The secondary threshold-audit modules are **not FIPS 204 tests**. This project is distributed under the [MIT License](LICENSE).
