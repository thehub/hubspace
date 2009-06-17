<?python
from hubspace.utilities.uiutils import oddOrEven, attr_not_none
oddness = oddOrEven()
?>
<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">
          <div py:def="load_memberServices(object)" py:strip="True">
				<table class="servicesTable data" cellpadding="" cellspacing="0">
					<tr py:if="attr_not_none(object, 'handset')" class="${oddOrEven()}">
						<td class="line">Phone handset number</td>
						<td>${object.handset}</td>
					</tr>
					<tr py:if="attr_not_none(object, 'ext')" class="${oddOrEven()}">
						<td class="line">Extension number</td>
						<td>${object.ext}</td>
					</tr>
					<tr py:if="attr_not_none(object, 'frank_pin')" class="${oddOrEven()}">
						<td class="line">Franking machine pin</td>
						<td>${object.frank_pin}</td>
					</tr>
					<tr py:if="attr_not_none(object, 'gb_storage')" class="${oddOrEven()}">
						<td class="line">Storage allocation on hub server (GB)</td>
						<td>${object.gb_storage}</td>
					</tr>
					<tr py:if="attr_not_none(object, 'os')" class="${oddOrEven()}">
						<td class="line">Type of computer</td>
						<td>${object.os}</td>
					</tr>
					<tr py:if="attr_not_none(object, 'storage_loc')" class="${oddOrEven()}">
						<td class="line">Location of storage</td>
						<td>${object.storage_loc}</td>
					</tr>
				</table>
			</div>
${load_memberServices(object)}	
</div>
