<!-- Copilot instructions for OTPBOT_FOR_RED_TEAM -->
# Copilot / AI agent instructions — OTP Voice App (educational)

Purpose
- Provide immediate, actionable context so an AI coding agent can be productive in this repository.

Big picture (what this repo does)
- This is a Flask-based educational web app that demonstrates voice-delivered OTPs with fallback SMS and a Telegram bot UI.
- Core integrations: Twilio (voice & SMS), ElevenLabs (TTS), Telegram (bot/webhooks). The app is intentionally modular: `services/` implements third-party integrations; `routes/` exposes HTTP and webhook endpoints; `config/` stores script and settings JSON.

Key files & directories (where to look first)
- `app.py` — Flask app entrypoint and route registration.
- `routes/` — HTTP endpoints and webhook handlers:
  - `routes/api_routes.py` — REST API for OTP operations (`/api/otp/*`, `/api/validate/*`).
  - `routes/telegram_routes.py` — Telegram webhook handlers (expects `/telegram/webhook`).
  - `routes/voice_routes.py` — TwiML endpoints for call flows.
- `services/` — Integration logic:
  - `twilio_service.py` — Twilio voice + SMS; TwiML generation and status callbacks.
  - `elevenlabs_service.py` — ElevenLabs TTS wrapper and voice selection.
  - `telegram_service.py` — Telegram bot interaction helpers.
  - `otp_service.py` — OTP generation, formatting, and rate-limiting checks.
- `config/` — Operational configuration:
  - `settings.py` and `settings.json` — where runtime settings are read.
  - `scripts.json` — voice script templates and `userid`→script mappings.
- `utils/` — helpers (e.g., `logger.py`, `env_utils.py`).
- `templates/index.html` — basic web UI used by tests/manual flows.

How the pieces interact (data flow)
- API request (POST `/api/otp/voice`) → `routes/api_routes.py` → `otp_service.py` for OTP logic → `elevenlabs_service.py` to generate audio (or TTS streaming) → `twilio_service.py` to initiate a call and return TwiML webhook endpoints.
- Telegram commands are parsed in `routes/telegram_routes.py` and call `telegram_service.py` which often delegates to `otp_service.py` and `twilio_service.py`.

Important developer workflows (commands & environment)
- Install deps: `pip install -r requirements.txt` (repo uses plain Flask + service SDKs).
- Local run (development): `python app.py` (reads `config/settings.json` and environment variables).
- Production run (example): `gunicorn app:app --bind 0.0.0.0:5000`.
- Webhooks: use `ngrok` and set `NGROK_URL` in environment (README shows example). Ensure the Telegram webhook is set to `<NGROK_URL>/telegram/webhook`.

Environment variables (what to set)
- `TELEGRAM_BOT_TOKEN` — Telegram bot token.
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` — Twilio creds and phone.
- `ELEVENLABS_API_KEY` — ElevenLabs API key.
- `NGROK_URL` — tunnel URL for webhook testing.
- The repo references an `.env` (from README); search for env parsing in `config/settings.py` or `utils/env_utils.py` to confirm exact keys.

Repository-specific patterns & conventions
- Services are single-responsibility modules in `services/` — prefer adding new provider integrations here.
- Routes are thin: they parse input, validate with `otp_service.py`, then call `services/*` for external interactions.
- Voice scripts mapping: `config/scripts.json` maps `userid` to `ScriptID`, `ScriptNAME`, and `Voice`. When modifying or adding scripts, preserve the existing JSON keys.
- Logging: use `utils/logger.py` — keep logs consistent and include `user_id`, `phone_number`, and `request_id` where applicable.

Integration tips & pitfalls
- Twilio webhooks: Twilio will POST call status and TwiML requests — ensure endpoints in `routes/voice_routes.py` are publicly reachable (ngrok) and validate Twilio signatures if verification is present.
- ElevenLabs: TTS can be synchronous/streamed; check `elevenlabs_service.py` for expected return (audio file vs URL).
- Telegram: webhook handler will expect JSON from Telegram — verify `routes/telegram_routes.py` path and token checks.

Examples (concrete references)
- To trigger a voice OTP locally:
  - POST to `/api/otp/voice` with `{ "phone_number": "+1234567890", "script_name": "microsoft" }` (see README and `routes/api_routes.py`).
- To inspect which voice a user mapping uses, open `config/scripts.json` and search for the user's `userid`.

What not to change lightly
- `config/scripts.json` keys and shape — other code reads `userid` and `ScriptNAME` directly.
- Twilio/TwiML endpoints in `routes/voice_routes.py` — changing paths breaks existing webhook URLs and ngrok setup.

Checklist for PRs an AI agent should follow
- Run `python app.py` locally and smoke test the endpoint you change.
- Update `config/scripts.json` only when adding new script templates; keep existing entries intact.
- Add small unit or integration tests only if the repo already contains tests — otherwise open an issue requesting test scaffolding.

Safety & policy notes
- This repo is explicitly educational and warns against misuse — do not implement or suggest features that enable abusive messaging or covert account access. Respect the README's safety notice.

If anything is unclear
- Ask for the runtime `.env` loader details (which file reads env vars) before changing environment keys.
- Point to the exact file you want to modify; include a short description of the desired behavior.

-- End of instructions
