from django.contrib.auth import login
from django.shortcuts import render, redirect

from users.forms import CreateUserForm


# Create your views here.

def register_view(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CreateUserForm()

    return render(request, 'users/register.html', {'form': form})

