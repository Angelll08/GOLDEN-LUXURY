from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Usuario


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Usuario o correo'


class RegistroForm(UserCreationForm):
    email = forms.EmailField(label='Correo electrónico', required=True)

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('username', 'first_name', 'email', 'telefono')

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con ese correo.')
        return email
