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
        database.run_with_transaction(sync_joinus_field)

def sync_joinus_field(): 
    """Copy the existing joinus text to the joinConfirm page
    """
    from hubspace.model import Page
    for joinus_page in Page.selectBy(path_name='joinus.html'):
        Page.selectBy(path_name='joinConfirm',
                      location=joinus_page.location)[0].content = joinus_page.content
    
  

