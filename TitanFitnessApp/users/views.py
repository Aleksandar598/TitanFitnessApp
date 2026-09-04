from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils import timezone

from users.forms.LoginUserForm import LoginUserForm
from users.forms.CreateUserForm import CreateUserForm
from users.forms.UserSettingsForm import UserSettingsForm
from users.models import WeightLog


# Create your views here.
def unregistered_menu_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return render(request, 'users/unregistered_menu.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CreateUserForm()

    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginUserForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'You are now logged in')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid Credentials')
    else:
        form = LoginUserForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def settings_view(request):
    if request.method == 'POST':
        form = UserSettingsForm(
            request.POST,
            instance=request.user,
        )

        if form.is_valid():
            with transaction.atomic():
                updated_user = form.save()

                WeightLog.objects.update_or_create(
                    user=updated_user,
                    date=timezone.localdate(),
                    defaults={
                        'weight': updated_user.current_weight,
                    },
                )

            messages.success(
                request,
                'Your settings have been updated.',
            )
            return redirect('settings')
    else:
        form = UserSettingsForm(instance=request.user)

    return render(request, 'users/settings.html', {
        'form': form,
    })


@login_required
def logout_view(request):
    if request.user.is_authenticated and request.method == 'POST':
        logout(request)
        return redirect('home')
    else :
        return render(request, 'users/unregistered_menu.html')
