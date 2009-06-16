<?python
from hubspace.utilities.permissions import locations, is_host
from hubspace.utilities.uiutils import select_home_hub
from hubspace.controllers import get_place, permission_or_owner
from hubspace.templates.locationAdmin import loc_admin
?>

<div id="adminContent" class="pane" xmlns:py="http://purl.org/kid/ns#" py:strip="True">    
  	 <h1>Administration</h1>
         Location: <select id="select_admin_location" name="select_admin_location"><option py:for="location in locations('manage_resources')" py:attrs="select_home_hub(location)" value="${location.id}">${location.name}</option></select>
        <div id="resource_location" py:if="permission_or_owner(None, None, 'manage_resources')">
          ${loc_admin(is_host(object, object.homeplace) and object.homeplace or locations('manage_resources')[0])}
        </div>	
</div>
