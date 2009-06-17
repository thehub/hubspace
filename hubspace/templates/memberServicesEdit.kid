<?python
from hubspace.utilities.uiutils import oddOrEven, print_error
oddness = oddOrEven()
if 'tg_errors' not in locals():
    tg_errors = None
?>
<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">		
    <div py:def="load_memberServicesEdit(object, tg_errors)" class="dataBoxContent">
	<table class="servicesTable data" cellpadding="" cellspacing="0">
		<tr class="${oddness.odd_or_even()">
			<td class="line">Phone handset number</td>
			<td><input type="text" class="text" id='handset' value='${object.handset}' name='handset'/><div class="errorMessage" py:if="tg_errors">${print_error('handset', tg_errors)}</div></td>
		</tr>
		<tr class="${oddness.odd_or_even()">
			<td class="line">Extension number</td>
			<td><input type="text" class="text" id='ext' value='${object.ext}' name='ext'/><div class="errorMessage" py:if="tg_errors">${print_error('ext', tg_errors)}</div></td>
		</tr>
		<tr class="${oddness.odd_or_even()">
			<td class="line">Franking machine pin</td>
			<td><input type="text" class="text" id='frank_pin' value='${object.frank_pin}' name='frank_pin'/><div class="errorMessage" py:if="tg_errors">${print_error('frank_pin', tg_errors)}</div></td>
		</tr>
		<tr class="${oddness.odd_or_even()">
			<td class="line">Storage allocation on hub server (GB)</td>
			<td><input type="text" class="text" id='gb_storage' value='${object.gb_storage}' name='gb_storage'/><div class="errorMessage" py:if="tg_errors">${print_error('gb_storage', tg_errors)}</div></td>
		</tr>
		<tr class="${oddness.odd_or_even()">
			<td class="line">Type of computer</td>
			<td><input type="text" class="text" id='os' value='${object.os}' name='os'/><div class="errorMessage" py:if="tg_errors">${print_error('os', tg_errors)}</div></td>
		</tr>
		<tr class="${oddness.odd_or_even()">
			<td class="line">Location of storage</td>
			<td><input type="text" class="text" id='storage_loc' value='${object.storage_loc}' name='storage_loc'/><div class="errorMessage" py:if="tg_errors">${print_error('storage_loc', tg_errors)}</div></td>
		</tr>
	</table>
    </div>
    ${load_memberServicesEdit(object, tg_errors=tg_errors)}
</div>
