<?python
from hubspace.model import Todo,Invoice, User, Location, Group
from datetime import datetime,timedelta
from docutils.core import publish_parts
from sqlobject import AND
from hubspace.utilities.uiutils import oddOrEven,c2s
from hubspace.controllers import groups_in_place, reminders, urgent, events, invoices_to_create, invoices_unsent, todos, permission_or_owner
from hubspace.validators import datetimeconverter, dateconverter
datetimecon = datetimeconverter.from_python
date = dateconverter.from_python
from hubspace.utilities.uiutils import oddOrEven,c2s, now
import turbogears
odd_or_even = oddOrEven().odd_or_even

def today(user):
    right_now = now(user.homeplace)
    return datetime(right_now.year, right_now.month, right_now.day)

def hosts_available():
    """all hosts for whom the current user has the manage_users permission for their homeplace
    """
    users = []
    for location in Location.select():
        if permission_or_owner(location,None,"manage_users"):
            groups = list(Group.selectBy(place=location, level="host"))
            if groups:
                for user in groups[0].users:
                     if user not in users:
                         users.append(user)
    return users

def current_host(host, object):
    if host.id == object.id:
        return {'selected':'selected'}
    return {} 

def bar_style(id, cssclass):
    style = {}
    if id:
      style['id'] = id
    if cssclass:
      style['class'] = cssclass
    return style

def barId(bar):
    if str(bar.action) in ['edit', '']:
       return "todobar-"+str(bar.id)
    else:
       return bar.action +"-"+ str(bar.id)
?>
<div id="todosContent" class="pane" xmlns:py="http://purl.org/kid/ns#" py:strip="True">

    <div py:def="render_todo(todo)" id="${todo.id}Todo${todo.action}" class="${todo.id}">
            <span class="enteredBy">created by ${todo.createdby} on ${datetimecon(todo.opened)}</span>
            <a class="${todo.action}" id="${todo.action}-${todo.action_id}" style="cursor:pointer;">${todo.subject}</a> 
            <span py:if="'extra_action' in todo" > /
               <a class="${todo.extra_action}" id="${todo.extra_action}-${todo.action_id}" style="cursor:pointer;">Ignore</a>
            </span>
            <div py:if="todo.due!=None">Completion Due: ${date(todo.due)}</div>
            <div py:if='todo.body' class="description" id="description_${todo.action}_${todo.action_id}"><p>${XML(publish_parts(todo.body, writer_name="html")["html_body"])}</p></div>
            <div py:if='todo.closed' class="closed"><strong>This todo is closed!</strong></div>
    </div>

     <div py:def='todobox(current_user, todos, barsubject, barbody=None, bar_id="", cssclass=None, bar_type="user", show_closed=False, bar_action="")' py:attrs="bar_style(bar_id, cssclass)">
	<div class="dataBoxHeader">
           <span py:strip="True" py:if="permission_or_owner(current_user.homeplace, None,'manage_todos') and 'edit' in bar_action">
                <a class="addTodo modify show">Add Todo</a> 
                <a class="showClosed show">Show Closed</a>
                <a class="deleteBar show">Delete List</a>
           </span>
           <a class="title" id="link_todobar_${bar_id}"><h2>$barsubject</h2></a>
        </div>

	    <div class="dataBoxContent" id="todo_content_${bar_id}">
		<ul py:def='todo_content(todos, show_closed=False)' >
		   <li py:for='todo in todos' py:if="todo.closed==None or show_closed" class="${odd_or_even()}">
                     ${render_todo(todo)}
                     <span py:if="todo.action in ['edit', 'edit_urgent', 'followup', 'followup_urgent']" id="${todo.id}Todo${todo.action}Edit" style="cursor:pointer;">edit</span>
                   </li>
                 </ul>
                 ${todo_content(todos, show_closed=False)}
	    </div>
     </div>		


     <c py:def="load_todos(object)" py:strip="True"> 
        <div class="chooseHost">Select host: <select id="choose_host"><option py:for="host in hosts_available()" py:attrs="current_host(host, object)" value="${host.id}">${host.display_name}</option></select></div>  
        <h1>${object.display_name}'s List</h1> 
            <span id="host_id" class="${object.id}" style="display:none;" />           
             ${todobox(object, urgent(object), 'Urgent', cssclass="dataBox urgent", bar_type="system", bar_id="urgent", bar_action="urgent")}
             ${todobox(object, events(object, today(object)), "Today's bookings", cssclass="dataBox today", bar_type="system", bar_id="today", bar_action="booking")}
             ${todobox(object, events(object, (today(object)+timedelta(days=1))), "Tomorrow's bookings", cssclass="dataBox tomorrow", bar_type="system", bar_id="tomorrow", bar_action="booking")}
             ${todobox(object, invoices_unsent(object), 'Invoices to be sent', cssclass="dataBox invoices", bar_type="system", bar_id="invoices_unsent",  bar_action="send_invoices")}
             ${todobox(object, reminders(object),'Payment reminders',cssclass="dataBox invoices", bar_type="system", bar_id="payment_reminders", bar_action="remind_debtors")}
            <c py:strip='True' py:if="bar.closed==None" py:for='bar in Todo.selectBy(parent=None, foruser=object.id)'>
                 ${todobox(object, todos(bar, object), bar.subject, bar.body, bar_id=barId(bar), bar_type="user", bar_action=bar.action)}
            </c>          
     		<div id="add_list"></div>
	    	<a py:if='permission_or_owner(turbogears.identity.current.user.homeplace,None,"manage_todos")' style="cursor:pointer;"  id="addTodoBar">Add new Todo list</a>
     </c>
   <c py:if="'show_closed' not in locals()">
     ${load_todos(object)}
   </c>
   <c py:if="'show_closed' in locals()">
        ${todo_content(todos(bar, object), show_closed=show_closed)}
   </c>
</div>
