from django.core.management.base import BaseCommand, CommandError
from personalise.models import Feeds
import MySQLdb
import feedparser
import urllib2
import string
import unicodedata
import math
import re
import datetime
import urlparse

class Command(BaseCommand):

    help = 'Stores new feeds from feeds.txt file.'

    def handle(self, *args, **options):
        corp = Corpus()
        corp.initDB()
        corp.build_feeds()

class Corpus():
    
    def initDB(self):
        ### Execute this first to open DB connection.
        print "Init"
        self.db=MySQLdb.connect(passwd="",db="tfidf",charset = "utf8",use_unicode=True)
        self.db.set_character_set("utf8")
        
    def build_feeds(self):
        #### Builds a corpus of documents from a set of feeds.
        
        feeds = open("newfeed.txt", "r")
        for feedurl in feeds:
            c=self.db.cursor()
            if (c.execute("""SELECT * FROM feeds WHERE url = %s""",(feedurl))==0):
                c.execute("""INSERT INTO feeds (url,toplevel) VALUES (%s,%s)""",(feedurl, urlparse.urlparse(feedurl).hostname)) 
        feeds.close()
        
