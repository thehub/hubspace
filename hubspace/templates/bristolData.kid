<?python
from hubspace.utilities.uiutils import oddOrEven
oddness = oddOrEven().odd_or_even
?>
<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">
    <table py:def="load_bristolData(object, user)" class="memberProfileInner detailTable" cellpadding="0" cellspacing="0">
					<tr class="subHead">
						<td colspan="2">Your organisation</td>
					</tr>
					<tr class="${oddness()}">
						<td class="line wide">Organisation type</td>
                                                <td py:if="'org_type' not in object"></td>
						<td py:if="'org_type' in object">
						   ${object.org_type}
						</td>
					</tr>
					<tr class="${oddness()}">
						<td class="line wide">Number of employees</td>
						<td py:if="'no_of_emps' not in object"></td>
						<td py:if="'no_of_emps' in object">${object.no_of_emps}</td>
					</tr>
					<tr class="${oddness()}">
						<td class="line wide">Areas of interest</td>
						<td>
                                                    <ul py:if="'interest_areas' in object">
                                                        <li py:for="val in object.interest_areas">
                                                           ${val}
                                                        </li>
                                                    </ul>
						</td>
					</tr>
					<tr class="${oddness()}">
						<td class="line wide">Organisational Responsibilities</td>
						<td py:if="'org_res' not in object"></td>
						<td py:if="'org_res' in object">${object.org_res}</td>
					</tr>
					<tr class="subHead">
						<td colspan="2">Social and environmental responsibility</td>
					</tr>
					<tr class="${oddness()}">
						<td  class="line wide">Progressive organisational practices</td>
						<td py:if="'org_prog' not in object"></td>
						<td py:if="'org_prog' in object">${object.org_prog}</td>
					</tr>
					<tr class="subHead">
						<td colspan="2">Your Membership </td>
					</tr>
					<tr class="${oddness()}">
						<td class="line wide">How did you hear about SVN?</td>
						<td py:if="'heard' not in object"></td>
						<td py:if="'heard' in object">${object.heard}</td>
					</tr>
					<tr class="${oddness()}">
						<td class="line wide">What benefits would membership of SVN bring you?</td>
						<td py:if="'benefits' not in object"></td>
						<td py:if="'benefits' in object">${object.benefits}</td>
					</tr>
					<tr class="${oddness()}">
						<td class="line wide">What contribution do you think you can make to SVN? </td>
						<td py:if="'contribution' not in object"></td>
						<td py:if="'contribution' in object">${object.contribution}</td>
					</tr>
					<tr class="subHead">
						<td colspan="2">Additional Information </td>
					</tr>
					<tr class="${oddness()}">
						<td class="line wide">Any additional information you would like to provide:</td>
                                                <td py:if="'additional' not in object"></td>
						<td py:if="'additional' in object">${object.additional} 
                                                
                                                </td>
					</tr>
				</table>

${load_bristolData(object, user)}
</div>
