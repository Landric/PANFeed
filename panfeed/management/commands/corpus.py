## A corpus is a body of work consisting of many Documents
from panfeed.models import Corpus as MCorpus

from django.db.models import Q
from django.core.management.base import BaseCommand

import feedparser
import urllib2

import string
import unicodedata
import math
import re
import datetime

from progressbar import ProgressBar as PB

class Command(BaseCommand):

    help = 'Loads all the corpus stuff'

    def handle(self, *args, **options):
        print("Building Corpus")
        build_corpus()

def build_corpus():
    #### Builds a corpus of documents from a set of feeds.
    
    feeds = open("newfeed.txt", "r")
    for feedurl in PB()(list(feeds)):
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
                            date = dStr
                        ).save()
                        
                except Exception as e:
                    print(e)
        except urllib2.URLError:
            print "Error getting page: ", feedurl

    feeds.close()
