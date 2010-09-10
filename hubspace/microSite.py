import os
import os.path
import glob
from turbogears import controllers, expose, redirect, identity, validators as v, validate, config
from turbogears.identity.exceptions import IdentityFailure
from hubspace.validators import *
from formencode import ForEach
from hubspace.utilities.templates import try_render
from hubspace.utilities.login import login_args, requestPassword, resetPassword
from hubspace.utilities.dicts import AttrDict
from hubspace.utilities.permissions import is_host, addUser2Group
from hubspace.utilities.object import modify_attribute, obj_of_type
from hubspace.model import Location, LocationMetaData, User, RUsage, Group, MicroSiteSpace, ObjectReference, ListItem, Page, MetaWrapper, PublicPlace, List
from sqlobject import AND, SQLObjectNotFound, IN, LIKE, func
from sqlobject.events import listen, RowUpdateSignal, RowCreatedSignal, RowDestroySignal
import os, re, unicodedata, md5, random, sys, datetime, traceback, hmac as create_hmac
from hashlib import sha1
import cherrypy
from kid import XML
from hubspace.feeds import get_local_profiles, get_local_future_events, get_local_past_events
from BeautifulSoup import BeautifulSoup
import sendmail
import hubspace.model
model = hubspace.model 
from hubspace.utilities.cache import strongly_expire
from hubspace.utilities.uiutils import now
import hubspace.sync.core as sync

from turbogears import database
import urlparse
from urllib import quote, urlencode
from urllib2 import urlopen, Request, build_opener, install_opener, HTTPCookieProcessor, HTTPRedirectHandler
import cookielib
from hubspace import configuration

import vobject
import patches
import logging
applogger = logging.getLogger("hubspace")

def place(obj):
    if isinstance(obj, Location):
        return obj
    elif hasattr(obj, 'location'):
        return obj.location
    elif hasattr(obj, 'place'):
        return obj.place
    else:
        raise AttributeError("object has not location")
    

def bs_preprocess(html):
     """remove distracting whitespaces and newline characters"""
     html = re.sub('\n', ' ', html)     # convert newlines to spaces
     return html 

def html2xhtml(value):
    value = value.strip()
    value = BeautifulSoup(value).prettify()
    value = bs_preprocess(value)
    try:
        XML(value).expand()
    except:
        cherrypy.response.headers['X-JSON'] = 'error'
        print "not good XML"
    return value

def get_profiles(*args, **kwargs):
    location = kwargs.get('location')
    no_of_images = 9
    only_with_images = True
    profiles = get_local_profiles(location, only_with_images, no_of_images)
    if len(args) >=1:
        profiles.update(get_user(*args))
    return profiles

def get_user(*args, **kwargs):
    if len(args) >= 1:
        user = User.by_user_name(args[0])
        if user.public_field and user.active:
            return {'user': user}
    return {}

def get_public_place(*args, **kwargs):
    if len(args) >= 1:
        place = PublicPlace.select(AND(PublicPlace.q.name==args[0]))
        if place.count():
            return {'place': place[0]}
    return {'place': None}
    

def get_events(*args, **kwargs):
    no_of_events = 5
    location = kwargs.get('location')
    events = get_local_future_events(location, no_of_events)
    events.update(get_local_past_events(location, no_of_events))
    if len(args) >=1:
        events.update(get_event(*args))
    return events

def parseSubpageId(list_name):
    if list_name.startswith('subpage'):
        list_name,pageid=list_name.split('_')
    else:
        pageid = None
    return (list_name,pageid)        



standard_kw = ['microsite', 'page', 'location']

class RedirectToClient(Exception):
    def __init__(self, url):
        self.url = url

