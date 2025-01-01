from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django import forms
from datetime import datetime
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Employee, Question, Choice, LanguageTest, Language
from django.contrib.auth.password_validation import validate_password
from .models import Refugee, LanguageCourse, Semester, Recruitment


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
    

class RefugeeRegistrationForm(forms.ModelForm):
    rodo_consent = forms.BooleanField(
    required=True,
    label="I consent to the processing of my personal data in accordance with GDPR."
    )
    truth_confirmation = forms.BooleanField(
        required=True,
        label="I confirm that the information provided is true and accurate."
    )
    class Meta:
        model = Refugee
        fields = ['first_name', 'last_name', 'gender', 'dob', 'phone_number', 'nationality', 'residency', 'language', 'comments']
        labels = {
            'dob': 'Date of Birth',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'inputmode': 'numeric', 'pattern': '\d*', 'oninput': 'this.value = this.value.replace(/[^0-9]/g, "")'}),
            'nationality': forms.Select(attrs={'class': 'form-control'}),
            'residency': forms.Select(attrs={'class': 'form-control'}),
            'language': forms.Select(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_dob(self):
        dob = self.cleaned_data.get('dob')
        if not dob:
            raise forms.ValidationError("Date of birth is required.")
        try:
            dob_str = dob.strftime("%Y-%m-%d")
            parsed_dob = datetime.strptime(dob_str, "%Y-%m-%d")
        except ValueError:
            raise forms.ValidationError("Invalid date format.")
        if parsed_dob > datetime.now():
            raise forms.ValidationError("Date of birth cannot be in the future.")
        return dob

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        active_recruitment = Recruitment.objects.filter(
            active=True
        ).first()
        
        if active_recruitment:
            available_languages = Language.objects.filter(
                languagetest__in=active_recruitment.language_tests.all()
            ).distinct()
        else:
            available_languages = Language.objects.none()
        self.fields['language'].queryset = available_languages
        self.fields['language'].label = "Select language (available courses)"

class LanguageTestForm(forms.ModelForm):
    class Meta:
        model = LanguageTest
        fields = ['title', 'description', 'language']
        labels = {
            'title': 'Nazwa testu', 
            'description': 'Opis',
            'language': 'Język',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'language': forms.Select(attrs={'class': 'form-control'}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'order']

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']

ChoiceFormSet = inlineformset_factory(
    Question,
    Choice,
    form=ChoiceForm,
    fields=['text', 'is_correct'],
    extra=3,
    can_delete=True
)

class LanguageCourseForm(forms.ModelForm):
    class Meta:
        model = LanguageCourse
        fields = ['name', 'language', 'semesters', 'is_slavic']
        labels = {
            'name': 'Nazwa (PO ANGIELSKU)', 
            'language': 'Język',
            'semesters': 'Semestry',
            'is_slavic': 'Kurs dla osób z krajów słowiańskich',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'language': forms.Select(attrs={'class': 'form-control'}),
            'semesters': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'is_slavic': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        error_messages = {
            'name': {'required': 'To pole jest wymagane.'},
            'language': {'required': 'Musisz wybrać język.'},
            'semesters': {'required': 'Musisz zaznaczyć co najmniej jeden semestr.'},
        }


class LanguageForm(forms.ModelForm):
    class Meta:
        model = Language
        fields = ['name']
        labels = {
            'name': 'Nazwa języka (PO ANGIELSKU)',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dodaj nowy język'}),
        }

class RecruitmentForm(forms.ModelForm):
    language_tests_by_language = {}

    class Meta:
        model = Recruitment
        fields = ['name', 'start_date', 'end_date', 'semester', 'max_people']  # Usuń 'language_tests' z pól
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'max_people': forms.NumberInput(),
            'semester': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        grouped_tests = {}
        for test in LanguageTest.objects.select_related('language'):
            if test.language.name not in grouped_tests:
                grouped_tests[test.language.name] = []
            grouped_tests[test.language.name].append(test)

        self.language_tests_by_language = grouped_tests

        for language, tests in self.language_tests_by_language.items():
            choices = [(test.id, test.title) for test in tests]
            self.fields[f'language_tests_{language}'] = forms.ChoiceField(
                choices=[('', 'Wybierz test')] + choices,
                widget=forms.RadioSelect,
                required=False,
                label=f"Testy dla języka {language}"
            )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date <= start_date:
            raise forms.ValidationError("Data zakończenia rekrutacji musi być późniejsza niż data rozpoczęcia.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        selected_tests = []
        for language, tests in self.language_tests_by_language.items():
            test_field_name = f'language_tests_{language}'
            test_id = self.cleaned_data.get(test_field_name)
            if test_id: 
                selected_tests.append(int(test_id))
        if commit:
            instance.save()
            instance.language_tests.set(selected_tests) 
        return instance
