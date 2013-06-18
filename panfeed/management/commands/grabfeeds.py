from django.core.management.base import BaseCommand
from panfeed.models import AcademicFeeds, Corpus
from xml.sax import SAXException
from contextlib import closing

import feedparser
import urllib2
import datetime
import httplib
from progressbar import ProgressBar as PB

import traceback

class Command(BaseCommand):

    help = 'Grabs new items from feeds in the database.'

    def handle(self, *args, **options):
        build_corpus()

def build_corpus():
    #### Builds a corpus of documents from a set of feeds.

    #c.execute("""SELECT url,toplevel FROM feeds""")

    for feed in PB()(AcademicFeeds.objects.all()):
        try:
            cache_values = {}
            if feed.etag is not None:
                cache_values["etag"] = feed.etag
            if feed.modified is not None:
                cache_values["modified"] = feed.modified.strftime('%a, %d %b %Y %H:%M:%S %Z')

            parsedfeed = feedparser.parse(feed.url, **cache_values)
            if parsedfeed.status == httplib.NOT_MODIFIED:
                continue
            else:
                old = {
                    "etag":feed.etag,
                    "modified": feed.modified
                }
                feed.etag = getattr(parsedfeed, "etag", None)
                mod = getattr(parsedfeed, "modified_parsed", None)
                if mod is not None:
                    feed.modified = datetime.datetime(*mod[0:6])
                feed.save()

                new = {
                    "etag":feed.etag,
                    "modified":feed.modified
                }

                if old["etag"] == new["etag"] or old["modified"] >= new["modified"]:
                    continue

            for item in parsedfeed.entries:
                d = getattr(item, "date_parsed", None)
                defaults = {
                    "title":item.title,
                    "description":item.description,
                    "date":datetime.datetime(*(d[0:6])) if d else datetime.datetime.now()
                }
                corpus, created = Corpus.objects.get_or_create(url=item.link, feed=feed, defaults=defaults)
                if not created:
                    if d:
                        del defaults["date"]
                    update(corpus, defaults)
        except urllib2.URLError:
            print "Error getting page: ", feed.url
        except SAXException:
            print "Error parsing page: ", feed.url


def update(instance, fields):
    updated = False
    for key, value in fields.items():
        old = getattr(instance, key)
        if not old == value:
            setattr(instance, key, value)
            updated = True
    if updated:
        instance.save()