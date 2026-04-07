from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistrationForm(UserCreationForm):
    email = forms.CharField(
        max_length=100,
        required=True,
        label="Email",
        # widget = forms.TextInput(attrs={'placeholder': 'Enter your email'})
        )
    
    mobileno = forms.CharField(
        max_length=10,
        required=True,
        label="Mobile No.",
        # widget = forms.TextInput(attrs={'placeholder': 'Enter your Mobile Number'})
        )
    
    first_name = forms.CharField(
        max_length=100,
        required=True,
        label="Name",
        # widget = forms.TextInput(attrs={'placeholder': 'Enter your Name'})
        )

    class Meta:
        model = User
        fields = fields = ('username', 'first_name', 'email', 'mobileno', 'password1', 'password2')

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)