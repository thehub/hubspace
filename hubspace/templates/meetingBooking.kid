<?python
from hubspace.bookinglib import isAvailabilityInfoReqValid, canConfirm
from hubspace.utilities.uiutils import oddOrEven, c2s
from hubspace.controllers import can_delete_rusage, permission_or_owner
odd_or_even = oddOrEven().odd_or_even
from hubspace.validators import dateconverter
def add_zero(min):
    if len(str(min))<2:
        return "0"+ str(min) 
    else:
        return str(min)

def display_time(date):
    if date.hour/13==0:
       return str(date.hour)+ ":"+add_zero(date.minute)+"am"
    else:
       return str(date.hour%12)+":" +add_zero(date.minute)+"pm"

def public_or_private(rusage):
    if rusage.public_field:
       return "(Publicised on the Hub Website)"
    return ""

nl2br = lambda s: s.replace("\n","<br/>")
?>

<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">
     <div py:def="meetingBooking(rusage=None, message='')">
           <a py:if="rusage and can_delete_rusage(rusage)" class="modify" id="meetingBookingEdit">edit</a>
	   <table py:def="meeting(rusage, message)" class="booking_popupTable" cellpadding="" cellspacing="0" >
                <tr py:if="message">
		     <td class="left">Unavailable</td>
                     <td class="right">
                         <span class="message">${XML(message)}</span>
                     </td>
                </tr>		
                <c py:if="rusage" py:strip="True">
                    <tr>
			<td class="left">Resource</td>
				<td class="right">${rusage.resource.name}  
                                      <span style="display:none" id="rusage_id" class="${rusage.id}" /> 
                                </td>
			</tr>
			<tr py:if="rusage.resource.type=='room'">
				<td class="left">Meeting name</td>
				<td class="right">${rusage.meeting_name} ${public_or_private(rusage)}</td>
			</tr>
			<tr py:if="rusage.resource.type=='room'">
				<td class="left">Meeting Description</td>
                                <td class="right">${XML(nl2br(rusage.meeting_description))}</td>
			</tr>
                        <tr>
				<td class="left">Date</td>
				<td class="right">${dateconverter.from_python(rusage.start)}</td>
			</tr>
			<tr>
				<td class="left">Time</td>
				<td class="right">${display_time(rusage.start)} - ${display_time(rusage.end_time)}</td>
			</tr>
			<tr py:if="rusage.resource.type=='room'">
				<td class="left">Number of people</td>
				<td class="right">${str(rusage.number_of_people)}</td>
			</tr>
	                <tr py:if="rusage.suggested_usages">
				<td class="left">Extras</td>
				<td class="right">
                                    <li>
                                        <ul py:for="usage in [usage for usage in rusage.suggested_usages if not usage.cancelled]">${usage.resource_name}</ul>
                                    </li>
                                </td>
			</tr>
                        <tr>
                                <td class="left">Cost</td>
				<td class="right">${rusage.resource.place.currency} ${rusage.customcost != None and c2s(rusage.customcost) or c2s(rusage.cost)} <c py:if="rusage.resource.place.vat_included" py:strip="True">(including VAT)</c><c py:if="not rusage.resource.place.vat_included" py:strip="True">(excluding VAT)</c></td>
                        </tr>
                        <tr>
                                <td class="left">Booked For</td>
                                <td class="right">${rusage.user.display_name}</td>
                        </tr>
                        <tr py:if="rusage.bookedby and permission_or_owner(rusage.resource.place, None, 'manage_resources')">
                                <td class="left">Booked By</td>
                                <td class="right">${rusage.bookedby.display_name}</td>
                        </tr>
			<tr py:if="rusage.notes">
				<td class="left">Additional Information</td>
				<td class="right">${rusage.notes}
                                  </td>
			</tr>
                        <tr py:if="rusage.confirmed and permission_or_owner(rusage.resource.place, None, 'manage_resources')">
                              <td class="left">Repeat Booking</td>
                              <td class="right">
                                <ul>
                                <li><a id="caladd-${rusage.id}" class="repeat_booking">Repeat this Booking</a></li>
                                <li py:if="rusage.repetition_id">
                                    <a id="calshow-${rusage.repetition_id}" class="repeat_booking_info">Show repeated bookings</a>
                                </li>
                                </ul>
                            </td>
                        </tr>
	                <tr py:if="can_delete_rusage(rusage)">
                              <td class="left">Cancel Booking</td>
                              <td class="right">
                              <ul>
                              <li><a class="del_booking" id="caldel-${rusage.id}">Cancel this Booking</a></li>
                              <li><a py:if="rusage.repetition_id" class="del_repeatbooking" id="caldel-${rusage.repetition_id}">
                                Cancel all occurances of this Booking</a>
                              </li>
                              </ul>
                              </td>
                        </tr>	
                        <tr py:if="rusage.resource.place.tentative_booking_enabled and rusage.resource.type == 'room'">
                                <td class="left">Tentative</td>
                                <td class="right">${rusage.confirmed and "No" or "Yes"}</td>
                        </tr>
                        <tr py:if="isAvailabilityInfoReqValid(rusage)">
                                <td/>
                                <td class="right">
                                <input type="submit" value="Request availability notification for this booking" 
                                    class="notify_on_available" id="rusage-${rusage.id}"/>
                                    <br/>(You will be notified if this booking expires/confirmed)
                                </td>
                        </tr>
                        <tr py:if="canConfirm(rusage)">
                            <td/>
                            <td><input class="confirmBooking" id="rusage-${rusage.id}" type="submit" value="Confirm this booking"/></td>
                        </tr>
                      </c>
       	           </table>
${meeting(rusage=rusage, message=message)}
            </div>
       <c py:if="'rusage' in locals() and 'message' not in locals()" py:strip="True">
          ${meetingBooking(rusage=rusage, message=None)}
       </c>
       <c py:if="'booking' in locals()" py:strip="True">
          ${meeting(rusage=booking, message=None)}
       </c> 
       <c py:if="'message' in locals()" py:strip="True">
          ${meetingBooking(message=message)}
       </c>   
</div>
