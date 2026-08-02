from django.core.exceptions import ValidationError
from django.utils import timezone

MINIMUM_WEIGHT = 20
MAXIMUM_WEIGHT = 500
MINIMUM_HEIGHT = 80

def validate_realistic_height(height):
    if height < MINIMUM_HEIGHT:
        raise ValidationError("Height cannot be below 80")

def validate_maximum_weight(weight):
    if weight > MAXIMUM_WEIGHT:
        raise ValidationError("Weight cannot be above 500")

def validate_minimum_weight(weight):
    if weight < MINIMUM_WEIGHT:
        raise ValidationError("Weight cannot be below 20")

def validate_birth_date(birth_date):
    if birth_date and birth_date > timezone.now().date():
        raise ValidationError("Birth Date cannot be in the future")
    return birth_date

def validate_fitness_goal(fitness_goal, current_weight, target_weight):
    if current_weight is None or target_weight is None:
        return fitness_goal

    if fitness_goal == 0:
        if current_weight != target_weight:
            raise ValidationError("Fitness goal must correspond to weight goal")
    if fitness_goal == 250:
        if current_weight >= target_weight:
            raise ValidationError("Fitness goal must correspond to weight goal")
    if fitness_goal == -250:
        if current_weight <= target_weight:
            raise ValidationError("Fitness goal must correspond to weight goal")
    return fitness_goal