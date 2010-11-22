import patches.base
import patches.utils
from turbogears import database
from datetime import datetime
from sqlobject import AND, IN, OR, NOT

class Patch(patches.base.Patch):
    description = "Changes to the architecture of MicroSites to support the concepts of Pages, list_items, and rendered objects"
    def apply(self):
        # This is copied from patch #25
        access_tuple = patches.utils.parseDBAccessDirective()
        con = patches.utils.getPostgreSQLConnection(*access_tuple)
        cur = con.cursor()
        cur.execute("ALTER TABLE location ADD COLUMN is_region int DEFAULT 0")
        cur.execute("ALTER TABLE location add column in_region_id INTEGER CONSTRAINT in_region_id_exists REFERENCES location(id)")
        cur.execute("""alter table location add column city VARCHAR(40);""")
        con.commit()
        # end of patch # 25
        dburi = patches.utils.parseDBURI('dev.cfg').split('=')[1][1:-1]
        database.set_db_uri(dburi)
        database.run_with_transaction(setup_microsite_spaces)
        database.run_with_transaction(migrate)


def setup_microsite_spaces(): 
    """Create the microsites spaces object
    """
    from hubspace.model import ObjectReference, Page, ListItem, PublicSpace, Location, MetaData, MicroSiteSpace, PublicPlace, User
    from hubspace.microSite import microsite_pages, microsite_page_types, microsite_left_page_list, microsite_right_page_list, append_existing_item
    Page.createTable(ifNotExists=True)
    ObjectReference.createTable(ifNotExists=True)
    ListItem.createTable(ifNotExists=True)
    PublicSpace.createTable(ifNotExists=True)
    PublicPlace.createTable(ifNotExists=True)
    MetaData.createTable(ifNotExists=True)
    for user in User.select():
        ObjectReference(**{'object': (user.__class__.__name__, user.id)})

    for loc in Location.select():
        if loc.id == 16 or not loc.url:
            continue
       
        try:
            old_space = MicroSiteSpace.select(AND(MicroSiteSpace.q.locationID==loc.id,
                                                  MicroSiteSpace.q.nextID==None))[0]
        except IndexError:
            print `loc.name` + " doesn't have any spaces to migrate"
            old_space = None
            
        next_item = None
        while old_space:
            new_space = PublicSpace(name=old_space.name, description=old_space.description, image=old_space.image)
            object_ref = ObjectReference.selectBy(object_type='PublicSpace', object_id=new_space.id)[0]
            new_list_item = ListItem(next=next_item, location=loc, active=old_space.active, list_name="spaces_list", object_ref=object_ref)
            next_item = new_list_item
            old_space = old_space.previous

        ObjectReference(**{'object': (loc.__class__.__name__, loc.id)})
        for page, type in microsite_pages.items():
            microsite_page_types[type].create_page(page, loc, {})
        
        kwargs = {'location':loc, 'object_type': Page, 'active': 1}
        for page in microsite_left_page_list:
            kwargs.update({'name':page})
            try:
                page = Page.select(AND(Page.q.location == loc,
                                       IN(Page.q.path_name, [page, page + '.html'])))[0]
                append_existing_item('left_tabs', page, **kwargs)
            except IndexError:
                pass
        for page in microsite_right_page_list: 
            kwargs.update({'name':page})
            try:
                page = Page.select(AND(Page.q.location == loc,
                                       IN(Page.q.path_name, [page, page + '.html'])))[0]
                append_existing_item('right_tabs', page, **kwargs)
            except IndexError:
                pass
  

def migrate():
    from hubspace.microSite import migrate_data 
    migrate_data()

def add_cities(): 
    """Add cities to Locations
    """
    from hubspace.model import Location
    for loc in Location.select():
        if loc.name not in ['Southbank', 'Kings Cross', 'Islington']:
            loc.city = loc.name
        else:
            loc.city = "London"

 
