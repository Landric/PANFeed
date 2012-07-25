from tastypie.resources import ModelResource
from panfeed.models import Feed, FeedItem, SpecialIssue


class FeedResource(ModelResource):
    class Meta:
        queryset = Feed.objects.all()

class FeedItemResource(ModelResource):
    class Meta:
        queryset = FeedItem.objects.all()

class SpecialIssueResource(ModelResource):
    class Meta:
        queryset = SpecialIssue.objects.all()
