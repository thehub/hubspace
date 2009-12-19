<?python
from hubspace.utilities.uiutils import oddOrEven,c2s
from hubspace.controllers import Invoice, permission_or_owner
from hubspace.templates.invoicesnippet import display_invoice
odd_or_even = oddOrEven().odd_or_even
from hubspace.templates.billingDetails import load_billingDetails
from hubspace.validators import dateconverter
import urllib

def billingEdit(object):
    if permission_or_owner(object.homeplace, object, "manage_invoices"): 
        if not object.billto or object.billto.id==object.id:
             return True
    if permission_or_owner(object.homeplace, None,"manage_invoices"):
        return True
    return False

def genInvoiceName(invoice):
    invoice_no = invoice.number
    display_name = invoice.user.display_name.replace(" ","_")
    try:
        sent_time = invoice.sent.strftime('%Y%m%d')
    except:
        sent_time = "00000000"
    return "%(display_name)s-%(invoice_no)s-%(sent_time)s" % locals()

?>
<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">
    <div py:strip="True" py:def="load_billing(object)">
        <h1 py:content="_(u'Billing and Invoicing - %(name)s' % {'name':object.display_name})">Billing and Invoicing for name</h1> 
	<div class="dataBox"> <div class="dataBoxHeader"><a py:if='billingEdit(object)'  class="modify" id="billingDetails_${object.id}Edit">edit</a><a class="title" id="billingDetailsLink"><h2>Billing Details</h2></a></div>
		<div class="dataBoxContent" id="billingDetails_${object.id}">
			 ${load_billingDetails(object)} 
		</div>
	</div>
        <div id="${object.id}_uninvoiced">		
 	${display_invoice(object)}
        </div>
    <h2>Invoice History</h2>
    <div class="dataBox">

		<div class="dataBoxHeader"><a class="title" id="link_invoice_history"><h2>Invoice History</h2></a></div>
		<div class="dataBoxContent">
			<table class="detailTable data invoice_history" cellpadding="" cellspacing="0">
				<tr class="header">
				        <td>Invoice Ref</td>
				        <td>Date sent</td>
					<td>Amount <em>(Including VAT)</em></td>
					<td>View</td>
				</tr>
				<tr py:for='invoice in Invoice.selectBy(user=object.id).orderBy("sent")' class="$odd_or_even()">
					<td>${invoice.number}</td>
					<td py:if="invoice.sent" class="resent_${object.id}">${dateconverter.from_python(invoice.sent)}&nbsp;&nbsp;<a py:if='permission_or_owner(object.homeplace, None, "manage_invoices")' id="resent_invoice_${object.id}" class="${invoice.id}">re-send invoice</a></td> 
                                        <td py:if="not invoice.sent" class="unsent" id="unsent_${object.id}"><c py:if='not permission_or_owner(object.homeplace, None, "manage_invoices")' py:strip="True">unsent</c><a py:if='permission_or_owner(object.homeplace, None, "manage_invoices")' id="unsent_invoice_${object.id}" class="${invoice.id}">send invoice</a></td>
					<td>${c2s(invoice.amount)+ " "+ invoice.location.currency}</td>
					<td>
                                           <a py:if="invoice.sent or not permission_or_owner(object.homeplace, None, 'manage_invoices')" class="view_invoice" id="invoice_${invoice.id}">As HTML</a>
                                           <a class="view_invoice" id="invoice_${invoice.id}" py:if="not invoice.sent and permission_or_owner(object.homeplace, None, 'manage_invoices')">Modify</a>&nbsp;&nbsp;
                                           <a class="remove_invoice" id="removeInvoice_${invoice.id}" py:if="not invoice.sent and permission_or_owner(object.homeplace, None, 'manage_invoices')">Remove</a> &nbsp;&nbsp;
                                           <a href="/pdf_invoice/${invoice.id}/${genInvoiceName(invoice)}.pdf" target="_blank">As PDF</a></td>


				</tr>
			</table>
		</div>
	<div id="invoice_area_${object.id}"></div>
       <div> <a name="send_it"></a><div class="send_invoice" id="send_invoice_${object.id}"></div></div>
	</div>
   </div>
   ${load_billing(object)}
</div>
