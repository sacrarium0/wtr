#! /usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import etree
from lxml import html
import glob
import hashlib
import os
import re
import shutil
import sys

os.chdir(os.path.dirname(__file__) + '/..')

def mkdirp(d):
    if not os.path.isdir(d):
        os.mkdir(d)

def sha2(s):
    m = hashlib.sha256()
    m.update(s)
    return m.hexdigest()

def convertlinks(content, pdir):
    pwd = os.getcwd()
    os.chdir(pdir)
    def repl(s):
        url = s.group(1)
        sha = sha2(url)[:32]
        g = glob.glob('../img/' + sha + '*')
        if not g:
            return s.group(0)
        return '<img src="%s"' % g[0]
    content = re.sub(r'<img src="([^"]+)"',  repl, content)
    os.chdir(pwd)
    return content
style_map = {
    "color: #0040ff"     : 'blue',
    "color: #336600"     : 'olive',
    "color: #3f33cc"     : 'indigo',
    "color: #800000"     : 'maroon',
    "color: #99cc99"     : 'mint',
    "color: black"       : 'black',
    "color: #c0c0c0"     : 'silver',
    "color: #f5070b"     : 'pink',
    "color: #ff6600"     : 'blaze',
    "color: #ff9999"     : 'peach',
    "color: green"       : 'green',
    "color: grey"        : 'grey',
    "color: orange"      : 'orange',
    "color: purple"      : 'purple',
    "color: red"         : 'red',
    "color: transparent" : 'trans',
    "color: violet"      : 'violet',
    "color: white"       : 'white',
    "color: yellow"      : 'yellow',
    "font-family: 'Andalus'"        : 'serif',
    "font-family: 'bahnschrift'"    : 'serif',
    "font-family: 'book antiqua'"   : 'serif',
    "font-family: 'Century Gothic'" : 'serif',
    "font-family: 'courier new'"    : 'mono',
    "font-family: 'georgia'"        : 'serif',
    "font-family: 'impact'"         : 'sans bold',
    "font-family: 'trebuchet ms'"   : 'sans',
    "font-size: 10px"               : 'xsmall',
    "font-size: 12px"               : 'small',
    "font-size: 15px"               : '',
    "font-size: 18px"               : 'large',
    "font-size: 22px"               : 'xlarge',
    "font-size: 26px"               : 'xlarge',
    "font-size: 9px"                : 'xsmall',
    "text-align: center"            : 'center',
    "text-align: left"              : 'left',
    "text-align: right"             : 'right',
    "text-decoration: line-through" : 'strike',
    "text-decoration: underline"    : 'under',
    "vertical-align:sub"            : 'sub',
    "vertical-align:super"          : 'sup',
}

def tostring(x):
    return etree.tostring(x, method="html")

import cgi

def paragraph(a):
    def elem(a):
        yield cgi.escape(a.text.lstrip())
        for b in a:
            if b.get("class") == 'messageTextEndMarker':
                continue
            yield etree.tostring(b, method="html", with_tail=False)
            if b.tail:
                yield cgi.escape(b.tail.lstrip() if b.tag == 'br' else b.tail)
        if a.tail:
            yield cgi.escape(a.tail)
    s = '<p>'
    br = 0
    for x in elem(a):
        if x == '<br>':
            br += 1
        elif x:
            if br > 1:
                s = s.rstrip() + '</p>\n<p>'
                br -= 2
            s += '<br>\n' * br + x
            br = 0
    return s.rstrip() + '</p>\n'

def get_chapters():
    def clean(x):
        if not x:
            return ''
        def repl(m):
            return {160:'&nbsp;', 201:u'É', 224:u'à', 225:u'á', 226:u'â',
                    228:u'ä', 230:u'æ', 231:u'ç', 232:u'è', 233:u'é',
                    234:u'ê', 235:u'ë', 237:u'í', 240:u'ð', 241:u'ñ',
                    243:u'ó', 244:u'ô', 246:u'ö', 249:u'ù', 250:u'ú',
                    252:u'ü', 275:u'ē', 288:u'Ġ', 324:u'ń', 363:u'ū',
                    466:u'ǒ', 7703:u'ḗ', 8211:u'–', 8217:u'’', 8220:u'“',
                    8221:u'”', 8230:u'…', 9792:u'♀'}.get(int(m.group(1)), m.group(0))
        x = re.sub('&#([0-9]+);', repl, x)
        x = re.sub(u'([a-zA-Z])’([a-zA-Z])', "\\1'\\2", x)
        x = re.sub('(\s)\s+', '\\1', x)
        def repl2(m):
            if m.group(1) in style_map:
                v = style_map[m.group(1)]
                return ' class="%s"' % v if v else ''
            return m.group(0)
        x = re.sub(' style="([^"]*)"', repl2, x)
        x = re.sub('<span class="([^"]*)"><span class="([^"]*)">([^<]*</span></span>)',
                   r'<span class="\1 \2">\3', x)
        x = re.sub('<span class="([^"]*)"><span class="([^"]*)">([^<]*</span></span>)',
                   r'<span class="\1 \2">\3', x)
        return re.sub('</p>\n', '</p>\n\n', x)

    c = 1
    t = 0
    title = ''
    for src_path in sorted(glob.glob('src/page_*.html')):
        with open(src_path) as f:
            tree = etree.parse(f, etree.HTMLParser())
        for foo in tree.xpath('//div[@class="messageContent"]|'
                              '//div[contains(@class,"threadmarker")]/span[@class="label"]'):
            if foo.tag == 'span':
                t += 1
                print t,
                title = re.sub('^.*<strong>Threadmarks:</strong>\s*(.*\S)\s*</span>\s*$',
                               r'\1', etree.tostring(foo, method="html").encode('utf-8'),
                               flags=re.DOTALL)
                c = 1
                continue
            s = ''
            for a in foo.xpath('./article/*'):
                s += paragraph(a)
            yield (title, t, c, clean(s).encode('utf-8'))
            c+=1

