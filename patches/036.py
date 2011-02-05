import patches.base
import patches.utils
from turbogears import database
from datetime import datetime
from sqlobject import AND, IN, OR, NOT

class Patch(patches.base.Patch):
    description = "ensure every user and Location has an object reference"
    def apply(self):
        # This is copied from patch #25
        dburi = patches.utils.parseDBURI('dev.cfg').split('=')[1][1:-1]
        database.set_db_uri(dburi)
        database.run_with_transaction(fix_users_without_object_references)


def fix_users_without_object_references():
    from hubspace.model import User, ObjectReference, create_object_reference, Location 
    for user in User.select():
        try:
            object_ref = ObjectReference.select(AND(ObjectReference.q.object_type ==  user.__class__.__name__, 
                                                    ObjectReference.q.object_id == user.id))[0] 
        except IndexError:
            print "giving " + user.username + "an object reference"
            create_object_reference({'class':User, 'id':user.id}, None)

    for loc in Location.select():
        try:
            object_ref = ObjectReference.select(AND(ObjectReference.q.object_type ==  loc.__class__.__name__, 
                                                    ObjectReference.q.object_id == loc.id))[0] 
        except IndexError:
            create_object_reference({'class':Location, 'id':loc.id}, None)
            print "giving " + loc.name + "an object reference"

