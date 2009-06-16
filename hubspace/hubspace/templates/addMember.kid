<?python
from hubspace.templates.memberProfileEdit import load_memberProfileEdit
from hubspace.templates.memberDescriptionEdit import load_memberDescriptionEdit
from hubspace.templates.memberCommunitiesEdit import load_memberCommunitiesEdit
from hubspace.templates.memberServicesEdit import load_memberServicesEdit

from hubspace.controllers import get_attribute_names
from hubspace.model import User #, initial_cops
from hubspace.utilities.dicts import AttrDict
#defaults
attrs = dict((key, '') for key in get_attribute_names(User))
attrs['active'] = True
attrs['public_field'] = False
#attrs['cops'] = initial_cops
if 'new_user' not in locals():
    new_user = AttrDict(attrs)
if 'tg_errors' not in locals():
    tg_errors = None
?>

<div id="networkContent" class="pane" xmlns:py="http://purl.org/kid/ns#" py:strip="True">
  <form py:def="add_member(new_user, tg_errors)" id="add_member">		
        ${load_memberProfileEdit(new_user, tg_errors)}	
        ${load_memberDescriptionEdit(new_user, tg_errors)}
       <!-- ${load_memberCommunitiesEdit(new_user)}-->
        ${load_memberServicesEdit(new_user, tg_errors)}
  <input type="button" value="${_('Add Member')}" id="submit_add_member" />
  </form>
   ${add_member(new_user, tg_errors)}
</div>
  

  
   
  


 
