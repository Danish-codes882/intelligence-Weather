"""
app.py – Weather Intelligence Platform
Production Flask application with layered architecture.
"""

import logging
import re
import sys
import os
from datetime import datetime, timezone

from flask import Flask, render_template, jsonify, request, abort
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from apscheduler.schedulers.background import BackgroundScheduler

# Local imports
sys.path.insert(0, os.path.dirname(__file__))
from config import Config
from services.weather_service import build_weather_payload
from services.ml_service import run_full_analysis
from services.risk_service import compute_all_risks
from services.outfit_service import get_outfit_products
from services.city_service import get_city_content
from services.theme_service import get_theme

# ─── Logging ───────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S',
)
logger = logging.getLogger(__name__)

# ─── App Factory ───────────────────────────────────────────────────────────

def create_app(config_name: str = 'default') -> Flask:
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)

    # Extensions
    cache = Cache(app)
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=['200 per day', '60 per hour'],
        storage_uri='memory://',
    )

    # Background scheduler for auto-refresh
    scheduler = BackgroundScheduler(timezone='UTC')
    scheduler.start()

    # Store last update times
    app.last_updates = {}

    # ─── Helper: Input Sanitization ────────────────────────────────────────

    def sanitize_city(city: str) -> str | None:
        if not city:
            return None
        city = city.strip()
        # Allow letters, spaces, hyphens, apostrophes, commas (for "city, country")
        if not re.match(r"^[A-Za-zÀ-ÿ\s\-',\.]{1,80}$", city):
            return None
        return city[:80]

    # ─── Routes ────────────────────────────────────────────────────────────

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/weather', methods=['GET'])
    @limiter.limit('30 per minute')
    @cache.cached(timeout=600, query_string=True)
    def weather_api():
        city_raw = request.args.get('city', '').strip()
        city = sanitize_city(city_raw)

        if not city:
            return jsonify({'error': 'Invalid city name. Please use letters only.', 'code': 'INVALID_INPUT'}), 400

        logger.info(f"Weather request for city: {city}")

        # 1. Fetch weather data
        weather = build_weather_payload(city)
        if not weather:
            return jsonify({'error': f'City "{city}" not found or weather data unavailable.', 'code': 'CITY_NOT_FOUND'}), 404

        # 2. ML Analysis
        try:
            ml_analysis = run_full_analysis(weather)
        except Exception as e:
            logger.error(f"ML analysis failed: {e}")
            ml_analysis = {'error': 'ML analysis unavailable'}

        # 3. Risk Index
        try:
            risks = compute_all_risks(weather['current'])
        except Exception as e:
            logger.error(f"Risk computation failed: {e}")
            risks = {}

        # 4. Outfit Products
        try:
            clothing_primary = ml_analysis.get('clothing', {}).get('primary', 'T-Shirt')
            temp = weather['current']['temperature']
            products = get_outfit_products(clothing_primary, temp)
        except Exception as e:
            logger.error(f"Outfit fetch failed: {e}")
            products = []

        # 5. City Content
        try:
            city_name = weather['city']['name']
            country = weather['city']['country']
            city_content = get_city_content(city_name, country)
        except Exception as e:
            logger.error(f"City content fetch failed: {e}")
            city_content = {'name': city, 'description': '', 'images': [], 'tourist_spots': []}

        # 6. Theme
        category_key = ml_analysis.get('category', {}).get('key', 'normal')
        icon_key = weather['current'].get('icon_key', '')
        theme = get_theme(category_key, icon_key)

        # Update timestamp
        app.last_updates[city.lower()] = datetime.now(timezone.utc).isoformat()

        return jsonify({
            'status': 'success',
            'data': {
                'weather': weather,
                'ml': ml_analysis,
                'risks': risks,
                'products': products,
                'city_content': city_content,
                'theme': theme,
            },
            'meta': {
                'fetched_at': weather['fetched_at'],
                'city': city,
                'cache_expires_in': 600,
            },
        })

    @app.route('/api/last-updated', methods=['GET'])
    def last_updated():
        city = sanitize_city(request.args.get('city', ''))
        if not city:
            return jsonify({'minutes_ago': None})
        ts = app.last_updates.get(city.lower())
        if not ts:
            return jsonify({'minutes_ago': None, 'timestamp': None})
        last_dt = datetime.fromisoformat(ts)
        now = datetime.now(timezone.utc)
        delta_minutes = int((now - last_dt).total_seconds() / 60)
        return jsonify({'minutes_ago': delta_minutes, 'timestamp': ts})

    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'version': '1.0.0', 'time': datetime.utcnow().isoformat()})

    # ─── Error Handlers ────────────────────────────────────────────────────

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return jsonify({'error': 'Rate limit exceeded. Please wait before trying again.', 'code': 'RATE_LIMITED'}), 429

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Endpoint not found.', 'code': 'NOT_FOUND'}), 404

    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Internal server error: {e}")
        return jsonify({'error': 'Internal server error.', 'code': 'INTERNAL_ERROR'}), 500

    return app


# ─── Entry Point ───────────────────────────────────────────────────────────

app = create_app()

if __name__ == '__main__':
    logger.info("Starting Weather Intelligence Platform")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
