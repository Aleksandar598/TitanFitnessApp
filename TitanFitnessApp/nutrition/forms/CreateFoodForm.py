from django import forms

from nutrition.models import Food


class CreateFoodForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

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
        name = name.strip()
        if self.user and Food.objects.filter(user=self.user, name__iexact=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("You already have a saved food with this name")
        return name

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is None or quantity <= 0.0:
            raise forms.ValidationError("Quantity cannot be negative")
        return quantity

    def clean_protein(self):
        protein = self.cleaned_data.get('protein')
        if protein is None or protein < 0.0:
            raise forms.ValidationError("Protein cannot be negative")
        return protein

    def clean_carbohydrates(self):
        carbohydrates = self.cleaned_data.get('carbohydrates')
        if carbohydrates is None or carbohydrates < 0.0:
            raise forms.ValidationError("Carbohydrates cannot be negative")
        return carbohydrates

    def clean_fat(self):
        fat = self.cleaned_data.get('fat')
        if fat is None or fat < 0.0:
            raise forms.ValidationError("Fats cannot be negative")
        return fat

    def save(self, commit=True):
        food = super().save(commit=False)
        # Calories are derived from the current macro values, including edits.
        food.calories = None
        food.full_clean()
        if commit:
            food.save()
        return food
