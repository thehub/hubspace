<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" >
<head>


    <link rel="stylesheet" href="/static/css/micro/blueprint/screen.css" type="text/css" media="screen, projection, print"/>
    <!--[if lt IE 8]> 
    <link rel="stylesheet" href="/static/css/micro/blueprint/ie.css" type="text/css" media="screen, projection"/>
    <![endif]-->
    <link rel="stylesheet" href="/static/css/micro/typography.css" type="text/css" media="screen, projection, print"/>
    <link rel="stylesheet" href="/static/datepicker/css/datepicker.css" type="text/css" />

    <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js"></script>

    <script type="text/javascript" src="/static/datepicker/js/datepicker.js"></script>
    <script type="text/javascript" src="/static/datepicker/js/eye.js"></script>
    <script type="text/javascript" src="/static/datepicker/js/layout.js"></script>


</head>

<body>  

<?python
from hubspace.model import RUsage
booking = RUsage.get(booking_id)
repeat_usages = RUsage.selectBy(repetition_id=booking_id).orderBy('start')
?>

<h4 class="box">Bookings Details</h4>
<table class="prepend-1">
<tr>
    <th>Resource</th>
    <td> ${booking.resource.name} </td>
</tr>
<tr>
    <th>Meeting</th>
    <td> ${booking.meeting_name} </td>
</tr>
<tr>
    <th>Description</th>
    <td> ${booking.meeting_description} </td>
</tr>
<tr>
    <th>Public</th>
    <td> ${booking.public_field and "Yes" or "No"} </td>
</tr>
</table>

<h4 class="box">Repeated bookings</h4>
<table class="prepend-1 append-1 span-15  colborder">
<tr>
    <th class="span-2">Sr. No.</th>
    <th class="span-5">Date</th>
    <th class="span-3">Start Time</th>
    <th class="span-3">End Time</th>
</tr>
<tr py:for="i, usage in enumerate(repeat_usages)">
    <td>${i+1}</td>
    <td>${usage.start.date().strftime("%a, %b %d %Y")}</td>
    <td>${usage.start.strftime("%l:%M %P")}</td>
    <td>${usage.end_time.strftime("%l:%M %P")}</td>
</tr>
</table>


</body>

</html>
