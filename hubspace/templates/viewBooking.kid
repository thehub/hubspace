<?python
from hubspace.templates.meetingBooking import meetingBooking
from hubspace.utilities.uiutils import oddOrEven
odd_or_even = oddOrEven().odd_or_even
tg_errors = None
resource = None
message = None
rusage = None
?>

<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">
    <div py:def="meeting_booking(rusage=None, tg_errors=None,  message=None)" py:strip="True">
        <a title="close popup" class="close_popup">X</a>
        <form py:if="rusage" py:strip="True">
           <div id="meetingBooking">
                ${meetingBooking(rusage, message)}	
            </div>
        </form>
        <c py:if="message" py:strip="True">
                <div>${XML(message)}</div>
        </c>
    </div>
    ${meeting_booking(rusage=rusage, tg_errors=tg_errors, message=message)}
</div>
