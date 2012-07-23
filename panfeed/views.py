# Create your views here.
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseForbidden
import feedparser
import json
from urlparse import urlparse

from panfeed.models import AcademicFeeds,Feed,FeedItem
from panfeed.urltorss2 import ItemMaker

from django.shortcuts import render_to_response, get_object_or_404, redirect

from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from forms import FeedForm, FeedItemForm
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import ModelFormMixin

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
    pass

class PublishNews(FeedCRUDMixin, ListView):
    context_object_name = "feeds"
    template_name = "panfeed/publishnews.html"
    
    def get_queryset(self):
        return self.model.objects.filter(owner=self.request.user)

def managefeed(request, feed_id=None):
    """
    Route to the correct view based on Method or the existance of
    feed_id.
    """
    if request.method == 'DELETE':
        return FeedDeleteView.as_view()(request=request, pk=feed_id)
    else:
        if feed_id:
            return FeedUpdateView.as_view()(request=request, pk=feed_id)
        else:
            return FeedCreateView.as_view()(request=request)


class ItemMixin(object):
    model = FeedItem

class ItemListView(ItemMixin, ListView):
    context_object_name = "items"

class ItemCRUDMixin(LoginRequiredMixin, FeedMixin):
    form_class = FeedItemForm
    def get_success_url(self):
        return reverse('publishnews')
    
    def get_queryset(self):
        """
        Only operate on items that belong to feeds the current user owns
        """
        return self.model.objects.filter(feed__owner=self.request.user)
        
    def get_context_data(self, **kwargs):
        context = super(ItemCRUDMixin, self).get_context_data(**kwargs)
        context["feed"] = feed = get_object_or_404(Feed, id=self.kwargs["feed"])
        return context

class ItemDetailView(ItemCRUDMixin, DetailView):
    pass
class ItemCreateView(ItemCRUDMixin, CreateView):
    template_name = "panfeed/feeditem_form.html"
class ItemDeleteView(ItemCRUDMixin, DeleteView):
    pass
class ItemUpdateView(ItemCRUDMixin, UpdateView):
    template_name = "panfeed/feeditem_form.html"

def manageitem(request, feed_id, item_id=None):
    """
    Route to the correct view based on Method or the existance of
    item_id.
    """
    
    feed = get_object_or_404(Feed, id=feed_id)
    if feed.owner != request.user:
        return HttpResponseForbidden("You do not have permission to edit this Feed.")

    if request.method == 'DELETE':
        return ItemDeleteView.as_view()(request=request, pk=item_id)
    else:
        if item_id:
            return ItemUpdateView.as_view()(request=request, pk=item_id)
        else:
            return ItemCreateView.as_view()(request=request, feed=feed_id)


def urltoitem(request):
    itemmaker = ItemMaker()
    itemmaker.parse_url(request.REQUEST["url"])
    return HttpResponse(json.dumps({ 'title':itemmaker.title, 'description':itemmaker.p, 'img':itemmaker.img }), mimetype="application/json")

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
