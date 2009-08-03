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

<div py:if="already_invoiced" class="errorMessage">
<strong>Warning: While changing Tariffs below usages are detected for which invoices are already sent. You may want to note
these and refund as per your policies.</strong>
<table cellspacing="0" cellpadding="0" class="detailTable">
<tr class="header">
    <td>Member</td>
    <td>Invoice Number</td>
    <td>Resource</td>
    <td>Booking time</td>
    <td>Tariff</td>
</tr>
<tr></tr>
<tr py:for="usage in already_invoiced">
    <td>${usage.user.display_name}</td>
    <td>${usage.invoice.number}</td>
    <td>${usage.resource.name}</td>
    <td>${usage.start.ctime()}</td>
    <td>${usage.tariff.name}</td>
</tr>
</table>
<!-- TODO <a href="#" id="send_already_invoiced_list" >"Send me this information"</a> -->
</div>
 
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
