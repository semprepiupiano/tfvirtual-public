from django import forms
from .models import SignUp
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from crispy_forms.bootstrap import AppendedText

class SignUpForm(forms.Form):
    performer = forms.CharField(max_length=100)
    parent_email = forms.EmailField(label='Parent Email')
    performer_email = forms.EmailField(label='Performer Email', required=False)
    instrument = forms.CharField(max_length=50)
    piece = forms.CharField(max_length=100)
    composer = forms.CharField(max_length=100)
    minutes = forms.IntegerField(min_value=2, max_value=6, label='')
    #seconds = forms.IntegerField(min_value=0, max_value=59, label='')

class LoginForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    whoami_choices = (
        ("performer", "Performer"),
        ("parent", "Parent"),
        ("other", "Other"),
    )
    whoami = forms.ChoiceField(label="I am a...", choices = whoami_choices)
    subject_choices = (
        ("General Inquiry", "General inquiry"),
        ("Password Request", "Password request"),
        ("Signup Cancellation", "Signup cancellation"),
        ("Website Error", "Website error"),
        ("Other", "Other"),
    )
    subject = forms.ChoiceField(label="Subject", choices=subject_choices)
    questions = forms.CharField(label="What's up?", widget=forms.Textarea)