<?python
from hubspace.utilities.uiutils import oddOrEven
odd_or_even = oddOrEven().odd_or_even
def tariffs(location):
   return sorted([resource for resource in location.resources if resource.type=='tariff'])
?>

<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">
  <div py:def="resources(location)" py:strip="True">
  	<div class="dataBox">
		<div class="dataBoxHeader">
                   <a class="modify" href="#add_tariff" id="addTariff">Add Tariff</a>
<a id="link_addTariff" class="title"><h2>Tariffs</h2></a>        
		</div>
	    <div class="dataBoxContent">
			<table id="tariff_management" class="detailTable data">
                                <tr class="header">
                                    <td>Name</td>
				    <td>Description</td>
				    <td>Percentage VAT (0-100)</td>
                                    <td>Active</td>
                                    <td>Default</td>
                                    <td>Resources</td>
                                </tr>
				<tr py:for="tariff in tariffs(location)" class="${odd_or_even()}">
					<td><div class="resourceName" id="resourceName_${tariff.id}">${tariff.name}</div><a id="resourceName_${tariff.id}Edit" class="button">edit</a></td>
					<td><div class="resourceDescription" id="resourceDescription_${tariff.id}">${tariff.description}</div><a id="resourceDescription_${tariff.id}Edit" class="button">edit</a></td>
                                        <td><div class="resourceVAT" id="resourceVAT_${tariff.id}">${[tariff.place.vat_default, tariff.vat][type(tariff.vat)==float]}</div><a id="resourceVAT_${tariff.id}Edit" class="button">edit</a></td>
                                        <td py:if="not tariff.active">Inactive <a class="button activate" id="activeness-${tariff.id}">activate</a></td>
                                        <td py:if="tariff.active">Active <a class="button activate" id="activeness-${tariff.id}">de-activate</a></td>
                                        <td py:if="tariff.default_tariff_for">True</td>
                                        <td py:if="not tariff.default_tariff_for">False&nbsp;&nbsp;<a class="defaultTariff" id="defaulttariff_${tariff.id}">make guest tariff</a></td>
					<td><a id="managePrices_${tariff.id}" class="button managePrices" href="#pricing">Price List</a></td>
				</tr>
			</table>	
	    </div>
            <a name="pricing"></a>
            <a name="add_tariff"></a>
            <div id="tariff_resources">
            </div>
    </div>
  </div>
${resources(object)}
</div>  	
  	
