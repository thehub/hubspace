#!/usr/bin/python2.4

from pysqlite2 import dbapi2 as sqlite

def update_schema(con):
    cur = con.cursor()
    cur.executescript("""
        alter table rusage add column tariff_id INT CONSTRAINT tariff_id_exists REFERENCES resource(id);

        alter table pricing add column resource_id INT CONSTRAINT resource_id_exists REFERENCES resource(id);

        alter table pricing add column nextperiod_id INT CONSTRAINT nextperiod_id_exists REFERENCES pricing(id);

        alter table pricing add column periodstarts TIMESTAMP;

        alter table pricing add column periodends TIMESTAMP;
    """)
    resource = con.cursor()
    resource.execute("""UPDATE pricing SET resource_id = (SELECT resource_id FROM resource_pricing WHERE pricing.id = resource_pricing.pricing_id);""")
    periodstarts = con.cursor()
    periodstarts.executescript("""UPDATE pricing SET periodstarts = '1970-1-1 0:0:1';""")
    droptable = con.cursor()
    droptable.execute("""DROP table resource_pricing""")
    deleterusages = con.cursor()
    deleterusages.execute("""DELETE from rusage
                             WHERE rusage.id IN (SELECT rusage.id FROM rusage, resource WHERE
                                                 (rusage.resource_id = resource.id
                                                  AND resource.type = 'tariff'));""")
##     deletememberships = con.cursor()
##     deletememberships.execute("""DELETE from user_group
##                                  WHERE ((user_group.group_id IN (SELECT user_group.group_id FROM user_group, tg_user, tg_group WHERE
##                                  (user_group.group_id = tg_group.id
##                                  AND user_group.user_id = tg_user.id
##                                  AND tg_group.level = 'member'
##                                  AND NOT tg_group.place_id = tg_user.homeplace_id)))
                                 
##                                  AND (user_group.user_id IN (SELECT user_group.user_id FROM user_group, tg_user, tg_group WHERE
##                                  (user_group.group_id = tg_group.id
##                                  AND user_group.user_id = tg_user.id
##                                  AND tg_group.level = 'member'
##                                  AND NOT tg_group.place_id = tg_user.homeplace_id))));""")
                            
    

    con.commit() 


if __name__ == "__main__":
    con = sqlite.connect("hubdata.sqlite")
    update_schema(con)
