"""
outfit_service.py
Scrapes outfit/clothing product suggestions based on weather clothing recommendation.
Uses DuckDuckGo shopping search to find real product data.
"""

import logging
import re
import requests
from bs4 import BeautifulSoup
from config import Config

logger = logging.getLogger(__name__)

# Curated product data per clothing category (fallback when scraping unavailable)
FALLBACK_PRODUCTS = {
    'heavy_cold': [
        {
            'name': 'Uniqlo Ultra Light Down Jacket',
            'price': '$69.90',
            'image': 'https://images.unsplash.com/photo-1547624643-3bf761b09502?w=400&q=80',
            'link': 'https://www.uniqlo.com/us/en/products/E420529-000/',
            'brand': 'Uniqlo',
            'tag': 'Best Seller',
        },
        {
            'name': 'The North Face ThermoBall Parka',
            'price': '$229.00',
            'image': 'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=400&q=80',
            'link': 'https://www.thenorthface.com/',
            'brand': 'The North Face',
            'tag': 'Top Rated',
        },
        {
            'name': 'Columbia Fleece Thermal Sweater',
            'price': '$89.95',
            'image': 'https://images.unsplash.com/photo-1578681994506-b8f463449011?w=400&q=80',
            'link': 'https://www.columbia.com/',
            'brand': 'Columbia',
            'tag': 'Warm & Cozy',
        },
    ],
    'cold': [
        {
            'name': 'Patagonia Nano Puff Jacket',
            'price': '$249.00',
            'image': 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400&q=80',
            'link': 'https://www.patagonia.com/',
            'brand': 'Patagonia',
            'tag': 'Eco-Friendly',
        },
        {
            'name': 'Arc\'teryx Atom LT Hoody',
            'price': '$259.00',
            'image': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400&q=80',
            'link': 'https://arcteryx.com/',
            'brand': 'Arc\'teryx',
            'tag': 'Premium',
        },
        {
            'name': 'Levi\'s Classic Wool Coat',
            'price': '$119.99',
            'image': 'https://images.unsplash.com/photo-1544022613-e87ca75a784a?w=400&q=80',
            'link': 'https://www.levi.com/',
            'brand': 'Levi\'s',
            'tag': 'Classic',
        },
    ],
    'light_cold': [
        {
            'name': 'Zara Light Windbreaker Jacket',
            'price': '$59.90',
            'image': 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400&q=80',
            'link': 'https://www.zara.com/',
            'brand': 'Zara',
            'tag': 'Trendy',
        },
        {
            'name': 'H&M Knit Zip-Through Hoodie',
            'price': '$34.99',
            'image': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80',
            'link': 'https://www2.hm.com/',
            'brand': 'H&M',
            'tag': 'Great Value',
        },
        {
            'name': 'Nike Sportswear Club Fleece',
            'price': '$65.00',
            'image': 'https://images.unsplash.com/photo-1612478236264-5b6a3abd7b0c?w=400&q=80',
            'link': 'https://www.nike.com/',
            'brand': 'Nike',
            'tag': 'Athletic',
        },
    ],
    'mild': [
        {
            'name': 'Linen Button-Down Shirt',
            'price': '$45.00',
            'image': 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=400&q=80',
            'link': 'https://www.gap.com/',
            'brand': 'GAP',
            'tag': 'Breathable',
        },
        {
            'name': 'Classic Chino Trousers',
            'price': '$55.00',
            'image': 'https://images.unsplash.com/photo-1584370848010-d7fe6bc767ec?w=400&q=80',
            'link': 'https://www.uniqlo.com/',
            'brand': 'Uniqlo',
            'tag': 'Versatile',
        },
        {
            'name': 'Premium Cotton Polo Shirt',
            'price': '$39.99',
            'image': 'https://images.unsplash.com/photo-1620012253295-c15cc3e65df4?w=400&q=80',
            'link': 'https://www.lacoste.com/',
            'brand': 'Lacoste',
            'tag': 'Smart Casual',
        },
    ],
    'warm': [
        {
            'name': 'Breathable Cotton T-Shirt',
            'price': '$24.99',
            'image': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=80',
            'link': 'https://www.hm.com/',
            'brand': 'H&M',
            'tag': 'Everyday',
        },
        {
            'name': 'Slim Fit Summer Shorts',
            'price': '$34.99',
            'image': 'https://images.unsplash.com/photo-1591195853828-11db59a44f43?w=400&q=80',
            'link': 'https://www.uniqlo.com/',
            'brand': 'Uniqlo',
            'tag': 'Light Weight',
        },
        {
            'name': 'Adidas Running Sneakers',
            'price': '$89.99',
            'image': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80',
            'link': 'https://www.adidas.com/',
            'brand': 'Adidas',
            'tag': 'Comfort',
        },
    ],
    'summer': [
        {
            'name': 'UPF 50 Sun Hat',
            'price': '$29.95',
            'image': 'https://images.unsplash.com/photo-1514327605112-b887c0e61c0a?w=400&q=80',
            'link': 'https://www.patagonia.com/',
            'brand': 'Patagonia',
            'tag': 'UV Protection',
        },
        {
            'name': 'Linen Shorts - Quick Dry',
            'price': '$39.00',
            'image': 'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=400&q=80',
            'link': 'https://www.gap.com/',
            'brand': 'GAP',
            'tag': 'Summer Essential',
        },
        {
            'name': 'Lightweight Sandals',
            'price': '$49.95',
            'image': 'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=400&q=80',
            'link': 'https://www.birkenstock.com/',
            'brand': 'Birkenstock',
            'tag': 'Iconic',
        },
    ],
}


