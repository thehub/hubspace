<?python
from turbogears import identity
from datetime import datetime, date as today
from hubspace.model import Note, User
from hubspace.validators import datetimeconverter as d
from hubspace.validators import dateconverter as date
if 'tg_errors' not in locals():
   tg_errors = None
from hubspace.controllers import permission_or_owner, get_attribute_names
from hubspace.utilities.dicts import AttrDict
from hubspace.utilities.uiutils import selected_user, all_hosts, print_error, now
from docutils.core import publish_parts
attrs = dict((key, '') for key in get_attribute_names(Note))

def ascending_dates(note1, note2):
    if note1.date <= note2.date:
        return 1
    else:
        return -1

def order_notes(user):
    x = list(user.notes_on)
    x.sort(ascending_dates)
    return x

if 'new_note' not in locals():
    new_note = AttrDict(attrs)

def past(note):
    if datetime.date(note.action.due)>=today.today():
        return False
    return True
?>

<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">

  
   <div py:def="show_note(note)" py:strip="True">
	<div class="noteHeader">
             <div>${note.title} - <span class="addedBy">added by ${note.byuser.display_name} on ${d.from_python(note.date)[:-3]}</span></div>
             <div py:if="not note.action" class="note_form">
                   <div class="note_action">
                   <a id="${note.id}NoteAddAction" title="Add Follow-Up Action" href="#"><img src="/static/images/bell_add.png" /></a></div>
                
                   <div id="${note.id}noteActionDisplay" style="display:none">
                       <form id="${note.id}notecreateAction">
                           <table>
                               <tr>
                                   <td><label>Details</label></td>
                                   <td><textarea name="body"></textarea></td>
                               </tr>
                               <tr>
                                   <td><label>Date to Follow Up</label></td>
                                   <td><input name="due" id="due_${note.id}" type="hidden" value="${date.from_python(now(note.byuser.homeplace))}"/>
                    <span id="show_due_${note.id}" style="cursor:pointer;">${date.from_python(now(note.byuser.homeplace))} <img src="/static/images/booking_down.png"/></span> 
		    <div class="errorMessage" py:if="tg_errors">${print_error('due', tg_errors)}</div></td>

                               </tr>
                               <tr>
                                   <td><label>For User</label></td>
                                   <td>
                                       <select name="foruser">
                                          <option py:for="opt in all_hosts()" value="${opt.id}" py:attrs="selected_user(opt, identity.current.user)">${opt.display_name}</option>
                                       </select>
                                   </td>
                               </tr>
                               <tr>
                                   <td></td>
                                   <td><input type="submit" value="Create Follow-Up Action" id="${note.id}noteSubmitAction" /></td>
                               </tr>
                           </table>
                       </form>
                   </div>
             </div>
             <div py:if="note.action" class="note_action_area">
                 <div class="note_action">
                      <a id="${note.id}NoteAction" href="#">
                         <img py:if="not past(note) and not note.action.closed" src="/static/images/bell.png" />
                         <img py:if="past(note) and not note.action.closed" src="/static/images/bell_error.png" />
                         <img py:if="note.action.closed" src="/static/images/accept.png" />
                      </a>
                </div>
                <div class="show_note_action" id="${note.id}noteActionDisplay" style="display:none;">
		         <table>
                               <tr>
                                   <td class="label">Follow-up Date</td>
                                   <td>${date.from_python(note.action.due)}</td>
                               </tr>
                               <tr>
                                   <td class="label">Details</td>
                                   <td>${note.action.body}</td>
                               </tr>
                               <tr>
                                   <td class="label">Action Assigned To</td>
                                   <td>${note.action.foruser.display_name}</td>
                               </tr>
                               <tr py:if="note.action.closed">
                                   <td class="label">Action Closed</td>
                                   <td>Closed</td>
                               </tr>
                         </table>                    

                 </div>
             </div>
        </div>
	<div class="noteBody">
		<p>${XML(publish_parts(note.body, writer_name="html")["html_body"])}</p>
	</div>


    </div>


   <div py:def="add_note(user, new_note, tg_errors)" class="dataNote data">
     <form id="create_note">
      <div class="noteHeader">Name of note: <input type="text" name="title" id="title" value="${new_note.title}" /><div class="errorMessage" py:if="tg_errors">${print_error('title', tg_errors)}</div></div>
      <div class="noteBody">
        <textarea name="body" id="body">${new_note.body}</textarea>
        <div class="errorMessage" py:if="tg_errors">${print_error('body', tg_errors)}</div>

        <input type="hidden" name='onuser' id='onuser' value="${user.id}"/>
       
      </div>
     </form>
     <div class="buttons">
			<input type="image" value="submit" src="/static/images/button_save.gif" id="submit_create_note" />
			<input type="image" value="cancel" src="/static/images/button_cancel.gif" id="cancel_create_note" />
     </div>
        <div class="clear" ></div>
   </div>
   <div py:def="show_notes(user)" id="user_notes-${user.id}">
     <div py:for="note in order_notes(user)" class="dataNote data" id="note_${note.id}">
       <span py:if='permission_or_owner(note.onuser.homeplace, None, "manage_users")' class="click_span" id="${note.id}NoteEdit">edit</span>
        <span class="click_span" py:if='permission_or_owner(note.onuser.homeplace, None, "manage_users")' id="${note.id}NoteDelete">delete</span>
       <div id="${note.id}Note" class="note">
           ${show_note(note)}
       </div>
     </div>
   </div>


    <c py:if="'user' in locals()" py:strip="True">
            ${show_notes(user)} 
    </c>
    <c py:if="'note' in locals()" py:strip="True">
            ${show_note(note)} 
    </c>
    <c py:if="'note' not in locals() and 'user' not in locals()" py:strip="True">
         ${add_note(object, new_note, tg_errors)}
    </c>
</div>
