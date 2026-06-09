from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-5 py-4 bg-zinc-800 border border-zinc-700 rounded-2xl text-white placeholder-zinc-500 focus:outline-none focus:border-green-500',
            'placeholder': 'your@email.com'
        })
    )

    class Meta:
        model = CustomUser
        # Yahan se password1 aur password2 hata diye hain
        fields = ['username', 'email'] 
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-5 py-4 bg-zinc-800 border border-zinc-700 rounded-2xl text-white placeholder-zinc-500 focus:outline-none focus:border-green-500',
                'placeholder': 'Choose a username'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Password fields par Tailwind classes lagane ka sahi tarika
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-5 py-4 bg-zinc-800 border border-zinc-700 rounded-2xl text-white placeholder-zinc-500 focus:outline-none focus:border-green-500',
            'placeholder': 'Create strong password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-5 py-4 bg-zinc-800 border border-zinc-700 rounded-2xl text-white placeholder-zinc-500 focus:outline-none focus:border-green-500',
            'placeholder': 'Confirm password'
        })

    # Yeh function automatically naye user ko Admin approval tak band rakhega
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False  # Account banega par permission nahi hogi
        if commit:
            user.save()
        return user

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['profile_pic', 'bio']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['profile_pic', 'bio']