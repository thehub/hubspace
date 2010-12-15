<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python

"""
invoice_data

[ 
    ( user, ( {resource: rusages,}, {resource: quantity}),
    ..       
]

"""
import datetime
import cherrypy
from hubspace.controllers import get_collected_invoice_data
from hubspace.controllers import show_quantity_or_duration, sum_resource_costs
from hubspace.invoice import calc_tax
from hubspace.utilities.uiutils import c2s
from hubspace.validators import dateconverter
from turbogears.validators import DateTimeConverter

formatDate = dateconverter.from_python
formatDate = lambda t: t.strftime("%-d/%m/%Y")
formatDateTime = lambda t: t.strftime("%-d/%m/%Y %R")
dtc = DateTimeConverter("%B %Y").from_python

def getResourceUsageCost(ivd, resource):
    rusages = ivd[0][resource]
    return c2s(sum_resource_costs(rusages))

def getRusageCost(rusage):
    return c2s(rusage.effectivecost)
    
def getRUsageCost(invoice, rusage):
    if invoice.rusages_cost_and_tax: 
        cost = invoice.rusages_cost_and_tax[rusage.id][0]
    else:
        cost = rusage.effectivecost
    return c2s(cost)

def getRUsageTax(invoice, rusage):
    if invoice.rusages_cost_and_tax: 
        tax = invoice.rusages_cost_and_tax[rusage.id][1]
    else:
        tax = getResourceVat(invoice, rusage.resource)
    return c2s(tax)

def getResourceVat(invoice, resource):
    return invoice.resource_tax_dict[resource.id][1]

def getResourceVATAmount(invoice, resource):
    return c2s(invoice.resource_tax_dict[resource.id][0])

def getDueDate(invoice):
    sent = invoice.sent or datetime.datetime.now()
    due = sent + datetime.timedelta(invoice.location.invoice_duedate)
    return formatDate(due)

def sum_tax_for_usages(invoice, rusages):
    if invoice.rusages_cost_and_tax: 
        return sum(invoice.rusages_cost_and_tax[ru.id][1] for ru in rusages)
    return getResourceVATAmount(invoice, rusages[0].resource)

def invoice_total(invoice, exclude_tax=False):
    total = invoice.amount
    if exclude_tax:
        total -= invoice.total_tax
    return c2s(total)


from itertools import chain

def sumUsageCosts(ivd):
    return c2s(sum_resource_costs(chain(*ivd[0].values())))

nl2br = lambda s: s.replace("\n","<br/>")

def lang():
    return cherrypy.session.get('locale', 'en')
?>

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" xml:lang="${lang()}" lang="${lang()}">

<style>
/* Normal */
@font-face {
   font-family: Deja;
   src: url(hubspace/static/fonts/dejavu-fonts-ttf-2.31/ttf/DejaVuSans.ttf);
}

/* Bold */
@font-face {
   font-family: Deja;
   src: url(hubspace/static/fonts/dejavu-fonts-ttf-2.31/ttf/DejaVuSans-Bold.ttf);
   font-weight: bold;
}

/* Italic */
@font-face {
   font-family: Deja;
   src: url(hubspace/static/fonts/dejavu-fonts-ttf-2.31/ttf/DejaVuSans-Oblique.ttf);
   font-style: italic;
}

/* Bold and italic */
@font-face {
   font-family: Deja;
   src: url(hubspace/static/fonts/dejavu-fonts-ttf-2.31/ttf/DejaVuSans-BoldOblique.ttf);
   font-weight: bold;
   font-style: italic;
}

@page {
  size: a4;
  margin: 1cm;
  margin-bottom: 3cm;
  @frame footer {
    -pdf-frame-content: footerContent;
    bottom: 2cm;
    margin-left: 1cm;
    margin-right: 1cm;
    height: 1cm;
  }
@frame nextpage {
  -pdf-frame-content: nextpage;
  }
}
.freetext {
    font-family: Deja; 
    border:.1px solid black;
    padding: 1;
    }
body { font-family: Deja; }
h1 {font-size:300%; color: grey;}
h2 {font-size:200%; color: grey;}
h3 {font-size:150%; color: grey;}
</style>

<body>

<?python
show_display_name = True
if invoice.user.billing_mode == 1:
    company_name = invoice.user.bill_to_company
    if company_name:
        show_display_name = False
else:
    company_name = invoice.user.organisation

invoice_data = get_collected_invoice_data(invoice=invoice)[0].items()
vat_included = invoice.sent and invoice.vat_included or invoice.location.vat_included
multiuser_invoice = (len(invoice_data) > 1)
negative_total = invoice.amount < 0
?>


