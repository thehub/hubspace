<?python
from hubspace.utilities.permissions import locations
from hubspace.utilities.uiutils import select_home_hub, now
from hubspace.controllers import get_place, permission_or_owner
from hubspace.templates.locationAdmin import loc_admin
from turbogears import identity
from hubspace.utilities.users import fields as user_fields

user_columns = user_fields.values()
?>

<div id="managementdataContent" class="pane" xmlns:py="http://purl.org/kid/ns#" py:strip="True">    
    <h1>Management Data</h1>

    <div class="dataBox">
        <div class="dataBoxHeader">
	    <a class="title" id="link_adminStuff"><h2>Export User Data</h2></a>
	</div>
    <div class="dataBoxContent">
        <!-- <table class="detailTable data"> -->
    
     <form id="users_export">
     <div>
         <span>Select Location</span>
         <select name="location">
            <option py:if="identity.has_permission('superuser')" value="all">All</option>
            <option py:for="location in locations()" value="${location.id}" py:attrs="select_home_hub(location)">${location.name}</option>
         </select>
     <i py:if="identity.has_permission('superuser')"> * Selecting "All" location may result in slower report generation</i>

     </div>
     <div>
          <table border="0">
          <tr>
          <td> Select columns to include</td>
          <td> <input type="checkbox" py:for="attr_d in user_columns" name="usercols_selction" py:attrs="attr_d" >${attr_d["label"]}</input> </td>
          </tr>
          <tr>
          <td> Select column to sort by</td>
          <td> <input type="radio" py:for="attr_d in user_columns" name="sortname" value="${attr_d['value']}" 
            py:attrs="attr_d['value'] == 'display_name' and {'checked': '1'} or {}">${attr_d["label"]}</input> </td>
          </tr>
          </table>
     </div>

      <div>
          <br />
          <a href="#" id="users_grid" class="buttonlikelink">View</a>
          <a href="#" class="buttonlikelink" id="users_csv" >Download spreadsheet</a>
      </div>
      </form>

    <br/>

    <table id="flex1"></table>

    </div>
    </div>
</div>
