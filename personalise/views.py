# Create your views here.
from django.core.context_processors import csrf
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseForbidden
from django.db import connection, transaction
from feed import PersonalFeed
import urllib2
import feedparser
import json
import sys
from urlparse import urlparse
from personalise.models import Feeds,Journals,JournalFeeds,Corpus,Corpuskeywords,Issue,IssueItem
from django.contrib.auth.models import User
from personalise.urltorss2 import ItemMaker
#import personalise.models
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.template import RequestContext
import pprint
from django.contrib.auth.decorators import login_required

def home(request):
    p = { 'title':'PANFeed', 'content':render_to_string('index.html') }
    return render_to_response('template.html', { 'page': p }, context_instance=RequestContext(request))

def about(request):
    p = { 'title':'About', 'content':render_to_string('about.html') }
    return render_to_response('template.html', { 'page': p }, context_instance=RequestContext(request))

def crawlme(request):
    p = { 'title':'Crawl Me', 'content':render_to_string('crawlme.html') }
    return render_to_response('template.html', { 'page': p }, context_instance=RequestContext(request))
    
@login_required
def createjournal(request):
    journal = Journals.objects.create(title="", owner=request.user)
    return HttpResponseRedirect("".join(['/managejournal/',str(journal.journalid)]))

@login_required
def managejournal(request,journalid):
    journal = Journals.objects.get(journalid=journalid, owner=request.user)

    if (not journal):
        p = { 'title':'Manage Journal', 'content':'This journal does not exist or you do not have permission to edit it.' }
        return render_to_response('template.html', { 'page':p }, context_instance=RequestContext(request))

    feeds = JournalFeeds.objects.filter(journalid=journalid)
    feed_list = ""

    for feed in feeds:
        feed_list = "\n".join([feed_list, feed.feedurl])

    p = { 'title':'Manage Journal', 'content':render_to_string('managejournal.html', { 'journalid':journalid, 'title':journal.title, 'description':journal.description, 'source_feeds':feed_list }) }
    return render_to_response('template.html', { 'page': p }, context_instance=RequestContext(request))

@login_required
def savejournal(request):
    journal = get_object_or_404( Journals, journalid=int(request.POST['journalid']) )

    if journal.owner != request.user:
        return HttpResponseForbidden("You do not have permission to edit this jounral.")
    
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
    return HttpResponseRedirect('/myfeeds')
        
def journallist(request):
    journals = Journals.objects.all();

    journal_list = []
    journal_list.append('<h2>PANFeed Journals</h2>')
    journal_list.append('<p>PANFeed Journals are mash-ups of other feeds created by users. They will often have a strong theme and clear purpose. As with all PANFeeds they are customised for personal maganzine readers so journals will always look engaging.</p>')
    
    journal_list.append('<ul class="journal_list">')
    for journal in journals:
        journal_list.append('<li>{1} <a target="_blank" href="/journal/{1}">View</a></li>'.format(journal.journalid, journal.title))
    journal_list.append('</ul>')

    p = { 'title':'Journals', 'content':"\n".join(journal_list) }
    return render_to_response('template.html', { 'page':p }, context_instance=RequestContext(request))

@login_required
def myfeeds(request):
    journals = Journals.objects.filter(owner=request.user);

    lists = []
    lists.append('<h2>My PANFeed Journals</h2>')
    lists.append('<p>A PANFeed Journal allows you to combine a set of existing news feeds from websites, blogs and repositories. The outcome is a rolling news feed that is taylored to your content. You can then add this news feed to your website, feed reader or personalised magazine software.</p>')
    lists.append('<p><a href="/createjournal">Create a new journal</a></p>')
    
    lists.append('<ul class="lists">')
    for journal in journals:
        lists.append('<li>{1} <a target="_blank" href="/journal/{0}">View</a> <a href="/managejournal/{0}">Edit</a></li>'.format(journal.journalid, journal.title))
    lists.append('</ul>')


    issues = Issue.objects.filter(owner=request.user);
    lists.append('<h2>My PANFeed Issues</h2>')
    lists.append('<p>A PANFeed Issue is a carefully taylored news feed hand curated by you. You select web pages of interest to appear as items on your new feed. Add your own editorials and notes from your blog and customize the titles, descriptions and images which apear in the feed. You have complete control.</p>')
    lists.append('<p><a href="/createissue">Create a new issue</a></p>')
    
    lists.append('<ul class="lists">')
    for issue in issues:
        lists.append('<li>{1}<a target="_blank" href="/issue/{0}">View</a><a href="/manageissue/{0}">Edit</a></li>'.format(issue.id, issue.title))
    lists.append('</ul>')

    p = { 'title':'My Feeds', 'content':"\n".join(lists) }
    return render_to_response('template.html', { 'page':p }, context_instance=RequestContext(request))

