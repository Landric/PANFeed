from django.contrib.syndication.views import Feed
from django.db import connection, transaction
from django.shortcuts import get_object_or_404
import datetime
import time
import sys
from operator import itemgetter
from panfeed.models import Corpus, FeedItem
from panfeed.models import Feed as MFeed
import feedparser

from haystack.query import SearchQuerySet

class PANFeed:
    title = ""
    description = ""
    link = ""
    
    def reorder(self, fieldname):
        foo = 1 + 1

    def beautify(self):
        foo = 1 + 1

    def __items(self):
        foo = 1 + 1


class PersonalFeed(Feed):
    title = "Your Feed"
    link = "/find/"
    description = "Your feed Personalised Academic News Feed from your keywords."
    keywords = [];

    def items(self,params):
        cursor = connection.cursor()
        words = params[0].split("_")
        urls = params[1].split("_") 
        
        results = []
        unique_results = {}
        
        
        formatstring = ",".join(["%s"] * len(urls))
        formatwordstring = ",".join(["%s"] * len(words))
        urls.append(urls[0])#.append(words
        urls.extend(words)
        
        corpuses = SearchQuerySet().models(Corpus).filter(contains=" ".join(words)).load_all()
        
        query = "SELECT corpus.*, corpuskeywords.rank FROM corpus,corpuskeywords WHERE corpus.id=corpuskeywords.itemid AND (corpus.toplevel IN (%s) OR %s = 'all') AND corpuskeywords.word IN (%s)" % (formatstring,"%s",formatwordstring)
        results = Corpus.objects.raw(query,tuple(urls))

        for item in results:
            if unique_results.has_key(item.id):
                unique_results[item.id].rank+=item.rank
            else:
                unique_results[item.id]=item

        for item in unique_results.values():
            item.hot=self.get_hot_ranking(item)    
        sort = sorted(unique_results.values(), key=lambda student: student.hot,reverse=True)
        return sort

    def title(self,obj):
        return "PANFeed of " + ", ".join(obj[0].split("_")) 

    def link(self, obj):
        return "http://panfeed.ecs.soton.ac.uk/find/"+obj[1]+"/"+obj[0]

    def item_title(self,item):
        return item.title
        
    def item_description(self,item):
        return item.description
        
    def item_link(self,item):
        return item.url
    
    def item_pubdate(self,item):
        return item.date
    
    def get_object(self,request,keywords,sources):
        return (keywords,sources) 

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
        return "http://panfeed.ecs.soton.ac.uk/issue/"+str(obj.id)

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
