<?python
from hubspace.utilities.uiutils import oddOrEven, attr_not_none 
from hubspace.utilities.dicts import AttrDict
from hubspace.templates.memberProfile import load_memberProfile
from hubspace.templates.memberDescription import load_memberDescription
from hubspace.templates.memberCommunities import load_memberCommunities
from hubspace.templates.memberRFID import load_memberRFID
from hubspace.templates.memberServices import load_memberServices
from hubspace.templates.tariffHistory import load_tariffHistory
from hubspace.templates.bristolData import load_bristolData
from hubspace.templates.notes import show_notes
from hubspace.templates.relationshipStatus import load_relationship_status
from hubspace.model import Location
from hubspace.utilities.permissions import pip,gip,is_owner, permission_or_owner, user_locations

from turbogears import identity
oddness = oddOrEven()

def locations(object):
    locations = []
    for group in object.groups:
            if group.place not in locations and group.place:
                locations.append(group.place)
    return locations

def current_loc(loc, location):
    if location == loc:
       return {'selected':'selected'}
    return {}
    

?>

<div id="profileContent" class="pane" xmlns:py="http://purl.org/kid/ns#" py:strip="True">
                <div py:def="tariff_bookings(location, object)" class="dataBox">
			<div py:if='permission_or_owner(location, object, "manage_users")' class="dataBoxHeader"><a py:if='permission_or_owner(location, None, "manage_users")' class="modify" id="tariffHistory-${object.id}Edit">edit</a><a class="title" id="link_tariffHistory-${location.id}"><h2>Membership history</h2></a></div>  
			<div class="dataBoxContent">
                               <select id="tariff_location_select-${object.id}">
                                   <option py:for="loc in locations(object)" py:attrs="current_loc(loc, location)" value="${loc.id}">
                                      ${loc.name}  
                                   </option>
                               </select>
                                <div id="tariffHistory-${object.id}">
                                      ${load_tariffHistory(object, location)}
				</div>
			</div>
		</div>
  <div py:def="load_profile(object)" py:strip="True">
           <a py:if='permission_or_owner(object.homeplace, object,"manage_users")' id="memberProfile_${object.id}Edit"  class="modify memberProfileEdit">edit</a>
           <div id="memberProfile_${object.id}" class="memberProfile">
		${load_memberProfile(object)}         
       	   </div>
           <div class="dataBox">
		<div class="dataBoxHeader"><a py:if='permission_or_owner(object.homeplace, object,"manage_users")' class="modify" id="memberDescription_${object.id}Edit">edit</a><a class="title" id="link_memberDesc"><h2>About me</h2></a></div>
	        <div class="dataBoxContent">
		    <div class="dataTextBox data" id="memberDescription_${object.id}">
                       ${load_memberDescription(object)}
                    </div>
                </div>	
	   </div>
  	   <div class="dataBox" py:if='permission_or_owner(user_locations(object, ["member"]), None, "manage_users")'>
                <div class="dataBoxHeader">
                     <a py:attrs="object.rfid and {'style':'display:none;'} or {'style':'display:block;'}" class='modify' id="addCard_${object.id}">add card</a>
                     <a class="title"><h2>Card Registration</h2></a>
                </div>
                <div class="dataBoxContent" id="cardRegistration_${object.id}">
		    <div class="dataTextBox data" id="memberRFID_${object.id}">
                                  ${load_memberRFID(object)}
                    </div>
                </div>
           </div>
  	   <div class="dataBox" py:if='permission_or_owner(object.homeplace, None, "manage_users")'>
			<div class="dataBoxHeader">
                             <a class='modify' py:if='permission_or_owner(object.homeplace, None, "manage_users")'  id="relationshipStatus_${object.id}Edit">edit</a>
                             <a class="title" id="relstatus"><h2>Relationship Details</h2></a>
                        </div>
			<div class="dataBoxContent" id="relationshipStatus_${object.id}">
                                  ${load_relationship_status(object)}
			</div>
		</div>
			
		<div class="dataBox" py:if='permission_or_owner(object.homeplace, None, "manage_users")'>
			<div class="dataBoxHeader"><a id="add_note_${object.id}" class="modify">add new note</a><a class="title" id="link_notes"><h2>Relationship History</h2></a></div>
			<div class="dataBoxContent" id="notes_area_${object.id}">
                                  ${show_notes(object)}				
			</div>
		</div>
		<div class="dataBox"  py:if='permission_or_owner(object.homeplace, object, "manage_users")'>
			<div class="dataBoxHeader"><a class='modify' py:if='permission_or_owner(object.homeplace, None, "manage_users")'  id="memberServices_${object.id}Edit">edit</a><a class="title" id="link_services"><h2>Member services</h2></a></div>
            <div class="dataBoxContent" id="memberServices_${object.id}">
		          ${load_memberServices(object)}
			</div>
		</div>
						
		
		<div class="dataBox" py:if="object.homeplace and object.homeplace.name=='Bristol' and identity.current.user.homeplace.name=='Bristol'">
			<div class="dataBoxHeader"><a class='modify' py:if='permission_or_owner(object.homeplace, object, "manage_users")'  id="bristolData_${object.id}Edit">edit</a><a class="title" id="link_services"><h2>Additional information for SVN</h2></a></div>
			<div class="dataBoxContent">
                            <div id="bristolData_${object.id}" class="bristolData">
                               ${load_bristolData(AttrDict(object.bristol_metadata), object)}
                            </div>
			</div>
		</div>
             <div id="tariff_booking_area-${object.id}" py:if='object.homeplace and permission_or_owner(object.homeplace, object, "manage_users")' >
               ${tariff_bookings(object.homeplace, object)}
	     </div>	
	     <div style="position:relative; height:500px;" />
	</div> 
  <c py:if="'action' not in locals()" py:strip="True">   
   ${load_profile(object)}
  </c>
  <c py:if="'action' in locals() and action=='tariff_loc'" py:strip="True">
    ${tariff_bookings(Location.get(location), object)}
  </c>  
</div>
			
