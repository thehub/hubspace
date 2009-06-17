from hubspace.model import RUsage, Resource, Location, User
from sqlobject import AND, OR
from hubspace.utilities.uiutils import now

##Tariff 
def get_tariff(loc, userid, usage_start_time, default=True):   
    result = Resource.select(AND(RUsage.q.resourceID == Resource.q.id,
                                 Resource.q.type=='tariff',
                                 RUsage.q.userID==userid,
                                 Resource.q.placeID==loc,
                                 RUsage.q.start <= usage_start_time,
                                 RUsage.q.end_time >= usage_start_time))

    try:
        return result[0]
    except:
        if default:
            return Location.get(loc).defaulttariff
        return None

def tariff_users(tariff):
    localtime = now(tariff.place)
    if isinstance(tariff, Resource) and tariff.type == 'tariff':
        return User.select(AND(RUsage.q.resourceID == tariff.id,
                               RUsage.q.userID == User.q.id,
                               RUsage.q.start <= localtime,
                               RUsage.q.end_time >= localtime))
        
    raise "input is not a tariff"
