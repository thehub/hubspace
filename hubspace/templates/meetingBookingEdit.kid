<?python
from hubspace.validators import dateconverter, datetimeconverter
from hubspace.utilities.uiutils import oddOrEven, print_error, c2s
from hubspace.utilities.dicts import AttrDict
from hubspace.controllers import get_pricing
from hubspace.tariff import get_tariff
from hubspace.utilities.permissions import permission_or_owner
from hubspace.openTimes import opening_times
from hubspace.model import User, Resource
from turbogears import identity
from docutils.core import publish_parts
from hubspace.utilities.image_helpers import image_src
from hubspace.bookinglib import t_booking_life_hrs
odd_or_even = oddOrEven().odd_or_even
from cgi import escape

def hours(location, date):
    times = opening_times(location.calendar, date)
    start, end = times[0][0], times[-1][1]
    return range(start.hour, end.hour)

def add_zero(hour):
    if len(str(hour))==1:
        return "0"+str(hour)
    return str(hour)
def display_hour(hour):
    return add_zero(hour) 

def start_hour(hour, rusage):
    if hour == rusage.start.hour:
        return {'selected':'selected'}
    return {}
def end_hour(hour, rusage):
    if hour == rusage.end_time.hour:
        return {'selected':'selected'}
    return {}
def start_minute(minute, rusage):
    if minute == rusage.start.minute:
        return {'selected':'selected'}
    return {}
def end_minute(minute, rusage):
    if minute == rusage.end_time.minute:
        return {'selected':'selected'}
    return {}
def setuptime(minutes, rusage):
    if 'setup_time' in rusage:
        if minutes == int(rusage.setup_time):
           return {'selected':'selected'}
    return {}

tg_errors = None
resource = None
create = False

def option_selected(rusage, option):
   if hasattr(rusage, 'options') and option.id in [int(option) for option in rusage.options]:
       return {'checked':'checked'}
   elif hasattr(rusage, 'suggested_usages') and option in [rusage.resource for rusage in rusage.suggested_usages if not rusage.cancelled]:     
       return {'checked':'checked'}
   return {}

def get_resource(rusage, resource):
   if not resource:
       return rusage.resource 
   return resource

def booking_user(rusage):
   try:
       return rusage.user
   except:
       return identity.current.user

def selected_object(selected, current):
   if selected.id==current.id:
       return {'selected':'selected'}
   else:
       return {}
?>
<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">

    <div py:def="load_meetingBookingEdit(rusage=None, resource=None, create=None, tg_errors=None)" py:strip="True">
      <table class="booking_popupTable" id="meetingBooking" cellpadding="" cellspacing="0">
        <tr>
            <td class="left">Select Resource</td>
            <td class="right">
                <select id="resource_id" name="resource_id">
                    <option py:for="res in resource.resgroup.resources_order" value="${res}" py:attrs="selected_object(Resource.get(res), resource)">${Resource.get(res).name}</option>
                </select>
            </td>
	</tr>
        <tr>
            <td class="left">&nbsp;</td>
            <td class="right"><img py:if="image_src(resource, 'resimage', '')" src="${image_src(resource, 'resimage', '/static/images/blank.jpg')}" />${XML(publish_parts(resource.description, writer_name="html")["html_body"])}</td>
        </tr>
        <tr py:if="resource.type=='room'">
            <td class="left">Meeting Name</td>
            <td class="right">
                <div class="rightFloat" id="publicise_event">
