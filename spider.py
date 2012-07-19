from django.core.management import setup_environ
import settings

setup_environ(settings)
from panfeed.models import SpiderToDo, SpiderDone, SpiderRSS 
import urllib2
import feedparser
import lxml.html
import urlparse
import datetime
import sys
#from sets import Set

#Globals
CRAWLER_NAME = 'RSSCrawl'
STARTURL = 'http://www.soton.ac.uk/'
DOMAIN = 'soton.ac.uk'
#STARTURL = 'http://blogs.ecs.soton.ac.uk/'
#DOMAIN = 'blogs.ecs.soton.ac.uk'
rssmimetypes = set(["application/rss+xml", "application/xhtml+xml", "text/xml", "text/rss+xml"])
htmlmimetypes = set(["text/html"])

def main():

    SpiderToDo(STARTURL).save()
    
    while SpiderToDo.objects.count() > 0:
        todo = SpiderToDo.objects.filter()[:1][0]
        process_url(todo.pageurl)
#        try:
#            process_url(todo.pageurl)
#        except:
#            print "foo"
#            sys.stderr.write("Unexpected error:" + str(sys.exc_info()[0]) + "\n")
        todo.delete()
        

class HeadRequest(urllib2.Request):
    ## Custom Headrequest Request class for urllib2 to get page headers.
    def get_method(self):
        return "HEAD"

def getPageMime(url):
    
    #########################################
    #Determines the mimetype of the given url.
    #########################################
    
    try:
        response = urllib2.urlopen(HeadRequest(url), timeout = 20)
        content = response.info()["content-type"]
        contents = content.split(";")
        return contents[0]
    except:
        return None
    
def parseforURLs(page, address):

    #########################################
    #Takes a page and its url, returns a list of absolute urls linked to on the page.
    #########################################

    try:
        webpage = lxml.html.fromstring(page)
        urls = webpage.xpath('//a/@href')
        validurls = []
        for item in urls:
            if urlparse.urljoin(address, item).startswith('http'):
                validurls.append(urlparse.urljoin(address, item))
        return validurls
    except lxml.etree.XMLSyntaxError:
        return []

def process_url(url):

    #########################################
    #Processes a url for extracting links or finding feeds.
    #########################################

    try: 
        url = url.encode('latin-1') 
    except UnicodeEncodeError: 
        try: 
            url = url.encode('utf-8') 
        except UnicodeEncodeError: 
            return
    
    SpiderDone(url).save()
    mime = getPageMime(url)

    if mime not in htmlmimetypes and mime not in rssmimetypes:
        return

    try:
        response = urllib2.urlopen(url)
    except:
        sys.stderr.write( "Error reading: " + str(url) + "\n"+ sys.exc_info()[0] + "\n" );
        return

    page = response.read()
    address = response.url


#assumes that if something parses as rss it cant also parse as html        
    if mime in rssmimetypes:
        if feedparser.parse(page).version:
            SpiderRSS(url).save()
        return
       
    if mime in htmlmimetypes:
        for item in parseforURLs(page, address):
            # URL field is max length 255 - you can't have a text field as PK - so deal with it
            if len(item) < 255 :
                if SpiderDone.objects.filter(doneurl=item).count() == 0:
        #note that if we start adding URLs anywhere else this check should be removed from here
                    if (DOMAIN in urlparse.urlparse(item).netloc):
                        SpiderToDo(item).save()


if __name__ == "__main__":
    main()


