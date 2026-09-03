
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from django.conf import settings

USDA_SEARCH_URL = 'https://api.nal.usda.gov/fdc/v1/foods/search'


class USDAApiError(Exception):
    """Raised when USDA API fails"""


def search_foods(query, *, page_size=10, api_key=None):
    query = query.strip() if isinstance(query, str) else ''
    if not query:
        raise ValueError('A food search query is required.')
    if not 1 <= page_size <= 200:
        raise ValueError('page_size must be between 1 and 200.')

    api_key = api_key or settings.USDA_FDC_API_KEY
    if not api_key:
        raise USDAApiError('USDA_FDC_API_KEY is not configured.')

    url = f'{USDA_SEARCH_URL}?{urlencode({"api_key": api_key, "query": query, "pageSize": page_size})}'
    try:
        with urlopen(url, timeout=10) as response:
            payload = json.loads(response.read().decode('utf-8'))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise USDAApiError('Unable to retrieve food data from USDA.') from error

    return [_normalise_food(food) for food in payload.get('foods', [])]


def _normalise_food(food):
    nutrients = food.get('foodNutrients', [])
    return {
        'fdc_id': food.get('fdcId'),
        'description': food.get('description', ''),
        'data_type': food.get('dataType', ''),
        'brand_owner': food.get('brandOwner', ''),
        'serving_size': food.get('servingSize'),
        'serving_size_unit': food.get('servingSizeUnit', ''),
        'calories': _nutrient_value(nutrients, names=('Energy',), numbers=('208',)),
        'protein': _nutrient_value(nutrients, names=('Protein',), numbers=('203',)),
        'carbohydrates': _nutrient_value(
            nutrients,
            names=('Carbohydrate, by difference',),
            numbers=('205',),
        ),
        'fat': _nutrient_value(nutrients, names=('Total lipid (fat)',), numbers=('204',)),
    }


def _nutrient_value(nutrients, *, names, numbers):
    for nutrient in nutrients:
        if nutrient.get('nutrientName') in names or str(nutrient.get('nutrientNumber')) in numbers:
            return nutrient.get('value')
    return None
