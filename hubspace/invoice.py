from decimal import Decimal
from model import Resource, RUsage
from sqlobject import AND

__all__ = ['calculate_tax_and_amount']

anomolies = file('anomolies.txt', 'a')

def calculate_tax_and_amount(invoice):
    resource_tax_dict, resource_cost_dict, rusages_cost_and_tax = invoice_tax_cost_breakdown(invoice)
    total_tax = Decimal("0")
    total_cost = Decimal("0")
    for res in resource_tax_dict:
        total_tax += resource_tax_dict[res][0]
        total_cost += resource_cost_dict[res]
    
    if total_cost != invoice.amount:
        invoice.amount = total_cost
    
    if total_tax != invoice.total_tax:
        invoice.total_tax = total_tax

    invoice.resource_tax_dict = resource_tax_dict

    if invoice.vat_included != invoice.location.vat_included:
        invoice.vat_included = invoice.location.vat_included
    
    invoice.rusages_cost_and_tax = rusages_cost_and_tax


def invoice_tax_cost_breakdown(invoice):
    """return a breakdown of the form {resource.id:resource_tax}
    """
    resource_tax = {}
    resource_cost = {}
    rusages_cost_and_tax = {}
    resources = Resource.select(AND(Resource.q.id==RUsage.q.resourceID, RUsage.q.invoiceID==invoice.id), distinct=True)
    get_resource_effective_vat = lambda resource: [resource.place.vat_default, resource.vat][type(resource.vat)==float]
    resource_vats = dict((resource, get_resource_effective_vat(resource)) for resource in resources)
    for resource in resources:
        res_cost = 0
        percent_vat = resource_vats[resource]
        vat_included = resource.place.vat_included
        for ruse in (ruse for ruse in invoice.rusages if ruse.resource == resource):
            ruse_cost = ruse.effectivecost
            vat = calc_tax(ruse_cost, percent_vat, vat_included)
            if not resource.place.vat_included:
                ruse_cost += vat
            res_cost += ruse_cost
            rusages_cost_and_tax[ruse.id] = (res_cost, vat)
        vat = calc_tax(res_cost, percent_vat, vat_included)
        resource_tax[resource.id] = (vat, percent_vat, vat_included)
        resource_cost[resource.id] = res_cost

    return resource_tax, resource_cost, rusages_cost_and_tax


def calc_tax(resource_total, percentage_tax, vat_included):
    """vat - we should zero rate usages which are: 
           a) bought in other countries AND b) the invoiced entity is vat registered
            -- otherwise charge local vat rate
       Currently - everything is charge at the local VAT level of the resource.
    """
    if vat_included:
        unrounded = Decimal(str(resource_total)) * Decimal(str(percentage_tax)) / (100+Decimal(str(percentage_tax)))
    else:
        unrounded = Decimal(str(resource_total)) * Decimal(str(percentage_tax)) / 100
    TWOPLACES = Decimal(10) ** -2
    #use a different exponent to round to say 5 eurocents
    rounded = unrounded.quantize(TWOPLACES)
    return rounded