<!-- <div id="headerContent">
<h3>The Hub ${invoice.location.name} </h3><br/>
</div>
<img src="${invoice.location.imageFilename('invlogo')}"/>
-->
<div id="billerContent">
    <p>
    <strong><c py:strip="True" py:if="invoice.location.company_name"> ${invoice.location.company_name} </c> <br /></strong>
    <c py:strip="True" py:if="invoice.location.company_no"><c>Company Number</c>: ${invoice.location.company_no} </c> 
    <c py:if="invoice.location.vat_no" py:strip="True"><c>VAT Number</c>: ${invoice.location.vat_no} <br/></c>
    <c py:strip="True" py:if="invoice.location.billing_address">${nl2br(invoice.location.billing_address)} <br /></c>
    <a href="invoice.location.url">${invoice.location.url}</a> <br /><br />
    <strong><c>Bank Details </c> <br /></strong>
    <c py:strip="True" py:if="invoice.location.bank">${invoice.location.bank}</c><br />
    <c py:if="invoice.location.account_no" py:strip="True"><c>Account Number</c>: ${invoice.location.account_no} </c><br />
    <c py:strip="True" py:if="invoice.location.sort_code"><c>Sort Code</c>: <c py:strip="True">${invoice.location.sort_code} <br/></c></c>
    <c py:if="invoice.location.swift_no" py:strip="True"><c>Swift Code</c>: ${invoice.location.swift_no} <br/></c>
    <c py:if="invoice.location.iban_no" py:strip="True"><c>IBAN</c>: ${invoice.location.iban_no}</c>
    </p>
</div>
<table border="0" align="center" width="100%">
<tr>
    <td valign="bottom" align="left" width="25%">
        <p>
        <strong> ${invoice.user.display_name}<br/> </strong>
        <c>Membership No.</c> ${invoice.user.id} <br/>
        </p>
        <p>
        <strong> ${company_name} <br/> </strong>

        <c py:strip="True" py:if="invoice.user.bill_to_profile"> ${nl2br(invoice.user.address_with_postcode)} </c>
        <address py:if="not invoice.user.bill_to_profile" py:strip="True">
            <c py:for="line in invoice.user.billingaddress.split('\n')">${line}<br/></c>
        </address>

        <c py:strip="True" py:if="invoice.user.bill_company_no and not invoice.user.bill_to_profile"><c>Company No. </c> ${invoice.user.bill_company_no}<br/></c>
        <c py:strip="True" py:if="not invoice.user.billto and invoice.user.bill_vat_no and not invoice.user.bill_to_profile"><c>VAT No.</c> ${invoice.user.bill_vat_no}</c>
        <c py:strip="True" py:if="invoice.user.billto and invoice.user.billto.bill_vat_no"><br/><c>VAT No.</c> ${invoice.user.billto.bill_vat_no}</c>
        <?python
            purchaseorders_string = ', '.join(invoice.ponumbers or [])
        ?>
        <c py:strip="True" py:if="purchaseorders_string"><br/><c>Purchase Order No: </c>${purchaseorders_string}</c>
        </p>
    </td>
    <td width="40%">
    </td>
    <td>
        <table cellpadding="1">
        <tr>
            <td colspan="2">
            <h2 py:if="negative_total">CREDIT NOTE</h2>
            <h1 py:if="not negative_total">INVOICE</h1>
            </td>
        </tr>
        <tr>
            <td width="30%">Number </td>
            <td width="70%"> ${invoice.number or 'unnumbered'}</td>
        </tr>
        <tr>
            <td>Date</td>
            <td>${formatDate(invoice.sent or datetime.datetime.now())}</td>  
        </tr>
        <tr>
            <td>Period</td>
            <td>${formatDate(invoice.start)} to ${formatDate(invoice.end_time)}</td>
        </tr>
        <tr>
            <td>Last date of period</td>
            <td>${formatDate(invoice.created)}</td>            
        </tr>
        <tr py:if="invoice.location.invoice_duedate">
            <td>Due Date</td>
            <td>${getDueDate(invoice)} </td>
        </tr>
        </table>
    </td>
</tr>
</table>

<p class="freetext" py:if="freetext1">
${XML(nl2br(freetext1))}
</p>

<h3>Summary of usage</h3>

