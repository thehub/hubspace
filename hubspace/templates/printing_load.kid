<?python
from hubspace.utilities.permissions import locations, is_host
from hubspace.utilities.uiutils import select_home_hub
from hubspace.controllers import get_place, permission_or_owner
from hubspace.templates.locationAdmin import loc_admin
?>

<div id="printingContent" class="pane" xmlns:py="http://purl.org/kid/ns#" py:strip="True">    
        <h1>Print Accounting</h1>
         <form id="print_accounting_form">
         Location: <select id="select_admin_location" name="location"><option py:for="location in locations('manage_resources')" py:attrs="select_home_hub(location)" value="${location.id}">${location.name}</option></select>
                <br />
              Please specify printer log file:
              <input type="file" name="datafile" size="20" />
                <br />
          <input type="button" id="print_accounting" value="Upload Print log"/>
          <div id="upload_print_status">
          <!-- check for passing location id and other details like filename etc -->
        </div>
        </form>
</div>
