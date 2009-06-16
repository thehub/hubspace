<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python
from hubspace.templates.mainProfile import load_profile
from hubspace.templates.network import network_skeleton
from turbogears import identity
if isinstance(object, type):
    object = identity.current.user


def namespace():
    return {'xmlns':"http://www.w3.org/1999/xhtml"}
?>

<html xmlns:py="http://purl.org/kid/ns#" py:extends="'location.kid'" py:strip="'ajax' in locals()" py:attrs="namespace()" >
  <head py:if="'ajax' not in locals()">
  </head>
  <body py:strip="'ajax' in locals()">
      <div id="profileContent" class="pane" py:strip="True">
        <div py:def="new_profile(object)" py:strip="True">		
          <div class="subBar" py:if="'area' not in locals() or area != 'network'">
	      <ul>
        	  <li class="selected"><a style="cursor:pointer;" id="profile-0" class="subsection">Profile</a></li>
		  <li><a style="cursor:pointer;" id="profile-1" class="subsection">Billing</a></li>
              </ul>		
          </div>
          <div class="paneContent">
	      <div id="profile-mainProfileContent" class="subsectionContent">
                  ${load_profile(object)} 
              </div>
	      <div id="profile-billingContent" class="subsectionContent">
              </div>
          </div> 
        </div> 
        ${new_profile(object)}
      </div>
  </body>
</html>
