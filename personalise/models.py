# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class Feeds(models.Model):
    url = models.URLField(primary_key=True,verify_exists=True)
    toplevel = models.URLField()
    class Meta:
        db_table = u'feeds'

class Corpus(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.TextField(blank=True)
    description = models.TextField(blank=True)
    url = models.CharField(max_length=6249, blank=True)
    feed = models.CharField(max_length=6249, blank=True)
    length = models.IntegerField(null=True, blank=True)
    keywords = models.TextField(blank=True)
    date = models.DateField(null=True, blank=True)
    toplevel = models.URLField()
    class Meta:
        db_table = u'corpus'

class Corpuskeywords(models.Model):
    itemid = models.IntegerField(primary_key=True)
    word = models.CharField(max_length=90, primary_key=True)
    rank = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'corpuskeywords'

class Tf(models.Model):
    word = models.CharField(max_length=90, primary_key=True)
    itemid = models.IntegerField()
    count = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'tf'

class Words(models.Model):
    word = models.CharField(max_length=90, primary_key=True)
    count = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'words'

