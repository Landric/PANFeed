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
from datetime import datetime

class Domains(models.Model):
    toplevel = models.URLField()
    
    def __unicode__(self):
        return self.toplevel

class AcademicFeeds(models.Model):
    url = models.URLField(verify_exists=True)
    toplevel = models.URLField()

    def __unicode__(self):
        return self.url;

class Corpus(models.Model):
    title = models.TextField(blank=True)
    description = models.TextField(blank=True)
    url = models.CharField(max_length=6249, blank=True)
    feed = models.CharField(max_length=6249, blank=True)
    length = models.IntegerField(null=True, blank=True)
    keywords = models.TextField(blank=True,null=True, default="")
    date = models.DateTimeField(null=True, blank=True)
    toplevel = models.URLField(blank=True)
    
    def __unicode__(self):
        return self.title
        
    class Meta:
        verbose_name_plural = "corpora"

class Corpuskeywords(models.Model):
    corpus = models.ForeignKey(Corpus)
    word = models.ForeignKey('Words')
    rank = models.IntegerField(null=True, blank=True)
    
    def __unicode__(self):
        return "{word} {corpus}".format(word = self.word, corpus = self.corpus)
    
    class Meta:
        unique_together = ("corpus","word")

class Tf(models.Model):
    word = models.ForeignKey('Words')
    corpus = models.ForeignKey(Corpus)
    count = models.IntegerField(null=True, blank=True)
    
    def __unicode__(self):
        return "{word} {count}".format(word = self.word, count=self.count)
    class Meta:
        unique_together = ("word","corpus")

class Words(models.Model):
    word = models.CharField(max_length=90, primary_key=True)
    count = models.IntegerField(null=True, blank=True)
    
    def __unicode__(self):
        return "{word} {count}".format(word=self.word, count=self.count)

class SpiderToDo(models.Model):
    pageurl=models.URLField(primary_key=True,max_length=255)

class SpiderDone(models.Model):
    doneurl=models.URLField(primary_key=True,max_length=255)

class SpiderRSS(models.Model):
    rssurl=models.URLField(primary_key=True,max_length=255)

class Feed(models.Model):
    owner = models.ForeignKey(User) 
    title = models.CharField('feed title', max_length=60, help_text='Try to keep your title brief but informative (e.g. "Student Project News")')
    description = models.TextField('feed description', help_text='Briefly describe the purpose of this feed (e.g. "Information for students working on their Third Year Project")')
    displayAll = models.BooleanField('publishing options', default=True, help_text='Don\'t worry, you can change this later if you change your mind') #True=display all items, False=only display latest publication

    def get_absolute_url(self):
        return "/news/"+str(self.id)

class SpecialIssue(models.Model):
    title = models.CharField('issue title', max_length=60)
    editorial = models.TextField(help_text='Briefly describe the contents of this Issue')

class FeedItem(models.Model):
    title = models.CharField(max_length=60)
    content = models.TextField(help_text='This content will be displayed in the viewer\'s Feed Reader. They can still click the link to view the full article')
    url = models.URLField(max_length=6249)
    img = models.URLField(max_length=6249, blank=True)
    date = models.DateTimeField(default=datetime.now, blank=True)
    feed = models.ForeignKey(Feed)
    special_issue = models.ForeignKey(SpecialIssue, null=True)
    issue_position = models.IntegerField(null=True, db_index=True)
