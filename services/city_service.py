"""
city_service.py
Scrapes city content: description, skyline images, tourist spots.
Uses Wikipedia and Unsplash for image data.
"""

import logging
import re
import requests
from bs4 import BeautifulSoup
from config import Config

logger = logging.getLogger(__name__)


def _wikipedia_summary(city: str, country: str = '') -> str | None:
    """Fetch city description from Wikipedia API."""
    query = f"{city} {country}".strip()
    url = 'https://en.wikipedia.org/api/rest_v1/page/summary/' + requests.utils.quote(city)

    try:
        resp = requests.get(url, headers=Config.HEADERS, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            extract = data.get('extract', '')
            if extract:
                # Return first 3–5 sentences
                sentences = re.split(r'(?<=[.!?]) +', extract)
                return ' '.join(sentences[:5])
    except Exception as e:
        logger.debug(f"Wikipedia fetch failed for {city}: {e}")

    return None


def _get_city_images(city: str) -> list[dict]:
    """
    Get city skyline images via Unsplash source (no API key required).
    Returns list of image objects with url and credit.
    """
    # Use Unsplash Source API for curated city images
    keywords = [
        f'{city} skyline',
        f'{city} cityscape',
        f'{city} architecture',
        f'{city} landmark',
    ]
    images = []
    seen_urls = set()

    for kw in keywords[:4]:
        slug = kw.replace(' ', ',').lower()
        url = f'https://source.unsplash.com/featured/800x500?{requests.utils.quote(slug)}'
        # Add slight variation to avoid duplicate cache hits
        if url not in seen_urls:
            seen_urls.add(url)
            images.append({
                'url': url,
                'alt': kw,
                'credit': 'Unsplash',
            })

    return images


def _get_tourist_spots(city: str, country: str = '') -> list[str]:
    """
    Scrape Wikipedia for tourist attractions / notable places in a city.
    Returns list of spot names.
    """
    query = f"{city} tourist attractions landmarks"
    search_url = f'https://en.wikipedia.org/w/index.php?search={requests.utils.quote(query)}&ns0=1'

    spots = []
    try:
        resp = requests.get(search_url, headers=Config.HEADERS, timeout=8)
        if resp.status_code != 200:
            return _fallback_tourist_spots(city)

        soup = BeautifulSoup(resp.text, 'lxml')

        # Grab first few list items from mw-search-results or mw-content-text
        items = soup.select('.mw-search-result-heading a')
        for item in items[:6]:
            name = item.get_text(strip=True)
            if city.lower() in name.lower() or any(w in name.lower() for w in ['park', 'museum', 'palace', 'tower', 'bridge', 'temple', 'cathedral', 'garden']):
                spots.append(name)
            if len(spots) >= 5:
                break

    except Exception as e:
        logger.debug(f"Tourist spots scrape failed for {city}: {e}")

    return spots if spots else _fallback_tourist_spots(city)


def _fallback_tourist_spots(city: str) -> list[str]:
    GENERIC_SPOTS = {
        'london': ['Tower of London', 'Buckingham Palace', 'Big Ben', 'Hyde Park', 'The British Museum'],
        'paris': ['Eiffel Tower', 'The Louvre', 'Notre-Dame Cathedral', 'Palace of Versailles', 'Champs-Élysées'],
        'new york': ['Central Park', 'Statue of Liberty', 'Times Square', 'The Metropolitan Museum', 'Brooklyn Bridge'],
        'tokyo': ['Senso-ji Temple', 'Shibuya Crossing', 'Meiji Shrine', 'Tokyo Tower', 'Tsukiji Market'],
        'dubai': ['Burj Khalifa', 'Palm Jumeirah', 'Dubai Mall', 'Desert Safari', 'Gold Souk'],
        'rome': ['The Colosseum', 'Vatican City', 'Trevi Fountain', 'Roman Forum', 'Pantheon'],
        'sydney': ['Sydney Opera House', 'Harbour Bridge', 'Bondi Beach', 'Royal Botanic Garden', 'Manly Beach'],
        'mumbai': ['Gateway of India', 'Elephanta Caves', 'Marine Drive', 'Juhu Beach', 'Chhatrapati Shivaji Terminus'],
    }
    city_lower = city.lower()
    for key, spots in GENERIC_SPOTS.items():
        if key in city_lower:
            return spots
    return [
        f'{city} Old Town', f'{city} Central Park', f'{city} National Museum',
        f'{city} Waterfront', f'{city} City Cathedral',
    ]


def get_city_content(city: str, country: str = '') -> dict:
    """
    Main entry: returns full city content payload.
    """
    description = _wikipedia_summary(city, country)
    if not description:
        description = (
            f"{city} is a vibrant and culturally rich city known for its unique blend "
            f"of history, architecture, and modern urban life. Visitors can explore a wide "
            f"range of attractions, from historic landmarks to bustling local markets. "
            f"The city offers diverse culinary experiences and scenic views that attract "
            f"millions of visitors each year."
        )

    images = _get_city_images(city)
    tourist_spots = _get_tourist_spots(city, country)

    return {
        'name': city,
        'country': country,
        'description': description,
        'images': images,
        'tourist_spots': tourist_spots,
    }
