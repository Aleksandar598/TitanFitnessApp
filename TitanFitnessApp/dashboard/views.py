from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone

from nutrition.models import FoodLog
from workout.models import WorkoutSession


@login_required
def dashboard_view(request):
    daily_intake = FoodLog.objects.filter(
        user=request.user,
        date=timezone.localdate(),
    ).aggregate(
        calories=Sum('calories'),
        protein=Sum('protein'),
        carbohydrates=Sum('carbohydrates'),
        fat=Sum('fat'),
    )

    for nutrient, value in daily_intake.items():
        daily_intake[nutrient] = round(value or 0)

    workout_calories_burned = WorkoutSession.objects.filter(
        user=request.user,
        status=WorkoutSession.STATUS_COMPLETED,
        completed_at__date=timezone.localdate(),
    ).aggregate(
        total=Sum('calories_burned'),
    )['total'] or 0

    weight_logs = list(
        request.user.weight_logs.order_by('-date')[:30]
    )
    weight_logs.reverse()

    weight_chart_data = {
        'labels': [
            weight_log.date.isoformat()
            for weight_log in weight_logs
        ],
        'weights': [
            weight_log.weight
            for weight_log in weight_logs
        ],
    }

    return render(request, 'dashboard/dashboard.html', {
        'username': request.user.username,
        'daily_intake': daily_intake,
        'daily_goals': request.user.daily_macronutrient_goals_with_workout(
            workout_calories_burned,
        ),
        'workout_calories_burned': round(workout_calories_burned),
        'weight_chart_data': weight_chart_data,
    })
