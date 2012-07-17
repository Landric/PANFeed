# Create your views here.
from django.core.context_processors import csrf
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseForbidden, Http404
from django.db import connection, transaction
import urllib2
import feedparser
import json
import sys
from urlparse import urlparse
from personalise.models import AcademicFeeds,Corpus,Corpuskeywords,Issue,IssueItem
from django.contrib.auth.models import User
from personalise.urltorss2 import ItemMaker
from django.contrib.sites.models import Site
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.template import RequestContext
import pprint
from django.contrib.auth.decorators import login_required
from forms import IssueForm
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
def manageissue(request,issueid=None):
    if request.method == "POST":
        form = IssueForm(request.POST)
        if form.is_valid():

            if issueid is None:
                issue = form.save(commit=False)
                issue.owner = request.user
                issue.save()
            else:
		if Issue.objects.filter(id=int(issueid), owner = request.user).exists():
                    issue = form.save(commit=False)
                    issue.owner = request.user
		    issue.id = issueid
                    issue.save(force_update=True)
                    IssueItem.objects.filter(issueid=issue.id).delete()
            
                else:
                    return HttpResponseForbidden("You do not have permission to edit this Issue.")

            for i, val in enumerate(request.REQUEST.getlist("item-title")) :
        
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

            return HttpResponseRedirect('/publishnews/')

    elif request.method == 'DELETE':
        issue = get_object_or_404( Issue, id=int(issueid) )

        if issue.owner != request.user:
            return HttpResponseForbidden("You do not have permission to edit this Issue.")

        else:
            issue.delete()
            return HttpResponseRedirect('/publishnews/')
    else:
        if issueid is None:
            form = IssueForm()
        else:
            issue = Issue.objects.get(id=issueid, owner=request.user)

            form = IssueForm(instance=issue)

    return render_to_response('manageissue.html', {'form': form, 'issueid': issueid}, context_instance=RequestContext(request))

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

    return HttpResponseRedirect('/publishnews')

def publishnews(request):
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
        invalid_feeds = []
        validate = URLValidator(verify_exists=True)
        for url in feeds:
	    try:
	        validate(url)
                hostname = urlparse(url).hostname
                if (hostname.endswith(".ac.uk") or hostname.endswith(".edu")):
                    if (feedparser.parse(url).version):
                        if (not AcademicFeeds.objects.filter(url=url).exists()):
                            AcademicFeeds.objects.create(url=url,toplevel=hostname)
		else:
	            invalid_feeds.append(url)
	    except ValidationError, e:
	        invalid_feeds.append(url)
        

        if invalid_feeds:
            content = 'The following feeds are invalid, or do not resolve to an academic domain, and could not be added to the PANFeed database. Please check they exist, and try again.'
            return render_to_response('error.html', {'title':'Error', 'header':'Invalid Feeds', 'content':content, 'data':invalid_feeds}, context_instance=RequestContext(request))
        else:
            content = 'Your feeds have been sucessfully added to PANFeed!'
            return render_to_response('success.html', {'title':'Crawl Me', 'header':'Success!', 'content':content}, context_instance=RequestContext(request))

    else:
        content = 'Your data was not submitted - please retry sending the form. If you have reached this page in error, please go back and try again. If the problem persists, inform an administrator.'
        
        return render_to_response('error.html', {'title':'Error', 'header':'No data recieved', 'content':content}, context_instance=RequestContext(request))

@login_required
def login_redirect(request):
    return redirect("/")


