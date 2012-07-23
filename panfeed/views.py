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
    def form_valid(self,form):
        # save but don't commit the model form
        self.object = form.save(commit=False)
        # set the owner to be the current user
        self.object.owner = self.request.user
        #
        # Here you can make any other adjustments to the model
        #
        self.object.save()
        # ok now call the base class and we are done.
        return super(OwnerModelFormMixin, self).form_valid(form)

def manageitem(request, feed_id, item_id=None):
    feed = get_object_or_404(Feed, id=feed_id)
    if feed.owner != request.user:
        return HttpResponseForbidden("You do not have permission to edit this Feed.")

    if request.method == "POST":
        form = FeedItemForm(request.POST)
        if form.is_valid():

            if item_id is None:
                item = form.save(commit=False)
                item.feed = feed
                item.save()
            else:
                if FeedItem.objects.filter(id=item_id, feed=feed_id).exists():
                    item = form.save(commit=False)
                    item.feed = feed_id
                    item.id = item_id
                    item.save(force_update=True)
                else:
                    return HttpResponseForbidden("You do not have permission to edit this Feed.")

            return HttpResponseRedirect('/publishnews/')

        else:
            return render_to_response('manageitem.html', {'form': form, 'feed_title':feed.title, 'edit': True}, context_instance=RequestContext(request))
        '''
        elif request.method == 'DELETE':
            item = get_object_or_404(Feed, id=item_id)

            if feed.owner != request.user:
                return HttpResponseForbidden("You do not have permission to edit this Feed.")
            else:
                feed.delete()
                return HttpResponseRedirect('/publishnews/')
        '''
    else:
        if item_id is None:
            form = FeedItemForm()
            return render_to_response('manageitem.html', {'form': form, 'feed_title':feed.title}, context_instance=RequestContext(request))

        else:
            item = FeedItem.objects.get(id=item_id)

            form = FeedItemForm(instance=item)
            return render_to_response('manageitem.html', {'form': form, 'feed_title':feed.title, 'edit':True}, context_instance=RequestContext(request))


class FeedMixin(object):
    model = Feed


class FeedListView(FeedMixin, ListView):
    context_object_name = "feeds"


class FindNews(FeedListView):
    template_name="panfeed/findnews.html"
    context_object_name = "feeds"
    queryset = Feed.objects.all().order_by('?')[:8]
    
    
class FeedCRUDMixin(LoginRequiredMixin, FeedMixin):
    form_class = FeedForm
    def get_success_url(self):
        return reverse('publishnews')
    
    def get_queryset(self):
        return self.model.objects.filter(owner=self.request.user)

class FeedDetailView(FeedCRUDMixin, DetailView):
    pass
class FeedCreateView(FeedCRUDMixin, OwnerModelFormMixin, CreateView):
    pass
class FeedDeleteView(FeedCRUDMixin, DeleteView):
    pass
class FeedUpdateView(FeedCRUDMixin, UpdateView):
    pass

class PublishNews(LoginRequiredMixin, ListView):
    model = Feed
    context_object_name = "feeds"
    template_name = "panfeed/publishnews.html"
    
    def get_queryset(self):
        return self.model.objects.filter(owner=self.request.user)


def managefeed(request, feed_id=None):
    if request.method == 'DELETE':
        return FeedDeleteView.as_view()(request=request, pk=feed_id)
    else:
        if feed_id:
            return FeedUpdateView.as_view()(request=request, pk=feed_id)
        else:
            return FeedCreateView.as_view()(request=request)


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
