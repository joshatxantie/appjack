from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.views import LoginView as AuthLoginView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm, ProfileForm, CustomAdminChangeUserForm
from django.urls import reverse
from django.http import HttpResponseRedirect

@user_passes_test(lambda u: u.is_superuser)
def view_all_users(request):
    users = User.objects.all()
    return render(request, 'accounts/users.html', {'users': users})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


class LoginView(AuthLoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been updated!')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)

    context = {'form': form}
    return render(request, 'accounts/edit.html', context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_profile_admin(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = CustomAdminChangeUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("accounts:users"))
    else:
        form = CustomAdminChangeUserForm(instance=user)
    context = {'form': form, 'user_id': user_id}
    return render(request, 'accounts/editUser.html', context)