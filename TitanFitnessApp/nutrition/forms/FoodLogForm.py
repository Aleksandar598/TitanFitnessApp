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
