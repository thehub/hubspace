<?python
from hubspace.utilities.uiutils import oddOrEven, c2s, now
from hubspace.utilities.permissions import locations, is_host
odd_or_even = oddOrEven().odd_or_even
from turbogears import identity
from hubspace.controllers import permission_or_owner, get_place, listSavedReports
from datetime import datetime
from hubspace.validators import dateconverter

from hubspace.utilities.image_helpers import image_src
from hubspace.model import Resource, resource_types, User

from hubspace.templates.locationProfile import load_locationProfile
def start_this_month(location):
    right_now = now(location)
    return dateconverter.from_python(datetime(right_now.year, right_now.month, 1))

def getResources(location):
    return [("Any", "all")] + [(r.name, r.id) for r in location.resources if r.type != "tariff"]

all_users = [("All", "all")] + [(u.user_name, u.id) for u in User.select()]


res_types = [type for type in resource_types if type not in ['calendar']]

rtype_opts = zip(res_types, res_types)

def makeOptDict(r, typ):
    def_d = dict (user = "All", r_type = "room", r_name = "Any")
    d = dict(value=r[1])
    if r[0] == def_d[typ]: d['selected'] = 'selected'
    return d

?>

<div id="adminContent" py:strip="True" xmlns:py="http://purl.org/kid/ns#" py:layout="'plusMaster.kid'">
    <script py:def="include_js()" src="/static/javascript/plus_admin.js"></script>
    <c py:strip="True" py:def="load_content(location)">
        <div id="admin_location" class="${location.id}" style="display:none;"/>
        <div class="dataBox" py:if='permission_or_owner(location, location, "manage_locations")'>
			<div class="dataBoxHeader"><a class="modify" id="locationProfile-${location.id}Edit">edit</a><a class="title" id="link_locationProfile-${location.id}"><h2>Location Details - ${location.name}</h2></a></div>  
			<div class="dataBoxContent"  id="locationProfile-${location.id}">
                               ${load_locationProfile(location)} 
			</div>
        </div>
        <div class="dataBox" py:if='permission_or_owner(location, location, "manage_locations")'>
            <div class="dataBoxHeader"><a class="title" id="link_locationProfile-${location.id}"><h2>Location Images - ${location.name}</h2></a></div>   
            <div class="dataBoxContent">                       
              <div class="location_image" id="invlogo_${location.id}">  
                <h1>Invoice Image</h1>
                <p>Image of 690px by 130px or equivalent proportions</p>
                <div class="imgwrap">
                   <span id="upload_invlogo" class="replace_image">replace image</span>
                   <img id="invlogo_image${location.id}" src="${image_src(location, 'invlogo', '/static/images/header.gif')}" /> 
                </div>
                <div id="iframe_area${location.id}"></div>
              </div>
              <div class="location_image" id="logo_${location.id}">  
                <h1>Top Bar Image</h1>
                <p>Image of 850px by 87px or equivalent proportions</p>
                <div class="imgwrap">
                   <span id="upload_logo" class="replace_image">replace image</span>
                   <img id="logo_image${location.id}" src="${image_src(location, 'logo', '/static/images/header_bg.gif')}" /> 
                </div>
                <div id="iframe_area${location.id}"></div>
              </div>
              <div class="hompage_image" id="homelogo_${location.id}">  
                <h1>Home Page Image</h1>
                <p>Image of 850px by 113px or equivalent proportions</p>
                <div class="imgwrap">
                   <span id="upload_homelogo" class="replace_image">replace image</span>
                   <img id="homelogo_image${location.id}" src="${image_src(location, 'homelogo', '/static/images/header_bg.gif')}" /> 
                </div>
                <div id="iframe_area${location.id}"></div>

              </div>
	    </div>
        </div>

  	<div class="dataBox">
		<div class="dataBoxHeader">
			<a class="title" id="link_adminStuff"><h2>Import / Export</h2></a>
		</div>
	    <div class="dataBoxContent">
			<table class="detailTable data">
	                        <tr class="odd">
					<td>Upload outstanding invoice data</td>
					<td>
                                             <iframe src="/upload_outstanding_form">
                                             </iframe>
                                       </td>
                                </tr>
				<tr class="even">
					<td>Download member list for Sage</td>
					<td><a href="/sage_user_list/${location.id}/${location.name}_sage_user_list.csv">${location.name} user list</a></td>
				</tr>
				<tr class="odd">
					<td>Download invoice list for Sage</td>
                                        <td>
                                              <div>
                                                    Start date: <a class="date_select" id="display_start_invoice_list-${location.id}">${start_this_month(location)}</a>
                                                    | End date: <a class="date_select" id="display_end_invoice_list-${location.id}">${dateconverter.from_python(now(location))}</a>
                                                    | <a id="listInvoices-${location.id}-${location.name}" class="date_select listInvoices">Download ${location.name} Invoices</a>
<input id="start_invoice_list-${location.id}" name="start" type="text" class="invisible_input" value="${start_this_month(location)}"/>
<input id="end_invoice_list-${location.id}" name="end" type="text" class="invisible_input" value="${dateconverter.from_python(now(location))}"/>
           <script type="text/javascript">
              var sage_invoice_list_dates = function() {
                  var end_date_input = jq('#end_invoice_list-${location.id}');
                  var end_date_trigger = jq('#display_end_invoice_list-${location.id}');
                  end_date_input.datepicker({onSelect:function(datetext){jq('#display_end_invoice_list-${location.id}').html(datetext);}});
                  end_date_trigger.click(function() {  
                      end_date_input.datepicker('show');
                      end_date_input.blur();
                  });
                  var date_input = jq('#start_invoice_list-${location.id}');
                  var date_trigger = jq('#display_start_invoice_list-${location.id}');
                  date_input.datepicker({onSelect:function(datetext){jq('#display_start_invoice_list-${location.id}').html(datetext);}});
                  date_trigger.click(function() {  
                      date_input.datepicker('show');
                      date_input.blur();
                  });
              };
              sage_invoice_list_dates();
	   </script>

                                                </div>
                                        </td>
				</tr>  
			</table>	
	    </div>
     </div>


  	<div class="dataBox" py:if='location in locations()'>
	    <div class="dataBoxHeader"> <a class="title" id="link_adminStuff0"><h2>Messages</h2></a> </div>
	    <div class="dataBoxContent">
            <h1>Translation</h1>
	    <table class="detailTable data">
            <tr>
                <td> Message catalogue file (.po) </td>
                <td><a href="/download_messages.po">Download</a> | <a href="mailto:world.tech.space@the-hub.net"> Send updated translation file </a></td>
                <td align="left"><a target="_blank" href="http://the-hub.pbworks.com/HubSpace%3A-Working-with-message-catalogues">Help</a></td>
            </tr>
            </table>
            <h1>Customization</h1>
            <iframe src ="/static/fe/messagecust.html" width="100%" height="595" scrolling="auto" frameborder="0" style="detailTable data">
              <p>Your browser does not support iframes.</p>
            </iframe>
            </div>
        </div>

</c>
</div>

