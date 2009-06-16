<?python
from hubspace.utilities.uiutils import oddOrEven, print_error, all_hosts, get_freetext_metadata, selected_user
oddness = oddOrEven()
if 'tg_errors' not in locals():
    tg_errors = None
?>
<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">		
    <div py:def="load_relationshipStatusEdit(object, tg_errors)" class="dataBoxContent">
	<table class="servicesTable data" cellpadding="" cellspacing="0">
		<tr class="${oddness.odd_or_even()">
			<td class="line">Introduced By</td>
			<td><input type="text" class="text" value="${get_freetext_metadata(object, 'introduced_by')}" name='introduced_by'/><div class="errorMessage" py:if="tg_errors">${print_error('introduced_by', tg_errors)}</div></td>
		</tr>
                <tr>
		    <td class="line">Signed By</td>
                    <td>
                        <select name="signedby">
                           <option value="0">Unknown</option>
                           <option py:for="user in all_hosts()" value="${user.id}" py:attrs="selected_user(user, object.signedby)">${user.display_name}</option>
                        </select><div class="errorMessage" py:if="tg_errors">${print_error('signedby', tg_errors)}</div>
                    </td>
                </tr>
                <tr>
		    <td class="line">Host Contact</td>
                    <td>
                        <select name="hostcontact">
                           <option value="0">Unknown</option>
                           <option py:for="user in all_hosts()" value="${user.id}" py:attrs="selected_user(user, object.hostcontact)">${user.display_name}</option>
                        </select><div class="errorMessage" py:if="tg_errors">${print_error('hostcontact', tg_errors)}</div>
                    </td>
                </tr>
	</table>
    </div>
    ${load_relationshipStatusEdit(object, tg_errors=tg_errors)}
</div>
