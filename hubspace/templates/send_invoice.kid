<?python
from hubspace.validators import dateconverter
date = dateconverter.from_python 
from hubspace.invoice import invoice_email
?>
<div xmlns:py="http://purl.org/kid/ns#"  py:strip="True">
    <div class="dataBox">
        <div class="dataBoxContent">
            <form id="send_invoice_form" class="send_invoice_form">
                <table cellpadding="0" cellspacing="0" class="detailTable">
                    <tr class="odd">
                        <td class="line">Attachment:</td>
                        <td>Invoice${object.id}.pdf<input type="hidden" id="invoiceid" name="invoiceid" value="${object.id}" /><span class="inv_by_mail"><input type="checkbox" name="send_it" value="1" checked="checked" />Send invoice by email</span></td>
                    </tr>
                    <tr class="even">
                        <td class="line">Subject:</td>
                        <td><input type="text" class="text" id="invoice_mail_subject" name="subject" value="The Hub | invoice" /></td>
                    </tr>
                    <tr class="odd">
                        <td class="line">Message:</td>
                        <td>
                            <textarea id="invoice_mail_body" name="body">${invoice_email(object)}
                            </textarea>
                        </td>
                    </tr>
                </table>
            </form> 
        </div>
    </div>
    <div style="position:relative;top:10px;">
        <input type="image" src="/static/images/button_save.gif" class="submit" value="ok" id="submit_invoice_mail" />
        <input type="image" src="/static/images/button_cancel.gif" class="cancel" value="ok" id="cancel_invoice_mail" />
    </div>
</div>
