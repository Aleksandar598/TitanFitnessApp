from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

# Create your models here.
class Food(models.Model):
    QUANTITY_TYPES = [
        ('g', 'Grams'),
        ('ml', 'Milliliters'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='custom_foods',
        null=True
    )
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    quantity = models.FloatField(validators=[MinValueValidator(0.0)])
    quantity_type = models.CharField(
        max_length=2,
        choices=QUANTITY_TYPES,
        default='g'
    )
    protein = models.FloatField(validators=[MinValueValidator(0.0)])
    carbohydrates = models.FloatField(validators=[MinValueValidator(0.0)])
    fat = models.FloatField(validators=[MinValueValidator(0.0)])
    calories = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)

    def __str__(self):
        return f"{self.name} {self.quantity}"

    def calculate_calories(self):
        return round(self.protein * 4 + self.carbohydrates * 4 + self.fat * 9)

    def clean(self):
        super().clean()
        macros = (self.protein, self.carbohydrates, self.fat)

        if None not in macros:
            if self.calories is None:
                self.calories = self.calculate_calories()

        total_macro_weight = (self.protein or 0) + (self.carbohydrates or 0) + (self.fat or 0)

        if self.quantity_type == 'g' and self.quantity is not None:
            if total_macro_weight > self.quantity:
                raise ValidationError(
                    f"Combined macronutrients ({total_macro_weight:.1f}g) cannot exceed total serving quantity ({self.quantity}g)."
                )