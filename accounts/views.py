from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth import authenticate, login, update_session_auth_hash

from .forms import (
    CustomUserCreationForm, EditAccountForm, CustomPasswordResetForm
)
from .models import PasswordReset


@login_required
def dashboard(request):
    """Displays the dashboard with courses of the user and some config options."""
    context = {}
    return render(request, 'accounts/dashboard.html', context)


@login_required
def edit(request):
    """Edits the account."""
    if request.method != 'POST':
        form = EditAccountForm(instance=request.user)
    else:
        form = EditAccountForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Suas informações foram atualizadas.')

    context = {'form': form}
    return render(request, 'accounts/edit.html', context)


@login_required
def edit_password(request):
    """Edits the password."""
    if request.method != 'POST':
        form = PasswordChangeForm(request.user)
    else:
        form = PasswordChangeForm(request.user, data=request.POST)
        if form.is_valid():
            form.save()
            # Re-auth the user.
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Sua senha foi alterada com sucesso!')
    
    context = {'form': form}
    return render(request, 'accounts/edit_password.html', context)


def password_reset(request):
    """Displays a form for entering the e-mail for reset the password."""
    if request.method != 'POST':
        form = CustomPasswordResetForm()
    else:
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            form.save(request)
            messages.info(request, 'Enviamos um e-mail para você criar uma nova senha.')
            form = CustomPasswordResetForm()

    context = {'form': form}
    return render(request, 'accounts/password_reset.html', context)


def password_reset_confirm(request, token):
    """Displays a form for entering a new password."""
    reset = get_object_or_404(PasswordReset, token=token, confirmed=False)

    if request.method != 'POST':
        form = SetPasswordForm(reset.user)
    else:
        form = SetPasswordForm(reset.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sua senha foi alterada com sucesso!')
            # Invalidates the token.
            reset.confirm()
            return redirect('accounts:login')
    
    context = {
        'form': form,
        'reset': reset,
    }
    return render(request, 'accounts/password_reset_confirm.html', context)


def register(request):
    """Registers a new user."""
    if request.method != 'POST':
        form = CustomUserCreationForm()
    else:
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(
                request,
                username=form.cleaned_data['username'], 
                password=form.cleaned_data['password1'],
            )
            login(request, user)
            messages.info(request, 'Sua conta foi criada com sucesso, boas vindas!')
            return redirect('core:home')

    context = {'form': form}
    return render(request, 'accounts/register.html', context)