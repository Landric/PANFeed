# Create your views here.
from django.core.context_processors import csrf
#from password_required.decorators import password_required
from django.http import HttpResponse,HttpResponseRedirect
from django.db import connection, transaction
from feed import PersonalFeed
import urllib2
import feedparser
import json
import sys
from urlparse import urlparse
from personalise.models import Feeds,Journals,JournalFeeds,Corpus,Corpuskeywords,Issue,IssueItem
from personalise.urltorss2 import ItemMaker
#import personalise.models
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
import pprint

def home(request):
    p = { 'title':'PANFeed', 'content':render_to_string('index.html') }
    return render_to_response('template.html', { 'page': p })

def about(request):
    p = { 'title':'About', 'content':render_to_string('about.html') }
    return render_to_response('template.html', { 'page': p })

def crawlme(request):
    p = { 'title':'Crawl Me', 'content':render_to_string('crawlme.html') }
    return render_to_response('template.html', { 'page': p })
    
def createjournal(request):
    journal = Journals.objects.create(title="")
    return HttpResponseRedirect("".join(['/managejournal/',str(journal.journalid)]))

def managejournal(request,journalid):
    journal = Journals.objects.get(journalid=journalid)

    if (not journal):
        p = { 'title':'Manage Journal', 'content':'This journal does not exist' }
        return render_to_response('template.html', { 'page':p })

    feeds = JournalFeeds.objects.filter(journalid=journalid)
    feed_list = ""

    for feed in feeds:
        feed_list = "\n".join([feed_list, feed.feedurl])

    p = { 'title':'Manage Journal', 'content':render_to_string('managejournal.html', { 'journalid':journalid, 'title':journal.title, 'description':journal.description, 'source_feeds':feed_list }) }
    return render_to_response('template.html', { 'page': p })

def savejournal(request):
    journal = Journals.objects.get( journalid=int(request.POST['journalid']) )

    if (not journal):
        p = { 'title':'Save Journal', 'content':'This journal does not exist' }
        return render_to_response('template.html', { 'page':p })
    
    journal.title = request.POST['title']
    journal.description = request.POST['description']
    journal.save();
    
    JournalFeeds.objects.filter(journalid=journal.journalid).delete()
    feeds = str(request.POST['source_feeds']).splitlines()
    for url in feeds:
        hostname = urlparse(url).hostname 
        if (hostname.endswith(".ac.uk") or hostname.endswith(".edu")):
            if (Feeds.objects.filter(url=url).count()==0):
                    Feeds.objects.create(url=url,toplevel=hostname)
        JournalFeeds.objects.create(journalid=journal.journalid, feedurl=url)
    return HttpResponseRedirect('/journallist/')
        
def journallist(request):
    journals = Journals.objects.all();

    journal_list = []
    journal_list.append('<h2>PANFeed Journals</h2>')
    journal_list.append('<p>PANFeed Journals are mash-ups of other feeds created by users. They will often have a strong theme and clear purpose. As with all PANFeeds they are customised for personal maganzine readers so journals will always look engaging.</p>')
    journal_list.append('<p><a href="/createjournal">Create a new journal</a></p>')
    
    journal_list.append('<ul class="journal_list">')
    for journal in journals:
        journal_list.append('<li><a href="">{1}</a></td> <td><a target="_blank" href="/journal/{0}">View</a></td> <td><a href="/managejournal/{0}">Edit</a></li>'.format(journal.journalid, journal.title))
    journal_list.append('</ul>')

    p = { 'title':'PANFeed Journals', 'content':"\n".join(journal_list) }
    return render_to_response('template.html', { 'page':p })

def journal(request, journalid):
    journal = Journals.objects.get( journalid=journalid )
    
    if (not journal):
        return HttpResponse("Journal not found")

    feeds = JournalFeeds.objects.filter(journalid=journal.journalid)
    items = Corpus.objects.filter(feed__in=feeds.values_list("feedurl", flat=True)).order_by("-date")[:3]
        
    return HttpResponse("".join(str(items.values_list("date", flat=True))))