def journal(request, journalid):
    journal = Journals.objects.get( journalid=journalid )
    
    if (not journal):
        return HttpResponse("Journal not found")

    feeds = JournalFeeds.objects.filter(journalid=journal.journalid)
    items = Corpus.objects.filter(feed__in=feeds.values_list("feedurl", flat=True)).order_by("-date")[:3]
        
    return HttpResponse("".join(str(items.values_list("date", flat=True))), context_instance=RequestContext(request))

@login_required
def createissue(request):
    issue = Issue.objects.create(title="", owner=request.user)
    return HttpResponseRedirect('/manageissue/' + str(issue.id))

@login_required
def manageissue(request,issueid):
    pagetitle = "Manage Issue"
    issue = Issue.objects.get(id=issueid, owner=request.user)

    if (not issue):
        p = { 'title':pagetitle, 'content':'This issue does not exist or you do not have permission to edit it.' }
        return render_to_response('template.html', { 'page':p }, context_instance=RequestContext(request))

    p = { 'title':pagetitle, 'content':render_to_string('manageissue.html', { 'issueid':issueid, 'title':issue.title, 'description':issue.description }) }
    return render_to_response('template.html', { 'page': p }, context_instance=RequestContext(request))

def issueitems(request, issueid):
    itemlist = [];
    for item in IssueItem.objects.filter(issueid=issueid):
        itemlist.append({'title':item.title, 'url':item.url, 'description':item.description, 'img':item.img})
    return HttpResponse(json.dumps(itemlist), mimetype="application/json", context_instance=RequestContext(request))

@login_required
def saveissue(request):
    pagetitle = "Save Issue"
    issue = Issue.objects.get( id=int(request.POST['issueid']), owner=request.user)

    if (not issue):
        p = { 'title':pagetitle, 'content':'This issue does not exist or you do not have permission to edit it.' }
        return render_to_response('template.html', { 'page':p }, context_instance=RequestContext(request))

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

    return HttpResponseRedirect('/myfeeds')

def issuelist(request):
    issues = Issue.objects.all();

    issue_list = []
    issue_list.append('<h2>PANFeed issues</h2>')
    issue_list.append('<p>PANFeed Issues are collections of resources curated by users. They will often have a strong theme and clear purpose. As with all PANFeeds they are customised for personal maganzine readers so issues will always look engaging.</p>')
    issue_list.append('<p><a href="/createissue">Create a new issue</a></p>')
    
    issue_list.append('<ul class="issue_list">')
    for issue in issues:
        issue_list.append('<li>{1}<a target="_blank" href="/issue/{0}">View</a></li>'.format(issue.id, issue.title))
    issue_list.append('</ul>')

    p = { 'title':'Issues', 'content':"\n".join(issue_list) }
    return render_to_response('template.html', { 'page':p }, context_instance=RequestContext(request))

def urltoitem(request):
    itemmaker = ItemMaker()
    itemmaker.parse_url(request.REQUEST["url"])
    return HttpResponse(json.dumps({ 'title':itemmaker.title, 'description':itemmaker.p, 'img':itemmaker.img }), mimetype="application/json")

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
    return render_to_response('template.html', {'page':p }, context_instance=RequestContext(request))

@login_required
def login_redirect(request):
    return redirect("/myfeeds")


