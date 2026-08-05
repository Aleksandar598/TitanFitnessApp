from django import forms

from nutrition.models import Food
from users.models import CustomUser


class CreateFoodForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = ('name',
                  'description',
                  'quantity',
                  'quantity_type',
                  'protein',
                  'carbohydrates',
                  'fat',
                    )

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Food.objects.filter(name=name).exists():
            raise forms.ValidationError("Food already exists")
        return name

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is None or quantity <= 0.0:
            raise forms.ValidationError("Quantity cannot be negative")


