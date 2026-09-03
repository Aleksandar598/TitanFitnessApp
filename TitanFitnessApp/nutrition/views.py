from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from nutrition.forms.CreateFoodForm import CreateFoodForm
from nutrition.forms.FoodLogForm import FoodLogForm
from nutrition.models import Food, FoodLog


@login_required
def nutrition_view(request):
    return render(request,'nutrition/nutrition.html')

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
def create_food_log_view(request):
    if request.method == 'POST':
        form = FoodLogForm(request.POST, user=request.user)
        if form.is_valid():
            food_log = form.save(commit=False)
            food_log.user = request.user
            food_log.save()
            return redirect('nutrition')
    else:
        form = FoodLogForm(user=request.user)

    return render(request, 'nutrition/create_food_log.html', {
        'form': form,
        'has_saved_foods': Food.objects.filter(user=request.user).exists(),
    })


@login_required
def remove_saved_food(request, food_id):
    if request.method == "POST":
        food_item = get_object_or_404(Food, id=food_id, user=request.user)
        food_item.delete()

    return redirect("saved_foods")
