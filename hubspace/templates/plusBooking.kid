<?python
from datetime import datetime, timedelta
from hubspace.validators import dateconverter
date_to_text = dateconverter.from_python
from hubspace.model import Location, Resourcegroup, Resource
from hubspace.templates.dayBooking import load_dayBooking
from hubspace.templates.weekBooking import load_weekBooking
from hubspace.utilities.booking import default_booking_params
from hubspace.utilities.permissions import permission_or_owner
from hubspace.utilities.uiutils import now
from docutils.core import publish_parts
from turbogears import identity

def selected_hub(location, loc):   
    if location and location.id==loc:
        return {'selected':'selected'}
    elif not location and identity.current.user.homeplace==loc:
        return {'selected':'selected'}
    return {}

def selected_view(view, value):
    if view==value:
        return {'checked':'checked'}
    return {}

def selected_group(group, current_group): 
    if group.id == current_group.id:
        return {'selected':'selected'}
    return {}

def selected_room(room, room_selected):
    if int(room)==int(room_selected):
        return ' label_selected'
    return ''

def display_room(room, rooms_displayed):
    if int(room) in rooms_displayed:
        return {'checked':'checked'}
    return {}
?>				
<div py:strip="True" xmlns:py="http://purl.org/kid/ns#" py:layout="'plusMaster.kid'">
   <div py:def="load_content(location=None)">
    <?python
        loc = 'location' in locals() and location or object.homeplace
        date='date' in locals() and date or now(loc)
        view='view' in locals() and view or 0
        location=loc
        room_selected='room_selected' in locals() and room_selected or None
        rooms_displayed='rooms_displayed' in locals() and rooms_displayed or []
        resgroup='res_group' in locals() and res_group or None
	only_my_bookings='only_my_bookings' in locals() and only_my_bookings or 0
        resgroup_order = location.resourcegroup_order
        if not resgroup_order:
            resgroup_order = []
        if not resgroup:
            rooms_displayed, room_selected, resgroup = default_booking_params(location, resgroup)
        if not resgroup:
            location = Location.select()[0]
            resgroup_order = location.resourcegroup_order
            rooms_displayed, room_selected, resgroup = default_booking_params(location, resgroup)
       ?>
      <form id="space_loc_time">
       <div class="bookingHub">Select Hub <select class="space_switch" name="location">
                                                <option py:for="loc in Location.select().orderBy('name')" py:if="len(loc.resourcegroups)" id="${loc.id}" value="${loc.id}" py:attrs="selected_hub(location, loc.id)">${loc.name}</option>
                                          </select>
       </div>
       <div class="dataBox">
           <div class="dataBoxHeaderCollapse" id="booking_help">
	       <a class="title" id="help_Booking_Help">
	           <h2>Need Help with Booking?</h2>
	       </a>
           </div>
           <div style="display: none;" class="dataBoxContent">
              <div class="dataTextBox data">To make a booking, or modify an existing one:
               <ol>
                   <li>Select the date you are looking for.</li>
                   <li>Click on the space and the time you would like.</li>
                   <li>Provide us with the booking details required.</li>
               </ol>
               <p>In the event of a cancellation, the individual or organization booking the space will be charged 50% of the total cost, unless it is cancelled more than two weeks prior to the event.</p>
               <p> A confirmation will be emailed to you as soon as the booking is made. For further information or to cancel a booking (starting in the next two weeks) please email <a href="mailto:${location.hosts_email}"> ${location.hosts_email}</a>.</p>
           </div>
         </div>
       </div>
   <c py:if="resgroup" py:strip="True">
       <div class="type_selector">
            What do you to want book? <select class="space_switch" name="res_group">
                                          <c py:for="group in resgroup_order" py:strip="True">
<?python
if group:
    group = Resourcegroup.get(group)
    if group.group_type=='host_calendar' and permission_or_owner(group.location, None, 'manage_resources'):
        pass
    elif group.group_type=='member_calendar':
        pass
    else:
        group = None
?>
                                               <option py:if="group" py:attrs="selected_group(group, resgroup)" value="${group.id}">${group.name}</option>
                                          </c>
                                      </select>
       </div>
       <div id="resource_group_description">${XML(publish_parts(resgroup.description, writer_name="html")["html_body"])}</div>
       <div py:attrs="{'style':view==1 and 'display:block' or 'display:none'}" id="room_selector_group">
             <input id="room_selected" name="room_selected" type="hidden" value="${room_selected}" />
             <div py:for="res in resgroup.resources_order" class="room_selector room${resgroup.resources_order.index(res)+1}" id="room_selector-${Resource.get(res).id}">
                  <a class="label${selected_room(res, room_selected)}" id="resource_label-${res}">${Resource.get(res).name}</a>
                  <span class="close"><input name="rooms_displayed" type="checkbox" value="${res}" py:attrs="display_room(res, rooms_displayed)" /></span>
             </div>
       </div>
     </c>
       <div id="calendarView">
           <input class="view_switch" id="day_view_switch" type="radio" name="view"  value="0" py:attrs="selected_view(view, 0)">Day View</input><br />
           <input class="view_switch" id="week_view_switch" type="radio" name="view"  value="1" py:attrs="selected_view(view, 1)">Week View</input>
       </div>
       <div id="onlyMyBookings">
           <input id="only_my_bookings" type="checkbox" name="only_my_bookings"  value="1" py:attrs="only_my_bookings and {'checked':'checked'} or {}">Only show my bookings</input><br />
       </div>
       <div id="bookingDate" class="bookingDate" py:if="view==0">
           <div class="date_area">
                <a id="leftArrow" class="${date_to_text(date-timedelta(days=1))}"><img src="/static/images/booking_left.png" alt="&lt;" /></a>
                <input name="date" value="${date_to_text(date)}" class="invisible_input" id="space_date_field" type="text"  />
                <h2 id="space_date">${date_to_text(date)}<img src="/static/images/booking_down.png" /></h2>
                <a id="rightArrow" class="${date_to_text(date+timedelta(days=1))}"><img src="/static/images/booking_right.png" alt="&gt;" /></a>
           </div>
       </div>
       <div id="bookingDateRange" class="bookingDate" py:if="view==1">
            <div class="date_range_area">
                <a id="leftArrow" class="${date_to_text(date-timedelta(days=date.weekday()+7))}"><img src="/static/images/booking_left.png" alt="&lt;" /></a>
                <input name="date" value="${date_to_text(date-timedelta(date.weekday()))+' - '+date_to_text(date+timedelta(6-date.weekday()))}" id="space_date_field" type="hidden" />
                <h2 id="space_date">${date_to_text(date-timedelta(days=date.weekday()))} - ${date_to_text(date+timedelta(days=6-date.weekday()))}<img src="/static/images/booking_down.png" /></h2>
                <a id="rightArrow" class="${date_to_text(date-timedelta(days=date.weekday()-7))}"><img src="/static/images/booking_right.png" alt="&gt;" /></a>
            </div>
       </div>
      </form>
   <c py:if="resgroup" py:strip="True">
      <div py:if="view==0" py:strip="True"> 
          ${load_dayBooking(location, resgroup, date, only_my_bookings)}
      </div>
      <div py:if="view==1" py:strip="True"> 
          ${load_weekBooking(location, resgroup, date, room_selected, rooms_displayed, only_my_bookings)}
      </div>
   </c>
    </div>
</div>
