<?python
from hubspace.utilities.date import get_week_dates
from hubspace.model import Location, Resource
from hubspace.utilities.booking import mybooking, week_event_style, week_unavailable_style, week_coordinates, get_week_overlaps
from hubspace.validators import dateconverter, timeconverter
from turbogears.validators import DateTimeConverter
from hubspace.controllers import get_rusage_bookings, unavailable_for_booking
from hubspace.openTimes import opening_times
from datetime import datetime, time, date
date_str = DateTimeConverter("%a, %d %b").from_python
dt_str = DateTimeConverter("%a, %d %B %Y").from_python

def dt_from_d_and_t(date, time):
    return datetime(date.year, date.month, date.day, time.hour, time.minute)

def max_open_times(week_times):
    start_time = time(11, 59)
    end_time = time(0, 0)
    for day, times in week_times.items():
        if times[0][0] < start_time:
            start_time = times[0][0]
        if times[-1][1] > end_time:
            end_time = times[-1][1]
    return (start_time, end_time)


def calendar_coordinates(week_times):
    start, end = max_open_times(week_times)
    dummy_date = date(1,1,1)
    start_datetime, end_datetime = datetime.combine(dummy_date, start), datetime.combine(dummy_date, end)
    height = end_datetime - start_datetime
    height = height.seconds/60.0/60.0
    height = (36 * height) + 1
    offset = start_datetime - datetime(1,1,1,0,0)
    offset = offset.seconds/60.0/60.0
    offset = 36 * offset #36pixels per hour    
    return {"style":"background-position: 0px -%spx; height: %spx;"%(offset, height)}
?>				
<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">
    <div py:def="load_weekBooking(location, resgroup, date, room_selected, rooms_displayed, only_my_bookings=0)" py:strip="True">
          <?python
             week_times = opening_times(location.calendar, date, period='week')
             start_time, end_time = max_open_times(week_times)
             resources = [Resource.get(res) for res in resgroup.resources_order]
             all_overlaps = get_week_overlaps(date, [res for res in resgroup.resources_order])
          ?>
        <div id="bookspacedate" class="bigcal_week" py:attrs="calendar_coordinates(week_times)" >
            <div id="start-${start_time.hour}" class="${dateconverter.from_python(date)}" />
            <div py:for="day in get_week_dates(date)" class="day_group">
               <?python
                   times = week_times[day]
               ?>
               <c py:for="res in resources" py:strip="True">
	         <div class="day_marker" id="${dt_str(day)}">${date_str(day)}</div>
                 <?python
                      start = dt_from_d_and_t(day, start_time)
                      end = dt_from_d_and_t(day, end_time)
                      unavailable = unavailable_for_booking(res.id, start, end, ignore_current_res=True)
                      rusages = get_rusage_bookings(res, start, end)
                 ?>

	        <div py:for="rusage in rusages"
                   py:attrs="week_event_style(resources, rusage, rooms_displayed, room_selected, start_time, all_overlaps, only_my_bookings)"
                   id="week_rusage-${rusage.id}-${'room'+str(resources.index(rusage.resource)+1)}">
                   <span class="display_start">${timeconverter.from_python(rusage.start)}</span> - 
                   <span class="display_end">${timeconverter.from_python(rusage.end_time)} ${rusage.confirmed and " " or  "(Tentative)"}</span>
                </div>
                <div py:for="other_rusage in unavailable" 
                    py:attrs="week_unavailable_style(resources, res, other_rusage, rooms_displayed, room_selected, start_time, all_overlaps, only_my_bookings)" 
                    id="week_unavailable-${other_rusage.id}-${res.id}-${'room'+str(resources.index(res)+1)}">
                    <span class="display_start">${timeconverter.from_python(other_rusage.start)}</span> - 
                    <span class="display_end">${timeconverter.from_python(other_rusage.end_time)}</span>
                </div>
               </c>
            </div>
            <div id="booking_popup" class="big_popup"><a name="booking_popup" /><div></div></div>
	</div>
        <div id="cal_key"><span id="mybookings">My bookings</span>&nbsp;<span id="unavailable_icon">Unavailable for booking</span>
        &nbsp;<span id="watching">Watching for availability</span></div>
    </div>
    ${load_weekBooking(location, resgroup, date, room_selected, rooms_displayed, only_my_bookings=0)}
</div>
