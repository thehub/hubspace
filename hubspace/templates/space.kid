<?python
from hubspace.model import Resource, Location
from hubspace.validators import dateconverter
from datetime import date, datetime, timedelta
from hubspace.templates.booking import load_booking
from hubspace.utilities.uiutils import oddOrEven, now
odd_or_even = oddOrEven().odd_or_even


def home_hub(user, loc):
    if user.homeplace.id==loc:
        return {'selected':'selected'}
    return {}


##are these used?
def today(location):
    return dateconverter.from_python(now(location))

def tomorrow(location):
    return dateconverter.from_python(now(location) + timedelta(days=1))

def yesterday(location):
    return dateconverter.from_python(now(location) - timedelta(days=1))


?>
				
<div py:strip="True" xmlns:py="http://purl.org/kid/ns#">
    <div id="spaceContent" class="pane"  py:def="load_space(user)" py:strip="True">
	<div class="subBar">
	    <ul>
	        <li class="selected"><a style="cursor:pointer;" id="space-0" class="subsection">Make Booking</a></li>
            </ul>			
	</div>
	<div class="paneContent">
	  <div id="space-bookingContent" class="subsectionContent">
               ${load_booking(date=now(user.homeplace), view=0, location=user.homeplace)}
	  </div>  
        </div>
    </div>
    ${load_space(user=object)}
</div>
