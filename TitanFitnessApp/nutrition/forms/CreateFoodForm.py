from django import forms

from nutrition.models import Food


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
        if not name or not name.strip():
            raise forms.ValidationError("Name cannot be empty")
        return name.strip()

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is None or quantity <= 0.0:
            raise forms.ValidationError("Quantity cannot be negative")
        return quantity

    def clean_protein(self):
        protein = self.cleaned_data.get('protein')
        if protein is None or protein <= 0.0:
            raise forms.ValidationError("Protein must be greater than 0")
        return protein

    def clean_carbohydrates(self):
        carbohydrates = self.cleaned_data.get('carbohydrates')
        if carbohydrates is None or carbohydrates <= 0.0:
            raise forms.ValidationError("Carbohydrates must be greater than 0")
        return carbohydrates

    def clean_fat(self):
        fat = self.cleaned_data.get('fat')
        if fat is None or fat <= 0.0:
            raise forms.ValidationError("Fats must be greater than 0")
        return fat
