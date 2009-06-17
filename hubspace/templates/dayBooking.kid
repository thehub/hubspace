<?python
from datetime import datetime
from hubspace.model import Location, Resource
from hubspace.openTimes import opening_times
from hubspace.controllers import get_rusage_bookings, unavailable_for_booking
from hubspace.validators import timeconverter, dateconverter
from hubspace.utilities.booking import mybooking, get_width, day_event_style, day_unavailable_style

def dt_from_d_and_t(date, time):
    return datetime(date.year, date.month, date.day, time.hour, time.minute)

def get_height(start, end):
    height = datetime.combine(datetime.min, end) - datetime.combine(datetime.min, start)
    height = int(height.seconds/60.0/60.0)
    return (36 * height) + 1

def get_offset(start):
    offset = datetime.combine(datetime.min, start) - datetime.min
    offset = int(offset.seconds/60.0/60.0)
    return 36 * offset #36pixels per hour

def height_and_offset(start, end):
    return {"style":"background-position: 0px -%spx; height: %spx;"%(get_offset(start), get_height(start, end))}

def height_and_width(start, end, no_rooms):
    return {"style":"height: %spx; width:%spx;"%(get_height(start, end), get_width(no_rooms))}


?>				
<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">

   <div py:def="load_dayBooking(location, resgroup, date, only_my_bookings=0)" py:strip="True">
       <?python
           times = opening_times(location.calendar, date)
           start_time, end_time = times[0][0], times[-1][1]
           resources = [Resource.get(res) for res in resgroup.resources_order]
           no_rooms = len(resources)
       ?>
       <div id="room_header">
           <div py:for="res in resources" class="room_selector room${resources.index(res)+1}" style="width: ${get_width(no_rooms)}px;">
               <a class="label" style="width: ${get_width(no_rooms)-6}px;">${res.name}</a>
           </div> 
       </div>
       <div id="bookspacedate" class="bigcal_day" py:attrs="height_and_offset(start_time, end_time)">
           <div id="start-${start_time.hour}" class="${dateconverter.from_python(date)}">
 	        <div py:for="res in resources" class="room_group" py:attrs="height_and_width(start_time, end_time, no_rooms)" id="res-${res.id}">
                     <?python
                         start = dt_from_d_and_t(date, start_time)
                         end = dt_from_d_and_t(date, end_time)
                         rusages =  get_rusage_bookings(res, start, end)
                         unavailable = unavailable_for_booking(res.id, start, end, ignore_current_res=True)
                     ?>
                     <div py:for="rusage in rusages" py:attrs="day_event_style(start_time, resources, res, rusage, no_rooms, only_my_bookings)" id="day_rusage-${rusage.id}"><span class="display_start">${timeconverter.from_python(rusage.start)} </span>-<span class="display_end">${timeconverter.from_python(rusage.end_time)} ${rusage.confirmed and " " or  "(Tentative)"}</span></div>
                     <div py:for="other_rusage in unavailable" py:attrs="day_unavailable_style(start_time, resources, res, other_rusage, no_rooms, only_my_bookings)" id="day_unavailable-${other_rusage.id}-${res.id}"><span class="display_start">${timeconverter.from_python(other_rusage.start)}</span>-<span class="display_end">${timeconverter.from_python(other_rusage.end_time)}</span></div>
                </div>
                <div id="booking_popup" class="big_popup"><a name="booking_popup" /><div></div></div>
           </div>
       </div>
       <div id="cal_key"><span id="mybookings">My bookings</span><span id="unavailable_icon">Unavailable for booking</span>
        <span id="watching">Watching for availability</span></div>
   </div>
   ${load_dayBooking(location, resgroup, date, only_my_bookings)}
</div>
