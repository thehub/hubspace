import patches.base
import patches.utils
from turbogears import database
from datetime import datetime
from sqlobject import AND, IN, OR, NOT

class Patch(patches.base.Patch):
    description = "Add city field to Location - this appears in the navigation. Once the city field is created add the location.name to location.city apart from London Hubs which will be set to 'London'"
    def apply(self):
        access_tuple = patches.utils.parseDBAccessDirective()
        con = patches.utils.getPostgreSQLConnection(*access_tuple)
        cur = con.cursor()
        cur.execute("""alter table location add column city VARCHAR(40);""")
        con.commit()
        dburi = patches.utils.parseDBURI('dev.cfg').split('=')[1][1:-1]
        database.set_db_uri(dburi)
        database.run_with_transaction(add_cities)

def add_cities(): 
    """Add cities to Locations
    """
    from hubspace.model import Location
    for loc in Location.select():
        if loc.name not in ['Southbank', 'Kings Cross', 'Islington']:
            loc.city = loc.name
        else:
            loc.city = "London"

  

