import patches.base
import patches.utils
from turbogears import database
from datetime import datetime
from sqlobject import AND, IN, OR, NOT

class Patch(patches.base.Patch):
    description = "Create microsite Spaces Type"
    def apply(self):
        access_tuple = patches.utils.parseDBAccessDirective()
        dburi = patches.utils.parseDBURI('dev.cfg').split('=')[1][1:-1]
        database.set_db_uri(dburi)
        database.run_with_transaction(setup_microsite_spaces)


def setup_microsite_spaces(): 
    """Create the microsites spaces object
    """
    from hubspace.model import MicroSiteSpace
    MicroSiteSpace.createTable(ifNotExists=True)
