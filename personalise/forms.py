from django.forms import ModelForm, HiddenInput, RadioSelect, ChoiceField
from models import Issue

class IssueForm(ModelForm):
    public = ChoiceField(label='Visibility', widget=RadioSelect(), choices=[['1','Public - anyone can view your Issue'],['0','Private - only you can view your Issue']] )
    
    class Meta:
        model = Issue
	exclude = ('owner', 'toplevel')
        fields = ('title', 'description', 'public')
