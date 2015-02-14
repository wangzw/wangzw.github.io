#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Zhanwei Wang'
SITENAME = u'攻城狮的生活'
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
LINKS = (('Pelican Doc', 'http://docs.getpelican.com'),
         ('<img src="https://camo.githubusercontent.com/a4e668f35df0e0059b76dc9bc1eb39895155d1a7/68747470733a2f2f7472617669732d63692e6f72672f77616e677a772f77616e677a772e6769746875622e696f2e7376673f6272616e63683d636f6465" alt="Build Status" data-canonical-src="https://travis-ci.org/wangzw/wangzw.github.io.svg?branch=code" style="max-width:100%;">',
          'https://travis-ci.org/wangzw/wangzw.github.io'),
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
