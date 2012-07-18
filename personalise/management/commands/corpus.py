## A corpus is a body of work consisting of many Documents
from personalise.models import AcademicFeeds, Corpuskeywords, Tf, Words
from personalise.models import Corpus as MCorpus

from django.db import connection
from django.core.management.base import BaseCommand, CommandError

from collections import namedtuple
import feedparser
import urllib2
import string
import unicodedata
import math
import re
import datetime

class Command(BaseCommand):

    help = 'Loads all the corpus stuff'

    def handle(self, *args, **options):
        load_generate_and_add_corpus_data()


class Corpus():
    
    db = None
    corpussize = None
        
    def build_corpus(self):
        #### Builds a corpus of documents from a set of feeds.
        
        feeds = open("newfeed.txt", "r")
        for feedurl in feeds:
            print feedurl
            try:
                page = urllib2.urlopen(feedurl)
                feed = feedparser.parse(page)
                for item in feed.entries:
                    try:
                        if not MCorpus.objects.filter(url=item.link, title=item.title).exists():
                            try:
                                d = datetime.datetime(*(item.date_parsed[0:6]))
                            except (AttributeError,TypeError):
                                d=datetime.datetime.now()
                            dStr = d.isoformat(' ')
                            try:
                                itemDesc = item.description
                            except:
                                itemDesc = ""
                            
                            MCorpus(
                                title = item.title,
                                description = itemDesc,
                                url = item.link,
                                feed = feedurl,
                                length = len(itemDesc+item.title),
                                date = dStr
                            ).save()
                            
                    except Exception as e:
                        print(e)
            except urllib2.URLError:
                print "Error getting page: ", feedurl
 
        feeds.close()
        
    def count_words_and_store(self):
        ### Performs a wordcount of each document and stores cumulative word count 
        ### and also wordcount specific to that document/word combination.
        corpusses = MCorpus.objects.all()
        for corpus in corpusses:
            if not Tf.objects.filter(corpus=corpus).exists():
                totaltext = unicodedata.normalize('NFKD',(corpus.title+' '+corpus.description)).encode('ascii','ignore')
                totaltext = self.__remove_extra_spaces(self.__remove_html_tags(totaltext))
                freq = self.__get_word_frequencies(self.__remove_single_characters((''.join((x for x in (totaltext.lower()) if x not in string.punctuation)))))
                for word in freq:
                    itemid = corpus.id
                    #print word, " ", freq[word], " ", itemid
                    dbword,created = Words.objects.get_or_create(word=word, defaults={'count':0})
                    dbword.count += 1
                    dbword.tf_set.add(Tf(corpus=corpus, count=freq[word]))
                    dbword.save()
            
    def __get_word_frequencies(self,text):
        result = dict([(w[:29], text.count(w[:29])) for w in text.split()])
        return result
        
    def __remove_html_tags(self,data):
        p = re.compile(r'<.*?>')
        return p.sub('', data)

    def __remove_extra_spaces(self,data):
        p = re.compile(r'\s+')
        return p.sub(' ', data)
        
    def __remove_single_characters(self,data):
        p=re.compile(r'(^|\s)[^ \t]($|\s)')
        return p.sub('',data)
        
    def calculate_keywords_for_all(self):
        corpusses = MCorpus.objects.all()
        global corpussize
        corpussize = MCorpus.objects.count()
        
        for corpus in corpusses:
            if not Corpuskeywords.objects.filter(corpus=corpus).exists():
                ### For each item from feeds
                worddata = {}
                words = corpus.tf_set
                ### For each word in that item
                for tf in corpus.tf_set.all():
                    worddata[tf.word.word] = (tf.count, tf.word.count)  #The count for the corpus, and the count for all words
                keywords = self.calculate_tfidf(worddata)
                topkeys = keywords[:10]
                for rank, word in topkeys:
                    corpus.corpuskeywords_set.add(Corpuskeywords(corpus=corpus, word=Words(pk=word), rank=rank))
                corpus.save()
        
    def calculate_tfidf(self,worddata):
        wordlist = []
        for word in worddata:
            idf = math.log(corpussize/(worddata[word][1]+1.0))
            tfidf = idf * worddata[word][0]
            wordlist.append((tfidf,word))
        return sorted(wordlist, reverse=True)
        
    def get_keywords_for_item(self,itemid):
        MCorpus.objects.get(id=itemid).corpuskeywords_set.values_list('word', flat=True)
        print words
        return words
        
    def find_matching_items(self,keywords):
        result = set()
        for key in keywords:
            matches = Corpuskeywords.objects.filter(word__word__contains=key).values("corpus", "corpus__title")
            MatchingItem = namedtuple('MatchingItem', ["corpus", "title"])
            for listitem in matches:
                result.add(MatchingItem(corpus=listitem["corpus"], title=listitem["corpus__title"]))
        print result

#    def  

def test():
    corp = Corpus()
    corp.get_keywords_for_item(MCorpus.objects.order_by('?')[0].id)
    corp.find_matching_items(("microsoft","apple","wireless"))
    
def load_generate_and_add_corpus_data():
    corp = Corpus()
    corp.build_corpus()
    corp.count_words_and_store()
    corp.calculate_keywords_for_all()
    
if __name__ == '__main__':
    load_generate_and_add_corpus_data()
    test()
