Evaluation framework for OTP Voice App

Overview
- This folder contains a small evaluation runner that performs safe, local checks
  to validate basic application behavior and configuration. It is intentionally
  conservative: it does not call Twilio or ElevenLabs APIs.

Files
- `run_evaluation.py`: runner that performs a set of checks and writes
  `eval/report.json` with results.

What the runner checks
- App import (`app.py`) and presence of a Flask `app` object
- Health endpoints: `/`, `/health`, `/api/health` (if present)
- Phone validation endpoint: `POST /api/validate/phone` with sample payload
- `config/scripts.json` structural checks (each entry should include `userid`, `ScriptNAME`, and `Voice`)
- `utils.env_utils.validate_configuration()` output (shows missing credentials)

How to run (PowerShell)
```powershell
# (optional) create virtualenv and activate
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run evaluation
python eval/run_evaluation.py
```

Output
- `eval/report.json` — JSON report containing test outputs and a small summary.

Notes
- The runner is designed to be safe for local use and will not perform any
  outbound calls to Twilio/ElevenLabs. If you want to add integration tests
  that hit external APIs, extend the runner and add explicit mocking or
  credentials handling.

Feedback
- If you want additional checks (e.g., more API endpoints, sample OTP flows,
  or mocked Twilio responses), tell me which areas to cover and I will add
  targeted tests or a mocked integration harness.
