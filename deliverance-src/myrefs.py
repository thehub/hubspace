import re,lxml
from lxml import etree,objectify
import re
import os
from deliverance.util.proxyrequest import Request, Response
from deliverance.exceptions import AbortProxy

#the whole lookup needs obviously to be extended once there is more then
#one site to cover

#lighty: http://bay.the-hub.net/public/(.*) -> http://spacedev.the-hub.net:8001/$1
#

deliverance_base = "http://space-hub.the-hub.net:8021" #'http://spacedev.the-hub.net:8001' #where are we
config = {}
config['wp_url'] = 'http://bayarea.wordpressdev.the-hub.net' #which blog to proxy
config['hubspace_url'] = 'http://bayarea.the-hub.net'   # 'http://hubspacedev.the-hub.net' # which microsite to proxy
config['events_hubspace'] = 'http://bayarea.the-hub.net/events' #which are the links that need rewriting
config['events_microsite'] = deliverance_base+'/public/events' #which events entry to use in the microsite 
config['calendarurl'] = deliverance_base+'/public/events__calendar.html' #where is the calendar to point the event widget links to
config['microsite_blog']=deliverance_base + '/public/theblog' #and where is the blog page for the blog based links in the sidebar

config['ajax_url'] = config['hubspace_url']+'/admin/lists'

def get_main_destination(request,log):
    if request.script_name:
        raise AbortProxy
    return config['hubspace_url']    

def get_ajax_destination(request,log):
    return config['ajax_url']

def get_wp_destination(request,log):
    return config['wp_url']

def get_theme_url(request, log):
    return os.path.join(config['hubspace_url'], 'static/deliverance')

#never theme ajax,css or images
def match_notheme(req, resp, headers, *args):
    if 'text/html' in resp.headers['Content-Type'].lower():
        return False
    else:
        return True

#some pages require not to have a sidebar. This might be
#because of nosidebarplease in the hubspace template or 
#content that was entered in one of the boxes on the page
def match_hasrightcolumn(req, resp, headers, *args):
    if 'wp-' in req.path_info:
        return False
    elif 'nosidebarplease' in resp.body:
        return False
    else:
        return True

#if we already have wp headers, we don't need them again
def match_needswpheaders(req,resp,headers,*args):
    if re.findall('<head>.*<script[^>]+wp-[^>]*>.*</head>',resp.body,re.S|re.I):
        return False
    else:
        return True

def match_hasbanner(req,resp,headers,*args):
    return 'nobannerplease' not in resp.body

def match_dropbanner(req,resp,headers,*args):
    return not match_hasbanner(req,resp,headers,*args)

def modify_blog_response(request, response, orig_base, proxied_base, proxied_url, log):
    # orig_base: the original URL base: http://localhost:8080/trac
    # proxied_base: where dest sent it to: http://localhost:10001/
    # proxied_url: the full destination, e.g.,
    #    http://localhost:10001/view/1
    # request.url: the full original URL, e.g.,
    #    http://localhost:8080/trac/view/1
    body = response.body

    #having text_small in the classes causes a conflict between prototype and jq based
    #scripts. 
    body = body.replace('text_small','')
    
    if orig_base.endswith('/'):
        orig_base = orig_base[:-1]
    
    #rewrite the urls from the sidebar to point to the blog in the microsite 
    body = body.replace(orig_base,config['microsite_blog'])

    #the validate script causes errors
    body = re.sub('<script[^>]*?validate[^>]*?>[^<]*</script>','',body)

    #rewrite the header of the events widget
    body = re.sub('<a class="rsswidget" href="[^"]+" title="Pipes Output"',
                  '<a class="rsswidget" href="%s" title="Pipes Output"' % config['calendarurl'], body)

    #...and the links in the events widget
    body = body.replace(config['events_hubspace'],config['events_microsite'])
    
    response.body = body
    return response 



def modify_main_response(request, response, orig_base, proxied_base, proxied_url, log):

    if 'wp-login' in request.path_info:
        response.body = re.sub(r'<body(.*?)class="(.*?)"([^>]*)>',r'<body\1class="login \2"\3>',response.body)

    #oh, what an ugly js hack. Kind of a custom noConflict
    if 'functions.js' in request.path_info:
        response.body = re.sub(r'\$',r'jq',response.body)
        
    return response 





