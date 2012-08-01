from django.contrib.auth.models import User
from tastypie.resources import ModelResource
from panfeed.auth import CustomAuthentication, CustomAuthorization
from panfeed.models import Feed, FeedItem, SpecialIssue

class FeedResource(ModelResource):
    class Meta:
        resource_name = 'feed'
        queryset = Feed.objects.all()
        allowed_methods = ['get']
    
    def dehydrate(self, bundle):
        bundle.data['url'] = bundle.obj.get_absolute_url()
        return bundle

class FeedItemResource(ModelResource):
    class Meta:
        resource_name = 'feed_item'
        queryset = FeedItem.objects.all()
        authentication = CustomAuthentication()
        authorization = CustomAuthorization()
        allowed_methods = ['get']

class SpecialIssueResource(ModelResource):
    class Meta:
        resource_name = 'special_issue'
        queryset = SpecialIssue.objects.all()
        authentication = CustomAuthentication()
        authorization = CustomAuthorization()
        allowed_methods = ['get']
