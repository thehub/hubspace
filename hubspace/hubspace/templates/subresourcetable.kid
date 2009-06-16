<?python
from hubspace.utilities.uiutils import oddOrEven, inv_currency, c2s
odd_or_even = oddOrEven().odd_or_even
from hubspace.controllers import show_quantity_or_duration, permission_or_owner
?>

<c xmlns:py="http://purl.org/kid/ns#"  py:strip="True">
<c py:if="'cost' in locals()" py:strip="True">
    <div id="cost-${rusage.id}" class="custom_cost">${inv_currency(invoice, billed_user)} ${c2s([rusage.customcost,rusage.cost][rusage.customcost == None])}</div><a py:if="permission_or_owner(billed_user.homeplace, None, 'manage_invoices')" id="cost-${rusage.id}Edit" style="cursor:pointer;">change</a>
</c>
<c py:if="'add_to_invoice' in locals()" py:strip="True">
    <a id="rusage-${rusage.id}" class="add_to_invoice">Add to Invoice</a>
</c>
<c py:if="'delrusage' in locals()" py:strip="True">
    <a id="delrusage-${rusage.id}" class="del_rusage">Delete</a>
</c>
<c py:if="'remove_from_invoice' in locals()" py:strip="True">
    <a id="rusage-${rusage.id}" class="remove_from_invoice">Remove from Invoice</a>
</c>
</c>
