<?python
from hubspace.utilities.uiutils import oddOrEven, print_error, zones
from hubspace.utilities.permissions import locations
from hubspace.controllers import get_place, permission_or_owner, roles_grantable
from hubspace.model import Location
from turbogears import identity
oddness = oddOrEven()
tg_errors = None
from hubspace.utilities.i18n import languages_dict, languages_list

def zone_selected(location, zone):
    if location.timezone == zone or (location.timezone == None and zone=="Europe/London"):
        return {'selected':'selected'}
    return {}

def lang_selected(location, lang):
    if location.locale == lang or (location.locale == None and lang=="en"):
        return {'selected':'selected'}
    return {}
?>

<div py:strip="True" xmlns:py="http://purl.org/kid/ns#">
    <c py:def="load_locationProfileEdit(location, tg_errors)" py:strip="True">
	<table class="locationProfileInner detailTable" cellpadding="0" cellspacing="0">	
		<tr>
                     <td class="line">Location Name</td>
		     <td><input name="name" type="text" value="${location.name}" /><div class="errorMessage" py:if="tg_errors">${print_error('name', tg_errors)}</div></td>
		</tr>
		<tr>
                     <td class="line">Local Currency</td>
		     <td><input name="currency" type="text" value="${location.currency or 'GBP'}" /><div class="errorMessage" py:if="tg_errors">${print_error('currency', tg_errors)}</div></td>
		</tr>
                <tr>
                     <td class="line">Local Time Zone</td>
		     <td><select name="timezone"><option py:for="zone in zones()" py:attrs="zone_selected(location, zone)" value="${zone}">${zone}</option></select><div class="errorMessage" py:if="tg_errors">${print_error('timezone', tg_errors)}</div></td>
		</tr>
                <tr>
                     <td class="line">Local Language</td>
		     <td><select name="locale"><option py:for="locale, lang in languages_list" py:attrs="lang_selected(location, locale)" value="${locale}">${lang}</option></select><div class="errorMessage" py:if="tg_errors">${print_error('locale', tg_errors)}</div></td>
		</tr>
       	        <tr py:if='identity.has_permission("superuser")'>
                     <td class="line">Vat Included</td>
		     <td><input name="vat_included" type="checkbox" value="1" py:attrs="location.vat_included and {'checked':'checked'} or {}" /><div class="errorMessage" py:if="tg_errors">${print_error('vat_included', tg_errors)}</div></td>
		</tr>
                <tr>
		    <td class="line">Tentative booking available</td>
	            <td> <input name="tentative_booking_enabled" type="checkbox" value="1"
                    py:attrs="location.tentative_booking_enabled and {'checked':'checked'} or {}" /><div
                    class="errorMessage" py:if="tg_errors">${print_error('tentative_booking_enabled', tg_errors)}</div></td>
	        </tr>
                <tr>
	            <td class="line">New Invoice numbering scheme</td>
		    <td><input name="invoice_newscheme" type="checkbox" value="1"
                    py:attrs="location.invoice_newscheme and {'checked':'checked'} or {}" /><div
                     class="errorMessage" py:if="tg_errors">${print_error('invoice_newscheme', tg_errors)}</div></td>
	        </tr>

       	        <tr py:if='identity.has_permission("superuser")'>
                     <td class="line">RFID Enabled</td>
		     <td><input name="rfid_enabled" type="checkbox" value="1" py:attrs="location.rfid_enabled and {'checked':'checked'} or {}" /><div class="errorMessage" py:if="tg_errors">${print_error('rfid_enabled', tg_errors)}</div></td>
		</tr>                
       	        <tr py:if='identity.has_permission("superuser")'>
                     <td class="line">Microsite Active</td>
		     <td><input name="microsite_active" type="checkbox" value="1" py:attrs="location.microsite_active and {'checked':'checked'} or {}" /><div class="errorMessage" py:if="tg_errors">${print_error('microsite_active', tg_errors)}</div></td>
		</tr>
       	        <tr>
                     <td class="line">Vat Number</td>
		     <td><input name="vat_no" type="text" value="${location.vat_no or ''}" /><div class="errorMessage" py:if="tg_errors">${print_error('vat_no', tg_errors)}</div></td>
		</tr>
                <tr>
                     <td class="line">Default Vat Level</td>
		     <td><input name="vat_default" type="text" value="${location.vat_default or 0}" /><div class="errorMessage" py:if="tg_errors">${print_error('vat_default', tg_errors)}</div></td>
		</tr>
                <tr>
                     <td class="line">Billing Address</td>
		     <td><input name="billing_address" type="text" value="${location.billing_address or ''}" /><div class="errorMessage" py:if="tg_errors">${print_error('billing_address', tg_errors)}</div></td>
		</tr>
                <tr>
                     <td class="line">Company No.</td>
		     <td><input name="company_no" type="text" value="${location.company_no or ''}" /><div class="errorMessage" py:if="tg_errors">${print_error('company_no', tg_errors)}</div></td>
		</tr>
                <tr>
                     <td class="line">Bank</td>
		     <td><input name="bank" type="text" value="${location.bank or ''}" /><div class="errorMessage" py:if="tg_errors">${print_error('bank', tg_errors)}</div></td>
		</tr>
                <tr>
                     <td class="line">Bank Account No.</td>
		     <td><input name="account_no" type="text" value="${location.account_no or ''}" /><div class="errorMessage" py:if="tg_errors">${print_error('account_no', tg_errors)}</div></td>
		</tr>
                <tr>
                     <td class="line">Sort Code (if applicable)</td>
		     <td><input name="sort_code" type="text" value="${location.sort_code or ''}" /><div class="errorMessage" py:if="tg_errors">${print_error('sort_code', tg_errors)}</div></td>
		</tr>
                <tr>
                     <td class="line">IBAN No.</td>
		     <td><input name="iban_no" type="text" value="${location.iban_no or ''}" /><div class="errorMessage" py:if="tg_errors">${print_error('iban_no', tg_errors)}</div></td>
		</tr>
                <tr>
                     <td class="line">Swift No.</td>
		     <td><input name="swift_no" type="text" value="${location.swift_no or ''}" /><div class="errorMessage" py:if="tg_errors">${print_error('swift_no', tg_errors)}</div></td>
		</tr>
                <tr>
                     <td class="line">Domain Name</td>
		     <td><input name="url" type="text" value="${location.url or ''}" /><div class="errorMessage" py:if="tg_errors">${print_error('url', tg_errors)}</div></td>
		</tr>
		<tr>
                     <td class="line">Telephone</td>
		     <td><input name="telephone" type="text" value="${location.telephone or ''}" /><div class="errorMessage" py:if="tg_errors">${print_error('telephone', tg_errors)}</div></td>
		</tr>
		<tr>
                     <td class="line">Payment Terms</td>
		     <td><input name="payment_terms" type="text" value="${location.payment_terms or ''}" /><div class="errorMessage" py:if="tg_errors">${print_error('payment_terms', tg_errors)}</div></td>
		</tr>
		<tr>
                     <td class="line">Homepage Title</td>
		     <td><input name="homepage_title" type="text" value="${location.homepage_title or ''}" /><div class="errorMessage" py:if="tg_errors">${print_error('homepage_title', tg_errors)}</div></td>
		</tr>
		<tr>
                     <td class="line">Homepage Description</td>
		     <td><textarea name="homepage_description" >${location.homepage_description or ''}</textarea><div class="errorMessage" py:if="tg_errors">${print_error('homepage_description', tg_errors)}</div></td>
		</tr>
	</table>
    </c>
  ${load_locationProfileEdit(object, tg_errors=tg_errors)}
</div>		
