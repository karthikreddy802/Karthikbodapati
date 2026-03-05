from email import message
from django import forms
from django.contrib.auth.models import User
from food.models import Feedback


class RegistrationForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['username', 'password']

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'rating', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'rating': forms.Select(attrs={'class': 'form-control'}),
        }