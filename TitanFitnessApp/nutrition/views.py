from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from nutrition.forms.CreateFoodForm import CreateFoodForm
from nutrition.forms.FoodLogForm import FoodLogForm, USDAFoodLogForm, USDASaveFoodForm
from nutrition.forms.FoodLogHistoryForm import FoodLogHistoryForm
from nutrition.models import Food, FoodLog
from nutrition.services.usda import USDAApiError, search_foods


@login_required
def nutrition_view(request):
    context = _food_log_context(
        request.user,
        timezone.localdate(),
    )

    return render(
        request,
        'nutrition/nutrition.html',
        context,
    )

@login_required
def create_food_view(request):
    if request.method == 'POST':
        food_form = CreateFoodForm(request.POST, user=request.user)
        if food_form.is_valid():
            food = food_form.save(commit=False)
            food.user = request.user
            food.save()
            return redirect('nutrition')
    else :
        food_form = CreateFoodForm(user=request.user)
    return render(request,'nutrition/create_food.html', {'form' : food_form})

@login_required
def saved_view_foods(request):
    foods_list = Food.objects.filter(user=request.user)
    return render(request, "nutrition/saved_foods.html", {"foods": foods_list})


@login_required
def edit_saved_food_view(request, food_id):
    food = get_object_or_404(Food, id=food_id, user=request.user)
    if request.method == 'POST':
        food_form = CreateFoodForm(request.POST, instance=food, user=request.user)
        if food_form.is_valid():
            food_form.save()
            return redirect('saved_foods')
    else:
        food_form = CreateFoodForm(instance=food, user=request.user)

    return render(request, 'nutrition/create_food.html', {
        'form': food_form,
        'is_edit': True,
    })


@login_required
def create_food_log_view(request):
    action = request.POST.get('action', 'manual') if request.method == 'POST' else None
    search_query = request.GET.get('q', '').strip()
    search_results = request.session.get('usda_search_results', [])
    search_error = None
    if search_query:
        try:
            search_results = search_foods(search_query)
            request.session['usda_search_results'] = search_results
        except (USDAApiError, ValueError) as error:
            search_error = str(error)

    manual_form = FoodLogForm(request.POST if request.method == 'POST' and action == 'manual' else None, user=request.user)
    usda_form = USDAFoodLogForm(
        request.POST if request.method == 'POST' and action == 'usda' else None,
        search_results=search_results,
    )
    usda_save_form = USDASaveFoodForm(
        request.POST if request.method == 'POST' and action == 'save_usda' else None,
        search_results=search_results,
    )

    if request.method == 'POST' and action == 'manual' and manual_form.is_valid():
        food_log = manual_form.save(commit=False)
        food_log.user = request.user
        food_log.save()
        return redirect('nutrition')

    if request.method == 'POST' and action == 'usda' and usda_form.is_valid():
        food = usda_form.selected_food
        multiplier = usda_form.cleaned_data['quantity'] / food['quantity']
        FoodLog.objects.create(
            user=request.user,
            food_name=food['description'],
            quantity=usda_form.cleaned_data['quantity'],
            quantity_type=food['quantity_type'].lower(),
            calories=round(food['calories'] * multiplier, 2),
            protein=round(food['protein'] * multiplier, 2),
            carbohydrates=round(food['carbohydrates'] * multiplier, 2),
            fat=round(food['fat'] * multiplier, 2),
            date=usda_form.cleaned_data['date'],
        )
        return redirect('nutrition')

    if request.method == 'POST' and action == 'save_usda' and usda_save_form.is_valid():
        usda_food = usda_save_form.selected_food
        if Food.objects.filter(user=request.user, name__iexact=usda_food['description']).exists():
            usda_save_form.add_error(None, 'You already have a saved food with this name.')
        else:
            food = Food(
                user=request.user,
                name=usda_food['description'],
                description=f"Imported from USDA FoodData Central (FDC ID: {usda_food['fdc_id']}).",
                quantity=usda_food['quantity'],
                quantity_type=usda_food['quantity_type'],
                calories=usda_food['calories'],
                protein=usda_food['protein'],
                carbohydrates=usda_food['carbohydrates'],
                fat=usda_food['fat'],
            )
            try:
                food.full_clean()
            except ValidationError as error:
                usda_save_form.add_error(None, error)
            else:
                food.save()
                return redirect('saved_foods')

    return render(request, 'nutrition/create_food_log.html', {
        'manual_form': manual_form,
        'usda_form': usda_form,
        'usda_save_form': usda_save_form,
        'has_saved_foods': Food.objects.filter(user=request.user).exists(),
        'search_query': search_query,
        'search_results': search_results,
        'search_error': search_error,
    })


def _food_log_context(user, selected_date):
    logs = FoodLog.objects.filter(user=user, date=selected_date).order_by('created_at')
    totals = {
        'calories': round(sum(log.calories for log in logs), 2),
        'protein': round(sum(log.protein for log in logs), 2),
        'carbohydrates': round(sum(log.carbohydrates for log in logs), 2),
        'fat': round(sum(log.fat for log in logs), 2),
    }
    return {'logs': logs, 'selected_date': selected_date, 'totals': totals}


@login_required
def today_food_log_view(request):
    context = _food_log_context(request.user, timezone.localdate())
    context['title'] = "Today's food log"
    context['show_history_form'] = False
    return render(request, 'nutrition/food_log.html', context)


@login_required
@require_POST
def remove_today_food_log_view(request, log_id):
    food_log = get_object_or_404(
        FoodLog,
        id=log_id,
        user=request.user,
        date=timezone.localdate(),
    )
    food_log.delete()
    return redirect('today_food_log')


@login_required
def food_log_history_view(request):
    history_form = FoodLogHistoryForm(request.GET or None)
    selected_date = timezone.localdate()
    if history_form.is_valid():
        selected_date = history_form.cleaned_data['date']

    context = _food_log_context(request.user, selected_date)
    context.update({
        'title': 'Food log history',
        'show_history_form': True,
        'history_form': history_form,
    })
    return render(request, 'nutrition/food_log.html', context)


@login_required
def remove_saved_food(request, food_id):
    if request.method == "POST":
        food_item = get_object_or_404(Food, id=food_id, user=request.user)
        food_item.delete()

    return redirect("saved_foods")
