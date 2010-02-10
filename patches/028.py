import patches.base
import patches.utils
from turbogears import database
from datetime import datetime
from sqlobject import AND, IN, OR, NOT

class Patch(patches.base.Patch):
    description = "Changes to microsites allowing subpages, and having lists living in the database"
    def apply(self):
        # This is copied from patch #25
        access_tuple = patches.utils.parseDBAccessDirective()
        con = patches.utils.getPostgreSQLConnection(*access_tuple)
        dburi = patches.utils.parseDBURI('dev.cfg').split('=')[1][1:-1]
        database.set_db_uri(dburi)
       
        database.run_with_transaction(setup_listtable)
        
        cur = con.cursor()
        cur.execute("ALTER TABLE list_item ADD COLUMN list_id INTEGER CONSTRAINT list_id_exists REFERENCES list(id)")
        con.commit()
        
        database.run_with_transaction(migrate_lists)
        database.run_with_transaction(create_subpage_lists)



def setup_listtable(): 
    """Create the microsites spaces object
    """
    #from hubspace.model import ObjectReference, Page, ListItem, PublicSpace, Location, MetaData, MicroSiteSpace, PublicPlace, User, List
    #from hubspace.microSite import microsite_pages, microsite_page_types, microsite_left_page_list, microsite_right_page_list, append_existing_item
    from hubspace.model import List
    List.createTable(ifNotExists=True)

def migrate_lists():
    from hubspace.model import Page, List, ListItem, Location
    from hubspace.microSite import list_types
    
    for location in Location.select():
        results = Page.selectBy(location=location,path_name='index.html')
        if results.count() == 0:
            continue;
        else:            
            indexpage = results[0] 

        for list_name, data in list_types.items():
            object_types = ','.join(data['object_types'])
            mode = data['mode']
            thelist = List(list_name=list_name,
                           object_types=object_types,
                           mode=mode,
                           page=indexpage,
                           location=location,)
            for listitem in ListItem.selectBy(location=location,list_name=list_name):
                listitem.list = thelist

def create_subpage_lists():
    from hubspace.model import Page, List
    from hubspace.microSite import list_types
    for page in Page.select():
        List(list_name='subpages_%s' % page.id,
             object_types='Page',
             mode='add_new',
             page=page,
             location=page.location)

