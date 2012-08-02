from django.core.management.base import BaseCommand
from panfeed.models import AcademicFeeds, Corpus
from xml.sax import SAXException
from contextlib import closing

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
            with closing(urllib2.urlopen(feed.url)) as page:
                parsedfeed = feedparser.parse(page)
                for item in parsedfeed.entries:
                    if hasattr(item,"date_parsed"):
                        d = datetime.datetime(*(item.date_parsed[0:6]))
                    else:
                        d=datetime.datetime.now()
                    try:
                        defaults = dict(
                            title=item.title,
                            description=item.description,
                            date=d
                        )
                        corpus, created = Corpus.objects.get_or_create(url=item.link, feed=feed, defaults=defaults)
                        if not created:
                            corpus.title=item.title
                            corpus.description=item.description
                            corpus.date=d
                            corpus.save()
                    except Exception as e:
                        print(e)
        except urllib2.URLError:
            print "Error getting page: ", feed.url
        except SAXException:
            print "Error parsing page: ", feed.url
