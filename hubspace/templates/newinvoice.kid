<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python
import datetime
from hubspace.controllers import get_collected_invoice_data
from hubspace.controllers import show_quantity_or_duration, sum_resource_costs
from hubspace.utilities.uiutils import c2s
from hubspace.validators import dateconverter
from turbogears.validators import DateTimeConverter

formatDate = dateconverter.from_python
formatDateTime = lambda t: t.strftime("%b %-d %Y %l:%M%P")
dtc = DateTimeConverter("%B %Y").from_python

def getResourceUsageCost(ivd, resource):
    rusages = ivd[0][resource]
    return c2s(sum_resource_costs(rusages))

def getRusageCost(rusage):
    return c2s(rusage.customcost or rusage.cost)

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
?>


<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" >

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
    <td align="left" width="20%">
        <br/>
        <strong>${invoice.user.display_name}</strong><br/>
        <c py:strip="True" py:if="invoice.user.bill_to_profile"> ${nl2br(invoice.user.address)} </c>
        <c py:strip="True" py:if="not invoice.user.bill_to_profile"> ${nl2br(invoice.user.billingaddress)} </c>
        <c py:strip="True" py:if="not invoice.user.bill_company_no and not invoice.user.bill_to_profile"> Company No. ${invoice.user.bill_company_no} </c>
        <br/>
    </td>
    <td width="40%">
    </td>
    <td>
        <table>
        <tr>
            <td><strong>Invoice no.</strong></td>
            <td><strong>${invoice.number}</strong></td>
        </tr>
        <tr>
            <td>Invoice Date</td>
            <td>${formatDate(invoice.sent or datetime.datetime.now())}</td>  
        </tr>
        <tr>
            <td>Invoice Period</td>
            <td>${formatDate(invoice.start)} to  <br/> ${formatDate(invoice.end_time)}</td>
        </tr>
        <tr py:if="invoice.location.invoice_duedate > -1">
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
    <div py:for="resource in ivd[0]">
    <tr width="80%" border="0.20">
        <td>
            <strong> ${resource.name} </strong> <br/>
            <small>
                <em> Inclusive of ${getResourceVat(invoice, resource)} % VAT </em>(${invoice.location.currency} ${getResourceVATAmount(invoice, resource)})
            </small>
        </td>
        <td align="right"> 
            ${getResourceUsageCost(ivd, resource)} <br/>
        </td>
    </tr>
    </div>
    <tr>
        <td><strong>Sub Total</strong></td>
        <td align="right">${sumUsageCosts(ivd)} </td>
    </tr>
    </table>

</div>

<br/>

<table width="100%" border="0.1" style="padding: 0.2em;">
<tr>
<td align="center"><strong>Total</strong></td>
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
    <td>Resource</td>
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
    <td>${rusage.resource.name} <div py:if="rusage.cancelled and not rusage.refund"><em>(Cancelled)</em></div>
                                <div py:if="rusage.refund"><em>(Refund)</em></div> </td>
    <td>${rusage.resource.time_based and "-" or rusage.quantity}</td>
    <td py:if="rusage.resource.time_based">${formatDateTime(rusage.start)} - <br/> ${formatDateTime(rusage.end_time)}</td>
    <td py:if="not rusage.resource.time_based">${rusage.resource.type == 'tariff' and dtc(rusage.start) or formatDateTime(rusage.start)}</td>
    <td align="right">
        ${c2s(rusage.cost)}<br/>
        <small> <em> Inclusive of ${getResourceVat(invoice, rusage.resource)} % VAT</em> </small>

    </td>
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
    <small>${invoice.location.billing_address} | ${invoice.location.url} | ${invoice.location.telephone}</small>
    </p>
</div>

</body>
</html>
