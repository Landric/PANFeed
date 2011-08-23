# Create your views here.
#from django.core.context_processors import csrf
from password_required.decorators import password_required
from django.http import HttpResponse
from django.db import connection, transaction
from models import Corpus,Corpuskeywords
from feed import PersonalFeed
import urllib2
import feedparser
from urlparse import urlparse
from personalise.models import Feeds
from django.shortcuts import render_to_response, get_object_or_404

def home(request):
    content = '''
    <h1>Welcome to PANFeed</h1>
	<p>PANFeed is a tool to help you take control of news feeds already existing on your university campus. It harvests feeds from university websites and uses them to build custom feeds of news you are actually interested in. The tool has a range of applications including personal custom news feeds, custom feeds for use in department websites or simply taking an inventory of your university feeds. Try out and take control of your news!</p>

	<h1>Try it out!</h1>
	<h4>PANFeed is in continuous development, and functionality may change or break without warning!  If you would like to give any feedback, please email panfeed[at]gmail[dot]com.  Thanks!</h4>
	<p>Enter some keywords separated by commas into the box below to create a custom news feed.</p>


	<div class="feed_gear">
	    <form onsubmit="return false;">
		<input type="text" id="keyword_input"><button type="submit" id="submit_keys" onclick="makeFeed()">Feed Me!</button><br /><br />
	     </form>
		<a id="google_link" href="http://fusion.google.com/add?source=atgs&feedurl=http%3A//panfeed.ecs.soton.ac.uk/find/apple"><img src="http://buttons.googlesyndication.com/fusion/add.gif" border="0" alt="Add to Google"></a>
		&nbsp;&nbsp;&nbsp;&nbsp;
		<a id="feed_link" href="http://panfeed.ecs.soton.ac.uk/find/apple" target="_blank">http://panfeed.ecs.soton.ac.uk/find/apple</a> 


	</div>

	<div id="feed_demo">  </div>

'''
    p = { 'title':'PANFeed', 'content':content }
    return render_to_response('template.html', { 'page': p })
#    return HttpResponse("Hello")

def about(request):
	content = '''<h1>About the Project</h1>

<h2>Who We Are</h2>
<p>We are a group of researchers based at the University of Southampton, in the Web And Internet Science research group.</p>

quid´Tyler has started vlogging! This is episode 1 (youtube.com)

submitted 1 hour ago by Krasso

    9 comments
    share
    save
    hide
    report<h2>What is PANFeed?</h2>
<p>PANFeed (Personal Academic News Feed) is a system spawned from the CampusROAR project, which is focused around making research more accessible, exciting and interesting, and to enable people to keep up to date on research in their areas of interest.</p>
<p>The purpose of PANFeed is to enable the creation of personalised, adaptive RSS feeds which are based on the news feeds available at your institution.  A crawler is used to find all RSS and Atom feeds under a University domain, which are then catalogued and analysed for keywords.  The PANFeed site can then be used to generate a personalised RSS feed based upon any set of keywords you provide.</p>

<h2>Contact</h2>
<p>To contact us:  <a href="mailto:pm5@ecs.soton.ac.uk">pm5@ecs.soton.ac.uk</a></p>
'''
	p = { 'title':'About', 'content':content }
	return render_to_response('template.html', { 'page': p })

def crawlme(request):
	content = '''<h1>How can my university be added?</h1>
	<p>At the moment we are monitoring the interest in PANFeed quite closely, in a friendly and personal way. If you would like us to add your university to the PANFeed service the please drop us an email at <a href="mailto:pm5@ecs.soton.ac.uk">pm5@ecs.soton.ac.uk</a>. In general we are trying to keep the news sources academic, as a result we would prefer to only harvest urls with a .ac.uk or .edu domain. We are reasonable people so if you have a good academic source at a different domain please still email us and well take a look.</p>

<h2>Add my feed!</h2>
<p>PANFeed is now able to take submissions of single feeds automatically. If you have a blog or repository or other RSS or Atom feed then we want to here from you. Your feed will be added to the queue of feeds we read and within the hour your feed will be crawlled, indexed and start appearing in the appropriate custom feeds. We only accept feeds from .ac.uk or .edu domains but if you have another source email us on the address above. </p> 

<p>To submit you feed simply copy its url into the box below. Remember your feed must be web accessible for us to index it. Happy feeding!</p>

<div class="feed_submission">
<FORM ACTION="/submit/" METHOD=POST>
	<textarea name=urls id="urls" ROWS=8 COLS=60>Paste feeds into here separated by newlines.</textarea> <INPUT TYPE=SUBMIT VALUE="Submit">
</FORM>
</div>
'''
	p = { 'title':'Crawl Me', 'content':content }
	return render_to_response('template.html', { 'page': p })
    
def find(request,keyword,sources):
    cursor = connection.cursor()
    words = keyword.split("_")
        
    sourcelist = sources.split("_")

    res = []
    for word in words:
        print word
        cursor.execute("SELECT corpus.* FROM corpus,corpuskeywords WHERE corpus.id=corpuskeywords.itemid AND (corpus.toplevel IN %s OR corpus.toplevel='all') AND corpuskeywords.word LIKE %s", (tuple(sourceids),[word]))
        results=[]
        results+=cursor.fetchall()

        for r in results:
            print r
            res+=(r[0],r[1],r[2],r[3],r[4],r[5])
            
    f = PersonalFeed(keyword)
    
    return HttpResponse(f)

#@password_required
def submit(request):
   
    feeds = str(request.POST['urls']).split("\\r\\")
    print feeds       
    for url in feeds:
        print urlparse(url)
        if (feedparser.parse(url).version):
            print Feeds.objects.filter(url=url).count()
            if (Feeds.objects.filter(url=url).count()==0):
                print "New feed added: " + url
                Feeds.objects.create(url=url,toplevel=urlparse(url).hostname)
    content = '''Feeds have now been added.'''
    p = {'title':'Submitted', 'content':content}
    return render_to_response('template.html', {'page':p })
