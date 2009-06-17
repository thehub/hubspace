<?python
from hubspace.utilities.uiutils import oddOrEven,c2s, select_home_hub
from hubspace.utilities.permissions import locations
from hubspace.templates.manageTariffs import resources 
from hubspace.controllers import get_place, permission_or_owner
from hubspace.model import Location
from turbogears import identity
odd_or_even = oddOrEven().odd_or_even


?>
<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">    
  	<h1>Resources and Tariffs</h1>
        Location: <select id="select_location" name="select_location"><option py:for="location in locations('manage_resources')" py:attrs="select_home_hub(location)" value="${location.id}">${location.name}</option></select>
        <select id="resources_or_tariffs" name="resources_or_tariffs">
             <option value="Tariffs">Manage Tariffs</option>
             <option value="Resources">Manage Resources</option>
        </select>
        <div id="resource_location">
          ${resources(object.homeplace)}
        </div>
</div>
