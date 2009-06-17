
<?python
from hubspace.utilities.uiutils import print_error
from hubspace.utilities.dicts import AttrDict
from hubspace.validators import dateconverter
from datetime import datetime
from hubspace.model import Todo
from hubspace.controllers import get_attribute_names
attrs = dict((key, '') for key in get_attribute_names(Todo))
todo = AttrDict(attrs)
tg_errors = None

def due(due_date):
  if not due_date:
     return _("To Set A Due Date Click Here")
  return dateconverter.from_python(due_date)
?>
<DIV CLASS="dataBox">
<DIV CLASS="dataBoxHeader"><A CLASS="title" id="link_addTodobar"><H2>Add a new list</H2></A></DIV>
<DIV CLASS="dataBoxContent">
<div xmlns:py="http://purl.org/kid/ns#"  py:strip="True">
  <div py:def="add_bar(object, todo, tg_errors)">
    <form id="create_todo_bar">
     <table cellpadding="0" cellspacing="0" class="detailTable">
		<tr class="even">
			<td class="line">Name of list:</td>
			<td><input type="text" name="subject" id="subject" value="${todo.subject}" />
			<div class="errorMessage" py:if="tg_errors">${print_error('subject', tg_errors)}</div></td>
		</tr>
	</table>
       <input name="foruser" type="hidden" value="${object.id}" />
   </form>
	<input type="image" src="/static/images/button_save.gif" class="submit" value="${_('save')}" id="submit_todo_bar" />
	<input type="image" src="/static/images/button_cancel.gif" class="cancel" value="${_('cancel')}" id="cancel_todo_bar" />
  </div>
  ${add_bar(object, todo=todo, tg_errors=tg_errors)}
</div>
</DIV>
</DIV>
