<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python 
import cherrypy
from hubspace.templates.memberslist import member_list
from hubspace.model import User, Location
from hubspace.controllers import title
# for date time  need for calendar
from turbogears import identity
from datetime import date, datetime, timedelta
from hubspace.utilities.image_helpers import image_src
from hubspace.validators import datetimeconverter2, timeconverter
def namespace():
    return {'xmlns':"http://www.w3.org/1999/xhtml"}
?>
<html xmlns:py="http://purl.org/kid/ns#" py:attrs="namespace()"  lang="en" xml:lang="en">

<head py:match="item.tag=='{http://www.w3.org/1999/xhtml}head'">
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <script src="/static/javascript/jquery.min.js"></script>
    <script src="/static/javascript/loginpage.js"></script>
    <title>Welcome to ${cherrypy.request.base in title and title[cherrypy.request.base] or "The Hub"}</title>
    <style type="text/css">
        @import url("/static/css/main.css");
        @import url("/static/css/hub_home.css");
        @import url("/static/toronto/css/hub_home.css");
        @import url("/static/css/feeds.css");
    </style>
</head>
<body py:match="item.tag=='{http://www.w3.org/1999/xhtml}body'" py:attrs="item.items()">
   <div py:if="location==None" id="wrap">
          <div py:replace="loginBox()" py:if="identity.current.anonymous">
          </div>
   </div>
   <div py:if="location!=None" id="wrap">
        <a href="/" title="Home" ><div id="header" class="clearfix">
        </div></a>
            <div class="updatesBar eventsFeed">
                <!--
                <div py:replace="events_feed(updates, location)">
                </div>
                -->
            </div> 
            <div  class="updatesBar profilesFeed" id="extras">
                <div py:replace="loginBox()" py:if="identity.current.anonymous">
                </div>
                <!--
                <div py:replace="profiles_feed(updates, location)">
                </div>
                -->
            </div> 
        <div py:replace="item[:]" />
        <div py:replace="footer()">
        </div>
    </div>
    <c py:def="events_feed(updates, location)" py:strip="True">
	<div>
                <?python
                     local = updates['local_events']
                ?>
		<div class="announceCategoryHeader">
			<h1>Upcoming Events in ${location.name}</h1>
		</div>	
		<div class="update" py:for="update_item in local">
			<a  href="/events/${update_item.id}">
                            <div class="update_text">
                            <h1>${update_item.meeting_name}</h1>
                            <p>${datetimeconverter2.from_python(update_item.start)} - ${timeconverter.from_python(update_item.end_time)}</p>
                            <h2>${update_item.location_name} - ${update_item.resource_name}</h2>
                            </div>
                        </a>
		</div>
		<div class="feedLink">
			<a href="/feed/rss2_0/events/${location.id}"><h1>Feed</h1></a>
		</div>
		<hr class="clear"/>
	</div>
	<div>
                <?python
                     glob = [x for x in updates['global_events'] if x not in local]
                ?>
		<div class="announceCategoryHeader">
			<h1>Upcoming Events in The Hub Network</h1>
		</div>	
		<div class="update" py:for="update_item in glob">
                    <a href="/events/${update_item.id}">
                        <div class="update_text">
                            <h1>${update_item.meeting_name}</h1>
                            <p>${datetimeconverter2.from_python(update_item.start)} - ${timeconverter.from_python(update_item.end_time)}</p>
                            <h2>${update_item.location_name} - ${update_item.resource_name}</h2>
                        </div>
                    </a>
		</div> 
		<div class="feedLink">
			<a href="/feed/rss2_0/events/0"><h1>Feed</h1></a>
		</div>
		<hr class="clear"/>
	</div>
    </c>
 <c py:def="profiles_feed(updates, location)" py:strip="True">
	<div class="announce">
                <?python
                     local = updates['local_profiles']
                ?>
		<div class="announceCategoryHeader">
			<h1>Recently Updated Profiles in ${location.name}</h1>
		</div>	
		<div class="update" py:for="update_item in local">
			<a href="/profiles/${update_item.user_name}"><img height="40px" width="40px" src="${image_src(update_item, 'thumbnail', '/static/images/shadow.png')}" /><div class="update_text"><h1>${update_item.display_name}</h1><h2>${update_item.organisation}</h2></div></a>
		</div>
		<div class="feedLink">
			<a href="/feed/rss2_0/profiles/${location.id}"><h1>Feed</h1></a>
		</div>
		<hr class="clear"/>
	</div>
	<div class="announce">
                <?python
                     glob = [x for x in updates['global_profiles'] if x not in local]
                ?>
		<div class="announceCategoryHeader">
			<h1>Recently Updated Profiles in The Hub Network</h1>
		</div>	
		<div class="update" py:for="update_item in glob">
			<a href="/profiles/${update_item.user_name}"><img height="40px" width="40px" src="${image_src(update_item, 'thumbnail', '/static/images/shadow.png')}" /><div class="update_text"><h1>${update_item.display_name}</h1><h2>${update_item.organisation}</h2></div></a>
		</div>
		<div class="feedLink">
			<a href="/feed/rss2_0/profiles/0"><h1>Feed</h1></a>
		</div>
		<hr class="clear"/>
	</div>
      </c>

 <div id="loginBox" py:def="loginBox()">
        <p>${login_message}</p>
        <form action="${previous_url}" method="POST">
            <div class="label">
                   <label for="user_name">User Name:</label>
            </div>
            <div class="field">
                <input type="text" id="user_name" name="user_name"/>
            </div>
            <div class="label">
                <label for="password">Password:</label>
            </div>
            <div class="field">
                <input type="password" id="password" name="password"/>
            </div>
            <div class="buttons">
                <input type="submit" name="login" value="Login"/>
            </div>
 
            <input py:if="forward_url" type="hidden" name="forward_url"
                value="${forward_url}"/>
                
            <input py:for="name,value in original_parameters.items()"
                type="hidden" name="${name}" value="${value}"/>
        </form>
        <div><a href='/requestPassword'>Forgot your password?</a></div>
   
    </div>


    <div id="footer" py:def="footer()">
    </div>
</body>
</html>
