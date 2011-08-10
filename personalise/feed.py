from django.contrib.syndication.views import Feed
from django.db import connection, transaction
import datetime
from operator import itemgetter

class PersonalFeed(Feed):
    title = "Your Feed"
    link = "/find/"
    description = "Your feed personalised from your keywords."
    
    def items(self,keywords):
        cursor = connection.cursor()
        words = keywords.split("_")
        
        results = []
        unique_results = {}
        for word in words:
            print word
            cursor.execute("SELECT corpus.*, corpuskeywords.rank FROM corpus,corpuskeywords WHERE corpus.id=corpuskeywords.itemid AND corpuskeywords.word LIKE %s", [word])

            results+=cursor.fetchall()
            

            for item in results:
                #print item[0]
                if unique_results.has_key(item[0]):
                    unique_results[item[0]][-1]=item[-1]
                else:
                    unique_results[item[0]]=list(item)
                #print "id " + str(item[0])
                #print unique_results[item[0]][-1]

        for item in unique_results.items():
            unique_results[item[0]][-1]=self.get_hot_ranking(unique_results[item[0]])    
        #print  unique_results.values()[0]
        #print results[0]
        sort = sorted(unique_results.values(), key=lambda student: student[-1],reverse=True)
        #print sort
        return sort
        
    def item_title(self,item):
        #print item[-1]
        return item[1]
        
    def item_description(self,item):
        return item[2]
        
    def item_link(self,item):
        return item[3]
    
    def item_pubdate(self,item):
        return item[7]
    
    def get_object(self,request,keywords):
        return keywords
        
    def get_hot_ranking(self,result_item):
        
        #print result_item[5]
        static_rank = result_item[-1]/float(result_item[5])
        #print "Static " + str(static_rank)
        difference = datetime.datetime.now() - result_item[-2]
        #print "days old " + str(difference.days)
        if (difference.days>0):
            hot_rank = static_rank/float(difference.days) 
        else:
            hot_rank = static_rank

        #print "hot rank "+ str(hot_rank)
        return hot_rank
