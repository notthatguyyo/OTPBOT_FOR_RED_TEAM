"""Clean application factory for OTP Voice App used by tests and eval.

This module provides `create_app()` and is safe to import for automated
tools. It mirrors `app.py` behavior but avoids running the server at import.
"""

from flask import Flask, render_template, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

from config.settings import Config
from routes.api_routes import api_bp
from routes.telegram_routes import telegram_bp
from routes.voice_routes import voice_bp
from services.telegram_service import TelegramService
from utils.logger import setup_logging

try:
    from utils.tracing import init_tracing, instrument_app
    init_tracing()
except Exception:
    pass

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    setup_logging()
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(telegram_bp, url_prefix='/telegram')
    app.register_blueprint(voice_bp, url_prefix='/voice')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'service': 'OTP Voice App'})

    try:
        instrument_app(app)
    except Exception:
        pass

    return app


def run():
    app = create_app()
    telegram_service = TelegramService()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

if __name__ == '__main__':
    run()
