<?python
from datetime import datetime
from hubspace.validators import dateconverter as dc, timeconverter as tc
from hubspace.openTimes import opening_times, week_from_date
from hubspace.utilities.permissions import locations
from hubspace.utilities.uiutils import select_home_hub
days = {0:_('Monday'),
        1:_('Tuesday'),
        2:_('Wednesday'),
        3:_('Thursday'),
        4:_('Friday'),
        5:_('Saturday'),
        6:_('Sunday')}

hours = range(0,24)
mins = ['00', '15', '30', '45']
?>
<div id="openTimesContent" class="pane" xmlns:py="http://purl.org/kid/ns#" py:strip="True">
     <h1>Under Construction</h1>
        <!-- week selector -->
<!--
    <select id="invoice_search_location" name="location"><option py:for="location in locations('manage_resources')" value="${location.id}" py:attrs="select_home_hub(location)">${location.name}</option></select>
    <c py:strip="True" py:def="open_times(location, date=datetime.today())">
        <form id="opening_times" name="opening_times" action="POST">
        <table id="OpenTimes" class="detailTable data">
            <?python
                day_times = opening_times(location.id, date, period='week')
            ?>
            <tr class="header">
                <td>Day</td>
                <td>Opening Times</td>
                <td>Make Default Time</td>
            </tr>
            <tr py:for="date in week_from_date(date)">
                <?python
                    times = day_times[date]
                ?>
                <td>
                    <span class="timing_label">${days[date.weekday()]}</span>
                </td>
                <td>
                    <c py:for="time in times" py:strip="True">
                        <span id="openTimeRange_${dc.from_python(time.date).replace(' ', '-').replace(',', '')}_${time.location.id}" class="openTime ${time.date and 'custom_date' or 'default_date'}" >${tc.from_python(time.t_open) + ' - ' + tc.from_python(time.t_close)}</span>
                        &nbsp;&nbsp;<a class="button" id="openTimeRange_${dc.from_python(time.date).replace(' ', '-').replace(',', '')}_${time.location.id}Edit" >Edit times</a>       
                        &nbsp;&nbsp;<a class="button">Add time</a>
                    </c>
                </td>
                <td>
                    <a py:if="times[0].date" class="button" id="save_default_times">for ${days[date.weekday()]} from ${dc.from_python(date)}</a>
                    <span py:if="not times[0].date">is default</span>
                </td>
            </tr>
        </table>
        </form>
    </c>
    ${open_times(object.homeplace)}-->
</div>
