"""
risk_service.py
Calculates Weather Risk Index indicators:
- Heatstroke Risk
- Cold Exposure Risk
- Humidity Discomfort Index
- UV Risk
- Wind Chill Risk
"""

import math


def heat_index(temp_c: float, humidity: float) -> float:
    """Compute Rothfusz heat index (°C)."""
    t = temp_c * 9 / 5 + 32  # to Fahrenheit
    rh = humidity
    if t < 80:
        return temp_c  # Heat index only meaningful above 80°F

    hi_f = (
        -42.379
        + 2.04901523 * t
        + 10.14333127 * rh
        - 0.22475541 * t * rh
        - 0.00683783 * t ** 2
        - 0.05481717 * rh ** 2
        + 0.00122874 * t ** 2 * rh
        + 0.00085282 * t * rh ** 2
        - 0.00000199 * t ** 2 * rh ** 2
    )
    return (hi_f - 32) * 5 / 9


def wind_chill(temp_c: float, wind_kmh: float) -> float:
    """Compute wind chill (°C) – valid below 10°C and wind > 4.8 km/h."""
    if temp_c >= 10 or wind_kmh < 4.8:
        return temp_c
    v = wind_kmh ** 0.16
    return round(13.12 + 0.6215 * temp_c - 11.37 * v + 0.3965 * temp_c * v, 1)


def calculate_heatstroke_risk(temp: float, humidity: float, uv_index: float = 0) -> dict:
    """
    Heatstroke risk (0–100 scale).
    Based on effective heat index and UV.
    """
    hi = heat_index(temp, humidity)
    uv_contrib = min(uv_index * 2, 20)  # max 20 pts from UV

    if hi < 27:
        base = 0
        level = 'none'
        label = 'No Risk'
        color = '#22c55e'
    elif hi < 32:
        base = 20
        level = 'low'
        label = 'Low'
        color = '#84cc16'
    elif hi < 38:
        base = 45
        level = 'moderate'
        label = 'Moderate'
        color = '#eab308'
    elif hi < 44:
        base = 70
        level = 'high'
        label = 'High'
        color = '#f97316'
    else:
        base = 90
        level = 'extreme'
        label = 'Extreme'
        color = '#ef4444'

    score = min(100, base + uv_contrib)

    return {
        'score': round(score),
        'level': level,
        'label': label,
        'color': color,
        'heat_index': round(hi, 1),
        'tip': _heatstroke_tip(level),
    }


def _heatstroke_tip(level: str) -> str:
    tips = {
        'none': 'Conditions are comfortable.',
        'low': 'Stay hydrated during outdoor activity.',
        'moderate': 'Limit prolonged sun exposure. Drink water frequently.',
        'high': 'Avoid strenuous outdoor activity. Seek shade and stay cool.',
        'extreme': 'Danger: avoid all outdoor exposure. Stay in air conditioning.',
    }
    return tips.get(level, '')


def calculate_cold_risk(temp: float, wind_kmh: float, humidity: float) -> dict:
    """Cold exposure / frostbite risk (0–100)."""
    wc = wind_chill(temp, wind_kmh)
    humidity_factor = max(0, (humidity - 60) * 0.2) if temp < 5 else 0  # wet cold worse

    if wc >= 10:
        base = 0
        level = 'none'
        label = 'No Risk'
        color = '#22c55e'
    elif wc >= 0:
        base = 15
        level = 'low'
        label = 'Low'
        color = '#38bdf8'
    elif wc >= -10:
        base = 35
        level = 'moderate'
        label = 'Moderate'
        color = '#818cf8'
    elif wc >= -25:
        base = 60
        level = 'high'
        label = 'High'
        color = '#6366f1'
    else:
        base = 85
        level = 'extreme'
        label = 'Extreme'
        color = '#4f46e5'

    score = min(100, base + humidity_factor)

    return {
        'score': round(score),
        'level': level,
        'label': label,
        'color': color,
        'wind_chill': wc,
        'tip': _cold_tip(level),
    }


def _cold_tip(level: str) -> str:
    tips = {
        'none': 'Pleasant conditions for outdoor activity.',
        'low': 'Wear a light jacket for extended outdoor time.',
        'moderate': 'Layer up. Protect exposed skin.',
        'high': 'Serious cold risk. Minimize outdoor exposure. Cover all skin.',
        'extreme': 'Life-threatening wind chill. Do not go outdoors.',
    }
    return tips.get(level, '')


def calculate_humidity_discomfort(temp: float, humidity: float) -> dict:
    """
    Humidex-based discomfort index (0–100).
    High temp + high humidity is most uncomfortable.
    """
    # Dewpoint approximation
    a = 17.625
    b = 243.04
    gamma = (a * temp / (b + temp)) + math.log(max(humidity, 1) / 100.0)
    dew_point = b * gamma / (a - gamma)

    humidex = temp + (5 / 9) * (6.105 * math.exp(25.22 * (dew_point - 273.16) / dew_point) - 10)

    if humidex < 20:
        score = 0
        level = 'comfortable'
        label = 'Comfortable'
        color = '#22c55e'
    elif humidex < 30:
        score = 20
        level = 'little_discomfort'
        label = 'Little Discomfort'
        color = '#84cc16'
    elif humidex < 40:
        score = 50
        level = 'noticeable'
        label = 'Noticeable Discomfort'
        color = '#eab308'
    elif humidex < 45:
        score = 72
        level = 'evident'
        label = 'Evident Discomfort'
        color = '#f97316'
    elif humidex < 54:
        score = 88
        level = 'intense'
        label = 'Intense Discomfort'
        color = '#ef4444'
    else:
        score = 100
        level = 'dangerous'
        label = 'Dangerous'
        color = '#dc2626'

    return {
        'score': min(100, max(0, round(score))),
        'level': level,
        'label': label,
        'color': color,
        'humidex': round(humidex, 1),
        'dew_point': round(dew_point, 1),
        'tip': _humidity_tip(level),
    }


def _humidity_tip(level: str) -> str:
    tips = {
        'comfortable': 'Humidity levels are pleasant.',
        'little_discomfort': 'Slight humidity. Generally fine.',
        'noticeable': 'Noticeably humid. Light breathable clothing advised.',
        'evident': 'Oppressively humid. Rest frequently and stay hydrated.',
        'intense': 'Intense discomfort. Limit outdoor activity.',
        'dangerous': 'Dangerous heat-humidity combination. Stay indoors.',
    }
    return tips.get(level, '')


def compute_all_risks(current: dict) -> dict:
    """Compute all risk indices from current weather data."""
    temp = current.get('temperature', 20)
    humidity = current.get('humidity', 50)
    wind = current.get('wind_speed', 0)
    uv = current.get('uv_index', 0)

    return {
        'heatstroke': calculate_heatstroke_risk(temp, humidity, uv),
        'cold_exposure': calculate_cold_risk(temp, wind, humidity),
        'humidity_discomfort': calculate_humidity_discomfort(temp, humidity),
    }
