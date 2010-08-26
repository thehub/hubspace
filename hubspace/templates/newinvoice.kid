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
from hubspace.utilities.i18n import hubspace_lang_code

formatDate = dateconverter.from_python
formatDate = lambda t: t.strftime("%b %-d %Y")
formatDateTime = lambda t: t.strftime("%b %-d %Y %l:%M%P")
dtc = DateTimeConverter("%B %Y").from_python

# rusages_cost_and_tax attribute is recently added so if this is not calculated we need to fall back to use older mechanisms

def getResourceUsageCost(invoice, ivd, resource):
    rusages = ivd[0][resource]
    if invoice.rusages_cost_and_tax:
        return c2s(sum(invoice.rusages_cost_and_tax[ru.id][0] for ru in rusages))
    return c2s(sum_resource_costs(rusages))

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

def sumUsageCosts(invoice, ivd):
    rusages = chain(*ivd[0].values())
    if invoice.rusages_cost_and_tax:
        return c2s(sum(invoice.rusages_cost_and_tax[ru.id][0] for ru in rusages))
    return c2s(sum_resource_costs(rusages))

nl2br = lambda s: s.replace("\n","<br/>")

lang = lambda invoice: hubspace_lang_code(invoice.location)
?>

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" xml:lang="${lang(invoice)}" lang="${lang(invoice)}">

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
</style>

<body>

<div id="headerContent">
<h3>The Hub ${invoice.location.name} </h3><br/>
</div>

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
?>

<img src="${invoice.location.imageFilename('invlogo')}"/>

<table border="0" align="center" width="100%">
<tr>
    <td align="left" width="25%">
        <p>
        <c py:if="show_display_name" py:strip="True"><strong> ${invoice.user.display_name}</strong><br/> </c>
        <c>Membership No.</c> ${invoice.user.id} <br/>
        <c py:if="company_name" py:strip="True"><strong> ${company_name}</strong><br/> </c>
        <c py:strip="True" py:if="invoice.user.bill_to_profile"> ${nl2br(invoice.user.address_with_postcode)} </c>
        <address py:if="not invoice.user.bill_to_profile" py:strip="True">
            <c py:for="line in invoice.user.billingaddress.split('\n')">${line}<br/></c>
        </address>

        <c py:strip="True" py:if="invoice.user.bill_company_no and not invoice.user.bill_to_profile"><c>Company No.</c>${invoice.user.bill_company_no}<br/></c>
        <c py:strip="True" py:if="not invoice.user.billto and invoice.user.bill_vat_no and not invoice.user.bill_to_profile"><c>VAT</c> ${invoice.user.bill_vat_no}</c>
        <c py:strip="True" py:if="invoice.user.billto and invoice.user.billto.bill_vat_no"><br/><c>VAT</c> ${invoice.user.billto.bill_vat_no}</c>
        </p>
    </td>
    <td width="50%">
    </td>
    <td>
        <strong>Invoice details</strong>
        <table cellpadding="2">
        <tr>
            <td width="30%">Number </td>
            <td width="70%"> ${invoice.number}</td>
        </tr>
        <tr>
            <td>Date</td>
            <td>${formatDate(invoice.sent or datetime.datetime.now())}</td>  
        </tr>
        <tr>
            <td>Period</td>
            <td>${formatDate(invoice.start)} to ${formatDate(invoice.end_time)}</td>
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

<h2>Summary of usage</h2>

<div width="80%" py:for="user, ivd in invoice_data">

    <h3 py:if="show_display_name and multiuser_invoice" py:strip="True">${user.display_name}</h3>

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
            ${getResourceUsageCost(invoice, ivd, resource)} <br/>
            <small>
                <span py:if="invoice.vat_included"> <em>Inclusive of VAT </em><em>(${getResourceVat(invoice, resource)} %) : </em> </span>
                <span py:if="not invoice.vat_included"> <em>Exclusive of VAT </em><em>(${getResourceVat(invoice, resource)} %): </em> </span>
                (${invoice.location.currency} ${sum_tax_for_usages(invoice, rusages)})
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
            ${getRUsageCost(invoice, rusage)}<br/>
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
        <td align="right">${sumUsageCosts(invoice, ivd)} </td>
    </tr>
    </table>

</div>

<br/>
<h3>Invoice Total</h3>
<table width="100%" border="0.1" style="padding: 0.2em;">
<thead style="background: #C0C0C0;">
<tr>
    <td>Description</td>
    <td align="right">Amount ${invoice.location.currency}</td>
</tr>
</thead>
<tr>
<td>Excluding VAT</td>
<td align="right">${invoice_total(invoice, exclude_tax=True)} </td>
</tr>
<tr>
<td>VAT</td>
<td align="right">${c2s(invoice.total_tax)} </td>
</tr>
<tr>
<td align="left"><strong>Total</strong></td>
<td align="right">${invoice_total(invoice)} </td>
</tr>
</table>

<?python
import itertools
c = itertools.count(1)
?>

<br/>

<h2>Usage details</h2>

<table width="100%" border="0.1" style="background: #eee; padding: 0.2em;"  repeat="1">
<tbody>
<thead style="background: #C0C0C0;">
<tr>
    <td valign="middle" width="5%">Sr. No.</td>
    <td py:if="multiuser_invoice" py:strip="True">Member</td>
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
    <td py:if="multiuser_invoice" py:strip="True">${rusage.user.display_name}</td>
    <td>${rusage.resource_name} <div py:if="rusage.cancelled and not rusage.refund"><em>(Cancelled)</em></div>
                                <div py:if="rusage.refund"><em>(Refund)</em></div>
        <div py:if="rusage.meeting_name"><em>${rusage.meeting_name}</em></div></td>
    <td>${rusage.resource.time_based and "-" or rusage.quantity}</td>
    <td py:if="rusage.resource.time_based">${formatDateTime(rusage.start)} - <br/> ${formatDateTime(rusage.end_time)}</td>
    <td py:if="not rusage.resource.time_based">${rusage.resource.type == 'tariff' and dtc(rusage.start) or formatDateTime(rusage.start)}</td>
    <td align="right">${getRUsageCost(invoice, rusage)} </td>
</tr>
<tr>
    <td></td>
    <td py:if="multiuser_invoice"></td>
    <td></td>
    <td></td>
    <td><strong>VAT</strong></td>
    <td align="right">${c2s(invoice.total_tax)}</td>
</tr>
<tr bgcolor="lightblue">
    <td></td>
    <td py:if="multiuser_invoice"></td>
    <td></td>
    <td></td>
    <td><strong>Total</strong></td>
    <td align="right">${invoice_total(invoice)}</td>
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
  ${invoice.location.bank}
  <br />
  <c py:if="invoice.location.account_no" py:strip="True"><c>Account Number</c> ${invoice.location.account_no} <br/></c>
  <c py:strip="True" py:if="invoice.location.sort_code"><br /><c>Sort Code</c> <c py:strip="True">${invoice.location.sort_code} <br/></c></c>
  <c py:if="invoice.location.swift_no" py:strip="True"><c>Swift Code</c> ${invoice.location.swift_no} <br/></c>
  <c py:if="invoice.location.iban_no" py:strip="True"><c>IBAN</c> ${invoice.location.iban_no} <br/></c>
  <c py:if="invoice.location.vat_no" py:strip="True"><c>VAT Number</c> ${invoice.location.vat_no} <br/></c>
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
