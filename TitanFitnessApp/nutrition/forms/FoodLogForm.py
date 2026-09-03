from django import forms
from django.utils import timezone

from nutrition.models import Food, FoodLog


class FoodLogForm(forms.ModelForm):
    class Meta:
        model = FoodLog
        fields = ('food', 'quantity', 'date')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'quantity': forms.NumberInput(attrs={'min': '0.01', 'step': '0.01'}),
        }

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['food'].queryset = Food.objects.filter(user=user).order_by('name')
        self.fields['date'].initial = self.initial.get('date', timezone.localdate())

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity <= 0:
            raise forms.ValidationError('Quantity must be greater than 0.')
        return quantity


class USDAFoodLogForm(forms.Form):
    fdc_id = forms.IntegerField(widget=forms.HiddenInput)
    quantity = forms.FloatField(min_value=0.01, widget=forms.NumberInput(attrs={'min': '0.01', 'step': '0.01'}))
    date = forms.DateField(initial=timezone.localdate, widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, search_results, **kwargs):
        super().__init__(*args, **kwargs)
        self.search_results = {str(food['fdc_id']): food for food in search_results if food.get('fdc_id') is not None}

    def clean_fdc_id(self):
        fdc_id = self.cleaned_data['fdc_id']
        try:
            self.selected_food = self.search_results[str(fdc_id)]
        except KeyError:
            raise forms.ValidationError('This USDA search result is no longer available. Search again.')
        return fdc_id

    def clean(self):
        cleaned_data = super().clean()
        if not hasattr(self, 'selected_food'):
            return cleaned_data

        food = self.selected_food
        reference_quantity = food.get('quantity')
        quantity_type = (food.get('quantity_type') or '').lower()
        if not reference_quantity or reference_quantity <= 0 or quantity_type not in ('g', 'ml'):
            raise forms.ValidationError('USDA did not provide a usable 100 g/ml reference quantity for this food.')
        if any(food.get(nutrient) is None for nutrient in ('calories', 'protein', 'carbohydrates', 'fat')):
            raise forms.ValidationError('USDA did not provide complete nutrition information for this food.')
        return cleaned_data


class USDASaveFoodForm(forms.Form):
    fdc_id = forms.IntegerField(widget=forms.HiddenInput)

    def __init__(self, *args, search_results, **kwargs):
        super().__init__(*args, **kwargs)
        self.search_results = {str(food['fdc_id']): food for food in search_results if food.get('fdc_id') is not None}

    def clean_fdc_id(self):
        fdc_id = self.cleaned_data['fdc_id']
        try:
            self.selected_food = self.search_results[str(fdc_id)]
        except KeyError:
            raise forms.ValidationError('This USDA search result is no longer available. Search again.')
        return fdc_id

    def clean(self):
        cleaned_data = super().clean()
        if hasattr(self, 'selected_food') and any(
            self.selected_food.get(nutrient) is None
            for nutrient in ('calories', 'protein', 'carbohydrates', 'fat')
        ):
            raise forms.ValidationError('USDA did not provide complete nutrition information for this food.')
        return cleaned_data
