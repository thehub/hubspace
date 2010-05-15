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

<div py:strip="True" xmlns:py="http://purl.org/kid/ns#" py:layout="'plusMaster.kid'">

  <script py:def="include_js()" src="/static/javascript/plus_space.js"></script>

    <div id="spaceContent" class="pane"  py:def="load_content(user)">	
	<div class="paneContent">
	    <div id="space-bookingContent" class="subsectionContent">
               ${load_booking(date=now(location), view=0, location=location)}
             </div>  
        </div>
    </div>
</div>
