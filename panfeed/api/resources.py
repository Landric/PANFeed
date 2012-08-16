from django.contrib.auth.models import User
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.validation import FormValidation
from tastypie.bundle import Bundle
from panfeed.models import Feed, FeedItem, SpecialIssue
from panfeed.forms import FeedItemForm, SpecialIssueForm

class DjangoAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        if request.method == 'GET' or request.user.is_authenticated:
          return True

        return False

class FeedItemAuthorization(Authorization):
    def apply_limits(self, request, object_list):
        if request and request.method == 'GET':
            return object_list.all()
 
        if isinstance(object_list, Bundle):
            if object_list.exists(feed__owner=request.user):
                return object_list
        print "FeedItem"
        return object_list.none()

class SpecialIssueAuthorization(Authorization):
    def apply_limits(self, request, object_list):
        if request and request.method == 'GET':
            return object_list.all()

        if isinstance(object_list, Bundle):
            if object_list.exists(feed__owner=request.user):
                return object_list

        print "Issue"
        return object_list.none()

class FeedResource(ModelResource):
    class Meta:
        resource_name = 'feed'
        queryset = Feed.objects.all()
        allowed_methods = ['get']
        authentication = DjangoAuthentication()

    def dehydrate(self, bundle):
        bundle.data['url'] = bundle.obj.get_absolute_url()
        return bundle

class SpecialIssueResource(ModelResource):
    feed = fields.ForeignKey(FeedResource, 'feed')

    class Meta:
        resource_name = 'specialissue'
        queryset = SpecialIssue.objects.all()
        allowed_methods = ['get', 'put', 'post']
        authentication = DjangoAuthentication()
        authorization = SpecialIssueAuthorization()

        def obj_create(self, bundle, request, **kwargs):
            bundle = self._meta.authorization.apply_limits(request, bundle)
            return super(FeedItemResource, self).obj_create(bundle, request, **kwargs)
 
        def obj_update(self, bundle, request, **kwargs):
            bundle = self._meta.authorization.apply_limits(request, bundle)
            return super(FeedItemResource, self).obj_update(bundle, request, **kwargs)

class FeedItemResource(ModelResource):
    feed = fields.ForeignKey(FeedResource, 'feed')
    special_issue = fields.ForeignKey(SpecialIssueResource, 'special_issue', null=True)

    class Meta:
        resource_name = 'feeditem'
        queryset = FeedItem.objects.all()
        allowed_methods = ['get', 'post', 'put']
        filtering = {
            "id": ALL,
            "special_issue": ALL,
        }
        authentication = DjangoAuthentication()
        authorization = FeedItemAuthorization()
        validation = FormValidation(form_class=FeedItemForm)
        
        def obj_create(self, bundle, request, **kwargs):
            bundle = self._meta.authorization.apply_limits(request, bundle)
            return super(FeedItemResource, self).obj_create(bundle, request, **kwargs)
 
        def obj_update(self, bundle, request, **kwargs):
            bundle = self._meta.authorization.apply_limits(request, bundle)
            return super(FeedItemResource, self).obj_update(bundle, request, **kwargs)
