from django.core.management.base import BaseCommand, CommandError
from personalise.models import AcademicFeeds, Corpus, Corpuskeywords, Tf, Words
from django.db import connection
import feedparser
import urllib2
import string
import unicodedata
import math
import re
import datetime
import time

class Command(BaseCommand):

    help = 'Grabs new items from feeds in the database.'

    def handle(self, *args, **options):
        corp = corpus_obj()
        corp.build_corpus()
        corp.count_words_and_store()
        corp.calculate_keywords_for_all()

class corpus_obj():
    
                
    def build_corpus(self):
        #### Builds a corpus of documents from a set of feeds.
    
        #c.execute("""SELECT url,toplevel FROM feeds""")
        feeds = AcademicFeeds.objects.all()
        for feedurl in feeds:
            print feedurl.url
            try:
                page = urllib2.urlopen(feedurl.url)
                feed = feedparser.parse(page)
                for item in feed.entries:
                    if (Corpus.objects.filter(url=item.link).filter(feed=feedurl.url).count()==0):
                        try:
                            d = datetime.datetime(*(item.date_parsed[0:6]))
                        except AttributeError:
                            d=datetime.datetime.now()
                        print item.title+" "+item.link
                        Corpus.objects.create(title=item.title,description=item.description,url=item.link,feed=feedurl.url,length=len(item.description+item.title),date=d,toplevel=feedurl.toplevel)
            except urllib2.URLError:
                print "Error getting page: ", feedurl.url
        
    def count_words_and_store(self):
        ### Performs a wordcount of each document and stores cumulative word count 
        ### and also wordcount specific to that document/word combination.
        corpusses = Corpus.objects.all()
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
                    dbword.save()
                    Tf(word = dbword, corpus = corpus, count = freq[word]).save()                
                
            
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
        corpusses = Corpus.objects.all()
        global corpussize
        corpussize = Corpus.objects.count()
        
        for corpus in corpusses:
            if not Corpuskeywords.objects.filter(corpus=corpus).exists():
                ### For each item from feeds
                worddata = {}
                words = Tf.objects.filter(corpus=corpus).values('word','count')
                ### For each word in that item
                for word in words:
                    wordcount = Words.objects.get(word['word']).count
                    worddata[word['word']] = (word['count'], wordcount)
                keywords = self.calculate_tfidf(worddata)
                topkeys = keywords[:10]
                for rank, word in topkeys:
                    Corpuskeywords(corpus=corpus, word=word, rank=rank).save()                
        
    def calculate_tfidf(self,worddata):
        wordlist = []
        for word in worddata:
            idf = math.log(corpussize/(worddata[word][1]+1.0))
            tfidf = idf * worddata[word][0]
            wordlist.append((tfidf,word))
        return sorted(wordlist, reverse=True)
        
    def get_keywords_for_item(self,itemid):
        words = Corpuskeywords.objects.filter(corpus__id=itemid).values_list('word', flat=True)
        print words
        return words
        
    def find_matching_items(self,keywords):
        result = set()
        for key in keywords:
            matches = Corpuskeywords.objects.filter(word__contains="foo").values("corpus", "corpus__title")
            for listitem in matches:
                result.add(listitem)
        print result
