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
from personalise.models import Feeds,Digests,DigestFeeds,Corpus,Corpuskeywords,Issue,IssueItem
from django.contrib.auth.models import User
from personalise.urltorss2 import ItemMaker
from django.contrib.sites.models import Site
#import personalise.models
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.template import RequestContext
import pprint
from django.contrib.auth.decorators import login_required

def home(request):
    return render_to_response('index.html', context_instance=RequestContext(request))

def about(request):
    return render_to_response('about.html', context_instance=RequestContext(request))

def crawlme(request):
    return render_to_response('template.html', context_instance=RequestContext(request))
    
@login_required
def createdigest(request):
    digest = Digests.objects.create(title="", owner=request.user)
    return HttpResponseRedirect("".join(['/managedigest/',str(digest.digestid)]))

@login_required
def managedigest(request,digestid):
    digest = Digests.objects.get(digestid=digestid, owner=request.user)

    if (not digest):
        p = { 'title':'Manage Digest', 'content':'This digest does not exist or you do not have permission to edit it.' }
        return render_to_response('template.html', { 'page':p }, context_instance=RequestContext(request))

    feeds = DigestFeeds.objects.filter(digestid=digestid)
    feed_list = ""

    for feed in feeds:
        feed_list = "\n".join([feed_list, feed.feedurl])

    public = ""
    if digest.public:
        public = "checked='checked'"


    p = { 'title':'Manage Digest', 'content':render_to_string('managedigest.html', { 'digestid':digestid, 'title':digest.title, 'description':digest.description, 'source_feeds':feed_list, 'siteUrl':Site.objects.get_current().domain, "public":public, 'objUrl':digest.get_absolute_url() }) }
    return render_to_response('template.html', { 'page': p }, context_instance=RequestContext(request))

@login_required
def savedigest(request):
    digest = get_object_or_404( Digests, digestid=int(request.POST['digestid']) )

    if digest.owner != request.user:
        return HttpResponseForbidden("You do not have permission to edit this jounral.")
    
    digest.title = request.POST['title']
    digest.description = request.POST['description']
    if 'public' in request.REQUEST :
        digest.public = request.POST['public']
    digest.save();
    
    DigestFeeds.objects.filter(digestid=digest.digestid).delete()
    feeds = str(request.POST['source_feeds']).splitlines()
    for url in feeds:
        hostname = urlparse(url).hostname 
        if (hostname.endswith(".ac.uk") or hostname.endswith(".edu")):
            if (Feeds.objects.filter(url=url).count()==0):
                    Feeds.objects.create(url=url,toplevel=hostname)
        DigestFeeds.objects.create(digestid=digest.digestid, feedurl=url)
    return HttpResponseRedirect('/myfeeds')
        
def digestlist(request):
    d = Digests.objects.filter(public=True)
        
    return render_to_response('digests.html', {'digests' : d}, context_instance=RequestContext(request))

@login_required
def myfeeds(request):
    digests = Digests.objects.filter(owner=request.user);

    lists = []
    lists.append('<h2>My PANFeed Digests</h2>')
    lists.append('<p>A PANFeed Digest allows you to combine a set of existing news feeds from websites, blogs and repositories. The outcome is a rolling news feed that is taylored to your content. You can then add this news feed to your website, feed reader or personalised magazine software.</p>')
    lists.append('<p><a href="/createdigest">Create a new digest</a></p>')
    
    lists.append('<ul class="lists">')
    for digest in digests:
        lists.append('<li>{1} <a target="_blank" href="/digest/{0}">View</a> <a href="/managedigest/{0}">Edit</a></li>'.format(digest.digestid, digest.title))
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

def digest(request, digestid):
    digest = Digests.objects.get( digestid=digestid )
    
    if (not digest):
        return HttpResponse("Digest not found")

    feeds = DigestFeeds.objects.filter(digestid=digest.digestid)
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

    public = ""
    if issue.public:
        public = "checked='checked'"

    p = { 'title':pagetitle, 'content':render_to_string('manageissue.html', { 'issueid':issueid, 'title':issue.title, 'description':issue.description, 'siteUrl':Site.objects.get_current().domain, "public":public, 'objUrl':issue.get_absolute_url() } ) }
    return render_to_response('template.html', { 'page': p }, context_instance=RequestContext(request))

def issueitems(request, issueid):
    itemlist = [];
    for item in IssueItem.objects.filter(issueid=issueid).order_by('ordernumber'):
        itemlist.append({'title':item.title, 'url':item.url, 'description':item.description, 'img':item.img})
    return HttpResponse(json.dumps(itemlist), mimetype="application/json")

@login_required
def saveissue(request):
    sys.stderr.write("i get here")
    pagetitle = "Save Issue"
    issue = get_object_or_404( Issue, id=int(request.POST['issueid']) )

    if issue.owner != request.user:
        return HttpResponseForbidden("You do not have permission to edit this issue.")

    if (not issue):
        p = { 'title':pagetitle, 'content':'This issue does not exist or you do not have permission to edit it.' }
        return render_to_response('template.html', { 'page':p }, context_instance=RequestContext(request))

    issue.title = request.REQUEST['title']
    issue.description = request.REQUEST['description']
    if 'public' in request.REQUEST :
        issue.public = request.REQUEST['public']
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
        item.ordernumber = i;
        item.save()

    return HttpResponseRedirect('/myfeeds')

def issuelist(request):
    issues = Issue.objects.filter(public=True)

    issue_list = []
    issue_list.append('<h2>PANFeed issues</h2>')
    issue_list.append('<p>PANFeed Issues are collections of resources curated by users. Each item is hand picked for you by the Issue\'s creator. As with all PANFeeds they are customised for personal maganzine readers so issues will always look engaging.</p>')
    
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


