# Create your views here.
from django.core.context_processors import csrf
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseForbidden, Http404
from django.db import connection, transaction
from feed import PersonalFeed
import urllib2
import feedparser
import json
import sys
from urlparse import urlparse
from personalise.models import Feeds,Digest,Corpus,Corpuskeywords,Issue,IssueItem
from django.contrib.auth.models import User
from personalise.urltorss2 import ItemMaker
from django.contrib.sites.models import Site
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.template import RequestContext
import pprint
from django.contrib.auth.decorators import login_required
from forms import DigestForm, IssueForm

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
                    digest.save(force_update=True)
            
                else:
                    return HttpResponseForbidden("You do not have permission to edit this journal.")
            return HttpResponseRedirect('/digestlist/')

        else:
            pass #Inform user form was invalid

    elif request.method == 'DELETE':
        digest = get_object_or_404( Digest, digestid=int(digestid) )

        if digest.owner != request.user:
            return HttpResponseForbidden("You do not have permission to edit this journal.")

        else:
            digest.delete()
 
    else:
        if digestid is None:
            form = DigestForm()
        else:
            digest = Digest.objects.get(digestid=digestid, owner=request.user)
            form = DigestForm(instance=digest)

    return render_to_response('managedigest.html', {'form': form,}, context_instance=RequestContext(request))

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
    return redirect("/")


