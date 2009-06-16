<?python
from hubspace.model import Resource, Location
from hubspace.validators import dateconverter
from datetime import date, datetime, timedelta
from hubspace.templates.bookingSheet import load_bookingSheet
from hubspace.utilities.uiutils import oddOrEven
odd_or_even = oddOrEven().odd_or_even


def home_hub(user, loc):
    if user.homeplace.id==loc:
        return {'selected':'selected'}
    return {}

def now():
    return datetime.now()


def today():
    return dateconverter.from_python(now())

def tomorrow():
    return dateconverter.from_python(now() + timedelta(days=1))

def yesterday():
    return dateconverter.from_python(now() - timedelta(days=1))


?>
				
<div py:strip="True" xmlns:py="http://purl.org/kid/ns#">
    <div id="spaceContent" class="pane"  py:def="load_space(user)" py:strip="True">
	<div class="subBar">
	    <ul>
	        <li class="selected"><a style="cursor:pointer;" id="space-0" class="subsection">Make Booking</a></li>
	        <li><a style="cursor:pointer;" id="space-1" class="subsection">My Bookings</a></li>
        </ul>			
	</div>
	<div class="paneContent">
	  <div id="space-spaceContent" class="subsectionContent">
		<h1>Space and Resource Booking</h1>
                <div class="dataBox">
                    <div class="dataBoxHeader" id="booking_help"><a class="title" id="help_Booking_Help"><h2>Need Help with Booking?</h2></a></div>
                    <div class="dataBoxContent">To make a booking, or modify an existing one:<ol>
<li>Select the date you are looking for.</li>
<li>Click on the space and the time you would like.</li>
<li>Provide us with the booking details required.</li>
</ol>
<p>In the event of a cancellation, the individual or organization booking the space will be charged 50% of the total cost, unless it is cancelled more than two weeks prior to the event.</p>
<p>
A confirmation will be emailed to you as soon as the booking is made. For further information or to cancel a booking (starting in the next two weeks) please email <a href="mailto:${user.homeplace.name.lower()}.hosts@the-hub.net">${user.homeplace.name.lower()}.hosts@the-hub.net</a>.</p> 
                    </div>
                </div>				
		<div class="bookingDate">
                   <form id="space_loc_time">
		     <div class="bookingHub">Select Hub <select id="location" name="location">
				          <option py:for="loc in Location.select()" id='${loc.id}' value='${loc.id}' py:attrs="home_hub(user, loc.id)">${loc.name}</option>
						
						         </select>
                     </div>
		     <a id="leftArrow" class="${yesterday()}"><img src="/static/images/arrow_left.png" alt="&lt;" /></a>
		    <h2 id="space_date"><img src="/static/images/calendar.gif" /> ${today()}</h2>
			<a id="rightArrow" class="${tomorrow()}"><img src="/static/images/arrow_right.png" alt="&gt;" /></a>
               <input type="hidden" name="date" id="space_date_field" value="${today()}" />
                 
                </form>

		 </div>
		 <div><img src="/static/images/booksheet_color_key.png" alt="booksheet color details" /></div>
                 <div id="bookspacedate">        									${load_bookingSheet(user.homeplace, now())}
                 </div>	
                                   
                 <div id="booking_area">
                 </div>
	</div>
      </div>
   </div>
${load_space(object)}
</div>
