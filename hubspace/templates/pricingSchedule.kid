<?python
from hubspace.utilities.uiutils import oddOrEven, c2s, months, print_error
from hubspace.model import Pricing, Resource
from hubspace.controllers import get_ordered_pricings
from hubspace.validators import dateconverter
odd_or_even = oddOrEven().odd_or_even
from datetime import datetime
if 'tg_errors' not in locals():
    tg_errors = None
def years():
    return range(2007, 2050)
def get_date(price):
    date = price.periodstarts
    if date<=datetime(1970, 1, 1,0,0,1):
         return ' -'
    return dateconverter.from_python(date)
?>
<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">
   <tr py:def="resource_pricing_entry(price)" class="${odd_or_even()}">
        <td>${get_date(price)}</td>
        <td>${price.resource.place.currency} ${c2s(price.cost)}</td>
        <td py:if="get_date(price)!=' -'"><a class="button delete_pricing" id="delprice_${price.id}">delete</a></td>
        <td py:if="get_date(price)==' -'"> -</td>
   </tr>
   <div class="dataBox" py:def="resource_pricing_schedule(resource, tariff_id)">
		<div class="dataBoxHeader">
		 <a class="title" id="link_pricing_schedule"><h2> Pricing Schedule - ${resource.name}</h2></a>
		</div>
      	        <div class="dataBoxContent">
	    	     <table class="detailTable data">
                                <tr class="header">
                                     <td>Period Starting</td>
                                     <td>${resource.name} - price</td>
                                     <td>Delete Pricing</td>
                                </tr>
				<c py:for="price in get_ordered_pricings(Resource.get(tariff_id), object)" py:strip="True">${resource_pricing_entry(price)}</c>
                                <tr>
                                        <td colspan="3" id="add_pricing_row"><a id="add_pricing" class="button">add pricing</a>
                                          <div id="add_pricing_divider"><span><form id="add_pricing_form" style="display:none;width:90%">
                                           <strong>Starting Period:</strong>  <span>month <select name="periodstarts.month"><option py:for="month in months()" value="${month[0]}">${month[1]}</option></select>
                                                 year <select name="periodstarts.year"><option py:for="year in years()" value="${year}">${year}</option></select>
                                            </span>
                                            <span id="price"><strong>Price: </strong> <input type="text" name="cost" /></span>
                                          </form></span><span id="submit_add_pricing" style="display:none;"><input type="image" src="/static/images/button_save.gif" /></span></div>
                                        </td>
                                </tr>
	            </table>	
	       </div>

    </div>
    <div py:strip="True" py:def="add_pricing_error(cost, month, year)">
        <span><form id="add_pricing_form" style="width:90%">
                       <strong>Starting Period:</strong>  <span>month <select name="periodstarts.month"><option py:for="month in months()" value="${month[0]}">${month[1]}</option></select>
                        year <select name="periodstarts.year"><option py:for="year in years()" value="${year}">${year}</option></select>
                        </span>
                        <span id="price"><strong>Price: </strong> <input type="text" name="cost" value="${cost}" /><div class="errorMessage"><span id="periodstarts_error" py:if="tg_errors">${print_error('periodstarts', tg_errors)}</span><span id="cost_error" py:if="tg_errors">${print_error('cost', tg_errors)}</span></div></span>
               </form></span><span id="submit_add_pricing"><input type="image" src="/static/images/button_save.gif" /></span>
    </div>
  

    <c py:if="'object' in locals()" py:strip="True">${resource_pricing_schedule(object, tariff)}</c>
    <c py:if="'tg_errors' in locals()" py:strip="True">${add_pricing_error(cost, month, year)}</c>
</div>
