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
    <script type="text/javascript" src="/static/javascript/jquery.confirm-1.3.js"></script>


</head>

<body>  

<?python
from hubspace.model import RUsage
repeat_usages = list(RUsage.selectBy(repetition_id=booking_id).orderBy('start'))
booking = repeat_usages[0]
?>

<script>
$(document).ready(function() {  
$('#result_area').hide();
$('#del_usages').click( function () {
    $('#result_area').show();
    var data = $("#del_bookings").serializeArray();
    $.ajax({
        url: "/delete_rusages",
        type: 'POST',
        data: data,
        beforeSend: function () {
            $('#result_area').text('processing...');
        },
        success: function (data) {
            $('#result_area').html('<span>' + data + '</span><br/>');
            $('.del_usage:checked').each(function(i, Element) {
                var usage_id = $(this).val();
                $('.del_usage-' + usage_id).remove();
            });
        }
    });
});
$('#del_usages').confirm({
    msg:'Do you really want to delete selected usages?'
});
});
</script>

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
<form id="del_bookings">
<table class="prepend-1 append-1 span-15  colborder">
<tr>
    <th class="span-2">Sr. No.</th>
    <th class="span-5">Date</th>
    <th class="span-3">Start Time</th>
    <th class="span-3">End Time</th>
    <th class="span-3">Delete</th>
</tr>
<tr py:for="i, usage in enumerate(repeat_usages)" class="del_usage-${usage.id}">
    <td>${i+1}</td>
    <td>${usage.start.date().strftime("%a, %b %d %Y")}</td>
    <td>${usage.start.strftime("%l:%M %P")}</td>
    <td>${usage.end_time.strftime("%l:%M %P")}</td>
    <td><input type="checkbox" name="rusage_ids" id="del-${usage.id}" class="del_usage" value="${usage.id}"/></td>
</tr>
</table>
</form>

<hr/>
<div class="prepend-2" id="result_area"/>

<div class="prepend-2">
<input type="button" id="del_usages" value="Delete selected"/>
</div>


</body>

</html>
