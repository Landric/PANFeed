from django.http import HttpResponse,HttpResponseRedirect,HttpResponseForbidden, Http404
import feedparser
import json
from urlparse import urlparse

from panfeed.models import AcademicFeeds,Feed,FeedItem,SpecialIssue

from django.shortcuts import render_to_response, get_object_or_404, redirect

from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from forms import FeedForm, FeedItemForm, SpecialIssueForm
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import ModelFormMixin
import urllib2
import ogp
from BeautifulSoup import BeautifulSoup

class LoginRequiredMixin(object):
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)
        

class OwnerModelFormMixin(ModelFormMixin):
    """
    Add the owner to the created object from the request.user instance
    """
    def form_valid(self,form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()
        return super(OwnerModelFormMixin, self).form_valid(form)


class FeedMixin(object):
    model = Feed

class FeedListView(FeedMixin, ListView):
    context_object_name = "feeds"

class FindNews(FeedListView):
    template_name="panfeed/findnews.html"
    queryset = Feed.objects.all().order_by('?')[:8]
    
class FeedCRUDMixin(LoginRequiredMixin, FeedMixin):
    """
    Mixin that holds common methods and properties for all the CRUD
    operations on the Feed model
    """
    form_class = FeedForm
    def get_success_url(self):
        """
        Whenever a feed is created or updated successfully this will
        return the user to the publishnews page with the feed they just
        messed with highlighted
        """
        feed = getattr(self,"object",False)
        if feed:
            return reverse('publishnews') + '#feed-{feed_id}'.format(feed_id = feed.id)
        else:
            return reverse('publishnews')
    
    def get_queryset(self):
        """
        Only operate on feeds the user owns
        """
        return self.model.objects.filter(owner=self.request.user)

class FeedDetailView(FeedCRUDMixin, DetailView):
    pass
class FeedCreateView(FeedCRUDMixin, OwnerModelFormMixin, CreateView):
    pass
class FeedDeleteView(FeedCRUDMixin, DeleteView):
    pass
class FeedUpdateView(FeedCRUDMixin, UpdateView):
    def get_feed_items(self, feed):
        plain_items = feed.feeditem_set.filter(special_issue__isnull=True)
        special_issues = feed.specialissue_set.all()
        
        #union and sort the items from plain_items and special_issues
        items_issues = sorted(
            list(plain_items) + list(special_issues),
            key = lambda obj: obj.created,
            reverse=True
        )
        table_list = []
        item_list = []
        #take each item in the union, if it has subitems add those too.
        for item_issue in items_issues:
            if hasattr(item_issue, "feeditem_set"):
                if item_list:
                    table_list.append(item_list)
                    item_list = []
                item_list.append(item_issue)

                issue_items = item_issue.feeditem_set.order_by('issue_position')
                for issue_item in issue_items:
                    item_list.append(issue_item)

                table_list.append(item_list)
                item_list = []

            else:
                item_list.append(item_issue)

        if item_list:
            table_list.append(item_list)

        return table_list

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['table_list'] = self.get_feed_items(self.object)
        return context

class PublishNews(FeedCRUDMixin, ListView):
    context_object_name = "feeds"
    template_name = "panfeed/publishnews.html"
    
    def get_queryset(self):
        return self.model.objects.filter(owner=self.request.user)

def managefeed(request, feed_slug=None):
    """
    Route to the correct view based on Method or the existance of
    feed_id.
    """
    if request.method == 'DELETE':
        return FeedDeleteView.as_view()(request=request, slug=feed_slug)
    else:
        if feed_slug:
            return FeedUpdateView.as_view()(request=request, slug=feed_slug)
        else:
            return FeedCreateView.as_view()(request=request)


class ItemMixin(object):
    model = FeedItem

class ItemListView(ItemMixin, ListView):
    context_object_name = "items"

class ItemCRUDMixin(LoginRequiredMixin, ItemMixin):
    form_class = FeedItemForm
    def get_success_url(self):
        return reverse('publishnews')
    
    def get_queryset(self):
        #Only operate on items that belong to feeds the current user owns
        return self.model.objects.filter(feed__owner=self.request.user)
    
    def get_success_url(self):
        """
        Whenever a feed is created or updated successfully this will
        return the user to the publishnews page with the feed they just
        messed with highlighted
        """
        item = getattr(self,"object",False)
        if item:
            return item.feed.get_modify_url() + '#item-{item_id}'.format(item_id = item.id)
        else:
            return reverse('publishnews')
    
    
    def get_context_data(self, **kwargs):
        context = super(ItemCRUDMixin, self).get_context_data(**kwargs)
        context["feed"] = self.kwargs["feed"]
        return context

class ItemDetailView(ItemCRUDMixin, DetailView):
    pass
class ItemCreateView(ItemCRUDMixin, CreateView):
    template_name = "panfeed/feeditem_form.html"
    
    def form_invalid(self,form):
        print form.errors
        return super(ItemCreateView, self).form_invalid(form)

    def form_valid(self,form):
        self.object = form.save(commit=False)
        self.object.feed = self.kwargs["feed"]
        self.object.save()
        return super(ItemCreateView, self).form_valid(form)
        
class ItemDeleteView(ItemCRUDMixin, DeleteView):
    pass
class ItemUpdateView(ItemCRUDMixin, UpdateView):
    template_name = "panfeed/feeditem_form.html"

def manageitem(request, feed_slug, item_slug=None):
    """
    Route to the correct view based on Method or the existance of
    item_id.
    """
    feed = get_object_or_404(Feed, slug=feed_slug)
    
    if feed.owner != request.user:
        return HttpResponseForbidden("You do not have permission to edit this Feed.")

    if request.method == 'DELETE':
        return ItemDeleteView.as_view()(request=request, slug=item_slug)
    else:
        if item_slug:
            return ItemUpdateView.as_view()(request=request, feed=feed, slug=item_slug)
        else:
            return ItemCreateView.as_view()(request=request, feed=feed)


class IssueMixin(object):
    model = SpecialIssue

class IssueListView(IssueMixin, ListView):
    context_object_name = "issues"

class IssueCRUDMixin(LoginRequiredMixin, IssueMixin):
    form_class = SpecialIssueForm
    def get_success_url(self):
        return reverse('publishnews')
    
    def get_context_data(self, **kwargs):
        context = super(IssueCRUDMixin, self).get_context_data(**kwargs)
        context["feed"] = get_object_or_404(Feed, slug=self.kwargs["feed"])
        return context

class IssueDetailView(IssueCRUDMixin, DetailView):
    pass
class IssueCreateView(IssueCRUDMixin, CreateView):
    template_name = "panfeed/specialissue_form.html"
    
    def form_valid(self,form):
        self.object = form.save(commit=False)
        self.object.feed_id = Feed.objects.get(slug=self.kwargs["feed"]).id
        self.object.save()
        return super(IssueCreateView, self).form_valid(form)
        
class IssueDeleteView(IssueCRUDMixin, DeleteView):
    pass
class IssueUpdateView(IssueCRUDMixin, UpdateView):
    template_name = "panfeed/specialissue_form.html"

def manageissue(request, feed_slug, issue_slug=None):
    """
    Route to the correct view based on Method or the existance of
    issue_id.
    """
    
    feed = get_object_or_404(Feed, slug=feed_slug)
    if feed.owner != request.user:
        return HttpResponseForbidden("You do not have permission to edit this Feed.")

    if request.method == 'DELETE':
        return IssueDeleteView.as_view()(request=request, slug=issue_slug)
    else:
        if issue_slug:
            return IssueUpdateView.as_view()(request=request, feed=feed_slug, slug=issue_slug)
        else:
            return IssueCreateView.as_view()(request=request, feed=feed_slug)


def urltoitem(request):
    try:
        urls = request.GET.getlist("url")
    except:
        raise Http404
    
    items = []
    for url in urls:
        og = ogp.OpenGraph(
            url=url,
            required_attrs = ("title", "description", "image", "url"),
            scrape=True,
        )
        items.append(og.items)

    return HttpResponse(json.dumps(items), mimetype="application/json")

def submit(request):
    if request.method == 'POST':
        feeds = str(request.POST['urls']).splitlines()
        invalid_feeds = []
        validate = URLValidator(verify_exists=True)
        for url in feeds:
            try:
                validate(url)
                hostname = urlparse(url).hostname
                if (hostname.endswith(".ac.uk") or hostname.endswith(".edu")):
                    if (feedparser.parse(url).version):
                        if (not AcademicFeeds.objects.filter(url=url).exists()):
                            AcademicFeeds.objects.create(url=url,toplevel=hostname)
                else:
                    invalid_feeds.append(url)
            except ValidationError, e:
                invalid_feeds.append(url)
        

        if invalid_feeds:
            content = 'The following feeds are invalid, or do not resolve to an academic domain, and could not be added to the PANFeed database. Please check they exist, and try again.'
            return render_to_response('error.html', {'title':'Error', 'header':'Invalid Feeds', 'content':content, 'data':invalid_feeds}, context_instance=RequestContext(request))
        else:
            content = 'Your feeds have been sucessfully added to PANFeed!'
            return render_to_response('success.html', {'title':'Crawl Me', 'header':'Success!', 'content':content}, context_instance=RequestContext(request))

    else:
        content = 'Your data was not submitted - please retry sending the form. If you have reached this page in error, please go back and try again. If the problem persists, inform an administrator.'
        
        return render_to_response('error.html', {'title':'Error', 'header':'No data recieved', 'content':content}, context_instance=RequestContext(request))
