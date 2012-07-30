from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.http import Http404
import datetime
from panfeed.models import Corpus, Feed as MFeed, FeedItem, SpecialIssue
import urllib


from haystack.query import SearchQuerySet, SQ

from collections import namedtuple

class PersonalFeed(Feed):
    description = "Your feed Personalised Academic News Feed from your keywords."

    def items(self,obj):

        words = obj["keywords"]
        urls = obj["sources"]
                
        #urls.append(urls[0])#.append(words
        #urls.extend(words)
        
        
        
        corpora = SearchQuerySet().models(Corpus)
        cfilter = {"words":SQ(), "urls":SQ()}
        for word in words:
            word = corpora.query.clean(word)
            cfilter["words"] = cfilter["words"] | SQ(content=word)
        
        for url in urls:
            url = corpora.query.clean(url)
            cfilter["urls"] = cfilter["urls"] | SQ(toplevel=url)
        
        if urls:
            cfilter = cfilter["words"] & cfilter["urls"]
        else:
            cfilter = cfilter["words"]
        
        corpora = corpora.filter(cfilter)
        
        if not len(corpora):
            raise(Http404)
        
        return (corpus.object for corpus in corpora.load_all())

    def title(self,obj):
        return "PANFeed of " + ", ".join(obj['keywords']) 

    def link(self, obj):
        return '{reverse}?{params}'.format(reverse=reverse('find'),params=urllib.urlencode(
            {'kw':obj['keywords']},
            {'url':obj['sources']}
            )
        )

    def catagories(self, obj):
        return obj["keywords"]
    
    
    def item_title(self,item):
        return item.title
        
    def item_description(self,item):
        return item.description
        
    def item_link(self,item):
        return item.url
    
    def item_pubdate(self,item):
        return item.date
    
    def get_object(self,request):
        get = request.GET
        obj = {
            "keywords":get.getlist("kw", []),
            "sources": get.getlist('url',[])
        }
        
        if not obj["keywords"]:
            raise(Http404)
        
        return (obj)

class UserFeed(Feed):

    def items(self,feed):
        if(feed.displayAll):
            return FeedItem.objects.filter(feed=feed).order_by("-date")

        else:  
            latest_item = FeedItem.objects.filter(feed=feed).order_by("-date")[:1]
            if latest_item:
                latest_item = latest_item.select_related().get()

                if (latest_item.special_issue):
                    issue_items = list(FeedItem.objects.filter(feed=feed, special_issue=latest_item.special_issue).order_by("issue_position"))
                    return issue_items
                else:
                    return latest_item

            else:
                return latest_item

    def title(self,feed):
        return feed.title 

    def description(self,feed):
        return feed.description 

    def link(self, feed):
        return "/feed/"+str(feed.slug)

    def item_title(self,item):
        return item.title

    def item_description(self,item):
        return "<img src='"+item.img+"' /> " + item.content

    def item_link(self,item):
        return item.url

    def item_pubdate(self,item):
        return item.date

    def get_object(self,request,feed_slug):
        return get_object_or_404(MFeed, slug=feed_slug);
