import json
from unittest.mock import patch

from django.test import SimpleTestCase
from django.test.utils import override_settings

from nutrition.services.usda import USDAApiError, search_foods


class FakeHttpResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return json.dumps(self.payload).encode('utf-8')


class USDASearchFoodsTest(SimpleTestCase):
    @patch('nutrition.services.usda.urlopen')
    def test_search_foods_normalises_usda_response_without_a_real_api_call(self, mock_urlopen):
        mock_urlopen.return_value = FakeHttpResponse({
            'foods': [{
                'fdcId': 123,
                'description': 'Cheddar cheese',
                'dataType': 'Branded',
                'brandOwner': 'Example Foods',
                'servingSize': 28,
                'servingSizeUnit': 'g',
                'foodNutrients': [
                    {'nutrientName': 'Energy', 'nutrientNumber': '208', 'value': 403},
                    {'nutrientName': 'Protein', 'nutrientNumber': '203', 'value': 25.1},
                    {'nutrientName': 'Carbohydrate, by difference', 'nutrientNumber': '205', 'value': 1.3},
                    {'nutrientName': 'Total lipid (fat)', 'nutrientNumber': '204', 'value': 33.1},
                ],
            }],
        })

        foods = search_foods('cheddar cheese', page_size=5, api_key='test-key')

        self.assertEqual(foods, [{
            'fdc_id': 123,
            'description': 'Cheddar cheese',
            'data_type': 'Branded',
            'brand_owner': 'Example Foods',
            'quantity': 100,
            'quantity_type': 'g',
            'calories': 403,
            'protein': 25.1,
            'carbohydrates': 1.3,
            'fat': 33.1,
        }])
        self.assertIn('api_key=test-key', mock_urlopen.call_args.args[0])
        self.assertIn('query=cheddar+cheese', mock_urlopen.call_args.args[0])

    @patch('nutrition.services.usda.urlopen')
    def test_empty_query_is_rejected_without_an_http_request(self, mock_urlopen):
        with self.assertRaisesMessage(ValueError, 'A food search query is required.'):
            search_foods('   ', api_key='test-key')

        mock_urlopen.assert_not_called()

    @override_settings(USDA_FDC_API_KEY='')
    def test_missing_api_key_is_reported_before_an_http_request(self):
        with self.assertRaisesMessage(USDAApiError, 'USDA_FDC_API_KEY is not configured.'):
            search_foods('banana', api_key='')
