"""Evaluation runner for OTP Voice App

This script performs a small set of automated smoke checks and configuration
validations that are safe to run locally (no external Twilio/ElevenLabs calls).

What it checks:
- App import and basic endpoints (health)
- `/api/validate/phone` endpoint behavior
- `config/scripts.json` structural integrity
- `utils.env_utils.validate_configuration()` output

Outputs a JSON report to `eval/report.json` and prints a short summary.
"""
import json
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("eval")


def load_app():
    try:
        # Prefer the clean factory in `app_main.py` to avoid importing
        # a corrupted `app.py` during automated runs.
        from app_main import create_app
        return create_app()
    except Exception as e:
        # Provide a clearer message for missing dependencies
        msg = str(e)
        if isinstance(e, ModuleNotFoundError):
            missing = e.name
            msg = (
                f"Missing Python package: {missing}.\n"
                "Run `pip install -r requirements.txt` in the project root and try again."
            )
        return {'error': f'Failed importing app: {msg}'}


def check_health_endpoints(client):
    paths = ['/api/health', '/health', '/']
    results = {}
    for p in paths:
        try:
            r = client.get(p)
            results[p] = {'status_code': r.status_code}
        except Exception as e:
            results[p] = {'error': str(e)}
    return results


def check_phone_validation(client):
    payload = {"phone_number": "+1234567890"}
    try:
        r = client.post('/api/validate/phone', json=payload)
        try:
            body = r.get_json()
        except Exception:
            body = None
        return {'status_code': r.status_code, 'body': body}
    except Exception as e:
        return {'error': str(e)}


def check_scripts_integrity():
    p = Path('config') / 'scripts.json'
    if not p.exists():
        return {'error': 'config/scripts.json not found'}
    try:
        data = json.loads(p.read_text(encoding='utf-8'))
        if not isinstance(data, list):
            return {'error': 'scripts.json root is not a list'}
        problems = []
        for i, entry in enumerate(data):
            if not isinstance(entry, dict):
                problems.append(f'entry[{i}] not an object')
                continue
            for k in ('userid', 'ScriptNAME', 'Voice'):
                if k not in entry:
                    problems.append(f'entry[{i}] missing {k}')
        return {'count': len(data), 'problems': problems}
    except Exception as e:
        return {'error': f'failed to parse scripts.json: {e}'}


def check_configuration_validation():
    try:
        from utils.env_utils import validate_configuration
        return validate_configuration()
    except Exception as e:
        return {'error': f'validate_configuration failed: {e}'}


def main():
    report = {'tests': {}, 'summary': {}}

    app_obj = load_app()
    if isinstance(app_obj, dict) and app_obj.get('error'):
        report['tests']['app_import'] = {'passed': False, 'error': app_obj['error']}
        logger.error(app_obj['error'])
        print(json.dumps(report, indent=2))
        Path('eval').mkdir(parents=True, exist_ok=True)
        Path('eval/report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        sys.exit(2)

    app = app_obj
    client = app.test_client()

    report['tests']['health_endpoints'] = check_health_endpoints(client)
    report['tests']['phone_validation'] = check_phone_validation(client)
    report['tests']['scripts_integrity'] = check_scripts_integrity()
    report['tests']['configuration_validation'] = check_configuration_validation()

    # Build a lightweight summary
    passed = True
    errors = []
    # app import already validated above
    # health endpoints: success if any returned 200
    he = report['tests']['health_endpoints']
    if not any((v.get('status_code') == 200 for v in he.values() if isinstance(v, dict))):
        passed = False
        errors.append('no health endpoint returned 200')

    pv = report['tests']['phone_validation']
    if pv.get('error') or pv.get('status_code') != 200:
        passed = False
        errors.append('phone validation endpoint failed or returned non-200')

    si = report['tests']['scripts_integrity']
    if si.get('error') or (si.get('problems') and len(si.get('problems')) > 0):
        passed = False
        errors.append('scripts.json integrity problems')

    cv = report['tests']['configuration_validation']
    if cv.get('twilio') and not cv['twilio'].get('valid'):
        # not a hard failure for evaluation — config may be purposely unset locally
        logger.warning('Twilio credentials appear to be missing or invalid')

    report['summary']['passed'] = passed
    report['summary']['errors'] = errors

    Path('eval').mkdir(parents=True, exist_ok=True)
    out_path = Path('eval') / 'report.json'
    out_path.write_text(json.dumps(report, indent=2), encoding='utf-8')

    logger.info('Evaluation complete — report saved to %s', out_path)
    print(json.dumps(report, indent=2))
    sys.exit(0 if passed else 2)


if __name__ == '__main__':
    main()
