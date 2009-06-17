<?python
from hubspace.utilities.uiutils import print_error,oddOrEven,c2s
from hubspace.model import User
from hubspace.controllers import permission_or_owner
from sqlobject import AND

odd_or_even = oddOrEven().odd_or_even

   

def bill_to_profile(user, tg_errors=None):
   attrs = {}
   if user.bill_to_profile==True:
      attrs['checked'] = 'true'
   if (not tg_errors) and (user.billto != None and user.billto.id!=user.id):
      attrs['disabled'] = 'true'
   return attrs

def show_checkbox(user,  tg_errors=None):
   if (not tg_errors) and (user.billto != None and user.billto.id!=user.id):
      return {'style':'display:none;'}
   return {}   

def show_field(user,  tg_errors=None):
    if (not tg_errors) and ((user.billto != None and user.billto.id!=user.id) or (user.bill_to_profile)):  
        return {'style':'display:none;'}
    return {}

def disable_field(user,  tg_errors=None):
    if (not tg_errors) and ((user.billto != None and user.billto.id!=user.id) or (user.bill_to_profile)): 
        return {'disabled':'disabled'}
    return {}

def selected(member, user):
   props = {}
   if member == user.billto:
       props['selected'] = 'selected'
   if user.billto == None and member.id == user.id:
       props['selected'] = 'selected'    
   return props

if 'tg_errors' not in locals():
    tg_errors = None

?>
<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">

	<table py:def="load_billingDetailsEdit(user, tg_errors)" class="servicesTable data" cellpadding="" cellspacing="0">
		<tr py:if="permission_or_owner(user.homeplace, None,'manage_invoices')" class="${odd_or_even()}">
			<td class="line">Member to bill</td>
			<td>
				<select id="billto" name="billto" class="submit">
					<option class="bill_options" id="self" py:attrs="selected(user, user)" value="${user.id}">Self</option>
					<option class="bill_options" py:for="member in User.select(AND(User.q.id!=user.id), orderBy='first_name')" py:attrs="selected(member, user)" value="${member.id}">${member.display_name}</option>
				</select>   
                     </td>
		</tr>
                <tr py:attrs="show_checkbox(user,  tg_errors=tg_errors)" class="${odd_or_even()}">
			<td class="line">Use profile details</td>
			<td><input type="checkbox" py:attrs="bill_to_profile(user, tg_errors=tg_errors)" name="bill_to_profile" id="bill_to_profile" value="1" />
<div class="errorMessage" py:if="tg_errors">${print_error('bill_to_profile', tg_errors)}</div>
			</td>
		</tr>	
		<tr py:attrs="show_field(user, tg_errors=tg_errors)" class="${odd_or_even()}">
			<td class="line">Company name</td>
			<td><input py:attrs="disable_field(user,  tg_errors=tg_errors)" type="text" class="text" id="bill_to_company" name="bill_to_company" value="${user.bill_to_company}" /><div class="errorMessage" py:if="tg_errors">${print_error('bill_to_company', tg_errors)}</div></td>
		</tr>
		<tr py:attrs="show_field(user, tg_errors=tg_errors)" class="${odd_or_even()}">
			<td class="line">Billing address</td>
			<td><textarea py:attrs="disable_field(user,  tg_errors=tg_errors)" id="billingaddress" name="billingaddress">${user.billingaddress}</textarea><div class="errorMessage" py:if="tg_errors">${print_error('billingaddress', tg_errors)}</div></td>
		</tr>
		<tr py:attrs="show_field(user, tg_errors=tg_errors)" class="${odd_or_even()}">
			<td class="line">Phone number</td>
			<td><input py:attrs="disable_field(user,  tg_errors=tg_errors)" type="text" class="text" name="bill_phone" id="bill_phone" value="${user.bill_phone}" /><div class="errorMessage" py:if="tg_errors">${print_error('bill_phone', tg_errors)}</div></td>
		</tr>
		<tr py:attrs="show_field(user, tg_errors=tg_errors)" class="${odd_or_even()}">
			<td class="line">Fax number</td>
			<td><input py:attrs="disable_field(user,  tg_errors=tg_errors)" type="text" class="text" name="bill_fax" id="bill_fax" value="${user.bill_fax}"/><div class="errorMessage" py:if="tg_errors">${print_error('bill_fax', tg_errors)}</div></td>
		</tr>
		<tr py:attrs="show_field(user, tg_errors=tg_errors)" class="${odd_or_even()}">
			<td class="line">Email contact</td>
			<td><input py:attrs="disable_field(user,  tg_errors=tg_errors)" type="text" class="text"  name="bill_email" id="bill_email" value="${user.bill_email}" /><div class="errorMessage" py:if="tg_errors">${print_error('bill_email', tg_errors)}</div></td>
		</tr>
		<tr py:attrs="show_field(user, tg_errors=tg_errors)" class="${odd_or_even()}">
			<td class="line">Company Number</td>
			<td><input py:attrs="disable_field(user,  tg_errors=tg_errors)" type="text" class="text"  name="bill_company_no" id="bill_company_no" value="${user.bill_company_no}"/><div class="errorMessage" py:if="tg_errors">${print_error('bill_company_no', tg_errors)}</div></td>
		</tr>	
		<tr py:attrs="show_field(user, tg_errors=tg_errors)" class="${odd_or_even()}">
			<td class="line">VAT Number</td>
			<td><input py:attrs="disable_field(user,  tg_errors=tg_errors)" type="text" class="text" name="bill_vat_no" id="bill_vat_no" value="${user.bill_vat_no}"/><div class="errorMessage" py:if="tg_errors">${print_error('bill_vat_no', tg_errors)}</div></td>
		</tr>	
	</table>
	${load_billingDetailsEdit(object, tg_errors=tg_errors)}
</div>	
