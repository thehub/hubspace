<?python
from hubspace.utilities.uiutils import oddOrEven, c2s, now, unsent_for_user
odd_or_even = oddOrEven().odd_or_even
from datetime import datetime, timedelta
from hubspace.validators import dateconverter
from hubspace.model import Invoice, Location
from sqlobject import AND
from hubspace.controllers import display_resource_table, get_collected_invoice_data, permission_or_owner
import calendar


def get_earliest(user):
    """no invoice open - start date == earliest uninvoiced resource 
    if there is an invoice created and not sent for the user start date same as invoice start date
    """
    unsent_invoice =  unsent_for_user(user) 
    if unsent_invoice:
        return unsent_invoice.start
    invoice_data=get_collected_invoice_data(user, None)[0]
    earliest = None
    for user in invoice_data:
       resources = invoice_data[user][0]
       for usages in resources.values():
          for usage in usages:
              if not earliest:
                  earliest = usage.start
              else:
                  earliest = min(earliest, usage.start)
    if not earliest:
       earliest = now(user.homeplace)
    return min(earliest, now(user.homeplace))
 
def get_latest(user):
    """end date == end of previous calendar month to now
    if end date - start date < 1 month => enddate=now
    if there is an invoice created and not sent end date same as invoice end date
    """
    unsent_invoice =  unsent_for_user(user)
    if unsent_invoice:
        return unsent_invoice.end_time

    start = get_earliest(user)
    right_now = now(user.homeplace)
    month = right_now.month-1
    year = right_now.year
    if month == 0:
        year = year-1
        month = 12
    end = datetime(year, month, calendar.monthrange(year, month)[1])
    if (end - start) > timedelta(days=end.day):
        return end
    else:
        return right_now

   
def resources():
    resources = []
    for location in Location.select():
        if permission_or_owner(location, None, "manage_resources"):
            for resource in location.resources:
                if resource not in resources and resource.type!='tariff' and resource.active:
                    resources.append(resource)
    return resources

def user_billed_for(user):
    billed = [u for u in user.billed_for]
    if user.billto==None and user not in billed:
        billed.append(user)
    return billed

def billed_by_someone(user):
    if len(user_billed_for(user))<1:
        return False
    return True

def billto(user):
    if user.billto:
        return user.billto
    return user
?>

<c xmlns:py="http://purl.org/kid/ns#" py:strip="True">
<c py:def="display_invoice(user=None, invoice=None)" py:strip="True">
    <div py:if='not invoice'>
           <h2>Uninvoiced</h2>
      <c py:strip="True" py:if="not billed_by_someone(user)">
          <div id="bill_redirect">
              <a id="redirect_billed_to" class="${billto(user).id}" href="#" py:content="user.display_name +' is currently billed to ' + billto(user).display_name" />
          </div>
      </c>
    
      <c py:strip="True" py:if="billed_by_someone(user)">
        From <a id="display_create_invoice_start_${user.id}" class="date_select">${dateconverter.from_python(get_earliest(user))} <img src="/static/images/booking_down.png" /></a> to <a id="display_create_invoice_end_${user.id}" class="date_select">${dateconverter.from_python(get_latest(user))} <img src="/static/images/booking_down.png" /></a>
        <a py:if="permission_or_owner(list(Location.select()), None, 'manage_invoices')" id="create_invoice_${user.id}" class="create_invoice">Create Invoice</a>
        <div style="color:#FF0000;display:none;" id="${user.id}_cannot_create" py:if='not invoice and unsent_for_user(user)'>You must send existing invoices before creating new ones</div>
    
        <form id="${user.id}_change_create_invoice_dates">
        <input type="hidden" name="userid" value="${user.id}" />
        <input id="create_invoice_start_${user.id}" name="start" type="text" class="invisible_input" style="top:-30px;margin-left:30px;position:relative;" value="${dateconverter.from_python(get_earliest(user))}"/> 
           <script type="text/javascript">
              var start_date_input = jq('#create_invoice_start_${user.id}');
              var start_date_trigger = jq('#display_create_invoice_start_${user.id}');
              start_date_input.datepicker({onSelect:function(datetext){change_rusages_date('start', datetext)}});
              start_date_trigger.click(function() {  
                   start_date_input.datepicker('show');
                   start_date_input.blur();
              });
	   </script>
           <input id="create_invoice_end_${user.id}" name="end_time" type="text" class="invisible_input" style="top:-30px;margin-left:145px;position:relative;" value="${dateconverter.from_python(get_latest(user))}"/> 
           <script type="text/javascript">
              var end_date_input = jq('#create_invoice_end_${user.id}');
              var end_date_trigger = jq('#display_create_invoice_end_${user.id}');
              end_date_input.datepicker({onSelect:function(datetext){change_rusages_date('end', datetext)}});
              end_date_trigger.click(function() {  
                   end_date_input.datepicker('show');
                   end_date_input.blur();
              });
	   </script>
       </form>
     </c>
       <div id="rusage_area_${user.id}">
           ${XML(display_resource_table(user=user, invoice=invoice, earliest=get_earliest(user), latest=get_latest(user)))}
       </div>
     
     <div py:if="permission_or_owner(user.homeplace, None, 'manage_invoices') and user.billto in [None, user]" id="${user.id}_add_rusage">
Add Resource Usage:<form id="${user.id}_add_rusage_form" class="add_rusage_form">
                       <select name="resource_id" id="${user.id}_resource">
                            <option disabled="disabled" selected="selected" value="0">choose a resource...</option>
                            <option py:for="resource in resources()" value="${resource.id}">${resource.name}</option>
                       </select> 
                       <div id="${user.id}_resource_form"></div>           
                   </form>
     </div>
   </div>
   <div py:if="invoice">
     <h2>Invoice ${invoice.number}</h2>
    ${XML(display_resource_table(user=user, invoice=invoice, earliest=get_earliest(user), latest=get_latest(user)))}
   </div>
  
</c>
${display_invoice(user=user, invoice=invoice)}
</c>

