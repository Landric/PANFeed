# Create your views here.
from django.core.context_processors import csrf
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseForbidden, Http404
from django.db import connection, transaction
import urllib2
import feedparser
import json
import sys
from urlparse import urlparse
from personalise.models import AcademicFeeds,UserFeeds,Digest,Corpus,Corpuskeywords,Issue,IssueItem
from django.contrib.auth.models import User
from personalise.urltorss2 import ItemMaker
from django.contrib.sites.models import Site
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.template import RequestContext
import pprint
from django.contrib.auth.decorators import login_required
from forms import DigestForm, IssueForm
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


def home(request):
    return render_to_response('index.html', context_instance=RequestContext(request))

def about(request):
    return render_to_response('about.html', context_instance=RequestContext(request))

def crawlme(request):
    return render_to_response('crawlme.html', context_instance=RequestContext(request))
    
def faq(request):
    return render_to_response('faq.html', context_instance=RequestContext(request))

def findnews(request):
    return render_to_response('findnews.html', context_instance=RequestContext(request))

@login_required
def managedigest(request,digestid=None):
    feeds = []
    if request.method == 'POST':
        form = DigestForm(request.POST)
        if form.is_valid():

            if digestid is None:
                digest = form.save(commit=False)
                digest.owner = request.user
                digest.save()
            else:
		if Digest.objects.filter(digestid=int(digestid), owner = request.user).exists():
                    digest = form.save(commit=False)
                    digest.owner = request.user
		    digest.digestid = digestid
            
                else:
                    return HttpResponseForbidden("You do not have permission to edit this journal.")

            digest.feeds.clear()
            feeds = request.POST.getlist('url')
            invalid_feeds = []
            if not (feeds is None):
                for feed in feeds:
                    if feed.strip() != '':
                        validate = URLValidator(verify_exists=True)
			try:
			    validate(feed)
			except ValidationError, e:
			    invalid_feeds.append(feed)

            if invalid_feeds:
                content = 'The following feeds are invalud and could not be added to your digest. Please check they exist, and try again.'
                p = {'title':'Error', 'header':'Invalid Feeds', 'content':content, 'data':invalid_feeds}
                return render_to_response('error.html', {'page':p }, context_instance=RequestContext(request))

            else:
		for feed in feeds:
                    if feed != '':
   		        if UserFeeds.objects.filter(url=feed).exists():
                            digest.feeds.add(UserFeeds.objects.get(url=feed))
                        else:
                            digest.feeds.create(url=feed)           
                digest.save(force_update=True)

		unusedFeeds = UserFeeds.objects.exclude(pk__in=Digest.feeds.through.objects.values('userfeeds'))
		unusedFeeds.delete()

                return HttpResponseRedirect('/digestlist/')

        else:
            pass

    elif request.method == 'DELETE':
        digest = get_object_or_404( Digest, digestid=int(digestid) )

        if digest.owner != request.user:
            return HttpResponseForbidden("You do not have permission to edit this journal.")

        else:
            digest.delete()
            unusedFeeds = UserFeeds.objects.exclude(pk__in=Digest.feeds.through.objects.values('userfeeds'))
	    unusedFeeds.delete()

            return HttpResponseRedirect('/digestlist/')
 
    else:
        if digestid is None:
            form = DigestForm()
        else:
            digest = Digest.objects.get(digestid=digestid, owner=request.user)
            form = DigestForm(instance=digest)
            feeds = digest.feeds.all()

    return render_to_response('managedigest.html', {'form': form, 'feeds' : feeds}, context_instance=RequestContext(request))

def digestlist(request):
    if request.user.is_authenticated():
        all_digests = Digest.objects.all()
        public = []
	personal = []
	for digest in all_digests:
            if digest.owner_id == request.user.id:
                personal.append(digest)
            
            if digest.public:
                public.append(digest)
    else:
        public = Digest.objects.filter(public=True)
	personal = None
        
    return render_to_response('digests.html', {'public' : public, 'personal' : personal}, context_instance=RequestContext(request))

def digest(request, digestid):
    digest = Digest.objects.get( digestid=digestid )
    
    if (not digest):
        return HttpResponse("Digest not found")

    feeds = digest.feeds
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

    return HttpResponseRedirect('/issuelist')

def issuelist(request):
    if request.user.is_authenticated():
        all_issues = Issue.objects.all()
        public = []
	personal = []
	for issue in all_issues:
            if issue.owner_id == request.user.id:
                personal.append(issue)
            
            if issue.public:
                public.append(issue)
    else:
        public = Issue.objects.filter(public=True)
	personal = None
        
    return render_to_response('issues.html', {'public' : public, 'personal' : personal}, context_instance=RequestContext(request))

def urltoitem(request):
    itemmaker = ItemMaker()
    itemmaker.parse_url(request.REQUEST["url"])
    return HttpResponse(json.dumps({ 'title':itemmaker.title, 'description':itemmaker.p, 'img':itemmaker.img }), mimetype="application/json")

def submit(request):
    if request.method == 'POST':
        feeds = str(request.POST['urls']).splitlines()

        for url in feeds:
            hostname = urlparse(url).hostname 
            if (hostname.endswith(".ac.uk") or hostname.endswith(".edu")):
                if (feedparser.parse(url).version):
                    if (not AcademicFeeds.objects.filter(url=url).exists()):
                        AcademicFeeds.objects.create(url=url,toplevel=hostname)

        content = 'Your feeds have been sucessfully added to PANFeed!'
        p = {'title':'Crawl Me', 'header':'Success!', 'content':content}
        return render_to_response('success.html', {'page':p }, context_instance=RequestContext(request))

    else:
        content = 'Your data was not submitted - please retry sending the form. If you have reached this page in error, please go back and try again. If the problem persists, inform an administrator.'
        p = {'title':'Error', 'header':'No data recieved', 'content':content}
        return render_to_response('error.html', {'page':p }, context_instance=RequestContext(request))

@login_required
def login_redirect(request):
    return redirect("/")