def _category_from_clothing(clothing_primary: str, temp: float) -> str:
    """Map clothing recommendation to product category key."""
    p = clothing_primary.lower()
    if 'thermal' in p or ('heavy' in p and 'jacket' in p and temp < 5):
        return 'heavy_cold'
    if 'heavy jacket' in p:
        return 'cold'
    if 'light jacket' in p:
        return 'light_cold'
    if 'sleeve' in p or 'chino' in p:
        return 'mild'
    if 't-shirt' in p or 'jeans' in p:
        return 'warm'
    if 'cotton' in p or 'summer' in p or 'linen' in p:
        return 'summer'
    return 'mild'


def get_outfit_products(clothing_primary: str, temp: float) -> list:
    """
    Return list of outfit product suggestions.
    Attempts live DuckDuckGo scrape; falls back to curated data.
    """
    cat_key = _category_from_clothing(clothing_primary, temp)
    products = FALLBACK_PRODUCTS.get(cat_key, FALLBACK_PRODUCTS['mild'])

    # Attempt to enrich with live data
    try:
        scraped = _scrape_fashion_products(clothing_primary)
        if scraped:
            return scraped[:3]
    except Exception as e:
        logger.debug(f"Live scraping failed, using fallback: {e}")

    return products[:3]


def _scrape_fashion_products(query: str) -> list:
    """
    Scrape DuckDuckGo for shopping results.
    Returns list of product dicts.
    """
    search_url = 'https://duckduckgo.com/html/'
    params = {'q': f'{query} buy online', 'ia': 'shopping'}

    resp = requests.get(
        search_url,
        params=params,
        headers={**Config.HEADERS, 'Referer': 'https://duckduckgo.com/'},
        timeout=8,
    )
    if not resp or resp.status_code != 200:
        return []

    soup = BeautifulSoup(resp.text, 'lxml')
    results = []

    for item in soup.select('.result__body')[:5]:
        title_el = item.select_one('.result__title')
        snippet_el = item.select_one('.result__snippet')
        link_el = item.select_one('.result__url')

        if not title_el:
            continue

        title = title_el.get_text(strip=True)
        snippet = snippet_el.get_text(strip=True) if snippet_el else ''
        link = link_el.get_text(strip=True) if link_el else '#'

        # Extract price from snippet
        price_match = re.search(r'\$[\d,]+\.?\d*', snippet)
        price = price_match.group(0) if price_match else 'Check Price'

        if not link.startswith('http'):
            link = 'https://' + link

        results.append({
            'name': title[:60],
            'price': price,
            'image': f'https://source.unsplash.com/400x300/?{query.replace(" ", ",")}',
            'link': link,
            'brand': 'Online Store',
            'tag': 'New Arrival',
        })

    return results
