#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *


PLUGIN_PATHS = ["plugins/pelican-plugins"]

PLUGINS = ['tipue_search', 'liquid_tags.img', 'liquid_tags.video',
           'liquid_tags.youtube', 'liquid_tags.vimeo',
           'liquid_tags.include_code', 'liquid_tags.notebook']

AUTHOR = u'Zhanwei Wang (王占伟)'
SITENAME = u'攻城狮的生活'
SITEURL = 'http://www.wangzw.org'
CATEGORIES_URL = 'categories.html'
TAGS_URL = 'tags.html'
RELATIVE_URLS = False

PATH = 'content'
STATIC_PATHS = ['images', 'extra/CNAME']
EXTRA_PATH_METADATA = {
    'extra/CNAME': {'path': 'CNAME'},
}

TIMEZONE = 'Asia/Shanghai'
DEFAULT_LANG = u'cn'

FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/%s.atom.xml'
TRANSLATION_FEED_ATOM = 'feeds/all-%s.atom.xml'
AUTHOR_FEED_ATOM = 'feeds/%s.atom.xml'
AUTHOR_FEED_RSS = 'feeds/%s.rss.xml'

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

# comments
DUOSHUO_SITENAME = 'wangzw'
DUOSHUO_ID_PREFIX_SLUG = True
DUOSHUO_DISPLAY_COUNTS = True

#DISQUS_SITENAME = 'wangzw'
DISQUS_NO_ID = False
DISQUS_ID_PREFIX_SLUG = True
DISQUS_DISPLAY_COUNTS = True

# display
DEFAULT_PAGINATION = 10

# Themes
THEME = 'themes/pelican-bootstrap3'
#BOOTSTRAP_THEME = 'readable-old'
BOOTSTRAP_THEME = 'flatly'
FAVICON = 'images/favicon.jpg'

# Side Bar
DISPLAY_CATEGORIES_ON_SIDEBAR = True
DISPLAY_RECENT_POSTS_ON_SIDEBAR = True
DISPLAY_TAGS_ON_SIDEBAR = True

# Github
GITHUB_USER = 'wangzw'
GITHUB_SKIP_FORK = True
GITHUB_SHOW_USER_LINK = False

# Menu
DISPLAY_PAGES_ON_MENU = True
DISPLAY_CATEGORIES_ON_MENU = False

# Tags
DISPLAY_TAGS_INLINE = True

# Content
SHOW_ARTICLE_AUTHOR = True
SHOW_ARTICLE_CATEGORY = True
DISPLAY_BREADCRUMBS = True
DISPLAY_CATEGORY_IN_BREADCRUMBS = True

# Index
DISPLAY_ARTICLE_INFO_ON_INDEX = True

# Navbar
BOOTSTRAP_NAVBAR_INVERSE = False

# Banner
BANNER = 'images/banner.jpg'
#BANNER_SUBTITLE = u'技术改变生活'

# Tipue Search
#DIRECT_TEMPLATES = ('index', 'archives')
DIRECT_TEMPLATES = (
    ('index',
     'tags',
     'categories',
     'authors',
     'archives',
     'search'))
# Others
LOAD_CONTENT_CACHE = False
DELETE_OUTPUT_DIRECTORY = True
