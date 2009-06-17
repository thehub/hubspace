<?python
import turbogears
from turbogears import identity
from hubspace.controllers import permission_or_owner, filter_members
from hubspace.feeds import get_updates_data
from hubspace.templates.mainProfile import load_profile
from hubspace.model import User
def namespace():
    return {'xmlns':"http://www.w3.org/1999/xhtml"}
subsection="mainProfile"
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns:py="http://purl.org/kid/ns#" py:extends="'location.kid'" py:attrs="namespace()" py:strip="'ajax' in locals()">
  <head py:if="'ajax' not in locals()">
  </head>
  <body py:strip="'ajax' in locals()">
      <div py:def="network_skeleton(object=None, subsection='mainProfile')" id="networkContent" class="pane"  py:strip="True">
	<div class="subBar">
		<ul>
			<li py:if='permission_or_owner(None, None, "manage_users")'><a style="cursor:pointer;" id="network-0" class="subsection">Add new member</a></li>
			<li class="selected"><a style="cursor:pointer;" id="network-1" class="subsection">Profile</a></li>
			<li py:if='permission_or_owner(None, None,"manage_users")'><a style="cursor:pointer;" id="network-2" class="subsection">Billing</a></li>
			<li><a style="cursor:pointer;" id="network-3" class="subsection">Search results</a></li>
		</ul>
	</div>
	<div class="paneContent">
              <div id="network-addMemberContent" class="subsectionContent">
              </div>
              <div id="network-mainProfileContent" class="subsectionContent">
                <c py:strip="True" py:if="object and object.id!=identity.current.user.id" >                          <c py:if="subsection=='mainProfile'" py:replace="load_profile(object)" />
                </c> 
                <c py:strip="True" py:if="object and object.id==identity.current.user.id">
                   <?python
                       from hubspace.templates.loginMaster import events_feed, profiles_feed
                       updates = get_updates_data(object.homeplace)
                   ?>
                   <div class="updatesBar eventsFeed" id="event_feed" py:content="events_feed(updates, object.homeplace)" >
                   </div>
                   <div class="updatesBar profilesFeed" id="profile_feed" py:content="profiles_feed(updates, object.homeplace)" >
                   </div>
                </c>
              </div>
	      <div id="network-billingContent" class="subsectionContent">
                   <?python 
                       from hubspace.templates.billing import load_billing
                   ?>
                   <c py:if="subsection=='billing'" py:replace="load_billing(object)" />
              </div>
	      <div id="network-fulltextsearchContent" class="subsectionContent">
              </div>
	</div>
</div>
${network_skeleton(object, subsection=subsection)}
</body>
</html>
