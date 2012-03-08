#!/usr/bin/python

import sys
import urllib2
import re
from urlparse import urlparse

from HTMLParser import HTMLParser

class ItemMaker(HTMLParser):
    pfound = 0
    titlefound = 0
    p = ""
    title = ""
    img = ""
    url = ""
    hostname = ""

    def parse_url(self , url):
        self.url = url
        if not url.endswith("/"):
            self.url = url + "/"
        self.hostname = urlparse(url).hostname

        try:
            response = urllib2.urlopen(url)
        except:
            sys.stderr.write( "Error reading: " + url + "\n"+ str(sys.exc_info()[0]) + "\n" )
            return

        self.feed(response.read())

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.titlefound = 1
        if tag == 'p' and len(self.p) < 50:
            self.pfound += 1
            
    def handle_endtag(self, tag):
        if tag == 'p' and self.pfound > 0:
            self.pfound -= 1
            if self.pfound == 0:
                if len(self.p) < 50:
                    self.p = ""
            
        if tag == 'title':
            self.titlefound = 0

    def handle_startendtag(self, tag, attrs):
        if tag == "img" and self.img == "":
            for tuple in attrs:
                if tuple[0] == "src":
                    if tuple[1].startswith("http"):
                        self.img = tuple[1]
                        return
                    if tuple[1].startswith("//"):
                        self.img = "http:" + tuple[1]
                        return
                    if tuple[1].startswith("/"):
                        self.img = self.hostname + "/" + tuple[1]
                        return
                    self.img = self.url + tuple[1]

    def handle_data(self, data):
        data = re.subn('\t', '', data)[0]
        data = re.subn('[\n\r]', ' ', data)[0]
        data = re.subn(' +', ' ', data)[0]
        if self.pfound > 0:
            self.p += data
        if self.titlefound > 0:
            self.title = data

#url = sys.argv[1];
#
#parser = ItemMaker()
#parser.parse_url(url)
#print parser.title;
#print parser.p;
#print parser.img;










