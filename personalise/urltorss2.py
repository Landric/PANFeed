#!/usr/bin/python

import sys
import urllib2
import re
from urlparse import urlparse
import lxml
from lxml import etree
import html5lib
import re
from bs4 import BeautifulSoup


class ItemMaker():
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

        html_string = response.read()
        re.subn("\n", " ", html_string)
        re.subn(" +", " ", html_string)

        title_search = re.search("<title>(.*)</title>", html_string, re.IGNORECASE)
        if title_search:
           self.title = title_search.group(1)
        
        img_search = re.search("<img[^>]*src=[\"']([^\"'>]+)", html_string, re.IGNORECASE)
        if img_search:
            if img_search.group(1).startswith("http"):
                self.img = img_search.group(1)
            else: 
                if img_search.group(1).startswith("//"):
                    self.img = "http:" + img_search.group(1)
                else: 
                    if img_search.group(1).startswith("/"):
                        self.img = "http://" + self.hostname + img_search.group(1)
                    else: 
                        self.img = self.url + img_search.group(1)

        
        for desc_type in ["description", "DC.description", "eprints.abstract"]:
            desc_search = re.search("(<meta[^>]*name=['\"]"+desc_type+"['\"][^>]*>)", html_string, re.IGNORECASE)
            if desc_search:
                desc_content = re.search('content="([^"]*)"', desc_search.group(1), re.IGNORECASE)
                if desc_content and len(desc_content.group(1)) > 0:
                    self.p = desc_content.group(1)
                    return
                desc_content = re.search("content=['\"]([^'\"]*)['\"]", desc_search.group(1), re.IGNORECASE)
                if desc_content and len(desc_content.group(1)) > 0:
                    self.p = desc_content.group(1)
                    return
        p_search = re.search("<p[^>]*>(.*)</p>", html_string, re.IGNORECASE)
        if p_search:
            self.p = re.subn("<[^>]*>", "", p_search.group(1))
