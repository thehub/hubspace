<?python
from hubspace.validators import datetimeconverter2, timeconverter
from hubspace.templates import oldLoginMaster
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="oldLoginMaster.kid">

<head>
</head>

<body>

	<div id="hubHomeContent" class="clearfix">
		<div id="main" >
                    <div id="pub_event" class="update_item">
			<h1>${rusage.meeting_name}</h1>
                        <table class="profileDetails">
                               <tr class="property"><td class="propertyTitle">Organisation</td><td class="propertyValue">${rusage.user.organisation}</td>
                               </tr>
                               <tr class="property"><td class="propertyTitle">Location</td><td class="propertyValue">${rusage.resource.place.name} - ${rusage.resource.name}</td>
                               </tr>
                               <tr class="property"><td class="propertyTitle">Date</td><td class="propertyValue">${datetimeconverter2.from_python(rusage.start)} - ${timeconverter.from_python(rusage.end_time)}</td>
                               </tr>
                               <tr py:if="rusage.meeting_description" class="property"><td class="propertyTitle">Description</td><td class="propertyValue">${rusage.meeting_description}</td>
                               </tr>
                        </table>
                    </div>
		</div>
	</div>

</body>


</html>
