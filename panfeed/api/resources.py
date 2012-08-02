from django.contrib.auth.models import User
from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from panfeed.models import Feed, FeedItem

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
        resource_name = 'feeditem'
        queryset = FeedItem.objects.all()
        allowed_methods = ['get']
        filtering = {
            "id": ALL,
        }
