import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'wx-intel-secret-2024-change-in-prod')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

    # Caching
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 600  # 10 minutes

    # Rate limiting
    RATELIMIT_DEFAULT = '60 per minute'
    RATELIMIT_STORAGE_URL = 'memory://'

    # Weather data sources
    WTTR_BASE_URL = 'https://wttr.in'
    OPEN_METEO_URL = 'https://api.open-meteo.com/v1/forecast'
    GEOCODING_URL = 'https://geocoding-api.open-meteo.com/v1/search'

    # Scraping
    REQUEST_TIMEOUT = 10
    REQUEST_RETRIES = 3
    REQUEST_BACKOFF = 1.5

    HEADERS = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        ),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'application/json,text/html,application/xhtml+xml',
    }

    # Scheduler
    SCHEDULER_TIMEZONE = 'UTC'
    BACKGROUND_REFRESH_MINUTES = 10


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
