from django.contrib.auth.models import User
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from .authentication import SessionAuthentication
from tastypie.authorization import Authorization
from tastypie.validation import FormValidation
from panfeed.models import Feed, FeedItem, SpecialIssue
from panfeed.forms import FeedItemForm, SpecialIssueForm

class ReadAllWriteOwnedAuthentication(SessionAuthentication):
    def is_authenticated(self, request, **kwargs):
        if request.method == 'GET':
          return True

        else:
            return super(ReadAllWriteOwnedAuthentication, self).is_authenticated(request, **kwargs);

class FeedItemAuthorization(Authorization):
    def apply_limits(self, request, object_list):
        if request and request.method == 'GET':
            print "Item GET"
            return object_list.all()
 
        print "Item filter"
        return object_list.filter(feed__owner=request.user)

class SpecialIssueAuthorization(Authorization):
    def apply_limits(self, request, object_list):
        if request and request.method == 'GET':
            print "Issue GET"
            return object_list.all()
            
        print "Issue filter"
        return object_list.filter(feed__owner=request.user)

class FeedResource(ModelResource):
    class Meta:
        resource_name = 'feed'
        queryset = Feed.objects.all()
        allowed_methods = ['get']
        authentication = ReadAllWriteOwnedAuthentication()

    def dehydrate(self, bundle):
        bundle.data['url'] = bundle.obj.get_absolute_url()
        return bundle

class SpecialIssueResource(ModelResource):
    feed = fields.ForeignKey(FeedResource, 'feed')

    class Meta:
        resource_name = 'specialissue'
        queryset = SpecialIssue.objects.all()
        allowed_methods = ['get', 'put', 'post']
        filtering = {
            "id": ALL,
        }
        authentication = ReadAllWriteOwnedAuthentication()
        authorization = SpecialIssueAuthorization()

        def obj_create(self, bundle, request, **kwargs):
            bundle = self._meta.authorization.apply_limits(request, bundle)
            print "issue create"
            return super(SpecialIssueResource, self).obj_create(bundle, request, **kwargs)
 
        def obj_update(self, bundle, request, **kwargs):
            bundle = self._meta.authorization.apply_limits(request, bundle)
            return super(SpecialIssueResource, self).obj_update(bundle, request, **kwargs)

class FeedItemResource(ModelResource):
    feed = fields.ForeignKey(FeedResource, 'feed')
    special_issue = fields.ForeignKey(SpecialIssueResource, 'special_issue', null=True)

    class Meta:
        resource_name = 'feeditem'
        queryset = FeedItem.objects.all()
        allowed_methods = ['get', 'put', 'post', 'delete']
        filtering = {
            "id": ALL,
            "special_issue": ALL,
        }
        authentication = ReadAllWriteOwnedAuthentication()
        authorization = FeedItemAuthorization()
        validation = FormValidation(form_class=FeedItemForm)
        
        def obj_create(self, bundle, request, **kwargs):
            bundle = self._meta.authorization.apply_limits(request, bundle)
            print "item create"
            return super(FeedItemResource, self).obj_create(bundle, request, **kwargs)
 
        def obj_update(self, bundle, request, **kwargs):
            bundle = self._meta.authorization.apply_limits(request, bundle)
            return super(FeedItemResource, self).obj_update(bundle, request, **kwargs)
