from django.contrib.syndication.views import Feed
from django.db import connection, transaction
import datetime
from operator import itemgetter
from personalise.models import Feeds,Corpus

class PersonalFeed(Feed):
    title = "Your Feed"
    link = "/find/"
    description = "Your feed personalised from your keywords."
    
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
        print urls
        query = "SELECT corpus.*, corpuskeywords.rank FROM corpus,corpuskeywords WHERE corpus.id=corpuskeywords.itemid AND (corpus.toplevel IN (%s) OR %s = 'all') AND corpuskeywords.word IN (%s)" % (formatstring,"%s",formatwordstring)
        results = Corpus.objects.raw(query,tuple(urls))


        for item in results:
            print dir(item)
            if unique_results.has_key(item.id):
                unique_results[item.id].rank+=item.rank
            else:
                unique_results[item.id]=item
            #print "id " + str(item[0])
            #print unique_results[item[0]][-1]

        for item in unique_results.values():
            item.hot=self.get_hot_ranking(item)    
        #print  unique_results.values()[0]
        #print results[0]
        sort = sorted(unique_results.values(), key=lambda student: student.hot,reverse=True)
        #print sort
        return sort
        
    def item_title(self,item):
        #print item[-1]
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
        
        print dir(result_item)
        static_rank = result_item.rank/float(result_item.length)
        #print "Static " + str(static_rank)
        difference = datetime.datetime.now() - result_item.date
        #print "days old " + str(difference.days)
        if (difference.days>0):
            hot_rank = static_rank/float(difference.days) 
        else:
            hot_rank = static_rank

        #print "hot rank "+ str(hot_rank)
        return hot_rank

# vi: sw=4 ts=8 sts=4
