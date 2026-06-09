from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, ProfileUpdateForm


from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserCreationForm
from users.models import BetaCode   # ← Yeh line add karo

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        beta_code_input = request.POST.get('beta_code', '').strip().upper()

        if form.is_valid():
            if not beta_code_input:
                messages.error(request, "Beta Access Code is required for registration!")
                return render(request, 'accounts/signup.html', {'form': form})

            try:
                beta = BetaCode.objects.get(code=beta_code_input, is_used=False)
                
                user = form.save()
                user.is_beta_user = True
                user.beta_code_used = beta_code_input
                user.save()

                # Mark code as used
                beta.is_used = True
                beta.used_by = user
                beta.save()

                login(request, user)
                messages.success(request, "🎉 Welcome to ScrollGuru Beta! You are one of the first 10 users.")
                return redirect('feed')   # ya 'home'

            except BetaCode.DoesNotExist:
                messages.error(request, "Invalid or already used Beta Code")
                return render(request, 'accounts/signup.html', {'form': form})
        else:
            messages.error(request, "Please correct the errors below")
    
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/signup.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        print("Username:", username)  # Debugging line
        password = request.POST['password']
        [print("Password:", password)]  # Debugging line (remove in production!)
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
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
