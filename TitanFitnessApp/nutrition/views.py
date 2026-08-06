from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from nutrition.forms.CreateFoodForm import CreateFoodForm

@login_required
def nutrition_view(request):
    return render(request,'nutrition/nutrition.html')

@login_required
def create_food_view(request):
    if request.method == 'POST':
        food_form = CreateFoodForm(request.POST)
        if food_form.is_valid():
            food = food_form.save(commit=False)
            food.user = request.user
            food.save()
            return redirect('nutrition')
    else :
        food_form = CreateFoodForm()
    return render(request,'nutrition/create_food.html', {'form' : food_form})