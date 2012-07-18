from django.forms import ModelForm, HiddenInput, RadioSelect, ChoiceField
from models import Feed, FeedIte, SpecialIssue

class FeedForm(ModelForm):
    displayAll = ChoiceField(label='Publishing options', widget=RadioSelect(), choices=[['1','Show all - show all published items and Special Issues'],['0','Show latest - only show the latest published item or Special Issue']], help_text='Don\'t worry, you can change this later if you change your mind')
    
    class Meta:
        model = Feed
	exclude = ('owner')
        fields = ('title', 'description', 'displayAll')

class SpecialIssueForm(ModelForm):
    
    class Meta:
        model = SpecialIssue

class FeedItemForm(ModelForm):
    
    class Meta:
        model = FeedItem
	exclude = ('date', 'feed', 'special_issue', 'issue_position')
