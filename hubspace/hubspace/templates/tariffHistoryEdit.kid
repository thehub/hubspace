<?python
    from datetime import datetime, timedelta
    from hubspace.templates.tariffHistory import get_tariff_for_datetime, years, months
    from hubspace.controllers import get_tariff
    from hubspace.model import Location, Resource
    import calendar
    from hubspace.utilities.uiutils import now
    def can_change(location, user, month, year):
        right_now = now(location)
        if (month==right_now.month and year==right_now.year): #and not get_tariff_for_datetime(location, user, month, year):
            return True
        elif datetime(year, month, 1)>right_now and datetime(year, month, 1)<nowplusxmonths(right_now, 12):
            return True
        return False

    def nowplusxmonths(now, x):
        year = now.year + (now.month+x-1)/12
        month = (now.month+x-1)%12+1
        day = calendar.monthrange(year,month)[1]
        return datetime(year, month, day)

    def get_location(loc):
        return Location.get(loc)

    def tariffs(loc, user, month, year):
        tariffs = dict((tariff.id, tariff.name) for tariff in Resource.selectBy(type='tariff', place=loc, active=1) if tariff.id != loc.defaulttariff.id)
        tariffs[0] = "Guest Tariff"
        return tariffs

    def selected(loc, user, month, year, t_id):
        t= get_tariff(loc.id, user.id, datetime(year, month, 1, 0, 0, 1), False)
        if t:
            t = t.id
        else:
            t=0 
        if t==t_id: 
            return {'selected':'selected'}
        return {}
                
?>

<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">
    	<table py:def="edit_tariffHistory(user, location)" class="detailTable tariffs data" cellpadding="0" cellspacing="0" id="tariffHistory">
		<tr class="header">
                      <td></td>
                      <c py:for="year in years(user)" py:strip="True">
			<td>${year} Tariffs</td>
                      </c>  
                      <input type="hidden" id="location" name="location" value="${location.id}" />
		</tr>
		<tr py:for="month in months()" class="odd">
                     <td class="line">${month[1]}</td>
                    <c py:for="year in years(user)" py:strip="True">
			<td py:if="can_change(location, user, month[0], year)==False">${get_tariff_for_datetime(location, user, month[0], year)}</td>
                    <td py:if="can_change(location, user, month[0], year)">
                        <select class="tariffEdit" id="tariff.${year}.${month[0]}" name="tariff.${year}.${month[0]}">
                             <option py:for="t_id, t_name in tariffs(location, user, month[0], year).iteritems()" py:attrs="selected(location, user, month[0], year, t_id)" value="${t_id}">
                                  ${t_name}
                             </option>
                        </select>
                    </td>
		    </c>
		</tr>		
	</table>
     	${edit_tariffHistory(object, get_location(location))}   
</div>
