<?python
from hubspace.templates.meetingBookingEdit import load_meetingBookingEdit
from hubspace.utilities.uiutils import oddOrEven
odd_or_even = oddOrEven().odd_or_even
tg_errors = None
resource = None
message = None
?>

<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">
    <div py:def="meeting_booking(rusage=None, resource=None, create=None, tg_errors=None,  message=None)" py:strip="True">
        <a title="close popup" class="close_popup">X</a>
        <form id="add_booking" py:if="resource">
            <div>
                ${load_meetingBookingEdit(rusage, resource, create, tg_errors)}	
                <input type="button" class="rightFloat" value="${_('Add Booking')}" id="submit_add_booking" />
                <input type="button" id="submit_cancel_booking" class="close_popup" value="Cancel" />
            </div>
        </form>
        <c py:if="message" py:strip="True">
        <table class="detailTable data" id="meetingBooking" cellpadding="" cellspacing="0">
            <tr class="${odd_or_even()}">
                <td class="line">Message</td>
                <td>${XML(message)}</td>
            </tr>
        </table>
        </c>
    </div>

    ${meeting_booking(rusage=object, resource=resource, create=True, tg_errors=tg_errors, message=message)}


</div>
