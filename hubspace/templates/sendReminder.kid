<?python
from hubspace.validators import dateconverter
date = dateconverter.from_python 
from hubspace.utilities.uiutils import c2s, print_error
tg_errors = None
?>
<div xmlns:py="http://purl.org/kid/ns#"  py:strip="True">
    <form id="send_reminder_${object.id}">
    <table cellpadding="0" cellspacing="0" class="detailTable">
		<tr class="even">
			<td class="line">Subject:</td>
			<td><input type="text" class="text" id="reminder_mail_subject" name="subject" value="The Hub | payment reminder" /></td>
		</tr>
		<tr class="odd">
			<td class="line">Message:</td>
			<td>
				<textarea id="invoice_mail_body" name="body">
Dear ${object.first_name},

Please can we remind you to pay your outstanding balance of ${object.homeplace.currency}${c2s(object.outstanding)} at The Hub ${object.homeplace.name}. 

If you have any queries regarding this amount please contact The Hub's hosting team at ${object.homeplace.name.lower()}.hosts@the-hub.net or call us on 0207 8418900.

Thank you very much. 

The Hosting Team
</textarea></td>
		</tr>
	</table>
	
    <div class="errorMessage" py:if="tg_errors">${print_error('body', tg_errors)}</div>
		
    </form> 
<input type="image" src="/static/images/button_save.gif" class="submit" value="submit" id="submit_reminder_mail" />
		<input type="image" src="/static/images/button_cancel.gif" class="cancel" value="cancel" id="cancel_reminder_mail" />
		
</div>
