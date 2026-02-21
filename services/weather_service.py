import time
import logging
import requests
import json
from datetime import datetime, timedelta
from config import Config

logger = logging.getLogger(__name__)


def _make_request(url: str, params: dict = None, retries: int = None) -> requests.Response | None:
    """Make HTTP request with retry logic and timeout handling."""
    retries = retries or Config.REQUEST_RETRIES
    backoff = Config.REQUEST_BACKOFF

    for attempt in range(retries):
        try:
            resp = requests.get(
                url,
                params=params,
                headers=Config.HEADERS,
                timeout=Config.REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            return resp
        except requests.exceptions.Timeout:
            logger.warning(f"Request timeout on attempt {attempt + 1}: {url}")
        except requests.exceptions.HTTPError as e:
            logger.warning(f"HTTP error {e.response.status_code} on attempt {attempt + 1}: {url}")
            if e.response.status_code in (400, 404):
                return None  # No point retrying client errors
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection error on attempt {attempt + 1}: {url}")
        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")

        if attempt < retries - 1:
            time.sleep(backoff * (attempt + 1))

    return None


def geocode_city(city_name: str) -> dict | None:
    """Resolve city name to coordinates using Open-Meteo geocoding API."""
    resp = _make_request(
        Config.GEOCODING_URL,
        params={'name': city_name, 'count': 1, 'language': 'en', 'format': 'json'},
    )
    if not resp:
        return None

    data = resp.json()
    results = data.get('results', [])
    if not results:
        return None

    r = results[0]
    return {
        'name': r.get('name', city_name),
        'country': r.get('country', ''),
        'country_code': r.get('country_code', ''),
        'latitude': r['latitude'],
        'longitude': r['longitude'],
        'timezone': r.get('timezone', 'UTC'),
        'admin1': r.get('admin1', ''),
    }


def fetch_current_weather(lat: float, lon: float, timezone: str = 'UTC') -> dict | None:
    """Fetch current weather + 7-day history via Open-Meteo."""
    today = datetime.utcnow()
    seven_days_ago = today - timedelta(days=7)

    params = {
        'latitude': lat,
        'longitude': lon,
        'current': [
            'temperature_2m', 'apparent_temperature', 'relative_humidity_2m',
            'wind_speed_10m', 'wind_direction_10m', 'precipitation',
            'weather_code', 'surface_pressure', 'visibility', 'uv_index',
            'cloud_cover', 'is_day',
        ],
        'hourly': [
            'temperature_2m', 'relative_humidity_2m', 'wind_speed_10m',
            'apparent_temperature', 'precipitation_probability',
        ],
        'daily': [
            'temperature_2m_max', 'temperature_2m_min', 'precipitation_sum',
            'weather_code', 'wind_speed_10m_max',
        ],
        'timezone': timezone,
        'forecast_days': 7,
        'wind_speed_unit': 'kmh',
    }

    resp = _make_request(Config.OPEN_METEO_URL, params=params)
    if not resp:
        return None

    return resp.json()


def parse_wmo_code(code: int) -> str:
    """Convert WMO weather code to human-readable description."""
    wmo_map = {
        0: 'Clear Sky', 1: 'Mainly Clear', 2: 'Partly Cloudy', 3: 'Overcast',
        45: 'Fog', 48: 'Icy Fog',
        51: 'Light Drizzle', 53: 'Moderate Drizzle', 55: 'Dense Drizzle',
        61: 'Slight Rain', 63: 'Moderate Rain', 65: 'Heavy Rain',
        71: 'Slight Snow', 73: 'Moderate Snow', 75: 'Heavy Snow',
        77: 'Snow Grains',
        80: 'Slight Rain Showers', 81: 'Moderate Rain Showers', 82: 'Violent Rain Showers',
        85: 'Slight Snow Showers', 86: 'Heavy Snow Showers',
        95: 'Thunderstorm', 96: 'Thunderstorm with Hail', 99: 'Heavy Thunderstorm',
    }
    return wmo_map.get(code, 'Unknown')


def get_weather_icon_key(code: int, is_day: int = 1) -> str:
    """Map WMO code to icon key for frontend SVG system."""
    if code == 0:
        return 'sunny' if is_day else 'clear-night'
    if code in (1, 2):
        return 'partly-cloudy'
    if code == 3:
        return 'cloudy'
    if code in (45, 48):
        return 'fog'
    if code in (51, 53, 55, 61, 63, 65, 80, 81, 82):
        return 'rain'
    if code in (71, 73, 75, 77, 85, 86):
        return 'snow'
    if code in (95, 96, 99):
        return 'thunderstorm'
    return 'cloudy'


def build_weather_payload(city_name: str) -> dict | None:
    """
    Main entry point: geocode city then fetch all weather data.
    Returns structured dict ready for API response.
    """
    geo = geocode_city(city_name)
    if not geo:
        return None

    raw = fetch_current_weather(geo['latitude'], geo['longitude'], geo.get('timezone', 'UTC'))
    if not raw:
        return None

    current = raw.get('current', {})
    hourly = raw.get('hourly', {})
    daily = raw.get('daily', {})

    temp = current.get('temperature_2m', 0)
    feels_like = current.get('apparent_temperature', 0)
    humidity = current.get('relative_humidity_2m', 0)
    wind_speed = current.get('wind_speed_10m', 0)
    wind_dir = current.get('wind_direction_10m', 0)
    weather_code = current.get('weather_code', 0)
    pressure = current.get('surface_pressure', 1013)
    visibility = current.get('visibility', 10000)
    uv_index = current.get('uv_index', 0)
    cloud_cover = current.get('cloud_cover', 0)
    is_day = current.get('is_day', 1)
    precip = current.get('precipitation', 0)

    # Next 24-hour hourly data for ML
    temps_24h = hourly.get('temperature_2m', [])[:24]
    humidity_24h = hourly.get('relative_humidity_2m', [])[:24]
    wind_24h = hourly.get('wind_speed_10m', [])[:24]
    precip_prob_24h = hourly.get('precipitation_probability', [])[:24]
    apparent_24h = hourly.get('apparent_temperature', [])[:24]
    hourly_times = hourly.get('time', [])[:24]

    # 7-day forecast
    daily_forecast = []
    d_times = daily.get('time', [])
    d_max = daily.get('temperature_2m_max', [])
    d_min = daily.get('temperature_2m_min', [])
    d_codes = daily.get('weather_code', [])
    d_precip = daily.get('precipitation_sum', [])
    d_wind = daily.get('wind_speed_10m_max', [])

    for i in range(min(7, len(d_times))):
        daily_forecast.append({
            'date': d_times[i] if i < len(d_times) else '',
            'temp_max': round(d_max[i], 1) if i < len(d_max) else temp,
            'temp_min': round(d_min[i], 1) if i < len(d_min) else temp - 5,
            'weather_code': d_codes[i] if i < len(d_codes) else 0,
            'description': parse_wmo_code(d_codes[i] if i < len(d_codes) else 0),
            'icon_key': get_weather_icon_key(d_codes[i] if i < len(d_codes) else 0),
            'precipitation_sum': round(d_precip[i], 1) if i < len(d_precip) else 0,
            'wind_max': round(d_wind[i], 1) if i < len(d_wind) else wind_speed,
        })

    return {
        'city': {
            'name': geo['name'],
            'country': geo['country'],
            'country_code': geo['country_code'],
            'region': geo.get('admin1', ''),
            'latitude': geo['latitude'],
            'longitude': geo['longitude'],
            'timezone': geo.get('timezone', 'UTC'),
        },
        'current': {
            'temperature': round(temp, 1),
            'feels_like': round(feels_like, 1),
            'humidity': humidity,
            'wind_speed': round(wind_speed, 1),
            'wind_direction': wind_dir,
            'weather_code': weather_code,
            'description': parse_wmo_code(weather_code),
            'icon_key': get_weather_icon_key(weather_code, is_day),
            'pressure': round(pressure, 1),
            'visibility': round(visibility / 1000, 1),  # km
            'uv_index': uv_index,
            'cloud_cover': cloud_cover,
            'is_day': is_day,
            'precipitation': round(precip, 1),
        },
        'hourly_24h': {
            'times': hourly_times,
            'temperatures': [round(t, 1) for t in temps_24h],
            'humidity': humidity_24h,
            'wind_speeds': [round(w, 1) for w in wind_24h],
            'precipitation_probability': precip_prob_24h,
            'apparent_temperatures': [round(t, 1) for t in apparent_24h],
        },
        'daily_forecast': daily_forecast,
        'fetched_at': datetime.utcnow().isoformat(),
    }
