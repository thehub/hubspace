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
        database.run_with_transaction(bristol_vat_switch)

def bristol_vat_switch():
    """get the bristol invoices that were sent at 15% before mid day on the 2nd of december and set them to 17.5%
    """
    from hubspace.model import Invoice, Location
    from hubspace.invoice import calculate_tax_and_amount
    #recalculate all the old invoice costs and amounts, as used to happen everytime we did looked at the invoice!

    bristol = Location.get(2)
    start_switch_time = datetime(2008, 12, 1, 0, 0)
    end_switch_time = datetime(2008, 12, 2, 12, 0) 
    special = Invoice.select(AND(Invoice.q.locationID == 2,
                                 Invoice.q.created < end_switch_time,
                                 Invoice.q.created > start_switch_time))


    bristol.vat_default = 17.5

    for inv in special:
        tmp = inv.sent
        inv.sent = None
        calculate_tax_and_amount(inv)
        inv.sent = tmp

    bristol.vat_default = 15.0