class HTTPRedirectClient(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        m = req.get_method()
        if (code in (301, 302, 303, 307) and m in ("GET", "HEAD")
            or code in (301, 302, 303) and m == "POST"):
            # Strictly (according to RFC 2616), 301 or 302 in response
            # to a POST MUST NOT cause a redirection without confirmation
            # from the user (of urllib2, in this case).  In practice,
            # essentially all clients do redirect in this case, so we
            # do the same.
            # be conciliant with URIs containing a space
            newurl = newurl.replace(' ', '%20')
            raise RedirectToClient(newurl)
            #return Request(newurl,
            #               headers=req.headers,
            #               origin_req_host=req.get_origin_req_host(),
            #               unverifiable=True)
        else:
            raise HTTPError(req.get_full_url(), code, msg, headers, fp)

forwarded_request_headers = ['If-None-Match']
forwarded_response_headers = ['Etag', 'Last-Modified', 'X-Pingback', 'Cache-Control', 'Pragma', 'Expires']

class MediaContent(Exception):
    def __init__(self, response):
        self.response = response

class AjaxContent(Exception):
    def __init__(self, html):
        self.html = html


def get_blog(*args, **kwargs):
    blog_url = kwargs['page'].blog_url.strip()
    args = list(args)
    args.insert(0, blog_url)
    url = '/'.join(args)
    url += '/'
    kw_args = dict((key.replace('+', '-'), val) for key, val in kwargs.iteritems() if key not in standard_kw)
    post_data = None
    if kw_args:
        if cherrypy.request.method == 'GET':
            url += '?' + urlencode(kw_args)
        if cherrypy.request.method == 'POST':
            post_data = urlencode(kw_args)
   
    if cherrypy.session.has_key('cj'):
        cj = cherrypy.session['cj']
    else:
        cj = cherrypy.session['cj'] = cookielib.CookieJar() 

    opener = build_opener(HTTPCookieProcessor(cj), HTTPRedirectClient)
    install_opener(opener)   
    headers = {}
    for header in forwarded_request_headers:
        if cherrypy.request.headers.get(header, 0):
            headers[header] = cherrypy.request.headers[header]
    try:
        if post_data:
            blog = Request(url, post_data, headers)
        else:
            blog = Request(url, headers=headers)
        blog_handle = urlopen(blog)
    except RedirectToClient, e:
        redirect(e.url.replace(blog_url, cherrypy.request.base + '/public/' + kwargs['page'].path_name))
    except IOError, e:
        if hasattr(e, 'reason'):
            blog_body = "Could not get blog from: " +  url + " because " + e.reason
            blog_head = ""
        elif hasattr(e, 'code'):
            cherrypy.response.headers['status'] = e.code
            blog_body = "Could not get blog from: " +  url + " because " + str(e.code)
            blog_head = ""
    except ValueError:
	blog_body = ""
	blog_head = ""
        return {'blog': blog_body, 'blog_head': blog_head}

    else:
        content_type = blog_handle.headers.type
        if content_type not in ['text/html', 'text/xhtml']:
            raise redirect(url)
        blog = blog_handle.read()

        #replace any links to the blog_url current address
        our_url = cherrypy.request.base + '/public/' + kwargs['page'].path_name
        blog = blog.replace(blog_url, our_url)
        
        blog = BeautifulSoup(blog)
        #blog = bs_preprocess(blog)
        for input in blog.body.findAll('input', attrs={'name':re.compile('.*\-.*')}):
            input['name'] = input['name'].replace('-', '+') #hack around the awkwardness of submitting names with '-' from FormEncode

        #change back anything ending in .js .css .png .gif, .jpg .swf
        for link in blog.findAll('link', attrs={'href':re.compile('.*' + re.escape(our_url) + '.*')}):
            link['href'] = link['href'].replace(our_url, blog_url)
        for link in blog.findAll('img', attrs={'src':re.compile('.*' + re.escape(our_url) + '.*')}):
            link['src'] = link['src'].replace(our_url, blog_url)
        for link in blog.findAll('script', attrs={'src':re.compile('.*' + re.escape(our_url) + '.*')}):
            link['src'] = link['src'].replace(our_url, blog_url)

	for header in blog.body.findAll('div', attrs={'id':'header'}):
	     header.extract()
        for css in blog.head.findAll('link', attrs={'href':re.compile('.*standalone\.css')}):
             css.extract()
        blog_head = blog.head.renderContents()
        blog_body = blog.body.renderContents()

        for header in forwarded_response_headers:
            if blog_handle.headers.get(header, 0):
                cherrypy.response.headers[header] = blog_handle.headers[header]
    

    return {'blog': blog_body, 'blog_head': blog_head}





def get_blog2(*args, **kwargs):
    #import pdb; pdb.set_trace()
    thispage = kwargs['page']
    blog_url = thispage.blog_url.strip()
    args = list(args)
    args.insert(0, blog_url)
    url = '/'.join(args)
    #add a / if its not a .jpg or if its just the domain name
    if not url.endswith('/') and (not '.' in args[-1] or url.count('/') <3):
        url += '/'
    kw_args = dict((key.replace('+', '-'), val) for key, val in kwargs.iteritems() if key not in standard_kw)
    post_data = None
    if kw_args:
        if cherrypy.request.method == 'GET':
            url += '?' + urlencode(kw_args)
        if cherrypy.request.method == 'POST':
            post_data = urlencode(kw_args)
   
    if cherrypy.session.has_key('cj'):
        cj = cherrypy.session['cj']
    else:
        cj = cherrypy.session['cj'] = cookielib.CookieJar() 

    opener = build_opener(HTTPCookieProcessor(cj), HTTPRedirectClient)
    install_opener(opener)   
    headers = {}
    for header in forwarded_request_headers:
        if cherrypy.request.headers.get(header, 0):
            headers[header] = cherrypy.request.headers[header]
    try:
        if post_data:
            blog = Request(url, data=post_data, headers=headers)
        else:
            blog = Request(url, headers=headers)
        blog_handle = urlopen(blog)
    except RedirectToClient, e:
        redirect(e.url.replace(blog_url, cherrypy.request.base + '/public/' + kwargs['page'].path_name))
    except IOError, e:
        errorbody = e.read()
        if '<body id="error-page">' in errorbody:
            blog_body = "There was an error with wp"
            blog_head = ""
        elif hasattr(e, 'reason'):
            blog_body = "Could not get blog from: " +  url + " because " + e.reason
            blog_head = ""
        elif hasattr(e, 'code'):
            cherrypy.response.headers['status'] = e.code
            blog_body = "Could not get blog from: " +  url + " because " + str(e.code)
            blog_head = ""
    except ValueError:
	blog_body = ""
	blog_head = ""
        return {'blog': blog_body, 'blog_head': blog_head}
    else:
        content_type = blog_handle.headers.type
        if content_type not in ['text/html', 'text/xhtml']:
            raise MediaContent(blog_handle)

        #import pdb; pdb.set_trace()
        blog = blog_handle.read()

        #replace any links to the blog_url current address
        our_url = cherrypy.request.base + '/public/' + kwargs['page'].path_name
        blog = blog.replace(blog_url, our_url)
        
        blog = BeautifulSoup(blog)
        #blog = bs_preprocess(blog)
        #for input in blog.body.findAll('input', attrs={'name':re.compile('.*\-.*')}):
        for input in blog.findAll('input', attrs={'name':re.compile('.*\-.*')}):
            input['name'] = input['name'].replace('-', '+') #hack around the awkwardness of submitting names with '-' from FormEncode

        #change back anything ending in .js .css .png .gif, .jpg .swf
        #for link in blog.findAll('link', attrs={'href':re.compile('.*' + re.escape(our_url) + '.*')}):
        #    link['href'] = link['href'].replace(our_url, blog_url)
        #for link in blog.findAll('img', attrs={'src':re.compile('.*' + re.escape(our_url) + '.*')}):
        #    link['src'] = link['src'].replace(our_url, blog_url)
        #for link in blog.findAll('script', attrs={'src':re.compile('.*' + re.escape(our_url) + '.*')}):
        #    link['src'] = link['src'].replace(our_url, blog_url)
    if hasattr(blog,'body') and blog.body:
        #import pdb; pdb.set_trace()
        for header in blog.body.findAll('div', attrs={'id':'header'}):
            header.extract()
        for css in blog.head.findAll('link', attrs={'href':re.compile('.*standalone\.css')}):
            css.extract()
        #for script in blog.findAll('script',attrs={'src':re.compile('.*' + re.escape(blog_url) + '.*jquery\.js.*')}):
        #    script.extract()
        
        for script in blog.findAll('script',attrs={'src':re.compile('jquery\.js')}):
            script.extract()
            
        for script in blog.findAll('script',attrs={'src':re.compile('functions\.js')}):
            script.extract()

        for script in blog.findAll('script',attrs={'src':re.compile('jquery\.validate\.js')}):
            script.extract()



        sidebartext=''        
        #the sidebar get injected via deliverance
        for sidebar in blog.findAll('div',id='sidebar'):
            sidebartext = sidebar.renderContents().replace('text_small','text_real_small')
            sidebar.extract()
        
        for wphead in blog.findAll('div',id='wphead'):
            wphead.extract()
            pass

        blog_head = blog.head.renderContents()
        found =  blog.findAll(id='content')
        
        #if possible grep the content div
        if blog.findAll('div',id='content') and iswpadminurl(url):
            blog_body = blog.findAll('div',id='content')[0].renderContents()
        else: 
            blog_body = blog.body.renderContents()
        
        #for header in forwarded_response_headers:
        #    if blog_handle.headers.get(header, 0):
        #        cherrypy.response.headers[header] = blog_handle.headers[header]
    else:
        raise AjaxContent(blog.renderContents())
           
    #blog_body = ''
    #blog_head = ''
    return {'blog': blog_body, 'blog_head': blog_head,'sidebartext':sidebartext}


def sitesearch(*args,**kwargs):
        #title, description, url
        s = str(kwargs.get('s',''))
        s = s.lower().strip()
        page = kwargs['page']        
        location = page.location
        searchresults = []
        if s:
            access_tuple = patches.utils.parseDBAccessDirective()
            con = patches.utils.getPostgreSQLConnection(*access_tuple)
            cur = con.cursor()
            sql = """select distinct page.id from page left join object_reference on  page.id=object_reference.object_id left join meta_data on object_reference.id=meta_data.object_ref_id where page.location_id=%s and object_reference.object_type='Page' and (lower(page.content) like '%%' || %s || '%%' or lower(meta_data.attr_value) like '%%' || %s || '%%')"""
            #XXX no sql injections please!!!!
            id = str(page.location.id)
            cur.execute(sql,(id,s,s,))
            result = [r[0] for r in cur.fetchall()]            
            for id in result:
                page=Page.get(id)
                title = page.name and page.name or page.title
                url = cherrypy.request.base + '/public/' + page.path_name 
                description = re.sub(r'<[^>]*>','',page.content)[:100]
                searchresults.append(dict(url=url,title=title,description=description))
            blogs = Page.selectBy(location=page.location.id,page_type='blog2').orderBy('id')
            if blogs.count() > 0:
                blog = blogs[0]
                blog = MetaWrapper(blog)
                search_url = blog.blog_url.strip()
                if not search_url.endswith('/'):
                    search_url += '/'
                search_url += "?s=%s" % s
                blogresult = urlopen(search_url).read()
                blogsoup = BeautifulSoup(blogresult)
                for d in blogsoup.findAll("div", { "class" : re.compile('hentry') }):
                    title = d.h3.a.string
                    url = d.h3.a['href']
                    parts = urlparse.urlsplit(url)
                    url = cherrypy.request.base + '/public/' + blog.path_name + parts[2]
                    description = re.sub(r'<[^>]*>','',d.find('div', { "class" : "entry-content" }).p.string)
                    searchresults.append(dict(url=url,title=title,description=description))
        return dict(searchresults=searchresults,
                    s=s)
 


def iswpadminurl(url):
    if 'wp-admin'  in url or 'wp-login' in url:
        return True
    else: 
        return False

def get_event(*args):
    return {'event': RUsage.get(args[0])}

def experience_slideshow(*args, **kwargs):
    return {'image_source_list': [top_image_src(page, kwargs['microsite']) for page in Page.select(AND(Page.q.locationID == kwargs['location'],
                                                                                                       Page.q.image != None)) if page.active]}


def image_source(image_name, microsite, default=""):
    try:
        os.stat(microsite.upload_dir + image_name)
        return microsite.upload_url + image_name
    except:
        return default

def top_image_src(page, microsite):
    if page.image_name:
        return microsite.upload_url + page.image_name 
    else:
        try:
            os.stat(os.getcwd() + '/hubspace/static/images/micro/main-images/' + page.path_name.split('.')[0]+'.jpg')
            return '/static/images/micro/main-images/' + page.path_name.split('.')[0]+'.jpg'
        except OSError:
            return '/static/images/micro/main-images/index.jpg'

def page_image_source(page_name, **kwargs):
    return image_source(page_name + '.png', kwargs['microsite'], "/static/images/micro/main-images/" + page_name + '.jpg')

def standard_page(*args, **kwargs):
    return {}

valid_username_chars = r"[^0-9a-z._-]"
valid_phone_chars = r"[^0-9/.\(\)\+-]"

def create_inactive_user_host_email(**kwargs):
    """send a mail to the hosts with a link to create the user
    """
    location = Location.get(kwargs['location'])
    if not kwargs.get('user_name', None):
        kwargs['user_name'] = kwargs['first_name'] + '.' + kwargs['last_name']

    #normalize the user_name to ascii
    kwargs['user_name'] = unicodedata.normalize('NFKD', kwargs['user_name']).encode('ascii', 'ignore').lower()
    kwargs['user_name'] = re.sub(valid_username_chars, '', kwargs['user_name'])
    kwargs['phone'] = re.sub(valid_phone_chars, '', kwargs['phone'])
    #ensure username is unique
    try:
        User.by_user_name(kwargs['user_name'])
        try:
            kwargs['user_name'] = kwargs['user_name'][:-1] + str(int(kwargs['user_name'][-1]) + 1)
        except ValueError:
            kwargs['user_name'] += '2'
        kwargs['user_name'] = kwargs['user_name'].decode('utf-8')
        return create_inactive_user_host_email(**kwargs)    
    except SQLObjectNotFound:
        pass
    #if user with that email has already been created, don't create them again - but send a mail to hosts to inform them

    attributes =  {'user_name': kwargs['user_name'],
                   'first_name': kwargs['first_name'],
                   'last_name' : kwargs['last_name'],
                   'email_address': kwargs['email_address'],
                   'organisation': kwargs['organisation'],
                   'home': kwargs['phone'],
                   'location_url': location.url,
                   'location_path': location.url.split('://')[1].replace('.', '_').replace('-', '_'),
                   'location_name':location.name}
    
    try:
        User.by_email_address(kwargs['email_address'])
        link = "A user with this email address already exists so you cannot create this user"

    except SQLObjectNotFound:
        link = location.url + '/sites/%(location_path)s/edit/create_inactive_user?user_name=%(user_name)s&first_name=%(first_name)s&last_name=%(last_name)s&email_address=%(email_address)s&organisation=%(organisation)s&home=%(home)s' %dict((attr, quote(val.encode('utf-8'))) for attr, val in attributes.items())
        hmac_key = config.get('hmac_key', None)
        if hmac_key:
            auth_code = create_hmac.new(hmac_key, link, sha1)
            link += '&hmac=' + auth_code.hexdigest()
        link = "To create the user hit this %s" %(link) 

    attributes.update({'link': link})

    mail_body = u"""Dear %(location_name)s Hosts,\n\n Someone has enquired about membership of your Hub at %(location_url)s. The details are as follows\n\nname: %(first_name)s %(last_name)s\n\norganisation: %(organisation)s\n\nemail: %(email_address)s\n\ntel: %(home)s\n\n\n%(link)s
                    """ % attributes
    mail_body = mail_body.encode('utf-8')
    enquiries_address = location.name.lower().replace(' ', '') + ".enquiries@the-hub.net"
    sendmail.sendmail(enquiries_address, enquiries_address, "The Hub | enquiries", mail_body)
    return attributes


def create_enquiry(*args, **kwargs):    
    create_inactive_user_host_email(**kwargs)
    return {'first_name':kwargs['first_name'],
            'last_name': kwargs['last_name'],
            'organisation': kwargs['organisation'],
            'phone': kwargs['phone'],
            'email_address': kwargs['email_address'],
            'submit': True}
    

site_template_args = {'tg_css':[], 'tg_js_head':[], 'tg_js_bodytop':[], 'tg_js_bodybottom':[]}

list_types = {'spaces_list': {'object_types':['PublicSpace'], 'mode':'add_new'}, 
              'left_tabs': {'object_types':['Page'], 'mode':'add_new'}, 
              'right_tabs': {'object_types':['Page'], 'mode':'add_new'}, 
              'places_list': {'object_types':['PublicPlace'], 'mode':'add_new'},
              'people_list': {'object_types':['User'], 'mode':'add_existing'},
              'featured_list': {'object_types':['Location', 'User', 'Page'], 'mode':'add_existing'}
}
#jhb: idea could be to have the list_types in the database, (as per Tom), add a 'context' to them, eg. 
#the page on which they should appear.


def getList(list_name,location):
    #list_name,pageid = parseSubpageId(list_name)
    #if pageid:
    #    lists = List.selectBy(list_name=list_name,location=location,page=pageid)
    #else:        
    #    lists = List.selectBy(list_name=list_name,location=location)
    lists = List.selectBy(list_name=list_name,location=location)
    if lists.count() == 1:
        return lists[0]
    else:
        return None

def last_item(list_name, location):
    thelist = getList(list_name,location)
    if thelist:
        try:
            return ListItem.select(AND(ListItem.q.nextID == None,
                                   ListItem.q.listID == thelist))[0]
        except IndexError:
            return None
    return None


#    try:
#        return ListItem.select(AND(ListItem.q.nextID == None,
#                                   ListItem.q.list_name == list_name,
#                                   ListItem.q.locationID == location))[0]
#    except IndexError:
#        return None 

def append_existing_item(list_name, obj, **kwargs):
    #import pdb; pdb.set_trace()
    thelist = getList(list_name,kwargs['location'])
    old_last = last_item(list_name, kwargs['location'])
    object_ref = ObjectReference.select(AND(ObjectReference.q.object_type ==  obj.__class__.__name__, 
                                            ObjectReference.q.object_id == obj.id))[0]
    new_last = ListItem(**{'list_name':list_name, 'location':kwargs['location'], 'active':kwargs['active'], 'object_ref':object_ref,'list':thelist})
    if old_last:
        old_last.next = new_last

def append_to_list(list_name, **kwargs):
    #we could be adding to a subpages list. If foo.html gets a bar subpage, 
    #the name needs to be foo__bar.html
    #import pdb; pdb.set_trace()
    
    if kwargs['object_type'] == Page.__name__:
        path_name = kwargs['name']
        subpage_of=None
        if list_name.startswith('subpages_'):
            thelist = getList(list_name,kwargs['location'])
            page = thelist.page
            pagenamebase = page.path_name.split('.html')[0]
            path_name = pagenamebase+'__'+kwargs['name']
            subpage_of = list_name.split('subpages_')[1]

        page_type = kwargs.get('page_type', 'standard')
        new_obj = kwargs['site_types'][page_type].create_page(kwargs['name'], kwargs['location'],path_name=path_name,subpage_of=subpage_of)
    else:
        object_type = getattr(model, kwargs['object_type'])
        new_obj = object_type(**{'name': kwargs['name']})
    return append_existing_item(list_name, new_obj, **kwargs)

class PageType(object):
    def __init__(self, name, template, view_func=None, can_be_tab=True, static=True, default_vals=None):
        self.name = name
        self.template = template 
        self.view_func = view_func
        self.can_be_tab = can_be_tab
        self.static = static
        self.defaults_vals = default_vals
        if default_vals:
            self.default_vals = default_vals
        else:
            self.default_vals = {}
 
    def create_page(self, page_name, location, initial_vals=None,path_name=None,subpage_of=None):
        #import pdb; pdb.set_trace()
        if not path_name:
            path_name=page_name

        if self.static:
            path_name = path_name + '.html'
        
        attr_vals = dict(**self.default_vals)
        if initial_vals:
            attr_vals.update(initial_vals)

        page = Page(**{'page_type': self.name,
                       'name': page_name,
                       'path_name': path_name,
                       'location': location})
        #pages can have subpages
        List(list_name='subpages_%s' % page.id,
             object_types='Page',
             mode='add_new',
             page=page,
             location=page.location)
        page_wrapper = MetaWrapper(page)
        
        if subpage_of:
            attr_vals['subpage_of'] = subpage_of

        for attr, val in attr_vals.items():
            if not getattr(page_wrapper, attr):
                setattr(page_wrapper, attr, val)
        return page

login_page_type = PageType('login', 'hubspace.templates.microSiteLogin', login_args, static=False, default_vals={'name':"member login", 'subtitle':"book spaces and find members "})
request_password_type =  PageType('requestPassword', 'hubspace.templates.microSitePassword', requestPassword, static=False, can_be_tab=False)
reset_password_type = PageType('resetPassword', 'hubspace.templates.microSitePassword', resetPassword, static=False, can_be_tab=False)

# on starting the application, each type is added to the map
website_page_types =  {
    'home': PageType('home', 'hubspace.templates.webSiteHome', default_vals={'name':"home"}),
    'people': PageType('people', 'hubspace.templates.webSitePeople', get_user, default_vals={'name':"people"}),
    'standard': PageType('standard', 'hubspace.templates.webSiteStandard', default_vals={'name':"contact"}),
    'places': PageType('places', 'hubspace.templates.webSitePlaces', get_public_place, default_vals={'name':"places"}),
    'login': login_page_type,
    'requestPassword':request_password_type,
    'resetPassword':reset_password_type
}
website_pages = {
    'index':'home',
    'contact':'standard',
    'people':'people',
    'places':'places',
    'ideas':'standard',
    'about':'standard',
    'invitation':'standard',
    'contact':'standard',
    'login':'login',
    'requestPassword':'requestPassword',
    'resetPassword':'resetPassword'    
}
website_left_page_list = ['index', 'people', 'places', 'ideas', 'about', 'invitation'] #determines the order the pages appear in tabs which are autocreated
website_right_page_list = ['contact']


microsite_page_types =  {
    'home': PageType('home', 'hubspace.templates.microSiteHome', default_vals={'name':"King's Cross"}),
    'experience': PageType('experience', 'hubspace.templates.microSiteExperience', experience_slideshow, default_vals={'name':"experience", 'subtitle':"the hub at king's cross"}),
    'events': PageType('events', 'hubspace.templates.microSiteEvents', get_events, static=True, default_vals={'name':"events", 'subtitle':"upcoming events and activities"}),
    'spaces': PageType('spaces', 'hubspace.templates.microSiteSpaces', None, static=True, default_vals={'name':"spaces", 'subtitle':"for working and much more"}),
    'blog': PageType('blog', 'hubspace.templates.microSiteBlog', get_blog, static=False),
    'members': PageType('members', 'hubspace.templates.microSiteMembers', get_profiles, default_vals={'name':"our members", 'subtitle':"meet people at the hub"}),
    'join': PageType('join', 'hubspace.templates.microSiteJoinus', default_vals={'name':"join us", 'subtitle':"how to become a member"}),
    'joinConfirm': PageType('joinConfirm', 'hubspace.templates.microSiteJoinus', create_enquiry, static=False, can_be_tab=False),
    'contact': PageType('contact', 'hubspace.templates.microSiteContact', default_vals={'name':"contact", 'subtitle':"get in touch"}),
    'login': login_page_type,
    'requestPassword':request_password_type,
    'resetPassword':reset_password_type,
    'standard': PageType('standard', 'hubspace.templates.microSiteStandard', standard_page, default_vals={'name':"pagex", 'subtitle':"the Hub"}),
    'blog2': PageType('blog2', 'hubspace.templates.microSiteBlog2', get_blog2, static=False),
    'plain': PageType('plain', 'hubspace.templates.microSitePlain', standard_page, default_vals={'name':"pagex", 'subtitle':"the Hub"}),
    'plain2Column': PageType('plain2Column', 'hubspace.templates.microSitePlain2Col', standard_page, default_vals={'name':"pagex", 'subtitle':"the Hub"}),
    'search': PageType('search', 'hubspace.templates.microSiteSearch', sitesearch, static=False),
    }


#these are added to the database when a microsite is created
microsite_pages = {
    'index': 'home',
    'experience': 'experience',
    'events': 'events',
    'spaces':'spaces',
    'members':'members',
    'joinus':'join',
    'joinConfirm': 'joinConfirm',
    'contact': 'contact',
    'login':'login',
    'requestPassword':'requestPassword',
    'resetPassword':'resetPassword'
}

#determines the order the pages appear in tabs which are autocreated
microsite_left_page_list = ['index', 'experience', 'events', 'spaces', 'members', 'joinus']
microsite_right_page_list = ['login', 'contact']




def migrate_data():
    """
    """
    page_metadata_map = {'index':['sub_title', 'find_us_header', 'find_us', 'parking_header', 'parking', 'opening_hours', 'opening_hours_header', 'map_location'],
                         'experience': ['features_header', 'features_body'],
                         'events': ['upcoming_events', 'past_events'],
                         'spaces': ['meeting_rooms', 'meeting_rooms_intro'],
                         'members': ['profiles_header'],
                         'joinus': ['joinus_enquiry', 'joinus_enquiry_intro'],
                         'joinConfirm': ['joinus_body', 'joinus_confirm_header', 'joinus_confirm_body'],
                         'login': [],
                         'requestPassword': [],
                         'resetPassword': []}

    page_attributes = {'index': [('index_title', 'name'), ('site_title', 'title'), ('hub_description', 'content')], 
                       'experience': [('experience_title','name'), ('experience_header', 'title'), ('experience_body', 'content'), ('footer_experience', 'subtitle')],
                       'events': [('events_title','name'), ('events_header', 'title'), ('events_body', 'content'), ('footer_events', 'subtitle')],
                       'spaces': [('spaces_title','name'), ('spaces_header', 'title'), ('spaces_body', 'content'), ('footer_spaces', 'subtitle')],
                       'members': [('members_title','name'), ('members_header', 'title'), ('members_body', 'content'), ('footer_members', 'subtitle')],
                       'joinus': [('joinus_title','name'), ('joinus_header', 'title'), ('joinus_body', 'content'), ('footer_joinus', 'subtitle')],
                       'contact': [('contact_title','name'), ('contact_header', 'title'), ('contact_body', 'content'), ('footer_contact', 'subtitle')],              
                       'login':[('memberlogin_title', 'name')]}

    for loc in Location.select():
        if loc.id == 16:
            continue
        try:
            metadata = LocationMetaData.select(AND(LocationMetaData.q.location == loc,
                                                 LocationMetaData.q.attr_name == 'map_location'))[0]
            db_val = metadata.attr_value
            metadata.destroySelf()
        except IndexError:
            db_val = ""
        if db_val:
            MetaWrapper(loc).geo_address = db_val 

        if not loc.url:
            continue
        for page in Page.select(AND(Page.q.locationID==loc.id)):
            page = MetaWrapper(page)

            fake_microsite = AttrDict({'upload_dir': os.getcwd() + '/hubspace/static/' + loc.url.split('://')[1].replace('.', '_').replace('-', '_') + '/uploads/',
                                       'upload_url': '/static/' + loc.url.split('://')[1].replace('.', '_').replace('-', '_') + '/uploads/'})
            img_source = image_source(page.path_name.split('.')[0]+'.png', fake_microsite)
            if img_source:
                from file_store import LocationFiles
                img_obj = LocationFiles(location=loc, attr_name=page.path_name.split('.')[0]+'.png', mime_type='image/png')
                setattr(page, 'image', img_obj)

            for property in page_metadata_map.get(page.path_name.split('.')[0], []):
                try:
                    metadata = LocationMetaData.select(AND(LocationMetaData.q.location == loc,
                                                           LocationMetaData.q.attr_name == property))[0]
                    db_val = metadata.attr_value
                    metadata.destroySelf()
                except IndexError:
                    continue
                setattr(page, property, db_val)

            for old_property, new_property in page_attributes.get(page.path_name.split('.')[0], []):
                try:
                     metadata = LocationMetaData.select(AND(LocationMetaData.q.location == loc,
                                                             LocationMetaData.q.attr_name == old_property))[0]
                     db_val = metadata.attr_value
                     metadata.destroySelf()
                except IndexError:
                     continue
                setattr(page, new_property, db_val)

def relative_folder(site_url):
     """determine the position of the request compared to the root of the site
     This is used to ensure that relative links in the master template are correct independent of whether we are lower down the url hierarchy
     e.g. when we are at "/sites/kingscross_the_hub_net/members/tom.salfield" nav links should be prepended with "../"

     Overall I think I have learned that it would be better to use absolute urls and then rewrite links on the way out (if as in this case) we want to have dynamically generated templates which need to be viewed as static files at a different location
     """
     extra_path = cherrypy.request.path.replace('/' + site_url + '/', '')
     if 'edit' in extra_path or extra_path.endswith('.html'):
         return './' # this only works because all our staticly written files are at the first level in url hierarchy
     steps_back = extra_path.count('/')
     if steps_back:
         return '../' * steps_back
     else:
         return './'


from hubspace.file_store import save_file

#override with site_folders / functions (if necessary)


class SiteList(controllers.Controller):
    def __init__(self, site):
        super(SiteList, self).__init__()
        self.site = site

    def get_list(self, list_name, page=None):
        """This should return a list of objects which can be rendered by the appropriate templates
        e.g. in the case of spaces this should return a list of objects with the attributes 'name', 'description' and 'image'
        e.g.2. in the case of the site tabs, this should return a list of site_page 'objects' with the relavant metadate fields as attributes
        """
        #if page:
        #    lists = List.selectBy(location=self.site.location,list_name=list_name,page=page)
        #else:
        #    lists = List.selectBy(location=self.site.location,list_name=list_name)
        lists = List.selectBy(location=self.site.location,list_name=list_name)
        if lists.count() == 1:
            thelist = lists[0]
            return {'list_items':self.iterator(list_name), 'list_name':list_name, 'list_types':thelist.object_types.split(','), 'list_mode':thelist.mode}
        #return {'list_items':self.iterator(list_name), 'list_name':list_name, 'list_types':list_types[list_name]['object_types'], 'list_mode':list_types[list_name]['mode']}

    @expose(template='hubspace.templates.listEditor', fragment=True)
    def render_as_table(self, list_name):
        relative_path = relative_folder(self.site.site_url)
        #list_name,pageid = parseSubpageId(list_name)
        #import pdb; pdb.set_trace()
        #hack
        #if pageid :
        #    page = Page.get(pageid)
        #    template_args = self.get_list(list_name,page)
        #    #relative_path =  relative_path[3:] #remove the first ../           
        #    template_args.update({'pageid':pageid})
        #else:
        #    template_args = self.get_list(list_name)
        #    template_args.update({'pageid':None})
        template_args = self.get_list(list_name)
	template_args.update({'page_types_dict':self.site.site_types})
        template_args.update({'page_types':[type[0] for type in self.site.site_types.iteritems() if type[1].can_be_tab]})
        template_args.update({'relative_path': relative_path})
        #template_args.update({'orig_name':orig_name})
        return template_args

    @expose()
    @validate(validators={'list_name':v.UnicodeString(), "order":ForEach(v.Int())})
    def reorder(self, list_name, order=None):
        """iterate new list and check if each item is in the right place, if a next of an object doesn't correspond to the next in the list, change .next on the object. On the last object in the list, set next = None.
        We should put some safe guards in place to stop any possibility of cycling next references - this will block the application if it occurs
        """
	if not is_host(identity.current.user, Location.get(self.site.location)):
            raise IdentityFailure('what about not hacking the system')

        first = self.first(list_name)
        new_first = ListItem.get(order[0])
        if new_first != first:
            try:
               new_first.previous.next = None
            except AttributeError:
               pass
        previous = new_first
        for id in order[1:]:
            current = previous.next   
            new_current = ListItem.get(id)
            if current != new_current:
                previous.next = new_current
            previous = new_current

        new_last = ListItem.get(id)
        if new_last != self.last(list_name):
            new_last.next = None
        return "success"
     
    def last(self, list_name):
        return last_item(list_name, self.site.location)

    def first(self, list_name):
        lists = List.selectBy(list_name=list_name,location=self.site.location)
        if lists.count() == 1:
            thelist = lists[0]
            for item in ListItem.selectBy(list=thelist):
                if item.previous == None:
                   return item
        #below doesn't work because .previous doesn't exist where it isn't referenced by another "Space" with .next()
        #try:
        #    return MicroSiteSpace.select(AND(MicroSiteSpace.q.previous == None,
        #                                     MicroSiteSpace.q.locationID == self.site.location))[0]
        #except IndexError:
        #    return None
	    
    def iterator(self, list_name):
        current = self.first(list_name)
        if current:
            yield current
            while current.next:
                yield current.next
                current = current.next


    @expose()
    @validate(validators={'list_name':v.UnicodeString(), 'object_type':v.UnicodeString(), 'object_id':v.Int(), 'active':v.Int(if_empty=0),'pageid':v.Int(if_missing=1)})
    def append_existing(self, list_name, **kwargs):
        #import pdb; pdb.set_trace()
        if not is_host(identity.current.user, Location.get(self.site.location)):
            raise IdentityFailure('what about not hacking the system')
        kwargs['location'] = self.site.location
        kwargs['site_types'] = self.site.site_types
        try:
            obj = getattr(model, kwargs['object_type']).get(kwargs['object_id'])
            append_existing_item(list_name, obj, **kwargs)
        except:
            pass
        return self.render_as_table(list_name)

    @expose()
    @validate(validators={'list_name':v.UnicodeString(), 'object_type':v.UnicodeString(), 'page_type':v.UnicodeString(), 'name':v.UnicodeString(), 'active':v.Int(if_empty=0),'pageid':v.Int(if_missing=1)})
    def append(self, list_name, **kwargs):
        if not is_host(identity.current.user, Location.get(self.site.location)):
            raise IdentityFailure('what about not hacking the system')
        kwargs['location'] = self.site.location
        kwargs['site_types'] = self.site.site_types
        append_to_list(list_name, **kwargs)
        return self.render_as_table(list_name)

    @expose()
    @validate(validators={'list_name':v.UnicodeString(), 'item_id':v.Int(if_empty=None)})
    def remove(self, list_name, item_id):
        if not is_host(identity.current.user, Location.get(self.site.location)):
            raise IdentityFailure('what about not hacking the system')
        
        self._remove(list_name,item_id)
        return self.render_as_table(list_name)           

    def _remove(self,list_name,item_id): #XXX is this secured against web attacks?
        item = ListItem.get(item_id)
        if item.previous:
            if item.next:
                item.previous.next = item.next
            else:
                item.previous.next = None
        #pages have subpages - lets destroy them first, which could have subpages...               
        if item.object.__class__ == Page:
            for sublist in item.object.lists:
                for subitem in sublist.listitems:
                    self._remove(sublist.list_name,subitem.id)
                    #item.object.destroySelf()
                    #item.destroySelf()
                sublist.destroySelf()
        item.object.destroySelf()
        item.destroySelf()

    @expose()
    @validate(validators={'list_name':v.UnicodeString(), 'item_id':v.Int(if_empty=None)})
    def remove_existing(self, list_name, item_id):
        if not is_host(identity.current.user, Location.get(self.site.location)):
            raise IdentityFailure('what about not hacking the system')
        item = ListItem.get(item_id)
        if item.previous:
            if item.next:
                item.previous.next = item.next
            else:
                item.previous.next = None
        item.destroySelf()
        return self.render_as_table(list_name)


    @expose()
    @validate(validators={'list_name':v.UnicodeString(), 'object_id':v.UnicodeString(), 'active':v.Int(if_empty=0)})
    def toggle_active(self, list_name, object_id,  active=0):
        if not is_host(identity.current.user, Location.get(self.site.location)):
            raise IdentityFailure('what about not hacking the system')
        item = ListItem.get(object_id)
        item.active = active
        return self.render_as_table(list_name)

class MicroSiteEdit(controllers.Controller):
    def __init__(self, site):
        super(MicroSiteEdit, self).__init__()
        self.site = site

    @expose(template='hubspace.templates.uploadImage')
    def uploadImageIframe(self, id, type, attr, height=0, width=0, page_name=""):
        return {'id':id, 'type':type, 'attr':attr, 'relative_path':'../../../../' + relative_folder(self.site.site_url)+'edit/', 'height': height, 'width': width, 'page_name':page_name}


    @expose()
    @validate(validators={'object_id':real_int, 'object_type':v.UnicodeString(), 'property':v.UnicodeString(), 'height':v.Int(), 'width': v.Int(), 'page_name':v.UnicodeString()})
    def uploadImage(self, object_id, object_type, property, image, height=None, width=None, page_name='index.html', tg_errors=None):
        # for some very strange reason height and width come through as unicode
        if tg_errors:
            for tg_error in tg_errors:
                print `tg_error`, str(tg_errors[tg_error])
            return "error uploading"
        if height:
            height = int(height)
        if width:
            width = int(width)
        obj = MetaWrapper(obj_of_type(object_type, object_id))
        location = Location.get(self.site.location)
        if not is_host(identity.current.user, location):
            raise IdentityFailure('what about not hacking the system')

        elif object_type in ['PublicSpace', 'Page', 'PublicPlace', 'Location']:
            file_object = save_file(location.id, image, height=height, width=width, upload_dir=self.site.upload_dir)
            print `obj` + `property` + str(int(file_object.id))
            setattr(obj, property, str(int(file_object.id)))

        if page_name.endswith('.html'):
            self.site.render_page(page_name)
        return "<div id='new_image_src'>" + self.site.upload_url + file_object.attr_name + "</div>"

    @expose()
    @validate(validators={'user_name':username, 'first_name':no_ws_ne_cp, 'last_name':no_ws_ne_cp, 'email_address':email_address, 'organisation':no_ws, 'home':phone})
    def create_inactive_user(self, tg_errors=None, user_name=None, first_name=None, last_name=None, email_address=None, organisation=None, home=None, hmac=''):
        #check hmac
        hmac_key = config.get('hmac_key', None)
        if hmac_key:
            link, auth_code = cherrypy.request.browser_url.split('&hmac=')
            if create_hmac.new(hmac_key, link, sha1).hexdigest() != auth_code:
                raise "Invalid key"
        else:
            raise "please add an hmac_key='random_key' to the config file"

        if tg_errors:
            for tg_error in tg_errors:
                print `tg_error`, str(tg_errors[tg_error])
            return "Insufficient information to create a user - Please create this one manually"
        location = Location.get(self.site.location)
        user_args = {'user_name': user_name,
                     'first_name': first_name,
                     'last_name' : last_name,
                     'email_address': email_address,
                     'organisation': organisation,
                     'home': home,
                     'active': 0, 
                     'homeplace': location,
                     'password': md5.new(str(random.random())).hexdigest()[:8]}

        #create the user
        user = User(**user_args)

        #make user as a member of the homeplace
        home_group = Group.selectBy(level='member', place=location)[0]
        addUser2Group(user, home_group)

        #tag the user

        #redirect to hubspace
        redirect(cherrypy.request.base)

    @expose()
    @validate(validators={'object_type':v.UnicodeString(), 'object_id':real_int, 'property':v.UnicodeString(), 'default':v.UnicodeString()})
    def attribute_load(self, object_type, object_id, property, default=''):
        """load the attribute of any object type
        """
        obj = obj_of_type(object_type, object_id)
        obj = MetaWrapper(obj)
        try:
            val = getattr(obj, property)
        except AttributeError:
            val = default
        return val and val or default

    @expose()
    @strongly_expire
    @identity.require(identity.not_anonymous())
    @validate(validators={'object_type':v.UnicodeString(), 'property':v.UnicodeString(), 'q':v.UnicodeString()})
    def auto_complete(self, object_type, property, q, timestamp, **kwargs):
        q = '% '.join(q.split(' ')) + '%'
        type = getattr(model, object_type)
        magic_prop = getattr(type.q, property)
        members = list(type.select(AND(LIKE(func.lower(magic_prop), q.lower()), 
                                       User.q.public_field == 1))[:10])
        if len(members) < 10:
            q = '%' +q
            members = set(members).union(set(type.select(AND(LIKE(func.lower(magic_prop), q.lower()),
                                                              User.q.public_field == 1))[:10-len(members)]))

        members = [getattr(member, property) +'|'+ str(member.id) for member in members]
        return '\n'.join(members)


    @expose()
    @validate(validators={'object_type':v.UnicodeString(), 'object_id':real_int, 'property':v.UnicodeString(), 'value': v.UnicodeString(), 'page_name': v.UnicodeString()})
    def attribute_edit(self, object_type=None, object_id=None, property=None, value="", page_name="index.html", tg_errors=None):
        """edit the attribute of any object type
        """
        if tg_errors:
            cherrypy.response.headers['X-JSON'] = 'error'
            for tg_error in tg_errors:
                error = `tg_error` + " " + str(tg_errors[tg_error])
            return error

        page_name = page_name.split('#')[0]
        value = html2xhtml(value)

        obj = obj_of_type(object_type, object_id)
        obj = MetaWrapper(obj)
        if not is_host(identity.current.user, Location.get(self.site.location)):
            raise IdentityFailure('what about not hacking the system')

        if value != getattr(obj, property):
            setattr(obj, property, value)
            self.site.attr_changed(property, page_name)
        cherrypy.response.headers['X-JSON'] = 'success'
        return value


class MicroSite(controllers.Controller):
    def __init__(self, location, site_dir, site_url, static_url, site_types):
        super(MicroSite, self).__init__()
        self.location = location.id
        self.site_dir = site_dir
        self.site_url = site_url
        self.static_url = static_url
        self.upload_dir = self.site_dir + '/uploads/'
        self.upload_url = self.static_url + '/uploads/'
        self.initialized = False
        self.site_types = site_types
        self.add_edit_controllers()
                       
    def _cpOnError(self):
        try:
            raise # http://www.cherrypy.org/wiki/ErrorsAndExceptions#a2.2
        #use this for getting 404s...
        #except Exception, err:
        #    if isinstance(err, IndexError):

        #...or this for getting logging                
        #except:
        #    if 0: 
        except IndexError,err:
            applogger.exception("microsite request %s 404:" % cherrypy.request.path)
            cherrypy.response.status = 404
            cherrypy.response.body = "404"
        except Exception,err:
            """log the error and give the user a trac page to submit the bug
            We should give the error a UID so that we can find the error associated more easily
            """
            # If syncer transaction fails the syncer daemon takes care of rolling back the changes also
            # syncerclient then raises SyncerError effectively stops TG transaction from commiting
            # changes to native database.
            # For all other errors we should call syncer rollback here.
            # And finally if there is no error, we send transaction complete signal to syncer. Which is
            # handled by TransactionCompleter filter.
            if config.get('server.testing', False):
                cherrypy.response.status = 500
            else:
                cherrypy.response.status = 200
            e_info = sys.exc_info()
            e_id = str(datetime.datetime.now())
            e_path = cherrypy.request.path
            _v = lambda v: str(v)[:20]
            e_params = dict([(k, _v(v)) for (k, v) in cherrypy.request.paramMap.items()])
            e_hdr = cherrypy.request.headerMap
            applogger.error("%(e_id)s: Path:%(e_path)s" % locals())
            applogger.error("%(e_id)s: Params:%(e_params)s" % locals())
            applogger.exception("%(e_id)s:" % locals())
            if isinstance(e_info[1], sync.SyncerError):
                applogger.error("%(e_id)s: LDAP sync error" % locals())
            else:
                sync.sendRollbackSignal()
            tb = sys.exc_info()[2]
            e_str = traceback.format_exc(tb)
            if isinstance(e_info[1], hubspace.errors.ErrorWithHint):
                e_hint = e_info[1].hint
            else:
                e_hint = ""
            d = dict(e_id=e_id, e_path=e_path, e_str=e_str, e_hint=e_hint)
            cherrypy.response.body = try_render(d, template='hubspace.templates.issue', format='xhtml', headers={'content-type':'text/html'}, fragment=True)

    def attr_changed(self, property, page_name):
        if property in ('name', 'subtitle'):
            self.regenerate_all()
        elif self.site_types[Page.select(AND(Page.q.path_name == page_name,
                                             Page.q.locationID == self.location))[0].page_type].static:
            self.render_page(page_name)

    def add_edit_controllers(self):
        setattr(self, 'edit', MicroSiteEdit(self))
        setattr(self, 'lists', SiteList(self))
    
    def regenerate_all(self):
        for page in Page.select(AND(Page.q.location==self.location)):
            if self.site_types[page.page_type].static == True:
                try:
                    self.render_page(page.path_name, relative_path='./')
                except:
                    applogger.exception("failed to render page with name " + page.name + ", location " + `self.location` + " and id " + `page.id`  )

    def construct_args(self, page_name, *args, **kwargs):
        template_args = dict(site_template_args)
        try:
            page = MetaWrapper(Page.select(AND(Page.q.location==self.location, Page.q.path_name==page_name))[0])
        except (KeyError, IndexError):
            try:
                page = MetaWrapper(Page.select(AND(Page.q.location==self.location, Page.q.path_name==page_name + '.html'))[0])
            except:
                applogger.error("microsite: not found page for with location [%s] and page_name [%s]" % (self.location, page_name))
                applogger.debug("debug info: args [%s] kwargs [%s]" % (str(args), str(kwargs)))
                raise

        func = self.site_types[page.page_type].view_func
        if func:
             kwargs['location'] = self.location
             kwargs['microsite'] = self
             kwargs['page'] = page
             args_dict = func(*args, **kwargs)
        else:
             args_dict = {}
        if kwargs.get('relative_path', None):
            template_args.update({'relative_path': kwargs['relative_path']}) 
        else:
            template_args.update({'relative_path': relative_folder(self.site_url)})
        template_args.update({'static_files_path': self.upload_url})
        template_args.update({'lists': self.lists.iterator, 'upload_url': self.upload_url})
        template_args.update({'top_image_src': top_image_src(page, microsite=self)})
        template_args.update({'upload_url': self.upload_url})
        template_args.update(args_dict)
        location = MetaWrapper(Location.get(self.location))
        template_args.update({'page':page, 'location':location, 'site_url': self.site_url})

        return template_args

    def get_sidebar(self,location,page):
        blogs = Page.selectBy(location=location,page_type='blog2').orderBy('id')
        if blogs.count() > 0:
            sidebarblog = blogs[0]
            sidebarblog = MetaWrapper(sidebarblog)
            parts =  get_blog(location=location,page=sidebarblog,microsite=self)
            out = dict(blog_head=parts['blog_head'],blog=parts['sidebartext'])
        else:
            out = dict(blog_head='',blog='')
        return out


    @expose()
    def jhb(self, *args, **kwargs):
        raise 'foo2'
        return 'foo bar'

        
  
    @expose()
    def icalfeed_ics(self,eventid=None,*args,**kwargs):
        #import pdb; pdb.set_trace()
        location = Location.get(self.location)
        if eventid:
            events = [RUsage.get(eventid)]
        else:
            events = get_local_future_events(location=self.location, no_of_events=1000)['future_events']
        cal = vobject.iCalendar()
        cal.add('X-WR-CALNAME').value = "%s (%s) events" % (location.name,location.city)
        cal.add('X-WR-TIMEZONE').value = location.timezone
        length = 0
        for event in events:
            length += 1
            ve = cal.add('vevent')
            ve.add('summary').value = event.meeting_name
            ve.add('description').value = event.meeting_description
            ve.add('dtstart').value = event.start
            ve.add('dtend').value = event.end_time
            url = cherrypy.request.base + '/public/events/' + str(event.id)
            ve.add('uid').value = url
            ve.add('url').value = url

        cherrypy.response.headers['Content-Type'] = 'text/calendar'
        cherrypy.response.headers['Content-Disposition'] = 'attachment; filename="icalfeed.ics"'
        
        return cal.serialize()

    @expose()
    def default(self, *args, **kwargs):
        """This needs securing a little bit
        """
        if kwargs.get('tg_errors', None):
             return str(kwargs['tg_errors'])

        if cherrypy.request.path.split('/')[-1] == self.site_dir.split('/')[-1]:
             redirect(cherrypy.request.path + '/')

        if not args or args[0]=='':
            path_name = configuration.site_index_page[Location.get(self.location).url]
        else:
            path_name = args[0]
            args = args[1:]

        if not self.initialized:
            self.regenerate_all()
            self.initialized = True
        try:
            html =  self.render_page(path_name, *args, **kwargs)
            
            #page = Page.select(AND(Page.q.location==self.location, 
            #                       Page.q.path_name==path_name))[0]
            #sidebar_content = self.get_sidebar(location=self.location, page=page)
            #html = html.replace('<!-- sidebar headers -->',sidebar_content['blog_head'])
            #html = html.replace('<!-- sidebar content -->',sidebar_content['blog'])
            return html

        except MediaContent, e:
            cherrypy.response.headers['Content-Type'] = e.response.headers['Content-Type']
            cherrypy.response.headers['Content-Length'] = e.response.headers['Content-Length']
            return e.response.read()
        except AjaxContent, e:
            return e.html

    @expose()
    def blog_media_content(*args,**kwargs):
        path_name = args[0]
        subpath = '/'.join(args[1:])

        try:
            page = MetaWrapper(Page.select(AND(Page.q.location==self.location, Page.q.path_name==page_name))[0])
        except (KeyError, IndexError):
            page = MetaWrapper(Page.select(AND(Page.q.location==self.location, Page.q.path_name==page_name + '.html'))[0])
        
        if not page.page_type == 'blog': #should always be the case (in normal use)
            raise 'shit'
        if subpath.endswith('/'):
            subpath = subpath[:-1]
            
    def render_page(self, path_name, *args, **kwargs):
        applogger.debug("render_page: request for [%s]" % path_name)
        path_name = path_name.split('#')[0]
        try:
            template_args = self.construct_args(path_name, *args, **kwargs)
        except Exception, err:
            applogger.error("render_page: failed for path_name [%s], args [%s], kwargs [%s]" % (path_name, str(args), str(kwargs)))
            raise

        if path_name:
            page = Page.select(AND(Page.q.location==self.location, IN(Page.q.path_name, path_name + '.html')))[0]
            template = self.site_types[page.page_type].template
        else:
            page = None
            template = 'hubspace.templates.microSiteHome'
           
        out = try_render(template_args, template=template, format='xhtml', headers={'content-type':'text/xhtml'})

        if self.site_types[page.page_type].static:
            path = self.site_dir + '/' + page.path_name + '.html'
            applogger.info("render_page: generating [%s]" % path)
            new_html = open(path, 'w')
            new_html.write(out)
            new_html.close()
        return out

class Sites(controllers.Controller):
    def __init__(self):
        super(Sites, self).__init__()
        for loc in Location.select(AND(Location.q.url!=None)):
            self.add_site(loc)

    def add_site(self, loc):
        """This should be called when first setting the url of location
        """
        if not loc.url:
            return
        site_path = loc.url.split('://')[1].replace('.', '_').replace('-', '_')
        static_dir = os.getcwd() + '/hubspace/static/'
        static_url = '/static/' + site_path
        site_dir = static_dir + site_path
        site_url = 'sites/' + site_path
        if loc.url not in ["http://the-hub.net", "http://new.the-hub.net"]:
            site_types = microsite_page_types
            site_pages = microsite_pages
            site_left_tabs = microsite_left_page_list
            site_right_tabs = microsite_right_page_list
        else:
            site_types = website_page_types
            site_pages = website_pages
            site_left_tabs = website_left_page_list
            site_right_tabs = website_right_page_list
        #create the static directory if it doesn't exist
        try:
            os.stat(site_dir)
        except OSError:
            os.mkdir(site_dir)
            os.mkdir(site_dir + '/uploads')
        try:
            Page.select(AND(Page.q.location==loc))[0]
        except IndexError:
            index_pages = self.create_pages(loc, site_types, site_pages)
            self.create_page_lists(loc, site_left_tabs, site_right_tabs, index_pages[loc])

        setattr(self.__class__, site_path, MicroSite(loc, site_dir, site_url, static_url, site_types))

    def create_pages(self, loc, site_types, site_pages):
        index_pages = {}
        for page, type in site_pages.items():
            p = site_types[type].create_page(page, loc, {})
            if page == 'index':
                index_pages[loc] = p
        return index_pages

    def create_page_lists(self, loc, left_tabs, right_tabs, index_page):
        for list_name, data in list_types.items():
            object_types = ','.join(data['object_types'])
            List(list_name=list_name,
                 object_types=object_types,
                 mode=data['mode'],
                 page=index_page,
                 location=loc,)
        kwargs = {'location':loc, 'object_type': Page, 'active': 1}
        for page in left_tabs:
            kwargs.update({'name':page})
            try:
                page = Page.select(AND(Page.q.location == loc,
                                       IN(Page.q.path_name, [page, page + '.html'])))[0]
                append_existing_item('left_tabs', page, **kwargs)
            except IndexError:
                pass
        for page in right_tabs: 
            kwargs.update({'name':page})
            try:
                page = Page.select(AND(Page.q.location == loc,
                                       IN(Page.q.path_name, [page, page + '.html'])))[0]
                append_existing_item('right_tabs', page, **kwargs)
            except IndexError:
                pass
  
    def move_site(self, loc, new_url):
        """this should be called on changing the url of a location
        """
	pass
        
def refresh_static_pages():
    sites = (site for site in cherrypy.root.sites.__class__.__dict__.values() if isinstance(site, MicroSite))
    for site in sites:
        static_pages = glob.glob(site.site_dir + '/*.html')
        get_mtime = lambda path: datetime.datetime.fromtimestamp(os.stat(path).st_mtime)
        page_times = ((page, get_mtime(page)) for page in static_pages)
        for page, m_time in page_times:
            if not now(site.location).day == m_time.day:
                applogger.info("microsite: removing %s" % page)
                os.remove(page)

    
def remove_generated_page(location_id, page_type):
    sites = (site for site in cherrypy.root.sites.__class__.__dict__.values() if isinstance(site, MicroSite))
    for site in sites:
        if site.location == location_id: break
    else:
        applogger.warning("could not find microsite instance for location [%d] page_type [%s]" % (location_id, page_type))
        return
    if site.site_types[page_type].static:
        pages = Page.select(AND(Page.q.location==location_id, Page.q.page_type==page_type))
        for page in pages:
            path = site.site_dir + '/' + page.path_name
            applogger.info("microsite: removing %s" % path)
            if os.path.isfile(path):
                os.remove(path)

def on_add_rusage(kwargs, post_funcs):
    rusage = kwargs['class'].get(kwargs['id'])
    if rusage.public_field:
        applogger.info("microsite.on_add_rusage: added %(id)s" % kwargs)
        location = rusage.resource.place.id
        remove_generated_page(location, "events")

def on_del_rusage(rusage, post_funcs):
    if rusage.public_field:
        applogger.info("microsite.on_del_rusage: removing %s" % rusage.id)
        location = rusage.resource.placeID
        remove_generated_page(location, "events")

def on_updt_rusage(instance, kwargs):
    if 'public_field' in kwargs or instance.public_field: #  not precise logic
        applogger.info("microsite.on_updt_rusage: updating %s" % instance.id)
        location = instance.resource.placeID
        remove_generated_page(location, "events")
    
def on_add_user(kwargs, post_funcs):
    user = kwargs['class'].get(kwargs['id'])
    if user.public_field:
        applogger.info("microsite.on_add_user: updating %s" % instance.id)
        location = user.homeplaceID
        remove_generated_page(location, "members")

def on_updt_user(instance, kwargs):
    if 'public_field' in kwargs or instance.public_field: #  not precise logic
        applogger.info("microsite.on_updt_user: updating %s" % instance.id)
        location = instance.homeplaceID
        remove_generated_page(location, "members")

listen(on_add_rusage, RUsage, RowCreatedSignal)
listen(on_updt_rusage, RUsage, RowUpdateSignal)
listen(on_del_rusage, RUsage, RowDestroySignal)
listen(on_add_user, User, RowCreatedSignal)
listen(on_updt_user, User, RowUpdateSignal)