<label for="public_field">Publicise event to The Hub's website</label>               
                    <input id="privatePublic" name="public_field" value="1" type="checkbox" py:attrs="rusage.public_field and {'checked':'checked'} or {}" />
                </div>
                <input id="meeting_name" name="meeting_name" type="text" class="text" value="${rusage.meeting_name}"/>
                <div class="errorMessage" py:if="tg_errors">${print_error('meeting_name', tg_errors)}</div></td>
	</tr>
        <tr py:if="resource.type=='room'">
            <td class="left">Meeting Description</td>
            <td class="right"><textarea id="meeting_description" name="meeting_description">${rusage.meeting_description}</textarea></td>
            <div class="errorMessage" py:if="tg_errors">${print_error('meeting_description', tg_errors)}</div>
            <td colspan="2" class="td_space">&nbsp;</td>
	</tr>
        <tr>
            <td class="left">Date</td>
            <td class="right"><span id="date_display">${dateconverter.from_python(rusage.start)}</span><input type="text" id="date_field" name="date" value="${dateconverter.from_python(rusage.start)}" style="visibility:hidden;" />
            <div class="errorMessage" py:if="tg_errors">${print_error('date', tg_errors)}</div></td>
        </tr>
	<tr>
            <td class="left">Time</td>
            <td class="right">		
                    <select id="start_hour" class="start_time" name="start.hour">
		          <option py:for="hour in hours(resource.place, rusage.start)" py:attrs="start_hour(hour, rusage)">${display_hour(hour)}</option>
		    </select>:
                    <select id="start_minute" class="start_time" name="start.minute" >
		        <option py:attrs="start_minute(0, rusage)">00</option>
		        <option py:attrs="start_minute(15, rusage)">15</option>
                        <option py:attrs="start_minute(30, rusage)">30</option>
		        <option py:attrs="start_minute(45, rusage)">45</option>
		    </select>
                      &nbsp;&nbsp;to&nbsp;&nbsp;
                   <select id="end_hour" name="end.hour" class="end_time">
                       <option py:for="hour in hours(resource.place, rusage.start)" py:attrs="end_hour(hour, rusage)">${display_hour(hour)}</option>
                   </select>:
                   <select id="end_minute" name="end.minute" class="end_time">
                        <option py:attrs="end_minute(0, rusage)">00</option>
                        <option py:attrs="end_minute(15, rusage)">15</option>
                        <option py:attrs="end_minute(30, rusage)">30</option>
                        <option py:attrs="end_minute(45, rusage)">45</option>
                    </select>
                    <div><span class="errorMessage" py:if="tg_errors">${print_error('start', tg_errors)}</span>&nbsp;&nbsp;<span class="errorMessage" py:if="tg_errors">${print_error('end', tg_errors)}</span></div>
              </td>
        </tr>
        <!--
        <tr>
            <td class="left">Add invitee(s)</td>
	    <td class="right"> 
                <table cellpadding="0" cellspacing="0" id="list_invitees">
                <tr>
                <td>
                    <input type="text" id="add_invitee" value="" />
                    <input type="hidden" id="add_invitee_id" name="id_or_email" />
                </td>
                <td>
                    <input type="submit" value="Invite" />
                </td>
                </tr>
                </table>
            </td>
	</tr>
        -->


	<tr py:if="resource.type=='room'">
		<td class="left">Number of People</td>
		<td class="right"><input id="number_of_people" name="number_of_people" type="text" size="3" value="${str(rusage.number_of_people)}" />
                <div class="errorMessage" py:if="tg_errors">${print_error('number_of_people', tg_errors)}</div>
                </td>
	</tr>
	<tr>
		<td class="left">Extras</td>
                <td class="right"><ul>
                    <li py:for="option in resource.suggestions">
                         <input type="checkbox" name="options-${option.id}" value="${option.id}" py:attrs="option_selected(rusage, option)" class="setup" />${option.name}  (${resource.place.currency} ${get_pricing(get_tariff(resource.place.id, identity.current.user.id, rusage.start), option, rusage.start)} each)
                    </li>
                </ul></td>
             <div class="errorMessage" py:if="tg_errors">${print_error('options', tg_errors)}</div>
	</tr>
        <tr py:if="permission_or_owner(resource.place, None, 'manage_resources')">
		<td class="left">For User</td>
		<td class="right"> 
                     <?python
                        user = booking_user(rusage) 
                     ?>
                     <input type="text" id="booking_for" value="${user.display_name}" />
                     <input type="hidden" id="booking_for_id" name="user" value="${user.id}" />
                </td>
	</tr>
        <tr>
             <td class="left">Price</td>
             <td class="right">
             <c py:strip="True" py:if="permission_or_owner(resource.place, None, 'manage_resources')">
		<div class="rightFloat" py:if="rusage.customcost==None">Special price for this booking <input type="text" name="customcost" value="" /><span class="errorMessage" py:if="tg_errors">${print_error('customcost', tg_errors)}</span></div>
		<div class="rightFloat" py:if="rusage.customcost!=None">Special price for this booking <input type="text" name="customcost" value="${tg_errors and rusage.customcost or c2s(rusage.customcost)}" /><span class="errorMessage" py:if="tg_errors">${print_error('customcost', tg_errors)}</span></div>
	     </c><span>${resource.place.currency} ${c2s(get_pricing(get_tariff(resource.place.id, identity.current.user.id, rusage.start), resource, rusage.start))}/hour</span>
             </td>
	</tr>
        <tr>
             <td class="left">VAT</td>
             <td class="right">
                <em py:if="resource.place.vat_included">All prices include VAT</em><em py:if="not resource.place.vat_included" >All prices exclude VAT</em>
             </td>
	</tr>
	<tr>
		<td class="left">Additional Information</td>
		<td class="right"><textarea id="notes" name="notes">${rusage.notes}</textarea>
                    <div class="errorMessage" py:if="tg_errors">${print_error('notes', tg_errors)}</div>
                </td>
	</tr>
	<tr py:if="resource.place.tentative_booking_enabled and not hasattr(rusage, 'id')">
		<td class="left">Tentative</td>
                <td class="right"><input type="checkbox" name="tentative" py:attrs="(not rusage.confirmed) and {'checked':'checked'} or {}"/>
                Applicable for the bookings made ${t_booking_life_hrs} hours in advance
                <div><span class="errorMessage" py:if="tg_errors">${print_error('tentative', tg_errors)}</span>&nbsp;&nbsp;<span class="errorMessage" py:if="tg_errors">${print_error('end', tg_errors)}</span></div>
              </td>
        </tr>
        <tr>
            <td class="left">Edit all related Repeat bookings?</td>
            <td class="right" id="edit_repeat_booking">
                <input id="edit_all_repeat_bookings" name="edit_all_repeat_bookings" value="1" type="checkbox" py:attrs="{'checked':'checked'} or {}" />
                <label> The above changes in this booking will be applied to all repeated bookings.</label>               
                <div class="errorMessage" py:if="tg_errors">${print_error('meeting_name', tg_errors)}</div>
                </td>
        </tr>
      </table>
    </div>

${load_meetingBookingEdit(rusage=object, resource=get_resource(object, resource), create=create, tg_errors=tg_errors)}

</div>
