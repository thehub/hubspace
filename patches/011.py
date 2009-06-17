import patches.base
import patches.utils
from turbogears import database
from datetime import datetime
from sqlobject import AND, IN, OR, NOT

class Patch(patches.base.Patch):
    description = "Patch old invoice data"
    def apply(self):
        access_tuple = patches.utils.parseDBAccessDirective()
        dburi = patches.utils.parseDBURI('dev.cfg').split('=')[1][1:-1]
        database.set_db_uri(dburi)
        database.run_with_transaction(vat_switch)

def vat_switch():
    """add total taxes, resource_tax_dict, vat_included
    """
    from hubspace.model import Invoice, Location
    from hubspace.invoice import calculate_tax_and_amount
    #recalculate all the old invoice costs and amounts, as used to happen everytime we did looked at the invoice!

    london  = Location.get(1)
    bristol = Location.get(2)
    kx = Location.get(11)
    switch_time = datetime(2008, 12, 1, 0, 0) 
    special = Invoice.select(AND(IN(Invoice.q.locationID, [1, 2, 11]),
                                 Invoice.q.created < switch_time))

    not_special = Invoice.select(OR(NOT(IN(Invoice.q.locationID, [1, 2, 11])),
                                    Invoice.q.created >= switch_time))
    for inv in not_special:
        tmp = inv.sent
        inv.sent = None
        calculate_tax_and_amount(inv)
        inv.sent = tmp

    london.vat_default = 17.5
    bristol.vat_default = 17.5
    kx.vat_default = 17.5

    #might need to re-patch this bit later for bristol as I think they sent out some invoices at 17.5% after the 1st December
    for inv in special:
        tmp = inv.sent
        inv.sent = None
        calculate_tax_and_amount(inv)
        inv.sent = tmp

    london.vat_default = 15
    bristol.vat_default = 15
    kx.vat_default = 15
