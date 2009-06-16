<?python
from hubspace.utilities.uiutils import oddOrEven, print_error
from hubspace.utilities.dicts import AttrDict
oddness = oddOrEven().odd_or_even
tg_errors = None

def object_value(object, property):
   if isinstance(object, AttrDict):
       bristol_data = object
   else:
       bristol_data = object.bristol_metadata
   if property in bristol_data:
       return bristol_data[property]
   else:
       return ""

def has_value(object, property, value):
    if isinstance(object, AttrDict):
        bristol_data = object
    else:
        bristol_data = object.bristol_metadata
    if property in bristol_data and isinstance(bristol_data[property], list):
        if value in bristol_data[property]:
            return {'selected': 'selected'}
    return {} 
      
?>
<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">

	<table class="memberProfileInner detailTable" cellpadding="0" cellspacing="0">
					<tr class="subHead">
						<td colspan="2">Your organisation</td>
					</tr>
					<tr class="${oddness()}">
						<td class="line wide">Organisation type</td>
						<td>
							<select name="org_type">
								<option value="Private Sector" py:attrs="has_value(object, 'org_type', 'Private Sector')">Private Sector</option>
								<option value="Public Sector" py:attrs="has_value(object, 'org_type', 'Public Sector')">Public Sector</option>
								<option value="Non-profit distributing" py:attrs="has_value(object, 'org_type', 'Non-profit distributing')">Non-profit distributing</option>
							</select>
						</td>
					</tr>
					<tr class="${oddness()}">
						<td class="line wide">Number of employees</td>
						<td><input name="no_of_emps" value="${object_value(object, 'no_of_emps')}" type="text" /><div class="errorMessage" py:if="tg_errors">${print_error('no_of_emps', tg_errors)}</div></td>
					</tr>
					<tr class="${oddness()}">
						<td class="line wide">Areas of interest</td>
						<td>
						 <select name="interest_areas" multiple="true">
							<option value="Academia" py:attrs="has_value(object, 'interest_areas', 'Academia')" >Academia</option>
							<option value="Architecture" py:attrs="has_value(object, 'interest_areas', 'Architecture')" >Architecture</option>
							<option value="Banking" py:attrs="has_value(object, 'interest_areas', 'Banking')" >Banking</option>
							<option value="Body and health care" py:attrs="has_value(object, 'interest_areas', 'Body and health care')" >Body and health care</option>
							<option value="Campaigning" py:attrs="has_value(object, 'interest_areas', 'Campaigning')" >Campaigning</option>
							<option value="Charity" py:attrs="has_value(object, 'interest_areas', 'Charity')" >Charity</option>
							<option value="Coaching" py:attrs="has_value(object, 'interest_areas', 'Coaching')" >Coaching</option>
							<option value="Coffee" py:attrs="has_value(object, 'interest_areas', 'Coffee')" >Coffee</option>
							<option value="Communication" py:attrs="has_value(object, 'interest_areas', 'Communication')" >Communication</option>
							<option value="Conservation" py:attrs="has_value(object, 'interest_areas', 'Conservation')" >Conservation</option>
							<option value="Construction" py:attrs="has_value(object, 'interest_areas', 'Construction')" >Construction</option>
							<option value="Consulting" py:attrs="has_value(object, 'interest_areas', 'Consulting')" >Consulting</option>
							<option value="Cultural diversity" py:attrs="has_value(object, 'interest_areas', 'Cultural diversity')" >Cultural diversity</option>
							<option value="Culture" py:attrs="has_value(object, 'interest_areas', 'Culture')" >Culture</option>
							<option value="Development" py:attrs="has_value(object, 'interest_areas', 'Development')" >Development</option>
							<option value="Dialogue" py:attrs="has_value(object, 'interest_areas', 'Dialogue')" >Dialogue</option>
							<option value="Dissemination" py:attrs="has_value(object, 'interest_areas', 'Dissemination')" >Dissemination</option>
							<option value="Economics" py:attrs="has_value(object, 'interest_areas', 'Economics')" >Economics</option>
							<option value="Education" py:attrs="has_value(object, 'interest_areas', 'Education')" >Education</option>
							<option value="Energy" py:attrs="has_value(object, 'interest_areas', 'Energy')" >Energy</option>
							<option value="Environment" py:attrs="has_value(object, 'interest_areas', 'Environment')" >Environment</option>
							<option value="Events" py:attrs="has_value(object, 'interest_areas', 'Events')" >Events</option>
							<option value="Export" py:attrs="has_value(object, 'interest_areas', 'Export')" >Export</option>
							<option value="Film production" py:attrs="has_value(object, 'interest_areas', 'Film production')" >Film production</option>
							<option value="Finance" py:attrs="has_value(object, 'interest_areas', 'Finance')" >Finance</option>
							<option value="Food &amp; beverage" py:attrs="has_value(object, 'interest_areas', 'Food &amp; beverage')" >Food &amp; beverage</option>
							<option value="Foundation" py:attrs="has_value(object, 'interest_areas', 'Foundation')" >Foundation</option>
							<option value="Furniture" py:attrs="has_value(object, 'interest_areas', 'Furniture')" >Furniture</option>
							<option value="Hospitality" py:attrs="has_value(object, 'interest_areas', 'Hospitality')" >Hospitality</option>
							<option value="Information Technology" py:attrs="has_value(object, 'interest_areas', 'Information Technology')" >Information Technology</option>
							<option value="Investment" py:attrs="has_value(object, 'interest_areas', 'Investment')" >Investment</option>
							<option value="Law" py:attrs="has_value(object, 'interest_areas', 'Law')" >Law</option>
							<option value="Marketing" py:attrs="has_value(object, 'interest_areas', 'Marketing')" >Marketing</option>
							<option value="Media" py:attrs="has_value(object, 'interest_areas', 'Media')" >Media</option>
							<option value="Music" py:attrs="has_value(object, 'interest_areas', 'Music')" >Music</option>
							<option value="Product development" py:attrs="has_value(object, 'interest_areas', 'Product development')" >Product development</option>
							<option value="Project management" py:attrs="has_value(object, 'interest_areas', 'Project management')" >Project management</option>
							<option value="Property" py:attrs="has_value(object, 'interest_areas', 'Property')" >Property</option>
							<option value="Publishing" py:attrs="has_value(object, 'interest_areas', 'Publishing')" >Publishing</option>
							<option value="Real Estate" py:attrs="has_value(object, 'interest_areas', 'Real Estate')" >Real Estate</option>
							<option value="Recycling" py:attrs="has_value(object, 'interest_areas', 'Recycling')" >Recycling</option>
							<option value="Research" py:attrs="has_value(object, 'interest_areas', 'Research')" >Research</option>
							<option value="Retail" py:attrs="has_value(object, 'interest_areas', 'Retail')" >Retail</option>
							<option value="Spirituality" py:attrs="has_value(object, 'interest_areas', 'Spirituality')" >Spirituality</option>
							<option value="Technology" py:attrs="has_value(object, 'interest_areas', 'Technology')" >Technology</option>
							<option value="Tourism" py:attrs="has_value(object, 'interest_areas', 'Tourism')" >Tourism</option>
							<option value="Training" py:attrs="has_value(object, 'interest_areas', 'Training')" >Training</option>
							<option value="Travel" py:attrs="has_value(object, 'interest_areas', 'Travel')" >Travel</option>
							<option value="Welfare" py:attrs="has_value(object, 'interest_areas', 'Welfare')" >Welfare</option>
							</select>
						</td>
					</tr>
					<tr class="${oddness()}">
						<td class="line wide">Please briefly describe your responsibilities in your organisation</td>
						<td><textarea name='org_res'>${object_value(object, 'org_res')}</textarea><div class="errorMessage" py:if="tg_errors">${print_error('org_res', tg_errors)}</div></td>
					</tr>
					<tr class="subHead">
						<td colspan="2">Social and environmental responsibility</td>
					</tr>
					<tr class="${oddness()}">
						<td class="line wide">Please outline any of your organisations practices that could be described as progressive</td>
						<td><textarea name='org_prog'>${object_value(object, 'org_prog')}</textarea><div class="errorMessage" py:if="tg_errors">${print_error('org_prog', tg_errors)}</div></td>
					</tr>
					<tr class="subHead">
						<td colspan="2">Your Membership </td>
					</tr>
					<tr class="${oddness()}">
						<td class="line wide">How did you hear about SVN?</td>
						<td><textarea name='heard'>${object_value(object, 'heard')}</textarea><div class="errorMessage" py:if="tg_errors">${print_error('heard', tg_errors)}</div></td>
					</tr>
					<tr class="${oddness()}">
						<td class="line wide">What benefits would membership of SVN bring you?</td>
						<td><textarea name='benefits'>${object_value(object, 'benefits')}</textarea><div class="errorMessage" py:if="tg_errors">${print_error('benefits', tg_errors)}</div></td>
					</tr>
					<tr class="${oddness()}">
						<td class="line wide">What contribution do you think you can make to SVN? </td>
						<td><textarea name="contribution">${object_value(object, 'contribution')}</textarea><div class="errorMessage" py:if="tg_errors">${print_error('contribution', tg_errors)}</div></td>
					</tr>
					<tr class="subHead">
						<td colspan="2">Additional Information </td>
					</tr>
					<tr class="${oddness()}">
						<td class="line wide">Any additional information you would like to provide:</td>
						<td><textarea name='additional'>${object_value(object, 'additional')}</textarea><div class="errorMessage" py:if="tg_errors">${print_error('additional', tg_errors)}</div></td>
					</tr>
				</table>
</div>
