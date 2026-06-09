from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-5 py-4 rounded-2xl text-white placeholder-zinc-500 focus:outline-none',
                'placeholder': 'Choose a username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-5 py-4 rounded-2xl text-white placeholder-zinc-500 focus:outline-none',
                'placeholder': 'your@email.com'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'w-full px-5 py-4 rounded-2xl text-white placeholder-zinc-500 focus:outline-none',
                'placeholder': 'Create strong password'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'w-full px-5 py-4 rounded-2xl text-white placeholder-zinc-500 focus:outline-none',
                'placeholder': 'Confirm password'
            }),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['profile_pic', 'bio']