#!/usr/bin/env python
#coding=UTF-8

import re
import os
import time
import errno
import codecs
import socket
import httplib
import datetime
import urllib2
import sys
import md5
reload(sys)
sys.setdefaultencoding('UTF-8')
socket.setdefaulttimeout(45)


if len(sys.argv) < 2:
    print "usage: forum24-mirror.py <site-config>" 
    sys.exit(1)

execfile(sys.argv[1])

downloaded_files = {}
gentime = lambda t: datetime.datetime.fromtimestamp(int(t)).strftime("%Y.%m.%d %H:%M:%S")

def gettext(text, textname):
    if text!='':
        pref = "prefix-%s" % (textname)
        post = "postfix-%s" % (textname)
        if pref in forum.keys():
            text = forum[pref] + text
        if post in forum.keys():
            text = text + forum[post]
    return text

def opensavelocal(url, localpath, relative='../'):
    if not forum['image_caching']:
        return url
    loc = os.path.basename(url)
    locrel = '%s/%s-%s' % ( localpath, md5.new(url).hexdigest(), loc)
    page = Page( url, '%s/%s' % (forum['outdir'], locrel))
    if not url in downloaded_files:
        print "         + %s" %(url)
        downloader.open_page(page)
        downloaded_files[url] = page.savepath
    return "%s%s" % (relative, locrel)

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError, exc:
        if exc.errno == errno.EEXIST:
            pass
        else: raise

class SmartRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, headers):  
        result = urllib2.HTTPRedirectHandler.http_error_301(
            self, req, fp, code, msg, headers)              
        result.status = code
        return result                                       

    def http_error_302(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_302(
            self, req, fp, code, msg, headers)              
        result.status = code                                
        return result  

class Downloader:

    def __init__(self, log=None, maxretry=5):
        self.maxretry = maxretry
        self.count = 0
        self.error = 0

    def open_page(self, page):
        t1 = time.time()
        for retry in range(self.maxretry):
            try:
                request = urllib2.Request(page.url)
                opener = urllib2.build_opener(SmartRedirectHandler())
                web = opener.open(request)
                page.content = web.read()
                self.count += 1
                page.on_load()
                break
            except (IOError, httplib.IncompleteRead):
                if retry < self.maxretry:
                    print("Page %s fetch failed. Retry #%s" %(page.url, retry+1,))
                    time.sleep(retry*0.2)
                else:
                    raise Exception("Download failed: %s" % (page.url,))
        return True



class Page:

    def __init__(self, url, savepath=None):
        self.url = url
        self.savepath = savepath

    def on_load(self):
        if self.savepath:
            mkdir_p(os.path.dirname(self.savepath))
            f = codecs.open(self.savepath, 'w', 'ibm866')
            f.write(self.content.decode('ibm866'))
            f.close()

    def get_themes_count(self):
        r = re.compile("navigator_forum\('([0-9]*)'")
        m = r.search(self.content)
        if not m:
            raise Exception("Theme count not found")
        return int(m.group(1))

    def get_themes(self):
        r = re.compile("ubb\('.*?'\);\r")
        m = re.findall(r, self.content)
        def tparse(obj):
            t = obj[4:-3].split("','")
            theme = {   'timestamp' : gentime(t[1]),
                    'forum_id' : int(t[2]),
                    'id' : int(t[3]),
                    'spoiler' : unicode(t[4], 'cp1251'),
                    'title' : unicode(t[5], 'cp1251'),
                    'answers' : int(t[6]),
                    'views' : int(t[7]),
                    'author' : unicode(t[8], 'cp1251'),
                    'lastauthor' : unicode(t[9], 'cp1251'),
                    'lasttimestamp' : gentime(t[10]),
                    }
            theme['url'] = '%s/?1-%d-0-%08d-000-10001-0' % (forum['url'], theme['forum_id'], theme['id'])
            return theme
        return map(tparse, m)

    def parse_root(self):
        print (self.content)
        m = re.search ( re.compile("main\('0'\);(.*)main2_1\('", re.DOTALL), self.content)
        if not m:
            raise Exception("Incorrect root")
        block = { 'title':"untitled", 'blocks':[] }
        structure = []
        for line in m.group(1).split("\r"):
            line = unicode(line.strip(), 'cp1251')
            if line[0:3]=='st2': # new block ?
                if block['title'] != 'untitled':
                    structure.append(block)
                block = { 'title':line[5:-3], 'blocks':[] }
            elif line[0:3] == 'st(': # new theme 
                t = line[4:-3].split("','")
                theme = { 'title':t[1], 'id':int(t[0]), 'url': '%s/?0-%s' % (forum['url'], t[0]) }
                if not theme['id'] in forum['ignore_themes']:
                    block['blocks'].append(theme)
                if forum.has_key('add_themes'):
                    for add in forum['add_themes']:
                        if add['after'] == theme['id']:
                            theme = { 'title':add['title'], 'id':add['id'], 'url': '%s/?0-%s' % (forum['url'], add['id']) }
                            block['blocks'].append(theme)
        if len(block['blocks']) > 0:
            structure.append(block)
        return structure



    def get_posts(self):
        m = re.findall(re.compile("mo\('.*?'\);\r"), self.content)
        zv = re.search(r'var zv = new Array \(\'(.*?)\'\);', self.content)
        zvaniya = {}
        if zv:
            a = zv.group(1).split("','")
            for i in range(len(a)/2):
                zvaniya[a[i*2]] = a[i*2+1]
        diz = re.search(r'var diz = new Array \(\'(.*?)\);</script>', self.content)
        forum['diz'] = diz.group(1).split("','")
        zam = re.search(r'allzam = new Array \(\'(.*?)\'\);', unicode( self.content, 'cp1251'))
        zams = {}
        zam = zam.group(1).split("','")
        for z in zam:
            zz = z.split('­')
            if len(zz) == 2:
                if zz[0] in zams.keys():
                    zams[zz[0]].append(zz[1])
                else:
                    zams[zz[0]] = [ zz[1] ]

        def tparse(obj):
            def tag_more(mtch):
                global uniqid
                uniqid += 1
                return template['tag:more'] % { 'uniqid': '%04d' % (uniqid,), 'text': mtch.group(1) }
            def tag_local_img(match):
                url = re.sub ( r"\\", '', match.group(2))
                save = 'img/ext'
                if url[0]=='/':
                    url = "%s%s" % ( forum['url'], url) 
                for reg in forum['local_images_regex']:
                    if re.match(reg, url):
                        save = 'img/loc'
                        break
                try:
                    local = opensavelocal(url, save)
                except:
                    return '<img src="../%s" alt="Image download failed: %s"/>' %(forum['fail_image'], url)
                return '<img src="%s" alt="%s"/>' % (local, url)
            mod = { '\<img (.*?)src="(.*?)"(.*?)\>':tag_local_img, 
                    '\[more\](.*?)\[/more\]':tag_more,
                    '\[off\]\(.*?\)\[\/off\]':'<span class="offtopic">Оффтопик: \\1</span><BR>',
                    '\[BR\]': '<br/><span class="indent"></span>',
                    '<BR>': '<br/><span class="indent"></span>',
                    '\[quote\](.*?)\[\/quote\]':'</p><blockquote><p>\\1</p></blockquote><p>',
                    '\[pre\](.*?)\[\/pre\]':'<pre>\\1</pre>',
                    '\[pre2\](.*?)\[\/pre2\]':'<pre>\\1</pre>',
            }
            t = obj[4:-4].split("','")

            default_valgetter = lambda val: str(val)
            def getpo(post, varname, array, index, valgetter = default_valgetter, noprepost=False  ):
                if array[index]=='':  
                    post[varname]=''
                else:
                    t = re.sub(r'<\\\/', '</', unicode( array[index], 'cp1251'))
                    if noprepost:
                        post[varname] = valgetter(t)
                    else:
                        post[varname] = gettext(valgetter(t), varname)

            post = { }
            for infoindex, postinfo in enumerate ( ( 'author', 'title', 'text', 'sign', 'rang', ('timestamp', gentime), 'message_n',
                    'member', 'komu', 'cls', 'msgid', 'numcolor', 'ip', 'urlfoto', ('registered', gentime), 'gender', 
                    'country',  'city', 'reyting', 'userinfo', 'birth', 'avatar', ('thanks', default_valgetter, True))):
                if isinstance(postinfo, str):
                    getpo(post, postinfo, t, infoindex)
                else:
                    getpo(post, postinfo[0], t, infoindex, *postinfo[1:])

            post['location']=''
            if post['country'] != '' or post['city'] != '':
                if post['country'] != '' and post['city'] != '':
                    post['location'] = ', '.join((post['country'], post['city']))
                else:
                    post['location'] = post['country'] + post['city']
            post['location'] = gettext(post['location'], 'location')

            if post['thanks']:
                thanks = post['thanks'][1:-1].split('``')
                post['thanks'] = template['thanks'] % { 'count':len(thanks), 'users':', '.join(thanks) }
            if post['member'] in zvaniya:
                post['zvanie'] = unicode(zvaniya[post['member']], 'cp1251')
            else:
                post['zvanie'] = ''
            if post['avatar'] != "" and post['member'] != '':
                if post['avatar'] == "1":
                    vf = 'gif'
                elif post['avatar'] == "2":
                    vf = 'jpg'
                loc = '%s.%s' % (post['member'], vf)
                url = forum['avatars'] + loc
                local = opensavelocal(url, 'img/loc')
                post['avatar'] = '<img src="%s"/>' % (local,)
            else:
                post['avatar'] = ''
            if post['rang'] != "":
                r = int(post['rang'])
                if r>0:
                    r = r/30
                    if r > 10: r = 10
                    if r >0:
                        loc = "s%d.gif" % (r)
                        url = '%s%s' % (forum['diz'][0], loc)
                        local = opensavelocal(url, 'img/loc')
                        post['rang'] = '<img src="%s"/>' % (local)
                    else:
                        post['rang'] = ''
                else:
                    post['rang'] = ''
            post['zamechanie'] = ''
            if post['member'] in zams.keys():
                zamechaniya = zams[post['member']]
                for count, zame in enumerate(zamechaniya):
                    post['zamechanie'] += template['zamechanie'] % { 'count': count, 'user':post['member'], 'text': zame, 'gif': forum['gif-zamechanie'] }
            post['zamechanie'] = gettext(post['zamechanie'], 'zamechanie')

            for regexp, repl in mod.iteritems():
                post['text'] = re.sub(re.compile(regexp), repl, post['text'])
            return post
        return map(tparse, m)




uniqid = 0
downloader = Downloader()

forum['timestamp'] = gentime(time.time())
forum['relativepath']=''
forum['gif-zamechanie-url'] = "%s/gif/img/zm.gif" % ( forum['gifdomen'] )
forum['gif-zamechanie'] = opensavelocal(forum['gif-zamechanie-url'], 'img/loc')

page = Page(forum['url'])
downloader.open_page(page)
forum['structure'] = page.parse_root()

def render (outfile, templatename, dicts):
#    t = template[templatename] % { dic + '-' + k : globals()[dic][k] for dic in dicts for k in globals()[dic].keys()}
    tv = { }
    for dic in dicts:
        glob = globals()[dic]
        for k in glob.keys():
            tv [ "%s-%s" %( dic, k) ] = glob[k]
    t = template[templatename] % tv
    return outfile.write(t)

forum['outdir'] = re.sub(r'%FSTIMESTAMP%', 
        datetime.datetime.fromtimestamp(int(time.time())).strftime("%Y-%m-%d_%H%M%S"),
        forum['outdir'])
if os.system('cp -R "%s" "%s"' % (forum['indir'], forum['outdir'])) != 0:
    raise Exception('Failed indir->outdir copying')
mkdir_p('%s/data' % (forum['outdir']))


forum['filename']='%s/index.html' % (forum['outdir'])
ofindex = codecs.open(forum['filename'], 'w', 'utf-8')
render (ofindex, 'head', ['forum'])
render (ofindex, 'content', ['forum'])
render (ofindex, 'index', ['forum'])

for bgr in forum['structure']:
    forum['relativepath']='../'
    blockgroup = { 'title' : bgr['title'] }
    print ("Группа: %s" % (blockgroup['title']))
    render (ofindex, 'blockgroup', ['forum', 'blockgroup'])
    blockgroup['oddity'] = False
    for block in bgr['blocks']:
        blockgroup['oddity'] = not blockgroup['oddity']

        print ("  Раздел: %s %s" %(block['title'], block['url']))
        page = Page(block['url'])
        downloader.open_page(page)

        block["themes_count"] = page.get_themes_count()
        block["answers_count"] = 0
        block['filename'] = '%03d.html' % ( block['id'])
        if blockgroup['oddity']:
            block['oddity']='odd' 
        else: 
            block['oddity']='even'

        print ("    Число тем: %s" %(block["themes_count"],))
        themes = []
        for tp in range(block['themes_count']/forum['themes_per_page'] + 1):
            pageurl = '%s-%d' % (block['url'], tp*forum['themes_per_page'])
            print ('    '+pageurl)
            page = Page(pageurl)
            downloader.open_page(page)
            themes += page.get_themes()

        of = codecs.open('%s/data/%s' % (forum['outdir'], block['filename']), 'w', 'utf-8')
        forum['title'] = "%s [%s]" % ( block['title'], forum['alias'])
        render (of, 'head', ['forum'])
        render (of, 'content', ['forum'])
        render (of, 'block', ['forum', 'blockgroup', 'block'])

        odd = False
        for theme in themes:
            block["answers_count"] += theme['answers']
            odd = not odd
            if odd: 
                theme['oddity']='odd' 
            else: 
                theme['oddity']='even'
            theme['filename'] = 't%03d%08d.html' % ( theme['forum_id'], theme['id'])
            render (of, 'block_theme', ['forum', 'blockgroup', 'block', 'theme'])

            page = Page(theme['url'])
            print "      %s" % (theme['url'])
            downloader.open_page(page)
            posts = page.get_posts()
            otheme = codecs.open('%s/data/%s' % (forum['outdir'], theme['filename']), 'w', 'utf-8')
            if posts:
                forum['title'] = "%s [%s]" % ( posts[0]['title'], forum['alias'])
            else:
                print "Warning 0 themes!"
                forum['title'] = "*Untitled"
            render (otheme, 'head', ['forum'])
            render (otheme, 'content', ['forum'])
            render (otheme, 'theme', ['forum', 'blockgroup', 'block', 'theme'])
            oddpost = False
            for post in posts:
                oddpost = not oddpost
                if oddpost: 
                    post['oddity']='odd' 
                else: 
                    post['oddity']='even'
                render (otheme, 'post', ['forum', 'blockgroup', 'block', 'theme', 'post'])
            render (otheme, '/theme', ['forum', 'blockgroup', 'block', 'theme'])
            render (otheme, '/content', ['forum'])
            forum['source'] = theme['url']
            render (otheme, '/head',  ['forum'])
            otheme.close()
        render (ofindex, 'blockgroup_block', ['forum', 'blockgroup', 'block'])
        render (of, '/block', ['forum', 'blockgroup', 'block'])
        render (of, '/content', ['forum'])
        forum['source'] = block['url']
        render (of, '/head',  ['forum'])
        of.close()


forum['relativepath']=''
render (ofindex, '/index', ['forum'])
render (ofindex, '/content', ['forum'])
forum['source'] = forum['url']
render (ofindex, '/head', ['forum'])
ofindex.close()
