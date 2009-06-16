<?python
from hubspace.utilities.uiutils import oddOrEven, attr_not_none, c2s, get_freetext_metadata, get_singleselected, get_multiselected
oddness = oddOrEven()
from hubspace.controllers import gip, is_owner, permission_or_owner, get_place
from hubspace.validators import dateconverter

from hubspace.utilities.image_helpers import image_src

def locations(object):
    locations = []
    for group in object.groups:
            if group.place not in locations and group.place:
                locations.append(group.place)
    return locations

def any_aliases(object):
    try:
        object.alias[0]
	return True
    except:
        return False

def locations_string(object):
    return ", ".join([loc.name for loc in locations(object)])
?>

<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">
   <table py:def="load_memberProfile(object)" cellpadding="0" cellspacing="0" class="memberProfile">
	 <tr>
            	<td class="photo" id="photo${object.id}">
                      <div class="innerPhoto">
                          <p> ${object.display_name}</p>
                          <div class="imgwrap">                      
                              <img id="profile_image${object.id}" src="${image_src(object, 'image', '/static/images/shadow.png')}" /> 
                          </div>
                      </div>
                      <div py:if='permission_or_owner(object.homeplace,object,"manage_users")' id="upload_image${object.id}" class="replace_image">replace image</div>
                      <div id="iframe_area${object.id}"></div>
                </td>
	        <td>
			<table class="memberProfileInner detailTable" cellpadding="0" cellspacing="0">
						
                                                <tr py:if="attr_not_none(object, 'user_name')" class="${oddness.odd_or_even()}">
							<td class="line">Username</td>
							<td>${object.user_name}</td>
						</tr>
						<tr py:if="attr_not_none(object, 'organisation')" class="${oddness.odd_or_even()}">
							<td class="line">Organisation</td>
							<td>${object.organisation}</td>
						</tr>
                                                <tr py:if="attr_not_none(object, 'title') and permission_or_owner(object.homeplace,object,'manage_users')" class="${oddness.odd_or_even()}">
							<td class="line">Role</td>
							<td>${object.title}</td>
						</tr>
                                                <tr py:if="permission_or_owner(object.homeplace, None, 'manage_users')" class="${oddness.odd_or_even()}">
							<td class="line">Active?</td>
							<td>${object.active and "Yes" or "No"}</td>
						</tr>
                                                <tr py:if="attr_not_none(object, 'homeplace')" class="${oddness.odd_or_even()}">
							<td class="line">Home Hub</td>
							<td>${object.homeplace.name}</td>
						</tr>
                                                <tr py:if="get_freetext_metadata(object, 'biz_type')" class="${oddness.odd_or_even()}">
							<td class="line">Type of Business</td>
							<td>${get_freetext_metadata(object, 'biz_type')}</td>
						</tr>
						<tr py:if="attr_not_none(object, 'mobile')" class="${oddness.odd_or_even()}">
							<td class="line">Mobile</td>
							<td>${object.mobile}</td>
						</tr>
						<tr py:if="attr_not_none(object, 'work')" class="${oddness.odd_or_even()}">
							<td class="line">Work Phone</td>
							<td>${object.work}</td>
						</tr>
						<tr py:if="attr_not_none(object, 'home')" class="${oddness.odd_or_even()}">
							<td class="line">Home Phone</td>
							<td>${object.home}</td>
						</tr>
						<tr py:if="attr_not_none(object, 'fax')" class="${oddness.odd_or_even()}">
							<td class="line">Fax</td>
							<td>${object.fax}</td>
						</tr>
						<tr py:if="attr_not_none(object, 'email_address') and len(object.email_address.split('@', 1))==2" class="${oddness.odd_or_even()}">
							<td class="line">Default Email</td>
							<td><a href="mailto:${object.email_address}">${object.email_address}</a></td>
						</tr>
						<tr py:if="attr_not_none(object, 'email2')" class="${oddness.odd_or_even()}">
							<td class="line">Email 2</td>
							<td><a href="mailto:${object.email2}">${object.email2}</a></td>
						</tr>
						<tr py:if="attr_not_none(object, 'email3')" class="${oddness.odd_or_even()}">
							<td class="line">Email 3</td>
							<td><a href="mailto:${object.email3}">${object.email3}</a></td>
						</tr>
						<tr py:if="attr_not_none(object, 'website')" class="${oddness.odd_or_even()}">
							<td class="line">Website</td>
							<td><a href="${object.website}">${object.website}</a></td>
						</tr>
                                               
					        <tr py:if="attr_not_none(object, 'sip_id')" class="${oddness.odd_or_even()}">
						        <td>Internet Phone (SIP id)</td>
							<td>${object.sip_id}</td>
						</tr>
						<tr py:if="attr_not_none(object, 'skype_id')" class="${oddness.odd_or_even()}">
						     <td class="line">Skype name</td>
						     <td>${object.skype_id}</td>
						</tr>
			                        <tr py:if="attr_not_none(object, 'address')" class="${oddness.odd_or_even()}">
							<td class="line">Address</td>
							<td>${object.address}</td>
						</tr>
			                        <tr py:if="get_freetext_metadata(object, 'postcode')" class="${oddness.odd_or_even()}">
							<td class="line">Postcode</td>
							<td>${get_freetext_metadata(object, 'postcode')}</td>
						</tr>
						<tr  py:if="attr_not_none(object, 'id') and permission_or_owner(object.homeplace,object,'manage_users')" class="${oddness.odd_or_even()}">
						        <td class="line">Membership number</td>
							<td>${object.id}</td>
						</tr>
						<tr  py:if="attr_not_none(object, 'create')" class="${oddness.odd_or_even()}">
						        <td class="line">User created</td>
						        <td>${dateconverter.from_python(object.created)}</td>
						</tr>
						<tr py:if="any_aliases(object) and permission_or_owner(object.homeplace,object,'manage_users')" class="${oddness.odd_or_even()}">	
							<td class="line">Aliases</td>
							<td><span py:for="alias in object.aliases" py:strip="True">${alias.alias_name}, </span></td>
						</tr>
						<tr class="${oddness.odd_or_even()}">
						        <td class="line">Member of The Hub in</td>
						        <td>${locations_string(object)}</td>
						</tr>
	                                        <tr py:if="attr_not_none(object, 'outstanding') and permission_or_owner(object.homeplace,object,'manage_users')" class="${oddness.odd_or_even()}">
						        <td class="line">Outstanding Balance</td>
						        <td><span class="outstanding">${object.homeplace.currency} ${c2s(object.outstanding)}</span></td>
						</tr>
			</table>
		</td> 		
	</tr>

    </table>	        
${load_memberProfile(object)}
</div>
