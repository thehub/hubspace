<?python
from hubspace.utilities.uiutils import oddOrEven, attr_not_none
odd_or_even = oddOrEven().odd_or_even
def bill_someone_else(user):
    if user.billto != None and user.billto.id!=user.id:
        return True
    else:
        return False
from docutils.core import publish_parts
?>

<div  class="pane" xmlns:py="http://purl.org/kid/ns#" py:strip="True">
	<table py:def="load_billingDetails(user)" class="detailTable data" cellpadding="" cellspacing="0" >
		<tr py:if="bill_someone_else(user)" class="${odd_or_even()}">
			<td class="line">Member to bill</td>
			<td>${user.billto.display_name}</td>
		</tr>
                <c py:if="user.bill_to_profile and not bill_someone_else(user)" py:strip="True">
                      <tr class="${odd_or_even()}">
			<td class="line">Billing Address</td>
			<td>Use my normal profile address</td>
		      </tr>
                </c>
                <c py:if="bill_someone_else(user)!=True and not user.bill_to_profile">
		<tr py:if="attr_not_none(user,'bill_to_company')" class="${odd_or_even()}">
			<td class="line">Company name</td>
			<td>${user.bill_to_company}</td>
		</tr>
		<tr py:if="attr_not_none(user,'billingaddress')" class="${odd_or_even()}">
			<td class="line">Billing address</td>
			<td>${XML(publish_parts(user.billingaddress, writer_name="html")["html_body"])}</td>
		</tr>
		<tr py:if="attr_not_none(user,'bill_phone')" class="${odd_or_even()}">
			<td class="line">Phone number</td>
			<td>${user.bill_phone}</td>
		</tr>
		<tr py:if="attr_not_none(user,'bill_fax')" class="${odd_or_even()}">
			<td class="line">Fax number</td>
			<td>${user.bill_fax}</td>
		</tr>
		<tr py:if="attr_not_none(user,'bill_email')" class="${odd_or_even()}">
			<td class="line">Email contact</td>
			<td>${user.bill_email}</td>
		</tr>
		<tr py:if="attr_not_none(user,'bill_company_no')" class="${odd_or_even()}">
			<td class="line">Company Number</td>
			<td>${user.bill_company_no}</td>
		</tr>
		<tr py:if="attr_not_none(user,'bill_vat_no')" class="${odd_or_even()}">
			<td class="line">VAT Number</td>
			<td>${user.bill_vat_no}</td>
		</tr>
                </c>
	</table>
        ${load_billingDetails(object)}
</div>
