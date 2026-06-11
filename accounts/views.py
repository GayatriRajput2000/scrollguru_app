from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, ProfileUpdateForm
from users.models import BetaCode


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        beta_code_input = request.POST.get('beta_code', '').strip().upper()

        if form.is_valid() and beta_code_input:

            beta = BetaCode.objects.filter(
                code=beta_code_input,
                is_used=False
            ).first()

            if not beta:
                messages.error(request, "Invalid or already used Beta Code")
                return render(request, 'accounts/signup.html', {'form': form})

            user = form.save()

            if hasattr(user, 'is_beta_user'):
                user.is_beta_user = True

            if hasattr(user, 'beta_code_used'):
                user.beta_code_used = beta_code_input

            user.save()

            # beta.is_used = True

            if hasattr(beta, 'used_by'):
                beta.used_by = user

            beta.save()

            login(request, user)
            print(f"New user signed up: {user.username} (Beta Code: {beta_code_input})")  # Debugging line
            print(request.POST)  # Debugging line to see all form data
            messages.success(
                request,
                "🎉 Welcome to ScrollGuru Beta! Account created successfully."
            )
            return redirect('home')

        else:
            print("Form errors:", form.errors)
            print("Beta code input:", beta_code_input)

            if not beta_code_input:
                messages.error(request, "Beta Access Code is required!")
            else:
                messages.error(request, "Please correct the errors below.")

            return render(request, 'accounts/signup.html', {'form': form})

    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/signup.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")
    
    return render(request, 'accounts/login.html')


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully! ✅")
            return redirect('profile')   # ← Redirect back to profile
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')


def redirect_to_login(request):
    if request.user.is_authenticated:
        return redirect('home')      # Logged in user ko home bhej do
    return redirect('login')         # Anonymous user ko login page pe bhej do
