<?python
from hubspace.utilities.uiutils import oddOrEven, attr_not_none, c2s 
oddness = oddOrEven()
from hubspace.controllers import gip, is_owner, permission_or_owner
from hubspace.validators import dateconverter
from docutils.core import publish_parts
from hubspace.utilities.i18n import languages_dict
?>

<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">
   <div py:def="load_locationProfile(location)" py:strip="True">
	<table class="locationProfileInner detailTable"  cellpadding="0" cellspacing="0">
						
                                                <tr py:if="attr_not_none(location, 'name')" >
							<td class="line">Location Name</td>
							<td>${location.name}</td>
						</tr>
                                                <tr py:if="attr_not_none(location,'currency') and permission_or_owner(location, location, 'manage_locations')" >
							<td class="line">Local Currency</td>
							<td>${location.currency}</td>
						</tr>
						<tr py:if="attr_not_none(location, 'timezone')" >
							<td class="line">Local Time Zone</td>
							<td>${location.timezone}</td>
						</tr>
						<tr>
							<td class="line">Language</td>
							<td>${languages_dict[location.locale]}</td>
						</tr>
                                                <tr>
							<td class="line">Tentative booking available</td>
							<td>${location.tentative_booking_enabled and 'yes' or 'no'}</td>
						</tr>
						<tr>
							<td class="line">RFID Enabled</td>
							<td>${location.rfid_enabled and 'yes' or 'no'}</td>
						</tr>
						<tr>
							<td class="line">MicroSite Active</td>
							<td>${location.microsite_active and 'yes' or 'no'}</td>
						</tr>
                                                <tr>
							<td class="line">Invoice dute date (days after sending invoice)</td>
							<td>${location.invoice_duedate or "Not specified"}</td>
						</tr>
                                                <tr py:if="attr_not_none(location, 'payment_terms')" >
							<td class="line">Payment Terms</td>
							<td>${location.payment_terms}</td>
						</tr>
                                                <tr py:if="attr_not_none(location, 'invoice_bcc')" >
							<td class="line">Bcc Invoice</td>
							<td>${location.invoice_bcc}</td>
						</tr>
                                                <tr>
							<td class="line">New Invoice numbering scheme </td>
							<td>${location.invoice_newscheme and 'yes' or 'no'}</td>
						</tr>
                                                <tr>
							<td class="line">Vat Included</td>
							<td>${location.vat_included and 'yes' or 'no'}</td>
						</tr>
                                                <tr py:if="attr_not_none(location, 'vat_no')" >
							<td class="line">Vat Number</td>
							<td>${location.vat_no}</td>
						</tr>
                                                <tr py:if="attr_not_none(location, 'vat_default')" >
							<td class="line">Default Level of Vat Charged (0%-100%)</td>
							<td>${location.vat_default}</td>
						</tr>
                                                <tr py:if="attr_not_none(location, 'company_name')" >
							<td class="line">Company Name</td>
							<td>${location.company_name}</td>
						</tr> 
                                                <tr py:if="attr_not_none(location, 'company_no')" >
							<td class="line">Company No.</td>
							<td>${location.company_no}</td>
						</tr> 
                                                <tr py:if="attr_not_none(location, 'billing_address')" >
							<td class="line">Billing Address</td>
							<td>${location.billing_address}</td>
						</tr>
						<tr py:if="attr_not_none(location, 'bank')" >
							<td class="line">Bank</td>
							<td>${location.bank}</td>
						</tr>
						<tr py:if="attr_not_none(location, 'account_no')" >
							<td class="line">Bank Account No.</td>
							<td>${location.account_no}</td>
						</tr>
						<tr py:if="attr_not_none(location, 'sort_code')" >
							<td class="line">Sort Code</td>
							<td>${location.sort_code}</td>
						</tr>
						<tr py:if="attr_not_none(location, 'iban_no')" >
							<td class="line">IBAN No.</td>
							<td>${location.iban_no}</td>
						</tr>
						<tr py:if="attr_not_none(location, 'swift_no')" >
							<td class="line">Swift No.</td>
							<td>${location.swift_no}</td>
						</tr>
                                                <tr py:if="attr_not_none(location, 'url')" >
							<td class="line">Domain Name</td>
							<td>${location.url}</td>
						</tr>
                                                <tr py:if="attr_not_none(location, 'telephone')" >
							<td class="line">Telephone</td>
							<td>${location.telephone}</td>
						</tr>
                                                <tr py:if="attr_not_none(location, 'homepage_title')" >
							<td class="line">Homepage Title</td>
							<td>${location.homepage_title}</td>
						</tr>
                                                <tr py:if="attr_not_none(location, 'homepage_description')" >
							<td class="line">Homepage Description</td>
							<td>${XML(publish_parts(location.homepage_description, writer_name="html")["html_body"])}</td>
						</tr>
			</table>
    </div>	        
${load_locationProfile(object)}
</div>
