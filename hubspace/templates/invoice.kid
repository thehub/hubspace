<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
 <?python
from turbogears.validators import DateTimeConverter
dtc = DateTimeConverter("%B %y")
from hubspace.controllers import get_collected_invoice_data
from hubspace.utilities.uiutils import c2s
from hubspace.validators import dateconverter
from hubspace.controllers import show_quantity_or_duration, sum_resource_costs
import cherrypy
import datetime
def invoice_data(invoice):
    return get_collected_invoice_data(invoice=invoice)[0].items()

def image_path(location):
    return location.imageFilename('invlogo')
def lang():
    return cherrypy.session.get('locale', 'en')
?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" xml:lang="${lang()}" lang="${lang()}">
 <head>
 </head>
 <body>
  <table cellpadding="0" cellspacing="0" width="690">
   <tr height="130">
    <td valign="top">
     <center>
       <img src="${image_path(invoice.location)}" />
     </center>
    </td>
   </tr>
   <tr height="170">
    <td valign="top">
     <table bgcolor="#EBEBEB" cellpadding="0" cellspacing="0">
      <tr>
       <td bgcolor="#FFFFFF" width="30">
        <font color="#FFFFFF">.</font>
       </td>
       <td bgcolor="#FFFFFF" width="300">
        <b>
         <font face="arial" size="2">
           Invoice
         </font>
        </b>
       </td>
       <td bgcolor="#FFFFFF">
        <font color="#FFFFFF">.</font>
       </td>
      </tr>
      <tr>
       <td>
       </td>
       <td>
       </td>
       <td bgcolor="#EBEBEB" width="11" align="right" valign="top">
        <img src="hubspace/static/images/corner_top.gif" />
       </td>
      </tr>
      <tr>
       <td width="30">
       </td>
       <td valign="top">
        <table cellpadding="0" cellspacing="0">
         <tr>
          <td width="100">
           <font face="arial" size="2">
             Date
           </font>
          </td>
          <td width="200">
           <font face="arial" size="2">
            ${dateconverter.from_python(invoice.sent or datetime.datetime.now())}  
           </font>
          </td>
         </tr>
         <tr>
          <td>
           <font face="arial" size="2">Invoice No.</font>
          </td>
          <td>
           <font face="arial" size="2">
            ${invoice.number}
           </font>
          </td>
         </tr>
         <tr>
          <td>
           <font face="arial" size="2">Membership No.</font>
          </td>
          <td>
           <font face="arial" size="2">
            ${str(invoice.user.id)}
           </font>
          </td>
         </tr>
         <tr>
          <td>
           <font face="arial" size="2">
            Invoice to
           </font>
          </td>
          <td>
           <font face="arial" size="2">
            ${invoice.user.bill_to_profile and invoice.user.organisation or invoice.user.bill_to_company}
           </font>
          </td>
         </tr>
         <tr>
          <td>
          </td>
          <td>
           <font face="arial" size="2">
            ${invoice.user.display_name}
           </font>
          </td>
         </tr>
         <tr>
          <td>
          </td>
          <td>
           <font face="arial" size="2" py:if="invoice.user.bill_to_profile">${invoice.user.address}</font> 
           <c py:strip="True" py:if="not invoice.user.bill_to_profile">
           <?python
               multiline_addr = invoice.user.billingaddress.split('\n')
           ?>
               <c py:for="line in multiline_addr" py:strip="True"><font face="arial" size="2">${line}</font><br /></c>
           </c>

          </td>
         </tr>
         <tr py:if="invoice.user.bill_company_no and not invoice.user.bill_to_profile">
          <td>
          </td>
          <td>
           <font face="arial" size="2">Company no. <c py:strip="True">${invoice.user.bill_company_no}</c></font>
          </td>
         </tr>
         <tr py:if="invoice.user.bill_vat_no and not invoice.user.bill_to_profile">
          <td>
          </td>
          <td>
           <font face="arial" size="2">VAT <c py:strip="True">${invoice.user.bill_vat_no}</c></font>
          </td>
         </tr>
        </table>
       </td>
       <td>
       </td>
      </tr>
      <tr>
       <td width="30">
       </td>
       <td>
       </td>
       <td width="11" align="right" valign="bottom">
        <img src="hubspace/static/images/corner_bot.gif" />
       </td>
      </tr>
     </table>
    </td>
   </tr>
   <tr height="460">
    <td valign="top">
     <table cellpadding="0" cellspacing="0" id="invoiceItems" align="right">
      <tr class="header">
       <td>
       </td>
       <td>
        <b>
         <font face="arial" size="2">Description</font>
        </b>
       </td>
       <td class="amount">
        <b>
         <font face="arial" size="2">Amount</font>
        </b>
       </td>
      </tr>
      <tr class="border">
       <td class="topLeft">
        <img src="hubspace/static/images/top_left.gif" width="29" height="10" />
       </td>
       <td class="top">
        <img src="hubspace/static/images/top.gif" width="300" height="10" />
       </td>
       <td colspan="2" class="top">
        <img src="hubspace/static/images/top.gif" width="100" height="10" />
       </td>
      </tr>
      <span py:strip="True" py:for="user,ivd in invoice_data(invoice)">
       <?python
        all_rusages = []
       ?>
      <tr>
       <td colspan="4" class="left">
        <img src="hubspace/static/images/left.gif" width="29" height="14" />
        <font face="arial" size="2">
         <b>
          ${user.display_name}
         </b>
         <br />
        </font>
       </td>
      </tr>
      <span py:for="resource in ivd[0]" py:strip="True">
       <?python
               rusages = ivd[0][resource]
               rusage = rusages[0]
               all_rusages.extend(rusages)
       ?>
      <tr py:if="len(rusages)==1 or rusage.resource.type=='custom'" py:for="rusage in rusages">
       <td class="left">
        <img src="hubspace/static/images/left.gif" width="29" height="14" />
       </td>
       <td py:if="resource.type != 'tariff'" bgimage="hubspace/static/images/bg1.gif">
        <font face="arial" size="2">
         ${show_quantity_or_duration(rusage)} x ${rusage.resource_name}
        </font>
       </td>
       <td py:if="resource.type == 'tariff'" bgimage="hubspace/static/images/bg1.gif">
        <font face="arial" size="2">
         ${rusage.resource_name} - ${dtc.from_python(rusage.start)}
        </font>
       </td>
       <td>
        <font face="arial" size="2">
         ${invoice.location.currency}
        </font>
       </td>
       <td align="right">
        <font face="arial" size="2">
         ${c2s([rusage.customcost,rusage.cost][rusage.customcost == None])}
        </font>
       </td>
      </tr>
      <tr py:if="len(rusages)&gt;1 and rusage.resource.type!='custom'">
       <td class="left">
        <img src="hubspace/static/images/left.gif" width="29" height="14" />
       </td>
       <td py:if="resource.type != 'tariff'" bgimage="hubspace/static/images/bg1.gif">
        <font face="arial" size="2">
         ${show_quantity_or_duration(ivd[1][resource])} x ${rusage.resource_name}
        </font>
       </td>
       <td py:if="resource.type == 'tariff'" bgimage="hubspace/static/images/bg1.gif">
        <font face="arial" size="2">
         ${rusage.resource_name} - ${dtc.from_python(rusage.start)}
        </font>
       </td>
       <td>
        <font face="arial" size="2">
         ${invoice.location.currency}
        </font>
       </td>
       <td align="right">
        <font face="arial" size="2">
         ${c2s(sum_resource_costs(rusages))}
        </font>
       </td>
      </tr>
      </span>
      <tr>
       <td colspan="2" class="left">
        <img src="hubspace/static/images/left.gif" width="29" height="14" />
        <font face="arial" size="2">Sub Total<br /></font>
       </td>
       <td>
        <font face="arial" size="2">
         ${invoice.location.currency}
        </font>
       </td>
       <td align="right">
        <font face="arial" size="2">
         ${c2s(sum_resource_costs(all_rusages))}
        </font>
       </td>
      </tr>
      </span>
      <tr>
       <td colspan="4">
        <img src="hubspace/static/images/left.gif" width="29" height="14" />
       </td>
      </tr>
      <tr>
       <td colspan="2" class="left">
        <img src="hubspace/static/images/left.gif" width="29" height="14" />
        <font face="arial" size="2">Excluding VAT<br /></font>
       </td>
       <td>
        <font face="arial" size="2">
         ${invoice.location.currency}
        </font>
       </td>
       <td align="right">
        <font face="arial" size="2">
         ${c2s(invoice.amount-invoice.total_tax)}
        </font>
       </td>
      </tr>
      <tr>
       <td colspan="2" class="left">
        <img src="hubspace/static/images/left.gif" width="29" height="14" />
        <font face="arial" size="2">VAT<br /></font>
       </td>
       <td>
        <font face="arial" size="2">
         ${invoice.location.currency}
        </font>
       </td>
       <td align="right">
        <font face="arial" size="2">
         ${c2s(invoice.total_tax)}
        </font>
       </td>
      </tr>
      <tr>
       <td colspan="2" class="left">
        <img src="hubspace/static/images/left.gif" width="29" height="14" />
        <font face="arial" size="2">Total<br /></font>
       </td>
       <td>
        <font face="arial" size="2">
         ${invoice.location.currency}
        </font>
       </td>
       <td align="right">
        <font face="arial" size="2">
         ${c2s(invoice.amount)}
        </font>
       </td>
      </tr>
      <tr class="border">
       <td class="Left">
        <img src="hubspace/static/images/bot_left.gif" width="29" height="10" />
       </td>
       <td class="bottom">
        <img src="hubspace/static/images/bot.gif" width="300" height="10" />
       </td>
       <td colspan="2" class="bottom">
        <img src="hubspace/static/images/bot.gif" width="100" height="10" />
       </td>
      </tr>
     </table>
    </td>
   </tr>
   <tr height="150">
    <td valign="top">
     <table cellpadding="0" cellspacing="0">
      <tr>
       <td valign="top">
        <table bgcolor="#EBEBEB" cellpadding="0" cellspacing="0">
         <tr>
          <td width="30">
          </td>
          <td>
          </td>
          <td width="11" align="right" valign="top">
           <img src="hubspace/static/images/corner_top.gif" />
          </td>
         </tr>
         <tr>
          <td>
          </td>
          <td valign="top">
           <font face="arial" size="2">Thank you for your prompt payment<br /><br /><br /><br /></font>
          </td>
          <td>
          </td>
         </tr>
         <tr>
          <td width="30">
          </td>
          <td>
          </td>
          <td width="11" align="right" valign="bottom">
           <img src="hubspace/static/images/corner_bot.gif" />
          </td>
         </tr>
        </table>
       </td>
       <td>
        <font color="#FFFFFF">
         ...
        </font>
       </td>
       <td valign="top">
        <font face="arial" size="2">
         ${invoice.location.bank}
         <br />
         <c py:if="invoice.location.bank_account_name" py:strip="True">Account Name ${invoice.location.bank_account_name}</c>         
         <br />
         <c py:if="invoice.location.account_no" py:strip="True">Account Number ${invoice.location.account_no}</c>         
         <br />
         <c py:strip="True" py:if="invoice.location.sort_code"><br />Sort Code <c py:strip="True">${invoice.location.sort_code}</c></c>
         <br />
         <c py:if="invoice.location.swift_no" py:strip="True">Swift Code ${invoice.location.swift_no}</c>         
         <br />
         <c py:if="invoice.location.iban_no" py:strip="True">IBAN ${invoice.location.iban_no}</c>         
         <br />
         <c py:if="invoice.location.vat_no" py:strip="True">VAT Number ${invoice.location.vat_no}</c>         
         <br />
         Payment Terms <c py:strip="True">${invoice.location.payment_terms}</c>
        </font>
       </td>
      </tr>
     </table>
    </td>
   </tr>
   <tr>
    <td>
     <center>
      <font face="arial" size="2" color="#666666">
       ${invoice.location.billing_address} | <c py:strip="True">Company no.</c> ${invoice.location.company_no} | ${invoice.location.url} | ${invoice.location.telephone}
      </font>
     </center>
    </td>
   </tr>
  </table>
 </body>
</html>
