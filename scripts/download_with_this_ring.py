#! /usr/bin/env python

from lxml import etree
from lxml import html
import glob
import hashlib
import os
import re
import shutil
import sys
import urllib2

src_fmt = 'src/page_%02d.html'

os.chdir(os.path.dirname(__file__) + '/..')

def mkdirp(d):
    if not os.path.isdir(d):
        os.mkdir(d)
def sha2(s):
    m = hashlib.sha256()
    m.update(s)
    return m.hexdigest()

mkdirp('src')

mkdirp('img')

url_fmt = 'https://forums.sufficientvelocity.com/threads/' + \
    'with-this-ring-young-justice-si-story-only.25076/page-%d'
agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) ' + \
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3710.0 Safari/537.36'
for i in range(1, 81):
    sys.stdout.write('%d ' % i)
    sys.stdout.flush()
    uri = url_fmt % i
    try:
        f = urllib2.urlopen(urllib2.Request(uri, headers={'User-Agent': agent}))
        with open(src_fmt % i, 'w') as o:
            shutil.copyfileobj(f, o)
        f.close()
    except urllib2.HTTPError:
        print '\nfail: ', uri
        continue
    with open(src_fmt % i, 'r') as f:
        content = f.read()
    for match in re.finditer(r'<img src="([^"]+)"', content):
        url = match.group(1)
        sha = sha2(url)[:32]
        if glob.glob('img/%s*' % sha):
            continue
        try:
            f = urllib2.urlopen(urllib2.Request(url, headers={'User-Agent': agent}))
            tmap = { 'image/jpeg': '.jpg',
                     'image/png' : '.png',
                     'image/svg+xml' : '.svg'}
            ext = tmap.get(f.info().gettype(), '')
            if not ext:
                print('\n"%s"' % f.info().gettype())
            name = 'img/%s%s' % (sha, ext)
            with open(name, 'w') as o:
                o.write(f.read())
            f.close()
        except urllib2.HTTPError:
            print '\nfail: ', url, sha
        except ValueError:
            pass
