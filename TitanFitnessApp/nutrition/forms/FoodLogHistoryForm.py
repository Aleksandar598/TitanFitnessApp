from django import forms
from django.utils import timezone


class FoodLogHistoryForm(forms.Form):
    date = forms.DateField(
        initial=timezone.localdate,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