<div width="80%" py:for="user, ivd in invoice_data">

    <h3>${user.display_name}</h3>

    <table width="100%" border="0.1" style="padding: 0.2em;">
    <thead style="background: #C0C0C0;">
    <tr>
        <td>Description</td>
        <td align="right"><c>Amount</c> ${invoice.location.currency}</td>
    </tr>
    </thead>
    <div py:for="resource, rusages in ivd[0].items()">
    <div py:if="resource.type != 'custom'">
    <tr width="80%" border="0.20">
        <td>
            <strong> ${ivd[0][resource][0].resource_name} </strong> <br/>
        </td>
        <td align="right"> 
            ${getResourceUsageCost(ivd, resource)} <br/>
            <small>
                <span py:if="invoice.vat_included"> <em>Inclusive of VAT </em><em>(${getResourceVat(invoice, resource)} %) : </em> </span>
                <span py:if="not invoice.vat_included"> <em>Exclusive of VAT </em><em>(${getResourceVat(invoice, resource)} %): </em> </span>
                (${invoice.location.currency} ${getResourceVATAmount(invoice, resource)})
            </small>
        </td>
    </tr>
    </div>
    <div py:if="resource.type == 'custom'">
    <tr py:for="rusage in rusages">
        <td>
            <strong> ${rusage.resource_name}</strong><br/>
            <!-- <strong> ${rusage.resource_name}</strong>  X ${show_quantity_or_duration(rusage)} <br/> -->
        </td>
        <td align="right"> 
            ${getRusageCost(rusage)}<br/>
            <small>
                <span py:if="invoice.vat_included"> <em>Inclusive of VAT </em><em>(${getResourceVat(invoice, resource)} %) : </em> </span>
                <span py:if="not invoice.vat_included"> <em>Exclusive of VAT </em><em>(${getResourceVat(invoice, resource)} %): </em> </span>
                (${invoice.location.currency} ${getRUsageTax(invoice, rusage)})
            </small>
        </td>
    </tr>
    </div>
    </div>
    <tr>
        <td><strong>Sub Total</strong></td>
        <td align="right">${sumUsageCosts(ivd)} </td>
    </tr>
    </table>

</div>

<br/>
<h3 py:if="negative_total">Total</h3>
<h3 py:if="not negative_total">Invoice Total</h3>
<table width="100%" border="0.1" style="padding: 0.2em;">
<thead style="background: #C0C0C0;">
<tr>
    <td>Description</td>
    <td align="right"><c>Amount</c> ${invoice.location.currency}</td>
</tr>
</thead>
<tr>
<td>Excluding VAT</td>
<td align="right">${c2s(invoice.amount - invoice.total_tax)} </td>
</tr>
<tr>
<td>VAT</td>
<td align="right">${c2s(invoice.total_tax)} </td>
</tr>
<tr>
<td align="left"><strong>Total</strong></td>
<td align="right">${c2s(invoice.amount)} </td>
</tr>
</table>

<?python
import itertools
c = itertools.count(1)
?>

<br/>

<h3>Usage details</h3>

<table width="100%" border="0.1" style="background: #eee; padding: 0.2em;"  repeat="1">
<tbody>
<thead style="background: #C0C0C0;">
<tr>
    <td valign="middle" width="5%">Sr. No.</td>
    <td>Member</td>
    <td>Description</td>
    <td width="10%">Quantity</td>
    <td>Time</td>
    <td align="right"><c>Amount</c> ${invoice.location.currency}</td>
</tr>
</thead>

<?python
sorter = lambda rusage: rusage.start
rusages = sorted(invoice.rusages, key=sorter)
?>

<tr py:for="rusage in rusages">
    <td>${c.next()}</td>
    <td>${rusage.user.display_name}</td>
    <td>${rusage.resource_name} <div py:if="rusage.cancelled and not rusage.refund"><em>(Cancelled)</em></div>
                                <div py:if="rusage.refund"><em>(Refund)</em></div>
        <div py:if="rusage.meeting_name"><em>${rusage.meeting_name}</em></div></td>
    <td>${rusage.resource.time_based and "-" or rusage.quantity}</td>
    <td py:if="rusage.resource.time_based">${formatDateTime(rusage.start)} - <br/> ${formatDateTime(rusage.end_time)}</td>
    <td py:if="not rusage.resource.time_based">${rusage.resource.type == 'tariff' and dtc(rusage.start) or formatDateTime(rusage.start)}</td>
    <td align="right">${getRusageCost(rusage)} </td>
</tr>
<tr>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td><strong>VAT</strong></td>
    <td align="right">${c2s(invoice.total_tax)}</td>
</tr>
<tr bgcolor="lightblue">
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td><strong>Total</strong></td>
    <td align="right">${c2s(invoice.amount)}</td>
</tr>
</tbody>
</table>

<br/>
<br/>

<table>
<tr py:if="freetext2">
<td>
<p class="freetext">
${XML(nl2br(freetext2))}
</p>
</td>
</tr>
<tr><td></td></tr>
<tr>
<td align="left">
<!--
  <c py:strip="True" py:if="invoice.location.sort_code"><br />Sort Code <c py:strip="True">${invoice.location.sort_code} <br/></c></c>
  <c py:if="invoice.location.swift_no" py:strip="True">Swift Code ${invoice.location.swift_no} <br/></c>
  <c py:if="invoice.location.iban_no" py:strip="True">IBAN ${invoice.location.iban_no} <br/></c>
-->
  <c py:if="invoice.location.payment_terms" py:strip="True"><c>Payment Terms</c>: ${invoice.location.payment_terms}</c>
</td>
</tr>
</table>
<div id="footerContent">
    <p align="center">
    <small>${invoice.location.billing_address} <c py:strip="True" py:if="invoice.location.company_no">| ${invoice.location.company_no} </c> 
    | <a href="invoice.location.url">${invoice.location.url}</a> | ${invoice.location.telephone}</small>
    </p>
</div>
</body>
</html>
