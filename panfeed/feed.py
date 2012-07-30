from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.http import Http404
import datetime
from panfeed.models import Corpus
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

    def items(self,obj):
        if(obj.displayAll):
            return FeedItem.objects.filter(feeditem__id=obj.id).order_by("-date")

        else:  
            latestItem = FeedItem.objects.filter(feeditem__id=obj.id).order_by("-date")[:1]
            if (latestItem.special_issue):
                return FeedItem.objects.filter(feeditem__id=obj.id, feeditem__special_issue=latestItem.special_issue).order_by("issue_position")
            else:
                return latestItem

    def title(self,obj):
        return obj.title 

    def description(self,obj):
        return obj.description 

    def link(self, obj):
        return "/feed/"+str(obj.id)

    def item_title(self,item):
        return item.title

    def item_description(self,item):
        return "<img src='"+item.img+"' /> " + item.description

    def item_link(self,item):
        return item.url

    def item_pubdate(self,item):
        return item.date

    def get_object(self,request,issueid):
        return get_object_or_404(Issue, id=issueid);
