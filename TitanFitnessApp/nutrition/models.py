from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

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
    name = models.CharField(max_length=200)
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
        return self.name

    def calculate_calories(self):
        return round(self.protein * 4 + self.carbohydrates * 4 + self.fat * 9)

    def clean(self):
        super().clean()
        if self.quantity is not None and self.quantity <= 0:
            raise ValidationError({'quantity': 'Serving quantity must be greater than 0.'})

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

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='unique_food_name_per_user'),
        ]


class FoodLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    food = models.ForeignKey(Food, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.FloatField(validators=[MinValueValidator(0.0)])
    date = models.DateField(default=timezone.localdate)
    food_name = models.CharField(max_length=200, editable=False)
    quantity_type = models.CharField(max_length=2, choices=Food.QUANTITY_TYPES, editable=False)
    calories = models.FloatField(editable=False)
    protein = models.FloatField(editable=False)
    carbohydrates = models.FloatField(editable=False)
    fat = models.FloatField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.food_name} {self.quantity}{self.quantity_type} on {self.date}"

    def capture_food_snapshot(self):
        if not self.food_id:
            raise ValidationError('A food is required to create a food log.')
        if self.food.quantity <= 0:
            raise ValidationError('The food serving quantity must be greater than 0.')

        multiplier = self.quantity / self.food.quantity
        self.food_name = self.food.name
        self.quantity_type = self.food.quantity_type
        self.calories = round(self.food.calories * multiplier, 2)
        self.protein = round(self.food.protein * multiplier, 2)
        self.carbohydrates = round(self.food.carbohydrates * multiplier, 2)
        self.fat = round(self.food.fat * multiplier, 2)

    def save(self, *args, **kwargs):
        if self._state.adding and self.food_id and not self.food_name:
            self.capture_food_snapshot()
        super().save(*args, **kwargs)
