from django.core.management.base import BaseCommand
from panfeed.models import AcademicFeeds, Corpus

import feedparser
import urllib2
import datetime
from progressbar import ProgressBar as PB

class Command(BaseCommand):

    help = 'Grabs new items from feeds in the database.'

    def handle(self, *args, **options):
        build_corpus()

    
def build_corpus():
    #### Builds a corpus of documents from a set of feeds.

    #c.execute("""SELECT url,toplevel FROM feeds""")

    for feed in PB()(AcademicFeeds.objects.all()):
        try:
            page = urllib2.urlopen(feed.url)
            parsedfeed = feedparser.parse(page)
            for item in parsedfeed.entries:
                if not Corpus.objects.filter(url=item.link, feed=feed.url).exists():
                    try:
                        d = datetime.datetime(*(item.date_parsed[0:6]))
                    except AttributeError:
                        d=datetime.datetime.now()
                    try:
                        Corpus.objects.create(title=item.title,description=item.description,url=item.link,feed=feed.url,length=len(item.description+item.title),date=d,toplevel=feed.toplevel)
                    except Exception as e:
                        print(e)
        except urllib2.URLError:
            print "Error getting page: ", feed.url
