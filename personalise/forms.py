from django.forms import ModelForm, HiddenInput, RadioSelect, ChoiceField
from models import Digest, Issue

class DigestForm(ModelForm):
    public = ChoiceField(label='Visibility', widget=RadioSelect(), choices=[['1','Public - anyone can view your Digest'],['0','Private - only you can view your Digest']] )

    class Meta:
       model = Digest
       exclude = ('owner', 'feeds')
       fields = ('title', 'description', 'public')

class IssueForm(ModelForm):
    class Meta:
        model = Issue
