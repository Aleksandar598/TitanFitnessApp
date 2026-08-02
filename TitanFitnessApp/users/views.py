from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from users.forms.LoginUserForm import LoginUserForm
from users.forms.CreateUserForm import CreateUserForm


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
def dashboard_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    context = {'username' : request.user.username}
    return render(request, 'users/dashboard.html', context=context)

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')