<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<?python 
import cherrypy
from hubspace.templates.memberslist import member_list
from hubspace.model import User, Location

from hubspace.controllers import filter_members, permission_or_owner, title, new_or_old
from turbogears import config
mode = config.get('js_mode', 'prod')
from sqlobject import AND
from hubspace.utilities.static_files import get_version_no, css_files, js_files2
js_version_no = get_version_no("hubspace.js")
admin_js_version_no = get_version_no("admin.js")
from hubspace.utilities.permissions import user_locations
from hubspace.utilities.i18n import get_hubspace_locale, get_location_from_base_url
import turbogears
def host_in_rfid_location():
   return len([loc for loc in user_locations(turbogears.identity.current.user, ['host']) if loc.rfid_enabled])
   

?>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en" xmlns:py="http://purl.org/kid/ns#" py:extends="sitetemplate">
<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title py:content="title[cherrypy.request.base]">Bradford GRID</title>
    <c py:if="mode=='dev'" py:strip="True">
        <style py:for="filename in css_files" type="text/css">@import url(/static/css/${filename});</style>
    </c>
    <style py:if="mode=='prod'" type="text/css">@import url(/static/css/hubspace.css);</style>
        <!--[if gte IE 5]>
	    <style type="text/css">@import url(/static/css/ie.css);</style>
        <![endif]-->
    <style type="text/css">
        #pageLogin
        {
            font-size: 10px;
            font-family: verdana;
            text-align: right;
        }
    </style>
    <link rel="Shortcut icon" href="/static/images/favicon.ico" type="image/x-icon" />
    <link rel="stylesheet" type="text/css" href="/static/css/stripdown.css" />
    <c py:if="mode=='dev'" py:strip="True">
    <script py:for="filename in js_files2" src='/static/javascript/${filename}' ></script>
    </c>
    <script py:if="mode=='prod'" src="/static/javascript/pluspace${js_version_no}.js"></script>
    ${include_js()}
</head>
<body>
        <div id="current_user_id" class="${object.id}" style='display:none' />
        <input id="admin_js_no" value="${admin_js_version_no}" type="hidden" />
	<div id="content">
        <div id="main_body">
            <div py:if="tg.config('identity.on',False) and not 'logging_in' in locals()" id="pageLogin">
                <span py:if="tg.identity.anonymous">
                    <a href="/login">Login</a>
                </span>
            </div>
    <span id="throbber"><img src="/static/images/timer_2.gif" /> <span id="throbtext">loading... </span></span>
                
            <div id="contentPane">
            ${load_content(object)}
            </div> 
            </div> 
            </div> 
    </body>
</html>