def createissue(request):
    issue = Issue.objects.create(title="")
    return HttpResponseRedirect('/manageissue/' + str(issue.id))

def manageissue(request,issueid):
    pagetitle = "Manage Issue"
    issue = Issue.objects.get(id=issueid)

    if (not issue):
        p = { 'title':pagetitle, 'content':'This issue does not exist' }
        return render_to_response('template.html', { 'page':p })

    p = { 'title':pagetitle, 'content':render_to_string('manageissue.html', { 'issueid':issueid, 'title':issue.title, 'description':issue.description }) }
    return render_to_response('template.html', { 'page': p })

def issueitems(request, issueid):
    itemlist = [];
    for item in IssueItem.objects.filter(issueid=issueid):
        itemlist.append({'title':item.title, 'url':item.url, 'description':item.description, 'img':item.img})
    return HttpResponse(json.dumps(itemlist), mimetype="application/json")

def saveissue(request):
    pagetitle = "Save Issue"
    issue = Issue.objects.get( id=int(request.POST['issueid']) )

    if (not issue):
        p = { 'title':pagetitle, 'content':'This issue does not exist' }
        return render_to_response('template.html', { 'page':p })

    issue.title = request.REQUEST['title']
    issue.description = request.REQUEST['description']
    issue.save();

    IssueItem.objects.filter(issueid=issue.id).delete()

    for i, val in enumerate(request.REQUEST.getlist("item-title")) :
        pprint.pprint(request.REQUEST.getlist("item-url"), sys.stderr)
        
        if IssueItem.objects.filter(issueid=issue.id, url=request.REQUEST.getlist("item-url")[i]).count() > 0:
            item = IssueItem.objects.filter(issueid=issue.id, url=request.REQUEST.getlist("item-url")[i])[0]
        else:
            item = IssueItem.objects.create(issueid=issue.id)

        item.url = request.REQUEST.getlist("item-url")[i]
        item.title = request.REQUEST.getlist("item-title")[i]
        item.description = request.REQUEST.getlist("item-description")[i]
        item.img = request.REQUEST.getlist("item-img")[i]
        item.save()

    return HttpResponseRedirect('/issuelist')

def issuelist(request):
    issues = Issue.objects.all();

    issue_list = []
    issue_list.append('<h2>PANFeed issues</h2>')
    issue_list.append('<p>PANFeed Issues are collections of resources curated by users. They will often have a strong theme and clear purpose. As with all PANFeeds they are customised for personal maganzine readers so issues will always look engaging.</p>')
    issue_list.append('<p><a href="/createissue">Create a new issue</a></p>')
    
    issue_list.append('<ul class="issue_list">')
    for issue in issues:
        issue_list.append('<li>{1}<a target="_blank" href="/issue/{0}">View</a><a href="/manageissue/{0}">Edit</a></li>'.format(issue.id, issue.title))
    issue_list.append('</ul>')

    p = { 'title':'PANFeed Journals', 'content':"\n".join(issue_list) }
    return render_to_response('template.html', { 'page':p })

def urltoitem(request):
    itemmaker = ItemMaker()
    itemmaker.parse_url(request.REQUEST["url"])
    return HttpResponse(json.dumps({ 'title':itemmaker.title, 'description':itemmaker.p, 'img':itemmaker.img }), mimetype="application/json")

#@password_required
def submit(request):
   
    feeds = str(request.POST['urls']).splitlines()

    for url in feeds:
        hostname = urlparse(url).hostname 
        if (hostname.endswith(".ac.uk") or hostname.endswith(".edu")):
            if (feedparser.parse(url).version):
                if (Feeds.objects.filter(url=url).count()==0):
                   Feeds.objects.create(url=url,toplevel=hostname)

    content = '''Feeds have now been added.'''
    p = {'title':'Submitted', 'content':content}
    return render_to_response('template.html', {'page':p })


