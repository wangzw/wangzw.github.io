#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Zhanwei Wang'
SITENAME = u'Home'
SITEURL = ''

PATH = 'content'
STATIC_PATHS = ['images', 'extra/CNAME']
EXTRA_PATH_METADATA = {
    'extra/CNAME': {'path': 'CNAME'},
}

TIMEZONE = 'Asia/Shanghai'
DEFAULT_LANG = u'cn'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Pelican Doc', 'docs.getpelican.com'),
         )

# Social widget
SOCIAL = (('Github', 'https://github.com/wangzw'),
          ('Linkedin', 'http://cn.linkedin.com/in/wangzw'),
          ('Weibo', 'http://weibo.com/u/2064676750')
          )

DEFAULT_PAGINATION = 10

LOAD_CONTENT_CACHE = False
DELETE_OUTPUT_DIRECTORY = True
THEME = 'themes/pelican-bootstrap3'
FAVICON = 'images/favicon.jpg'
DISPLAY_CATEGORIES_ON_SIDEBAR = True
DISPLAY_RECENT_POSTS_ON_SIDEBAR = True
DISQUS_NO_ID = True
GITHUB_USER = 'wangzw'
GITHUB_SKIP_FORK = True
BOOTSTRAP_THEME = 'readable-old'
DISPLAY_TAGS_INLINE = True
DISQUS_SITENAME = 'wangzw'

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