extra_style = '''
body{
background-color:#282828;
color:#e6e6e6;
line-height:1.4;
font-family:sans-serif;
}
.blue  {color:#0040ff}
.olive {color:#336600}
.indigo{color:#3f33cc}
.maroon{color:#800000}
.mint  {color:#99cc99}
.black {color:black}
.silver{color:#c0c0c0}
.pink  {color:#f5070b}
.blaze {color:#ff6600}
.peach {color:#ff9999}
.green {color:green}
.grey  {color:grey}
.orange{color:orange}
.purple{color:purple}
.red   {color:red}
.trans {color:transparent}
.violet{color:violet}
.white {color:white}
.yellow{color:yellow}
'''

style = '''body{margin:8px auto;max-width:32em;padding:0 8px;}
pre{overflow-x:auto;}
div p{text-indent:2em;margin-top:0;margin-bottom:0}
div p:first-child{text-indent:0;}
a, a:link, a:visited, a:hover, a:active{color:inherit;text-decoration:underline}
img{max-width:30em;}
.serif {font-familt:serif}
.bold  {font-weight:bold}
.mono  {font-family:monospace}
.serif {font-familt:serif}
.xsmall{font-size:x-small}
.small {font-size:small}
.large {font-size:large}
.xlarge{font-size:x-large}
.xlarge{font-size:x-large}
.xsmall{font-size:x-small}
.center{text-align:center}
.left  {text-align:left}
.right {text-align:right}
.strike{text-decoration:line-through}
.under {text-decoration:underline}
.sub   {vertical-align:sub}
.sup   {vertical-align:super}
'''

head = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#282828">
<title>{0}</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
'''

footer = '''
</body>
</html>
'''

def write(directory, unstyle = False):
    mkdirp(directory)
    with open(directory + '/style.css', 'w') as o:
        o.write(style)
        o.write(extra_style)
    with open(directory + '/index.html', 'w') as idx:
        idx.write(head.format('With This Ring'))
        idx.write('<h1>With This Ring — Mr. Zoat</h1>\n\n')
        output = None
        current = None
        for title, t, c, content in get_chapters():
            if t != current:
                if output:
                    output.write('<p class="right">' +
                                 '<a href="./%03d.html">NEXT CHAPTER</a></p>\n\n' % t)
                    output.write(footer)
                    output.close()
                output = open(directory + '/%03d.html' % t, 'w')
                output.write(head.format(title))
                output.write('<h2>{0}</h2>\n\n'.format(title))
                idx.write('<a href="%03d.html">Chapter %d: %s</a><br>\n' % (t, t, title))
                if current:
                    output.write('<p class="right">' +
                                 '<a href="./%03d.html">BACK</a></p>\n\n' % current)
                current = t
            assert(output)
            name = '%03d-%03d' % (t, c)
            output.write('<h3 id="%s">%s %d</h3>\n\n' % (name, title, c))
            output.write('<p class="right small"><a href="#e%s">next</a></p>\n\n' % name)
            output.write('<div><!--BEGIN CONTENT-->\n\n')
            output.write(convertlinks(content, directory))
            output.write('</div><!--END CONTENT-->\n\n')
            output.write('<p id="e%s" class="right small"><a href="#%s">back</a></p>\n\n' % (name, name))
            output.write('<hr>\n\n')
        if output:
            output.write(footer)
            output.close()
        idx.write(footer)
write('book')
shutil.rmtree('eink', True)
shutil.copytree('book','eink')
with open('eink/style.css', 'w') as o:
    o.write(style)
for path in glob.glob('eink/*.html'):
    with open(path, 'r') as f:
        s = unicode(f.read(), encoding='utf-8')
    tree = html.fromstring(s)
    bads = ['blue', 'olive', 'indigo', 'maroon', 'mint', 'black', 'silver', 'pink', 'blaze', 'peach',
            'green', 'grey', 'orange', 'purple', 'red', 'trans', 'violet', 'white', 'yellow']
    for span in tree.xpath('//span'):
        for bad in bads:
            if bad in span.classes:
                span.classes.remove(bad)
                if 0 == len(span) and len(span.text) == 1:
                    span.classes.add('bold')
                    continue
                span.text = u'{%s}%s' % (bad, span.text if span.text else '')
                if len(span):
                    last = span[-1]
                    last.tail = u'%s{/}' % (last.tail if last.tail else '')
                else:
                    span.text = u'%s{/}' % (span.text)
    with open(path, 'w') as o:
        o.write(etree.tostring(tree, method="html", encoding='utf-8'))
