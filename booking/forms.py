from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Complaint, Review, UserProfile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"placeholder": "example@gmail.com"}))
    first_name = forms.CharField(max_length=80, widget=forms.TextInput(attrs={"placeholder": "First name"}))
    last_name = forms.CharField(max_length=80, required=False, widget=forms.TextInput(attrs={"placeholder": "Last name"}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={"placeholder": "Mobile number"}))

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "phone", "password1", "password2"]
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Choose a username"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data.get("last_name", "")
        if commit:
            user.save()
            UserProfile.objects.create(user=user, phone=self.cleaned_data["phone"])
        return user


class SearchForm(forms.Form):
    source = forms.CharField(max_length=100)
    destination = forms.CharField(max_length=100)
    travel_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["phone", "gender", "preferred_language", "favorite_routes"]
        widgets = {"favorite_routes": forms.CheckboxSelectMultiple}


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["booking", "subject", "message"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["booking"].queryset = user.bookings.all()
        self.fields["booking"].required = False
