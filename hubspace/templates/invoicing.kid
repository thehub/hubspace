<?python
from hubspace.utilities.permissions import locations
from hubspace.utilities.uiutils import select_home_hub, now
from hubspace.controllers import get_place, permission_or_owner
from hubspace.templates.locationAdmin import loc_admin
from hubspace.validators import dateconverter
# for date time  need for calendar
from datetime import datetime, timedelta
from turbogears import identity
?>

<div id="invoicingContent" class="pane" xmlns:py="http://purl.org/kid/ns#" py:strip="True">    
  <div py:def="invoicing_search()">
     <h1>Invoicing Search</h1>
     <form id="invoices_search_form">
     <div>
         <span>Search in Location&nbsp;&nbsp;&nbsp;</span><select id="invoice_search_location" name="location"><option py:for="location in locations('manage_resources')" value="${location.id}" py:attrs="select_home_hub(location)">${location.name}</option></select>
     </div>
     <div>
          <span>for users with non-invoiced items&nbsp;&nbsp;&nbsp;</span>
          <input type="checkbox" name="resource_type-2" checked="checked" value="tariff">Tariffs</input>
          <input type="checkbox" name="resource_type-1" checked="checked" value="resources">Other Resources Usages</input>
     </div>
     <div>
          <span>which finished on or before&nbsp;&nbsp;&nbsp;</span> 
          <a id="display_search_from_date"  class="date_select">${dateconverter.from_python(now(identity.current.user.homeplace))} <img src="/static/images/booking_down.png" /></a>
          <input id="search_from_date" class="invisible_input" name="search_from_date" type="text" value="${dateconverter.from_python(now(identity.current.user.homeplace))}"/>
            <script type="text/javascript">
              var show_calender = function() {
                  var date_input = jq('#search_from_date');
                  var date_trigger = jq('#display_search_from_date');
                  date_input.datepicker({onSelect:function(datetext){jq('#display_search_from_date').html(datetext);}});
                  date_trigger.click(function() {  
                      date_input.datepicker('show');
                      date_input.blur();
                  });
              };
              show_calender();
            </script>

      </div>
      <input type="checkbox" name="include_zero_usage_cost_members" checked="checked"/> Display members with zero usage cost
      <div>
          <br />
          <table>
          <tr>
          <td> <input type="button" value="Generate Invoices" id="gen_invoices" /> </td>
          <td> <input type="button" value="Search (Old way)" id="invoices_search" /></td>
          </tr>
          <tr>
          <td span="2">* Search (Old way) option is deprecated </td>
          </tr>
          </table>
      </div>
      </form>
      <div id="search_results">
      </div>	
    </div>
    ${invoicing_search()}
</div>
