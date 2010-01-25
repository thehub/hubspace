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
formatDate = lambda t: t.strftime("%b %-d %Y")
formatDateTime = lambda t: t.strftime("%b %-d %Y %l:%M%P")
dtc = DateTimeConverter("%B %Y").from_python

def getResourceUsageCost(ivd, resource):
    rusages = ivd[0][resource]
    return c2s(sum_resource_costs(rusages))

def getRusageCost(rusage):
    return c2s(rusage.effectivecost)

def getResourceVat(invoice, resource):
    return invoice.resource_tax_dict[resource.id][1]

def getResourceVATAmount(invoice, resource):
    return c2s(invoice.resource_tax_dict[resource.id][0])

def getDueDate(invoice):
    sent = invoice.sent or datetime.datetime.now()
    due = sent + datetime.timedelta(invoice.location.invoice_duedate)
    return formatDate(due)

from itertools import chain

def sumUsageCosts(ivd):
    return c2s(sum_resource_costs(chain(*ivd[0].values())))

nl2br = lambda s: s.replace("\n","<br/>")

def lang():
    return cherrypy.session.get('locale', 'en')
?>

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" xml:lang="${lang()}" lang="${lang()}">

<style>
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
    font-family: Helvetica; 
    white-space: pre;
    border:.1px solid black;
    padding: 1;
    }
</style>

<body>

<div id="headerContent">
<h3>The Hub ${invoice.location.name} </h3><br/>
</div>
<img src="${invoice.location.imageFilename('invlogo')}"/>

<table border="0" align="center" width="100%">
<tr>
    <td align="left" width="25%">
        <strong>${invoice.user.bill_to_profile and invoice.user.organisation or invoice.user.bill_to_company}</strong>
        <p>
        ${invoice.user.display_name}<br/>
        Membership No. ${invoice.user.id} <br/>
        </p>
        <c py:strip="True" py:if="invoice.user.bill_to_profile"> ${nl2br(invoice.user.address)} </c>
        <address py:if="not invoice.user.bill_to_profile">
            <c py:for="line in invoice.user.billingaddress.split('\n')">${line}<br/></c>
        </address>

        <c py:if="invoice.user.bill_company_no and not invoice.user.bill_to_profile"> Company No. ${invoice.user.bill_company_no} </c>
        <c py:if="invoice.user.bill_vat_no and not invoice.user.bill_to_profile"><br/>VAT ${invoice.user.bill_vat_no}</c>
        <br/>
    </td>
    <td width="50%">
    </td>
    <td>
        <strong>Invoice details</strong>
        <table>
        <tr>
            <td width="20%">Number</td>
            <td width="80%">${invoice.number}</td>
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

<pre class="freetext" py:if="freetext1">
${freetext1}
</pre>

<h2>Summary of usage</h2>

<?python
invoice_data = get_collected_invoice_data(invoice=invoice)[0].items()
vat_included = invoice.sent and invoice.vat_included or invoice.location.vat_included
?>

<div width="80%" py:for="user, ivd in invoice_data">

    <h3>${user.display_name}</h3>

    <table width="100%" border="0.1" style="padding: 0.2em;">
    <thead style="background: #C0C0C0;">
    <tr>
        <td>Description</td>
        <td align="right">Amount ${invoice.location.currency}</td>
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
                (${invoice.location.currency} ${calc_tax(rusage.effectivecost, getResourceVat(invoice, rusage.resource), invoice.vat_included)}
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

<h2>Usage details</h2>

<table width="100%" border="0.1" style="background: #eee; padding: 0.2em;"  repeat="1">
<tbody>
<thead style="background: #C0C0C0;">
<tr>
    <td valign="middle" width="5%">Sr. No.</td>
    <td>Member</td>
    <td>Description</td>
    <td width="10%">Quantity</td>
    <td>Time</td>
    <td align="right">Amount ${invoice.location.currency}</td>
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
<td border="1" class="freetext">
${freetext2}
<br/>
</td>
</tr>
<tr><td></td></tr>
<tr>
<td align="left">
  ${invoice.location.bank}
  <br />
  <c py:if="invoice.location.account_no" py:strip="True">Account Number ${invoice.location.account_no} <br/></c>
  <c py:strip="True" py:if="invoice.location.sort_code"><br />Sort Code <c py:strip="True">${invoice.location.sort_code} <br/></c></c>
  <c py:if="invoice.location.swift_no" py:strip="True">Swift Code ${invoice.location.swift_no} <br/></c>
  <c py:if="invoice.location.iban_no" py:strip="True">IBAN ${invoice.location.iban_no} <br/></c>
  <c py:if="invoice.location.vat_no" py:strip="True">VAT Number ${invoice.location.vat_no} <br/></c>
  <c py:if="invoice.location.payment_terms" py:strip="True">Payment Terms: ${invoice.location.payment_terms}</c>
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
