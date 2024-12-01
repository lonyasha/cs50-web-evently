from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.shortcuts import render, redirect
from ..forms import RegistrationForm, LoginForm, CustomPasswordResetForm, CustomSetPasswordForm


def login_view(request):
    """
    Handle user login. If the user is already authenticated, redirect to index.
    """
    if request.user.is_authenticated:
        return redirect("index")

    form = LoginForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect("index")
            else:
                messages.error(request, 'Invalid username or password.')

    return render(request, "registration/login.html", {"form": form})

class CustomPasswordResetView(PasswordResetView):
    """
    Custom view for password reset, using a custom form.
    """
    form_class = CustomPasswordResetForm
    template_name = "accounts/password_reset.html"
    success_url = reverse_lazy("password_reset_done")

class CustomPasswordResetDoneView(PasswordResetDoneView):
    """
    Custom view for password reset done page.
    """
    template_name = "accounts/password_reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Custom view for password reset confirmation page.
    """
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("password_reset_complete")
    form_class = CustomSetPasswordForm


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """
    Custom view for password reset complete page.
    """
    template_name = "accounts/password_reset_complete.html"

@login_required
def logout_view(request):
    """
    Handle user logout and redirect to the login page.
    """
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("index")

def register(request):
    """
    Handle user registration and redirect to the index page if successful.
    """
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Registration successful! You are now logged in.')
        return redirect("index")

    return render(request, 'registration/register.html', {'form': form})