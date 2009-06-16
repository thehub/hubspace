import patches.base
import patches.utils
from turbogears import database
from datetime import datetime
from sqlobject import AND, IN, OR, NOT

class Patch(patches.base.Patch):
    description = "Changes to the architecture of MicroSites to support the concepts of Pages, list_items, and rendered objects"
    def apply(self):
        access_tuple = patches.utils.parseDBAccessDirective()
        dburi = patches.utils.parseDBURI('dev.cfg').split('=')[1][1:-1]
        database.set_db_uri(dburi)
        database.run_with_transaction(setup_display_name_field)

def setup_display_name_field(): 
    """Create the microsites spaces object
    """
    from hubspace.model import User
    for user in User.select():
        user.display_name        

  

