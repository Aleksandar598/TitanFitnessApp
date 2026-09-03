

from django.test import TestCase

from nutrition.forms.CreateFoodForm import CreateFoodForm


class CreateFoodTest(TestCase):

    def setUp(self):
        self.food_data = {'name': 'Banana',
                          'description': 'A banana',
                          'quantity': 20,
                          'quantity_type': 'g',
                          'protein': 1,
                          'carbohydrates': 1,
                          'fat': 1,
                          }

    def test_create_food_form_valid(self):
        form = CreateFoodForm(self.food_data)
        self.assertTrue(form.is_valid())

    def test_name_is_valid(self):
        self.food_data['name'] = '     '
        form = CreateFoodForm(self.food_data)
        self.assertFalse(form.is_valid())

    def test_name_correct_clean(self):
        self.food_data['name'] = '    banana    '
        form = CreateFoodForm(self.food_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['name'] , 'banana')

    def test_protein_can_be_zero(self):
        self.food_data['protein'] = 0
        form = CreateFoodForm(self.food_data)
        self.assertTrue(form.is_valid())

    def test_carbohydrates_can_be_zero(self):
        self.food_data['carbohydrates'] = 0
        form = CreateFoodForm(self.food_data)
        self.assertTrue(form.is_valid())

    def test_fat_can_be_zero(self):
        self.food_data['fat']  = 0
        form = CreateFoodForm(self.food_data)
        self.assertTrue(form.is_valid())

    def test_quantity_less_than_0(self):
        self.food_data['quantity'] = 0
        form = CreateFoodForm(self.food_data)
        self.assertFalse(form.is_valid())
