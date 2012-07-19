import datetime
from haystack import indexes
from haystack import site
from personalise.models import Corpus

class CorpusIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    url = indexes.CharField(model_attr='url')
    feed = indexes.CharField(model_attr='feed')
    date = indexes.DateTimeField(model_attr='date')
    toplevel = indexes.CharField(model_attr='toplevel')

    def get_model(self):
        return Corpus

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

site.register(Corpus,CorpusIndex)
