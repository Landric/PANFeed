from django.contrib.auth.models import User
from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.validation import FormValidation
from panfeed.models import Feed, FeedItem, SpecialIssue
from panfeed.forms import FeedForm, FeedItemForm, SpecialIssueForm

class DjangoAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        if request.user.is_authenticated:
          return True

        return False

class FeedAuthorization(Authorization):
    def apply_limits(self, request, object_list):
        if request and hasattr(request, 'user'):
            return object_list.filter(owner=request.user)

        return object_list.none()

class FeedItemAuthorization(Authorization):
    def apply_limits(self, request, object_list):
        if request and hasattr(request, 'user'):
            return object_list.filter(feed__owner=request.user)

        return object_list.none()

class SpecialIssueAuthorization(Authorization):
    def apply_limits(self, request, object_list):
        if request and hasattr(request, 'user'):
            return object_list.filter(feed__owner=request.user)

        return object_list.none()

class FeedResource(ModelResource):
    class Meta:
        resource_name = 'feed'
        queryset = Feed.objects.all()
        allowed_methods = ['get']
        authentication = DjangoAuthentication()
        authorization = FeedAuthorization()
        validation = FormValidation(form_class=FeedForm)

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
            "special_issue": ALL,
        }
        authentication = DjangoAuthentication()
        authorization = FeedItemAuthorization()
        validation = FormValidation(form_class=FeedItemForm)

class SpecialIssueResource(ModelResource):
    class Meta:
        resource_name = 'speicalissue'
        queryset = SpecialIssue.objects.all()
        allowed_methods = ['put', 'post']
        authentication = DjangoAuthentication()
        authorization = SpecialIssueAuthorization()
        validation = FormValidation(form_class=SpecialIssueForm)
