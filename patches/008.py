import patches.base
import patches.utils
from turbogears import database

class Patch(patches.base.Patch):
    description = "Add resource_queue table"
    def apply(self):
        access_tuple = patches.utils.parseDBAccessDirective()
        dburi = patches.utils.parseDBURI('dev.cfg').split('=')[1][1:-1]
        database.set_db_uri(dburi)
        database.run_with_transaction(add_table)

def add_table():
    from hubspace.model import ResourceQueue
    ResourceQueue.createTable(ifNotExists=True)
