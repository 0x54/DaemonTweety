#!/usr/bin/env python
################################################################################
## DaemonTweety v0.1
##
## A simple twitter notification daemon
## https://github.com/0x54/DaemonTweety
##
## coded by Francesco Matarazzo (Ti)
## @0x54
## 19/11/2013
##
## Dependencies:
##    python-twitter (https://github.com/bear/python-twitter)
##
## This program is free software: you can redistribute it and/or modify it
## under the terms of the GNU General Public License version 3, as published
## by the Free Software Foundation.
##
## This program is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranties of
## MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
## PURPOSE.  See the GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along
## with this program.  If not, see <http://www.gnu.org/licenses/>.
##
################################################################################

import twitter
import time
import pynotify
import traceback
import sys
import urllib
import os
import gtk
import re

############## CREDENTIALS
consumer_key=''
consumer_secret=''
access_token_key=''
access_token_secret=''

api = 0
tweets = []
cwd = os.getcwd()
wait = 60 # seconds

url_re = re.compile(r"""
       [^\s]
       [a-zA-Z0-9:/\-]+
       \.(?!\.)
       [\w\-\./\?=&%~#]+
       [^\s]            """, re.VERBOSE) 

if not pynotify.init("DaemonTweety"):
    sys.exit(1)

def login():
    global api
    try:
        api = twitter.Api(consumer_key, consumer_secret, access_token_key, access_token_secret)
    except Exception:
        print traceback.format_exc()
        time.sleep(wait)
        return login()

def retweet(notifyObj, action, id):
    try:    
         api.PostRetweet(id, trim_user=False)
    except Exception, err:
                print "There was an error: %r" % err  
    gtk.main_quit()
    
def destroy(n, action=None):
    gtk.main_quit()

def notify(usr, message, icon, id):
    n = pynotify.Notification (usr, linkify(message), icon)
    n.add_action("retweet_tweet", "Retweet", retweet, id)
    n.connect('closed', destroy)
    try:
        n.show()
    except Exception:
        pass
    gtk.main()

def linkify(raw_message):
    message = raw_message
    for url in url_re.findall(raw_message):
        if url.endswith('.'):
            url = url[:-1]
        if 'http://' not in url:
            href = 'http://' + url
        else:
            href = url
        message = message.replace(url, '<a href="%s">%s</a>' % (href, url))
    return message

login()

while 1:
    try:    
        stat = api.GetHomeTimeline(count=20, since_id=None, max_id=None, trim_user=False, exclude_replies=False, contributor_details=False, include_entities=True)
    except Exception, err:
        print traceback.format_exc()
        time.sleep(wait)
        login()
    else:
        if len(tweets) == 0:
            for s in stat:
                tweets.append(s.text)
        for s in reversed(stat):
            if not s.text in tweets[:]:
                try:
                    urllib.urlretrieve(s.user.profile_image_url, "avatar/img")
                except Exception, e:
                        print "There was an error: %r" % e
                        
                notify(s.user.screen_name, s.text, cwd+"/avatar/img", s.id)
                tweets.insert(0,s.text)
                tweets.pop(-1)

        time.sleep(wait)
