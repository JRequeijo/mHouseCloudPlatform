from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField, \
    PasswordResetForm, SetPasswordForm
from django.utils.translation import ugettext, ugettext_lazy as _

from webapp.models import User


class RegisterUserForm(UserCreationForm):

    email = forms.CharField(
        label=_("Email Address"),
        strip=False,
        widget=forms.TextInput(attrs={'class':'form-control'}),
    )

    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class':'form-control'}),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'class':'form-control'}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email',)

class LoginForm(AuthenticationForm):
    username = UsernameField(
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': '', 'class':'form-control'}),
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class':'form-control'}),
    )

class PassRecverForm(PasswordResetForm):
    email = forms.EmailField(label=_("Email"), max_length=254,
                             widget=forms.TextInput(attrs={'autofocus':'', 'class':'form-control'}))

class NewPassSetForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'autofocus':'', 'class':'form-control'}),
        strip=False,
        help_text=password_validation.password_validators_help_texts(),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autofocus':'', 'class':'form-control'}),
    )
    