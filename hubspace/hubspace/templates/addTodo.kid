
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
     return _("Set A Due Date")
  return dateconverter.from_python(due_date)
?>
<div xmlns:py="http://purl.org/kid/ns#"  py:strip="True">
  <div py:def="edit(object, todo, tg_errors)">
    <form id="create_todo_${object.id}">
       <input name="action" type="hidden" value="edit"/>
       <input name="parent" type="hidden" value="${object.id}"/>
       
    <table cellpadding="0" cellspacing="0" class="detailTable">
		<tr class="even">
			<td class="line">Subject:</td>
			<td><input type="text" class="text" name="subject" id="subject" value="${todo.subject}" /><div class="errorMessage" py:if="tg_errors">${print_error('subject', tg_errors)}</div></td>
		</tr>
		<tr class="odd">
			<td class="line">Due Date:</td>
			<td><input id="due" name="due" type="hidden" value="${dateconverter.from_python(todo.due)}"/><span id="show_date" style="cursor:pointer;">${due(todo.due)} <img src="/static/images/booking_down.png" /></span>
                            <div class="errorMessage" py:if="tg_errors">${print_error('date', tg_errors)}</div></td>
		</tr>
		<tr class="even">
			<td class="line">Body:</td>
			<td><textarea name="body" id="body">${todo.body}</textarea><div class="errorMessage" py:if="tg_errors">${print_error('body', tg_errors)}</div></td>
		</tr>
    </table>
		</form>
		<div class="buttons">
			<input type="image" src="/static/images/button_save.gif" class="submit" value="${_('submit')}" id="submit_todo_${object.id}" />
			<input type="image" src="/static/images/button_cancel.gif" class="cancel" value="${_('cancel')}" id="cancel_todo_${object.id}" />
		</div>
  </div>
  ${edit(object, todo=todo, tg_errors=tg_errors)}
  <br class="clear" />
</div>
