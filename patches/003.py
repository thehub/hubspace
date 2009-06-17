import patches.base
from pysqlite2 import dbapi2 as sqlite
from patches.postgres_migration.sequences_sync import getPostgreSQLConnection
from hubspace.utilities.dicts import AttrDict
from turbogears import database
from sqlobject import AND

def capture_pg_uri():
    pg_user = raw_input("please enter your username for the db: ")
    pg_pass = raw_input("please enter your password for the db: ")
    return AttrDict(pg_uri="postgres://%(user)s:%(password)s@localhost/hubspace" %(dict(user=pg_user, password=pg_pass)))

import cPickle
empty_list_pickle = cPickle.dumps([])

class Patch(patches.base.Patch):
    description = "Some adjustments to postgres table...phew we can now alter columns"
    def apply(self):
        uri = capture_pg_uri()
        con = getPostgreSQLConnection(uri)
        cur = con.cursor()
        cur.execute("""
        ALTER TABLE tg_user ADD COLUMN rfid VARCHAR(40);
        ALTER TABLE location ADD COLUMN holidays BYTEA DEFAULT '%s';
        ALTER TABLE tg_user ADD COLUMN access_policies BYTEA DEFAULT '%s';
        ALTER TABLE tg_user ADD COLUMN disabled_policies BYTEA DEFAULT '%s';
        DROP TABLE open;
        ALTER TABLE location drop column opens RESTRICT,
        drop column closes RESTRICT;
        ALTER TABLE user_group add column id SERIAL PRIMARY KEY;
        ALTER TABLE resourcegroup add column group_type VARCHAR(40) DEFAULT 'member_calendar';
        ALTER TABLE location add column calendar_id INTEGER CONSTRAINT calendar_id_exists REFERENCES resource(id);
        """ %(empty_list_pickle, empty_list_pickle, empty_list_pickle))
        con.commit()
        database.set_db_uri(uri['pg_uri'])
        database.run_with_transaction(create_tables)
        database.run_with_transaction(update_locations)

def create_tables():
    from hubspace.model import AccessPolicy, Open, PolicyGroup
    PolicyGroup.createTable(ifNotExists=True)
    AccessPolicy.createTable(ifNotExists=True)
    Open.createTable(ifNotExists=True)
    
def update_locations():
    from hubspace.utilities.object import create_object
    from hubspace.openTimes import create_default_open_times, add_accessPolicy2Proxy
    from hubspace.model import Location, Group
    for location in Location.select():
        cal = create_object('Resource', type='calendar', time_based=1, active=0, place=location.id, name='calendar', description='calendar')
        location.calendar = cal.id
        for level in ['member', 'host', 'director']:
            group = Group.select(AND(Group.q.level == level,
                                     Group.q.placeID == location.id))[0]
            access_policy = add_accessPolicy2Proxy(cal, group.id, 'Group', 5, None, None)
            create_default_open_times(access_policy)
   

        # if this works then add access_policies too

        
