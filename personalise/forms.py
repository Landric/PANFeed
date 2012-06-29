from django.forms import ModelForm, HiddenInput
from models import Digest, DigestFeeds, Issue

class DigestForm(ModelForm):
    class Meta:
       model = Digest
       exclude = ('owner')
       fields = ('title', 'public', 'description', 'digestid')
       #widgets = {'digestid' : HiddenInput()}
       

class IssueForm(ModelForm):
    class Meta:
        model = Issue
