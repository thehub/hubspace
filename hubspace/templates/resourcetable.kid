<?python

from hubspace.utilities.uiutils import oddOrEven, inv_currency, c2s, colspan, unsent_for_user
from hubspace.controllers import show_quantity_or_duration, sum_resource_costs, permission_or_owner
odd_or_even = oddOrEven().odd_or_even
from datetime import datetime
from hubspace.validators import datetimeconverter
format_date = datetimeconverter.from_python
from hubspace.model import Invoice
from turbogears import identity

def vat_inclusive_invoice(invoice, user):
    try:
        invoice = Invoice.get(invoice)
    except:
        invoice = None
    if invoice:
        return invoice.vat_included
    return user.homeplace.vat_included

def vat_exception(rusage, invoice, user):
    if vat_inclusive_invoice(invoice, user) and not rusage.resource.place.vat_included:
       return " <em>(Excluding VAT)</em>"
    if not vat_inclusive_invoice(invoice, user) and rusage.resource.place.vat_included:
       return " <em>(Including VAT)</em>"
    return ""
?>

<c xmlns:py="http://purl.org/kid/ns#"  py:strip="True">
<c py:def="resource_table(invoice_data, user, invoice)" py:strip="True">
     <?python 
     x=0 
     ?>
     <div py:for="theuser, invdata in invoice_data[0].items()" class="dataBox">
       <?python
          cols = int(colspan(user, invoice))
       ?>
        <div class="dataBoxHeader"><a class="title" id="resources"><h2><div>${theuser.display_name}</div>
     
    </h2></a></div>

        <div class="dataBoxContent">
            <table class="detailTable data" id="table_${theuser.id}_${invoice or 0}_${user.id}" cellpadding="" cellspacing="0">
                <tr class="header">
                    <td>Resource</td>
                    <td>Start date</td>
                    <td>End date</td>
                    <td>Quantity / Duration</td>
                    <td>Place</td>
                    <td>Cost <em py:if="vat_inclusive_invoice(invoice, user)">(Including VAT unless stated otherwise)</em><em py:if="not vat_inclusive_invoice(invoice, user)">(Excluding VAT unless stated otherwise)</em></td>
                    <td py:if="unsent_for_user(user) and invoice==None and permission_or_owner(user.homeplace, None, 'manage_invoices')" id="open_invoice" class="${unsent_for_user(user).id}">Add To Open Invoice</td>
                    <td py:if="invoice==None and permission_or_owner(user.homeplace, None, 'manage_invoices')">Delete Resource Usage</td>
                    <td py:if="unsent_for_user(user) and unsent_for_user(user).id==invoice and permission_or_owner(user.homeplace, None, 'manage_invoices')">Remove from Open Invoice</td>
                </tr>
                <tr py:if="not invdata[0]" class="empty_table_warning">
                  <td colspan="${colspan(user, invoice)}">No Resource Usages</td>
                </tr>
                <span py:for='resource in invdata[0]' py:strip='True'>
<?python
rusages = invdata[0][resource]
x+=1
?>
                    <tr py:if="(len(rusages)==1 or resource.type=='custom') and resource.place == identity.current.user.homeplace" py:for="rusage in rusages" class="${odd_or_even()}">
                        <td py:content='rusage.resource_name'>Resource</td>
                        <td py:content='format_date(rusage.start)'>Start</td>
                        <td py:content='format_date(rusage.end_time)'>End</td>
                        <td py:content='show_quantity_or_duration(rusage)'>Quantity</td>
                        <td py:content='rusage.resource.place.name'>Place</td>
                        <td py:if="invoice==None"><div id="cost-${rusage.id}" class="custom_cost">${inv_currency(invoice, user)} ${c2s([rusage.customcost,rusage.cost][rusage.customcost == None])} ${XML(vat_exception(rusage, invoice, user))}</div> &nbsp;<a py:if="permission_or_owner(user.homeplace, None, 'manage_invoices')" id="cost-${rusage.id}Edit" style="cursor:pointer;">change</a></td>
                        <td py:if="invoice!=None">${inv_currency(invoice, user)} ${c2s([rusage.customcost,rusage.cost][rusage.customcost == None])} ${XML(vat_exception(rusage, invoice, user))}</td>
                        <td py:if="unsent_for_user(user) and invoice==None and permission_or_owner(user.homeplace, None, 'manage_invoices')"><a id="rusage-${rusage.id}" class="add_to_invoice">Add to Invoice</a></td>
                        <td py:if="invoice==None and permission_or_owner(user.homeplace, None, 'manage_invoices')"><a id="delrusage-${rusage.id}" class="del_rusage">Delete</a></td>
                        <td py:if="unsent_for_user(user) and unsent_for_user(user).id==invoice and permission_or_owner(user.homeplace, None, 'manage_invoices')"><a id="rusage-${rusage.id}" class="remove_from_invoice">Remove from Invoice</a></td>


                    </tr>
                  <span py:if="len(rusages)>1 and resource.type!='custom' and resource.place == identity.current.user.homeplace" py:strip="True">
                    <tr class="${odd_or_even()}">
                        <td class="composite_rusage" id="${theuser.id}_${invoice or 0}_${resource.id}_${user.id}">${rusages[0].resource_name}<a class="view_sub_usages" id="sub_${theuser.id}_${invoice or 0}_${resource.id}_${user.id}"></a></td>
                        <td py:content='format_date(min([r.start for r in rusages]))'>Start</td>
                        <td py:content='format_date(max([r.end_time for r in rusages]))'>End</td>
                        <td py:content='show_quantity_or_duration(invdata[1][resource])'>Quantity</td>
                        <td py:content='rusages[0].resource.place.name'>Place</td>
                        <td>${inv_currency(invoice, user)} ${c2s(sum_resource_costs(rusages))}  ${XML(vat_exception(rusage, invoice, user))}</td>
                        <td py:if="unsent_for_user(user) and invoice==None and invdata[0] and permission_or_owner(user.homeplace, None, 'manage_invoices')"></td>
                       <td py:if="invoice==None and permission_or_owner(user.homeplace, None, 'manage_invoices')"></td>
                        <td py:if="unsent_for_user(user) and unsent_for_user(user).id==invoice and permission_or_owner(user.homeplace, None, 'manage_invoices')"></td>
                    </tr>
                  </span>
                </span>
                <tr style="display:none">
                      <td py:for="x in range(0, cols-2)">a</td>
                </tr>
            </table>
        </div>
      </div>
    </c>
${resource_table(invoice_data, mainuser, invoice)}
</c>
