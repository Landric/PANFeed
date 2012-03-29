from django.core.management.base import BaseCommand, CommandError
from personalise.models import Feeds,Corpus
import MySQLdb
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
        corp.initDB()
        corp.build_corpus()
        corp.count_words_and_store()
        corp.calculate_keywords_for_all()

class corpus_obj():
    
    def initDB(self):
        ### Execute this first to open DB connection.
        print "Init"
        self.db=MySQLdb.connect(user="root",passwd="",db="tfidf",charset = "utf8",use_unicode=True)
        self.db.set_character_set("utf8")
        
    def build_corpus(self):
    #### Builds a corpus of documents from a set of feeds.
    
        c=self.db.cursor()
	#c.execute("""SELECT url,toplevel FROM feeds""")
        feeds = Feeds.objects.all()
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
        c=self.db.cursor()
        c.execute("""SELECT title,description,id FROM corpus""")
        text = c.fetchall()
        for item in text:
            if (c.execute("""SELECT itemid FROM tf WHERE itemid=%s""",(item[2]))==0):
                totaltext = unicodedata.normalize('NFKD',(item[0]+' '+item[1])).encode('ascii','ignore')
                totaltext = self.__remove_extra_spaces(self.__remove_html_tags(totaltext))
                freq = self.__get_word_frequencies(self.__remove_single_characters((''.join((x for x in (totaltext.lower()) if x not in string.punctuation)))))
                for word in freq:
                    itemid = item[2]
                    #print word, " ", freq[word], " ", itemid
                    c.execute("""INSERT INTO words (word,count) VALUES (%s,%s) ON DUPLICATE KEY UPDATE count=count+1""",(word,1))
                    c.execute("""INSERT INTO tf (word,itemid,count) VALUES (%s,%s,%s)""",(word,itemid,freq[word]))
                
                
            
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
        c=self.db.cursor()
        c.execute("""SELECT id FROM corpus""")
        itemids = c.fetchall()
        global corpussize
        corpussize = len(itemids)
        
        for itemid in itemids:
            if (c.execute("""SELECT itemid FROM corpuskeywords WHERE itemid=%s""",(itemid[0]))==0):
        ### For each item from feeds
                worddata = {}
                c.execute("""SELECT word,count FROM tf WHERE itemid=%s""",(itemid))
                ### For each word in that item
                for word in c.fetchall():
                    c.execute("""SELECT count FROM words WHERE word=%s""",(word[0]))
                    worddata[word[0]] = (word[1], c.fetchall()[0][0])
                keywords = self.calculate_tfidf(worddata)
                topkeys = keywords[:10]
                for key in topkeys:
                    c.execute("""INSERT INTO corpuskeywords (itemid,word,rank) VALUES (%s,%s,%s)""",(itemid[0],key[1],key[0]))
                
        
    def calculate_tfidf(self,worddata):
        wordlist = []
        for word in worddata:
            idf = math.log(corpussize/(worddata[word][1]+1.0))
            tfidf = idf * worddata[word][0]
            wordlist.append((tfidf,word))
        return sorted(wordlist, reverse=True)
        
    def get_keywords_for_item(self,itemid):
        c=self.db.cursor()
        c.execute("""SELECT word FROM corpuskeywords WHERE itemid=%s""",(itemid))
        print c.fetchall()
        return c.fetchall()
        
    def find_matching_items(self,keywords):
        c=self.db.cursor()
        result = set()
        for key in keywords:
            c.execute("""SELECT corpus.id,corpus.title FROM corpus,corpuskeywords WHERE corpus.id=corpuskeywords.itemid AND corpuskeywords.word LIKE %s""",(key))
            for listitem in c.fetchall():
                result.add(listitem)
        print result
