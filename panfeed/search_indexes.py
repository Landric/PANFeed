from haystack import indexes
from panfeed.models import Corpus

class CorpusIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    url = indexes.CharField(model_attr='url')
    feedurl = indexes.CharField(model_attr='feed__url')
    date = indexes.DateTimeField(model_attr='date')
    toplevel = indexes.CharField(model_attr='feed__toplevel')

    def get_model(self):
        return Corpus

    def index_queryset(self, **kwargs):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
    
    def get_updated_field(self):
        return "modified"