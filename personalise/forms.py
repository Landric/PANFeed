from django.forms import ModelForm, HiddenInput
from models import Digest, Issue

class DigestForm(ModelForm):
    class Meta:
       model = Digest
       exclude = ('owner')
       required_css_class = 'error'

class IssueForm(ModelForm):
    class Meta:
        model = Issue
