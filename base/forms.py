from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Employee
from django.contrib.auth.password_validation import validate_password

class EmployeeRegisterForm(UserCreationForm):
    email = forms.EmailField(
        label="Adres e-mail",
        required=True,
        error_messages={
            'required': "Adres e-mail jest wymagany.",
            'invalid': "Wprowadź poprawny adres e-mail.",
        }
    )
    first_name = forms.CharField(
        label="Imię",
        max_length=30,
        error_messages={
            'required': "Imię jest wymagane.",
        }
    )
    last_name = forms.CharField(
        label="Nazwisko",
        max_length=30,
        error_messages={
            'required': "Nazwisko jest wymagane.",
        }
    )
    is_admin = forms.BooleanField(
        label="Czy administrator",
        required=False
    )

    password1 = forms.CharField(
        label="Hasło",
        widget=forms.PasswordInput,
        error_messages={
            'required': "Hasło jest wymagane.",
        }
    )

    password2 = forms.CharField(
        label="Potwierdzenie hasła",
        widget=forms.PasswordInput,
        error_messages={
            'required': "Potwierdzenie hasła jest wymagane.",
            'password_mismatch': "Wprowadzone hasła nie są zgodne.",
        }
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']


# Błędy gdy hasło zbyt podobne do imienia lub nazwiska - TODO

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        try:
            validate_password(password, user=self.instance)
            print("Validation1 passed!") 
        except ValidationError as e:
            error_messages = []
            for error in e.error_list:
                print(f"Błąd: {error} - Kod: {error.code}")
                if error.code == 'password_too_short':
                    error_messages.append("Hasło jest zbyt krótkie. Musi zawierać co najmniej 8 znaków.")
                elif error.code == 'password_too_common':
                    error_messages.append("To hasło jest zbyt powszechne.")
                elif error.code == 'password_too_similar_first_name':
                    error_messages.append("Hasło jest zbyt podobne do imienia.")
                else:
                    error_messages.append(str(error))
            raise ValidationError(error_messages)
        return password

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError(("Wprowadzone hasła nie są zgodne."))
        try:
            validate_password(password2)
            print("Validation2 passed!") 
        except ValidationError as e:
            for error in e.error_list:
                print(f"Błąd: {error} - Kod: {error.code}")
                if error.code == 'password_too_short':
                    raise ValidationError(("Hasło jest zbyt krótkie. Musi zawierać co najmniej 8 znaków."))
                elif error.code == 'password_too_common':
                    raise ValidationError(("To hasło jest zbyt powszechne."))
        return password2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'usable_password' in self.fields:
            del self.fields['usable_password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        Employee.objects.create(
            user=user,
            is_admin=self.cleaned_data['is_admin']
        )
        return user


class UploadFileForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        file = self.cleaned_data['file']
        if not file.name.endswith('.xlsx') and not file.name.endswith('.xls'):
            raise forms.ValidationError('Plik musi być w formacie Excel (.xlsx lub .xls)')
        return file