<?python
from hubspace.utilities.uiutils import oddOrEven, c2s
from hubspace.model import Pricing
from hubspace.controllers import get_pricing

odd_or_even = oddOrEven().odd_or_even

def resources(tariff):
   return [res for res in tariff.place.resources if res.type!='tariff' or res.id==tariff.id]

def price(resource, tariff):
    pricing = get_pricing(tariff, resource)
    return c2s(pricing) 

?>
<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">
   <div class="dataBox" py:def="resource_pricing_table(object)">
		<div class="dataBoxHeader">
		 <a class="title" id="link_addResources"><h2>Tariff - ${object.name}</h2></a>
		</div>
      	        <div class="dataBoxContent">
	    	     <table class="detailTable data">
                                <tr class="header">
                                     <td>Name</td>
                                     <td>Price per hour/<br />Price per unit (Current) </td>
                                     <td>Pricing Schedule</td>
                                </tr>
				<tr py:for="resource in resources(object)" class="${odd_or_even()}">
					<td><div class="resourceName" id="resourceName_${resource.id}">${resource.name}</div></td>
					
                                        <td>${resource.place.currency} ${price(resource, object)}</td>
                                        <td><a href="#schedule_area" id="schedule_${resource.id}_${object.id}" class="button schedule">Schedule</a></td>
				</tr>
	            </table>	
	       </div>
         <a name="schedule_area" />
         <div id="schedule_area" /> 
    </div>
    <c py:strip="True">${resource_pricing_table(object)}</c>
</div>
