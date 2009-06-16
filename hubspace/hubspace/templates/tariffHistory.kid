<?python
from hubspace.model import User
from datetime import datetime
from hubspace.controllers import get_tariff,pip
from hubspace.utilities.uiutils import months
def years(user):
    create = user.created.year
    this = datetime.now().year
    return range(create, this+3)


def get_tariff_for_datetime(location, user, month, year):
    tariff =  get_tariff(location.id, user.id, datetime(year, month, 1,0,0,1), default=False)
    if tariff:
       return tariff.name
    return ""
     
if 'user' not in locals():
   user = User.select()[0]
if 'location' not in locals():
    location = user.homeplace
?>

<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">
 
 <div py:def="load_tariffHistory(user, location)" py:strip="True">
	<table class="detailTable tariffs data" cellpadding="0" cellspacing="0" >
		<tr class="header">
                      <td></td>
                      <c py:for="year in years(user)" py:strip="True">
			<td>${year} Tariffs</td>
                      </c>
		</tr>
		<tr py:for="month in months()" class="odd">
			<td class="line">${month[1]}</td>
                    <c py:for="year in years(user)" py:strip="True">
			<td>${get_tariff_for_datetime(location, user, month[0], year)}</td>
		    </c>
		</tr>             
	</table>
     </div>     
    ${load_tariffHistory(user, location)}
</div>
