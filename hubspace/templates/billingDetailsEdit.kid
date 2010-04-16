<?python
from hubspace.utilities.uiutils import print_error,oddOrEven
from hubspace.model import User
from hubspace.controllers import permission_or_owner
from sqlobject import AND

odd_or_even = oddOrEven().odd_or_even

def billing_mode_default(user, value):
    return user.billing_mode == value and dict(checked='checked') or {}

if 'tg_errors' not in locals():
    tg_errors = None

?>
<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">

	<table py:def="load_billingDetailsEdit(user, tg_errors)" class="servicesTable data" cellpadding="" cellspacing="0">
		<tr py:if="permission_or_owner(user.homeplace, None,'manage_invoices')" class="${odd_or_even()}">
			<td class="line">Billing</td>
			<td>
                                <input type="radio" name="billing_mode" value="0" py:attrs="billing_mode_default(user, 0)"/>
                                    Use main profile details<br/>
                                <input type="radio" name="billing_mode" value="2" py:attrs="billing_mode_default(user, 2)"/>Bill to: 
                                    <input type="text" id="for_billto" value="${user.billto and user.billto.display_name or ''}" />
                                    <input type="hidden" id="billto_id" name="billto" value="${user.billto and user.billto.id or user.id}" /> <br/>
                                <input type="radio" name="billing_mode" value="1" py:attrs="billing_mode_default(user, 1)"/>
                                    Use billing details below<br/>
                                <div class="errorMessage" py:if="tg_errors">${print_error('billing_mode', tg_errors)}</div>
                        </td>
		</tr>
		<tr class="${odd_or_even()}">
			<td class="line">Company name</td>
			<td><input type="text" class="text billing_details" id="bill_to_company" name="bill_to_company" value="${user.bill_to_company}" /><div class="errorMessage" py:if="tg_errors">${print_error('bill_to_company', tg_errors)}</div></td>
		</tr>
		<tr class="${odd_or_even()}">
			<td class="line">Billing address</td>
			<td><textarea id="billingaddress" class="billing_details" name="billingaddress">${user.billingaddress}</textarea><div class="errorMessage" py:if="tg_errors">${print_error('billingaddress', tg_errors)}</div></td>
		</tr>
		<tr class="${odd_or_even()}">
			<td class="line">Phone number</td>
			<td><input type="text" class="text billing_details" name="bill_phone" id="bill_phone" value="${user.bill_phone}" /><div class="errorMessage" py:if="tg_errors">${print_error('bill_phone', tg_errors)}</div></td>
		</tr>
		<tr class="${odd_or_even()}">
			<td class="line">Fax number</td>
			<td><input type="text" class="text billing_details" name="bill_fax" id="bill_fax" value="${user.bill_fax}"/><div class="errorMessage" py:if="tg_errors">${print_error('bill_fax', tg_errors)}</div></td>
		</tr>
		<tr class="${odd_or_even()}">
			<td class="line">Email contact</td>
			<td><input type="text" class="text billing_details"  name="bill_email" id="bill_email" value="${user.bill_email}" /><div class="errorMessage" py:if="tg_errors">${print_error('bill_email', tg_errors)}</div></td>
		</tr>
		<tr class="${odd_or_even()}">
			<td class="line">Company Number</td>
			<td><input type="text" class="text billing_details"  name="bill_company_no" id="bill_company_no" value="${user.bill_company_no}"/><div class="errorMessage" py:if="tg_errors">${print_error('bill_company_no', tg_errors)}</div></td>
		</tr>	
		<tr class="${odd_or_even()}">
			<td class="line">VAT Number</td>
			<td><input type="text" class="text billing_details" name="bill_vat_no" id="bill_vat_no" value="${user.bill_vat_no}"/><div class="errorMessage" py:if="tg_errors">${print_error('bill_vat_no', tg_errors)}</div></td>
                </tr>
	</table>
	${load_billingDetailsEdit(object, tg_errors=tg_errors)}
</div>	
