<?python
from hubspace.utilities.uiutils import print_error
from hubspace.validators import dateconverter
from datetime import datetime
def due(todo):
  if todo.due:
     return dateconverter.from_python(todo.due)
  return "Set Due Date"

def closed(todo):
  if todo.closed:
     return {'checked':'checked'}
  return {}

if 'tg_errors' not in locals():
    tg_errors = None
?>
<div xmlns:py="http://purl.org/kid/ns#"  py:strip="True">
  <div py:def="edit(todo, tg_errors)">
  
  <table cellpadding="0" cellspacing="0" class="detailTable">
		<tr class="even">
			<td class="line">Subject:</td>
			<td>
				<input type="text" class="text" name="subject" id="subject" value="${todo.subject}" />
				<div class="errorMessage" py:if="tg_errors">${print_error('subject', tg_errors)}</div>
			</td>
		</tr>
		<tr class="odd">
			<td class="line"> Due Date: </td>
			<td>
				<input id="action" name="action" type="hidden" value="${action}"/>
       <input id="due_${todo.id}" name="due" type="hidden" value="${dateconverter.from_python(todo.due)}"/>
      <span id="show_date_${todo.id}" style="cursor:pointer;">${due(todo)}  <img src="/static/images/booking_down.png" /> </span> 
    <div class="errorMessage" py:if="tg_errors">${print_error('date', tg_errors)}</div>
			</td>
		</tr>
		<tr class="even">
			<td class="line">Body:</td>
			<td>
				<textarea name="body" id="body">${todo.body}</textarea>
				<div class="errorMessage" py:if="tg_errors">${print_error('body', tg_errors)}</div>
			</td>
		</tr>
		<tr class="odd">
			<td class="line">Close:</td>
			<td>
				<input type="checkbox" value="1" py:attrs="closed(todo)" name="closed" />
			</td>
		</tr>
	</table>
    
  </div>
  ${edit(object, tg_errors=tg_errors)}
</div>
