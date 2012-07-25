from tastypie.resources import ModelResource
from panfeed.models import Feed, FeedItem, SpecialIssue


class FeedResource(ModelResource):
    class Meta:
        resource_name = 'feed'
        queryset = Feed.objects.all()
        #allowed_methods = ['get']

class FeedItemResource(ModelResource):
    class Meta:
        resource_name = 'feed_item'
        queryset = FeedItem.objects.all()
        #allowed_methods = ['get']

class SpecialIssueResource(ModelResource):
    class Meta:
        resource_name = 'special_issue'
        queryset = SpecialIssue.objects.all()
        #allowed_methods = ['get']
