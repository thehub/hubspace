<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" 
     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<?python 
import cherrypy
from hubspace.templates.memberslist import member_list
from hubspace.model import User, Location

from hubspace.controllers import filter_members, permission_or_owner, title, new_or_old
production = False
from sqlobject import AND
from hubspace.utilities.static_files import get_version_no, css_files, js_files
js_version_no = get_version_no("hubspace.js")
admin_js_version_no = get_version_no("admin.js")
from hubspace.utilities.permissions import user_locations
from hubspace.utilities.i18n import get_hubspace_locale, get_location_from_base_url
import turbogears
def host_in_rfid_location():
   return len([loc for loc in user_locations(turbogears.identity.current.user, ['host']) if loc.rfid_enabled])
   

?>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en" xmlns:py="http://purl.org/kid/ns#" py:extends="sitetemplate">
<head py:match="item.tag=='{http://www.w3.org/1999/xhtml}head'" py:attrs="item.items()">
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title py:content="title[cherrypy.request.base]">Bradford GRID</title>
    <c py:if="not production" py:strip="True">
        <style py:for="filename in css_files" type="text/css">@import url(/static/css/${filename});</style>
    </c>
    <style py:if="production" type="text/css">@import url(/static/css/hubspace.css);</style>
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
    <c py:if="not production" py:strip="True">
    <script py:for="filename in js_files" src='/static/javascript/${filename}' ></script>
    </c>
    <script py:if="production" src="/static/javascript/hubspace${js_version_no}.js" />
</head>
<body py:match="item.tag=='{http://www.w3.org/1999/xhtml}body'" py:attrs="item.items()" >
        <input id="admin_js_no" value="${admin_js_version_no}" type="hidden" />
	<div id="content">
		<a href="${new_or_old.get(cherrypy.request.base, 'old')=='new' and '/public/' or ''}"><div id="header">        </div></a>
        <div id="main_body">
            <div py:if="tg.config('identity.on',False) and not 'logging_in' in locals()" id="pageLogin">
                <span py:if="tg.identity.anonymous">
                    <a href="/login">Login</a>
                </span>
                <span py:if="not tg.identity.anonymous">
                    Hello ${tg.identity.user.first_name}.
                    <a href="/logout">Logout</a>
                </span>
            </div>
	    <ul id="nav">
	        <li id="networkBut" py:attrs="{'class':'area' in locals() and area=='network' and 'selected'}"><a style="cursor:pointer;" class="load_section" id="0">Network</a></li>
		<li id="profileBut" py:attrs="{'class':'area' in locals() and area=='profile' and 'selected'}"><a style="cursor:pointer;" class="load_section" id="1">My Profile</a></li>
		<li id="spaceBut" class="deselected"><a style="cursor:pointer;" class="load_section" id="2">Space</a></li>
		<li id="hostBut" class="deselected" style='${permission_or_owner(None, None, "manage_users") and " " or "display:none"}'><a style="cursor:pointer;" class="load_section" id="3">Hosting</a></li>
                <li id="microSiteLink" class="deselected" py:if="permission_or_owner(get_location_from_base_url(), None, 'manage_users')" ><a href="/admin/">Manage Website</a></li>
<li><span id="throbber"><img src="/static/images/timer_2.gif" /> <span id="throbtext">loading... </span></span></li>
                
	    </ul>
	    <div id="members">
		<input type="input" id="member_search" value="Search member names"/>
                <div id="search_type">
                    <div>
                       <input class="radio_button" type="radio" name="type" id="member_search_button"  value="member_search" checked="checked" />
                       <label>Search member names</label>
                    </div>
                    <div>
                       <input class="radio_button" type="radio" name="type" id="fulltext_member_search_button" value="fulltext_member_search" />
                       <label>Search everything</label>
                    </div>
                    <div py:if="host_in_rfid_location()" >
                       <input class="radio_button" type="radio" name="type" id="rfid_member_search_button" value="rfid_member_search" />
                       <label>Search by membership card</label>
                    </div>
                </div>
		<div id="searchExtra">
		    <select id="search_locality" name="hub">
			<option value="0" selected="selected">All Hubs</option>
		        <option py:for="location in Location.select(AND(Location.q.is_region==0), orderBy='name')" value="${location.id}">${location.name}</option>
		    </select>
		</div>
		<div class="scrollArrow up"><div class="scrollArrow" id="up"></div></div>
	        <div id="drag"></div>
	        <div id="track"></div>
	        <div id="memberList" style="height: 331px;">
		    <ul id="membersContent">
			  ${member_list(filter_members(location=None, text_filter="", type="member_search", active_only=False, start=0, end=80))}
		    </ul>
	        </div>
	        <div class="scrollArrow down"><div class="scrollArrow" id="down"></div></div>	
                <div py:if="permission_or_owner(None, None, 'manage_users')" id="color_key" />
                <div py:if="not permission_or_owner(None, None, 'manage_users')" id="member_color_key" />
       	        <div id="memberDetails">
	        </div>
	    </div>			           
            <div id="contentPane">
                <div py:replace="item[:]"/>
            </div> 
        </div>
    </div>
</body>
</html>
