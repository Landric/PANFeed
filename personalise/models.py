# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models
from django.contrib.auth.models import User
import re

class Domains(models.Model):
    toplevel = models.URLField()
    class Meta:
        db_table=u'domains'

class AcademicFeeds(models.Model):
    url = models.URLField(verify_exists=True)
    toplevel = models.URLField()

    def __unicode__(self):
        return self.url;

    class Meta:
        db_table = u'academic_feeds'

class Corpus(models.Model):
    title = models.TextField(blank=True)
    description = models.TextField(blank=True)
    url = models.CharField(max_length=6249, blank=True)
    feed = models.CharField(max_length=6249, blank=True)
    length = models.IntegerField(null=True, blank=True)
    keywords = models.TextField(blank=True,null=True, default="")
    date = models.DateTimeField(null=True, blank=True)
    toplevel = models.URLField(blank=True)
    class Meta:
        db_table = u'corpus'

class Corpuskeywords(models.Model):
    itemid = models.IntegerField()
    word = models.CharField(max_length=90)
    rank = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'corpuskeywords'
        unique_together = ("itemid","word")

class Tf(models.Model):
    word = models.CharField(max_length=90)
    itemid = models.IntegerField()
    count = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'tf'
        unique_together = ("word","itemid")

class Words(models.Model):
    word = models.CharField(max_length=90, primary_key=True)
    count = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'words'

class UserFeeds(models.Model):
    url = models.URLField(verify_exists=True)

    def __unicode__(self):
        return self.url;

    class Meta:
        db_table = u'user_feeds'

class Digest(models.Model):
    owner = models.ForeignKey(User) 
    public = models.BooleanField()
    digestid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=60)
    description = models.TextField()
    feeds = models.ManyToManyField(UserFeeds, blank=True)
    def get_absolute_url(self):
        return "/digest/"+str(self.digestid)+"/"+re.subn(r'[^A-Za-z0-9]+', '-', self.title)[0]

    class Meta:
        db_table = u'digest'

class SpiderToDo(models.Model):
    pageurl=models.URLField(primary_key=True,max_length=255)

class SpiderDone(models.Model):
    doneurl=models.URLField(primary_key=True,max_length=255)

class SpiderRSS(models.Model):
    rssurl=models.URLField(primary_key=True,max_length=255)

class IssueItem(models.Model):
    title = models.TextField(blank=True)
    description = models.TextField(blank=True)
    url = models.CharField(max_length=6249, blank=True)
    img = models.CharField(max_length=6249, blank=True)
    issueid = models.IntegerField()
    length = models.IntegerField(null=True, blank=True)
    keywords = models.TextField(blank=True,null=True, default="")
    date = models.DateTimeField(null=True, blank=True)
    toplevel = models.URLField(blank=True)
    public = models.BooleanField(default=True)
    ordernumber = models.IntegerField(null=True, db_index=True)

    class Meta:
        db_table = u'issue_item'

class Issue(models.Model):
    public = models.BooleanField(default=False)
    owner = models.ForeignKey(User) 
    title = models.CharField(max_length=60)
    description = models.TextField(blank=True)
    toplevel = models.URLField(blank=True,null=True,default="")

    def get_absolute_url(self):
        return "/issue/"+str(self.id)+"/"+re.subn(r'[^A-Za-z0-9]+', '-', self.title)[0]

    class Meta:
        db_table = u'issue'
