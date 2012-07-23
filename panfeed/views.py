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
from forms import FeedForm, FeedItemForm
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

def findnews(request):
    feeds = Feed.objects.all().order_by('?')[:8]
    return render_to_response('findnews.html', {'feeds1': feeds[:4], 'feeds2': feeds[4:8]}, context_instance=RequestContext(request))

def allfeeds(request):
    feeds = Feed.objects.all()
    return render_to_response('allfeeds.html', {'feeds': feeds}, context_instance=RequestContext(request))

def managefeed(request, feed_id=None):
    if request.method == "POST":
        form = FeedForm(request.POST)
        if form.is_valid():

            if feed_id is None:
                feed = form.save(commit=False)
                feed.owner = request.user
                feed.save()
            else:
                if Feed.objects.filter(id=feed_id, owner = request.user).exists():
                    feed = form.save(commit=False)
                    feed.owner = request.user
                    feed.id = feed_id
                    feed.save(force_update=True)
                else:
                    return HttpResponseForbidden("You do not have permission to edit this Feed.")

            return HttpResponseRedirect('/publishnews/')

        else:
            items = FeedItem.objects.filter(feed=feed_id)
            if(feed_id is None):
                return render_to_response('managefeed.html', {'form': form}, context_instance=RequestContext(request))
            else:
                return render_to_response('managefeed.html', {'form': form, 'edit': True, 'items': items}, context_instance=RequestContext(request))

    elif request.method == 'DELETE':
        feed = get_object_or_404(Feed, id=feed_id)

        if feed.owner != request.user:
            return HttpResponseForbidden("You do not have permission to edit this Feed.")
        else:
            feed.delete()
            return HttpResponseRedirect('/publishnews/')
    else:
        if feed_id is None:
            form = FeedForm()
            return render_to_response('managefeed.html', {'form': form}, context_instance=RequestContext(request))

        else:
            feed = Feed.objects.get(id=feed_id, owner=request.user)

            form = FeedForm(instance=feed)
            items = FeedItem.objects.filter(feed=feed_id)
            return render_to_response('managefeed.html', {'form': form, 'edit':True, 'items': items}, context_instance=RequestContext(request))

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

@login_required
def publishnews(request):
    feeds = Feed.objects.filter(owner=request.user.id)
    return render_to_response('publishnews.html', {'feeds':feeds}, context_instance=RequestContext(request))

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
