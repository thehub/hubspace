import patches.base
import patches.utils
from turbogears import database
from datetime import datetime
from sqlobject import AND, IN, OR, NOT

class Patch(patches.base.Patch):
    description = "Create new file store for Hub Sites"
    def apply(self):
        access_tuple = patches.utils.parseDBAccessDirective()
        dburi = patches.utils.parseDBURI('dev.cfg').split('=')[1][1:-1]
        database.set_db_uri(dburi)
        database.run_with_transaction(setup_site_metadata)


def setup_site_metadata(): 
    """Create the tables for site metadata for content managing public microsites
    """
    from hubspace.model import LocationFiles
    LocationFiles.createTable(ifNotExists=True)