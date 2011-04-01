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
  <form py:def="add_member(new_user, tg_errors)" id="add_member" name="add_member_form">
        ${load_memberProfileEdit(new_user, tg_errors)}	
        ${load_memberDescriptionEdit(new_user, tg_errors)}
       <!-- ${load_memberCommunitiesEdit(new_user)}-->
        ${load_memberServicesEdit(new_user, tg_errors)}
    <input type="button" value="${_('Add Member')}" id="submit_add_member"/>
  <!-- <input type="button" value="${_('Add Member')}" id="submit_add_member"  name="submit_button" onclick="document.add_member_form.submit_button.value='One Moment Please...'; document.add_member_form.submit_button.disabled=true; document.add_member_form.submit();" />
      Just a note: This could have been done by just adding onclick/onsubmit instead of defining names for form/button. But IE/FF works differently when it comes to disabling submit button and submitting teh form at the same time. If you disable submit button on onclick/onsubmit event, FF accepts the first click, submits the form and disables the button. But IE does not let the first click to occur, and disables the button as well as the click. So, had to process this current way. -->
  </form>
   ${add_member(new_user, tg_errors)}
</div>
  

  
   
  


 
