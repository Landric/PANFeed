from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
import datetime
from panfeed.models import Corpus
import urllib


from haystack.query import SearchQuerySet

from collections import namedtuple

class PersonalFeed(Feed):
    description = "Your feed Personalised Academic News Feed from your keywords."

    def items(self,obj):

        words = obj["keywords"]
        #urls = params[1].split("_") 
                
        #urls.append(urls[0])#.append(words
        #urls.extend(words)
        
        corpora = SearchQuerySet().models(Corpus).all()
        
        for word in words:
            corpora = corpora.filter_or(content=word)
        
        return (corpus.object for corpus in corpora.load_all())

    def title(self,obj):
        return "PANFeed of " + ", ".join(obj['keywords']) 

    def link(self, obj):
        return '/find?{params}'.format(params=urllib.urlencode(
            {'kw':obj['keywords']},
            {'url':obj['sources']}
            )
        )

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
        return (
            {
                "keywords":get.getlist("kw",[]),
                "sources": get.getlist('url',[])
            }
        )

    def get_hot_ranking(self,result_item):
        
        static_rank = result_item.rank/float(result_item.length)
        difference = datetime.datetime.now() - result_item.date
        if (difference.days>0):
            hot_rank = static_rank/float(difference.days) 
        else:
            hot_rank = static_rank

        return hot_rank

class UserFeed(Feed):

    def items(self,obj):
        return IssueItem.objects.filter(issue__id=obj.id).order_by("-date")

    def title(self,obj):
        return obj.title 

    def description(self,obj):
        return obj.description 

    def link(self, obj):
        return "/issue/"+str(obj.id)

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
