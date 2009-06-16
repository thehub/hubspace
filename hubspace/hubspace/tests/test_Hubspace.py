# -*- coding: iso-8859-15 -*-
"""testi FunkLoad test

$Id: $
"""
import unittest
from funkload.FunkLoadTestCase import FunkLoadTestCase
from webunit.utility import Upload

from turbogears import database, config, testutil
from hubspace import model
from hubspace.model import *
from sqlobject import AND, OR, IN
import inspect, sqlobject
from sqlobject.inheritance import InheritableSQLObject
from datetime import datetime, timedelta, time, date
from hubspace.validators import datetimeconverter, dateconverter
import re, calendar
from urllib import quote
from hubspace.openTimes import ConflictingPolicy
from time import sleep

base = '/'.join(model.__file__.split('/')[:-2])
database.set_db_uri(config.get("sqlobject.dburi"))

now = datetime.now()
year = now.year


month = now.month
fmt = '%d %B %Y %H:%M:%S'

class tmpstorage(object):
    pass

ids = tmpstorage()

def dt2string(datetime):
    return datetime.strftime(fmt)

def addmonth(dt,months):
    for i in range(1,months+1):
        dt = dt+timedelta(days=calendar.monthrange(dt.year,dt.month)[1])
    return dt

def gettime(days=0,hours=None,convert='datetime'):
    if not hours:
        hours = now.hour
    t = datetime.combine(now + timedelta(days=days), time(hours))
    if convert == 'datetime':
        return datetimeconverter.from_python(t)
    elif convert == 'date':
        return dateconverter.from_python(t)
    else:
        return t

nextmonth = addmonth(now,1)

nowplus1h = now + timedelta(hours=1)
otherday = gettime(3,8,False) #we book up to 3 days in advance

standardlogins = [('jhb','test'),
                   ('member1','test1'),
                   ('webapi','test'),
                   ('invalidlogin','wrongpassword')]

#from funkload.utils import xmlrpc_get_credential 
class Hubspace(FunkLoadTestCase):
    """XXX

    This test use a configuration file Testi.conf.
    """

    def setUp(self):
        """Setting up test."""
        self.server_url = self.conf_get('main', 'url')

        self.clearBasicAuth()
        #self.setBasicAuth('jhb','test')
        self.setBasicAuth('hubspaceadmin','secret')
        self.logd("setUp")

        # XXX here you can setup the credential access like this
        # credential_host = self.conf_get('credential', 'host')
        # credential_port = self.conf_getInt('credential', 'port')
        # self.login, self.password = xmlrpc_get_credential(credential_host,
        #                                                   credential_port)


    def call(self,url,description=None):
        return self.get(url,description)

    def getmaxid(self,objecttype):
        return int(float((self.get(self.server_url + '/maxid?objecttype=' + objecttype).body)))


    def assert_mass(self,url,assertions,logins=None,params=None,reverse=None,printresults=None):
        """self.assert_mass('/devel2/clients/',dict(testadmin=200,testeditor=200,default=401)) """
        debug = 1 
        out = []
        if not logins:
            logins = standardlogins
        if reverse:
            logins.reverse()
        if debug: 
            print 
            print 'testing %s ' % url
            if params:
                print 'POST: %s' % str(params)
        for l,p in logins:
            self.clearContext()
            self.setBasicAuth(l,p)
            if params:
                response = self.post(self.server_url + url,params=params)
            else:
                response = self.get(self.server_url + url)
            if printresults:
                print response.headers
                print response.body
            assertion = assertions.get(l,assertions.get('default','response.code == 403'))
            try:
                tmp = int(assertion)
                assertion = 'response.code == %s' % assertion
            except:
                pass
            if debug: 
                print '  with %-20s : %-35s (got %s)' % (l,assertion,response.code)    
            tmp =self.assert_(eval(assertion))
    

    
    def assert_one(self,url,assertion,user,password='test'):
        self.clearContext()
        self.setBasicAuth(user,password)
        response=self.get(self.server_url + url)
        print '  with %-20s : %-35s (got %s)' % (user,assertion,response.code)
        self.assert_(eval(assertion))

    def test_00000_run_application(self):
        # The description should be set in the configuration file
        server_url = self.server_url
        # begin of test ---------------------------------------------
        #self.clearBasicAuth()
        #self.setBasicAuth('jhb','test')
        self.setBasicAuth('hubspaceadmin','secret')


        result = self.get(self.server_url + "/setUp", description="")


        self.clearBasicAuth()
        self.setBasicAuth('jhb','test')
        result = self.get(server_url + "/create_location?name=dublin&currency=EUR") 
        ids.jhb = str(User.selectBy(user_name='jhb')[0].id)
        ids.dublin = self.getmaxid('Location')
        ids.dublin_default = self.getmaxid('Resource') - 1 # because calendar has been created too 
        ids.dublin_member = Group.select(AND(Group.q.placeID==ids.dublin,
                                             Group.q.level=='member'))[0].id
        ids.dublin_host = Group.select(AND(Group.q.placeID==ids.dublin,
                                           Group.q.level=='host'))[0].id
        ids.dublin_director = Group.select(AND(Group.q.placeID==ids.dublin,
                                               Group.q.level=='director'))[0].id

        result = self.get(server_url + "/create_user?billto=&homeplace=%s&first_name=host&last_name=1&user_name=host1&password2=test1&password=test1&email_address=host1%%40test.com&active=1" % ids.dublin)

        ids.dublin_host1 = self.getmaxid('User')
        
        result = self.get(server_url + "/create_user?billto=&homeplace=%s&first_name=host&last_name=2&user_name=host2&password2=test1&password=test1&email_address=host2%%40test.com&active=1" % ids.dublin)


        ids.dublin_host2 = self.getmaxid('User')

        result = self.get(server_url + "/create_user?billto=&homeplace=%s&first_name=member&last_name=1&user_name=member1&password2=test1&password=test1&email_address=member1%%40test.com&active=1" % ids.dublin)

        ids.dublin_member1 = self.getmaxid('User')

        result = self.get(server_url + "/create_user?billto=&homeplace=%s&first_name=member&last_name=2&user_name=member2&password2=test1&password=test1&email_address=member2%%40test.com&active=1" % ids.dublin)


        ids.dublin_member2 = self.getmaxid('User')
        result = self.get(server_url + "/create_user?billto=&homeplace=%s&first_name=director&last_name=1&user_name=director1&password2=test1&password=test1&email_address=director1%%40test.com&active=1" % ids.dublin)

        ids.dublin_director1 = self.getmaxid('User')

        result = self.get(server_url + "/create_user?billto=&homeplace=%s&first_name=director&last_name=2&user_name=director2&password2=test1&password=test1&email_address=director2%%40test.com&active=1" % ids.dublin)

        ids.dublin_director2 = self.getmaxid('User')

        for id in ['host', 'director', 'member']:
            for i in range(1,3):
                url = "/addUser2Group?user=%s&group=%s"% (getattr(ids,'dublin_%s%s' %(id,i)), getattr(ids,'dublin_'+id))

                self.assert_mass(url,assertions=dict(jhb=200))

        self.clearBasicAuth()
        self.setBasicAuth('jhb','test')

        result = self.get(server_url + "/create_tariff?active=True&place=%s&name=tariff1000&description=Tariff+tariff1000+in+dublin&tariff_cost=20" % ids.dublin)
        ids.dublin_tariff1000 = self.getmaxid('Resource')

        result = self.get(server_url + "/create_tariff?active=True&place=%s&name=tariff2000&description=Tariff+tariff2000+in+dublin&tariff_cost=40" % ids.dublin)

        ids.dublin_tariff2000 = self.getmaxid('Resource')

        result = self.get(server_url + "/create_tariff?active=True&place=%s&name=tariff3000&description=Tariff+tariff3000+in+dublin&tariff_cost=60" % ids.dublin)

        ids.dublin_tariff3000 = self.getmaxid('Resource')

        result = self.get(server_url + "/create_resource?type=printer&place=%s&name=printer1&description=Resource+printer1+in+dublin&tariffs-1.id=%s&tariffs-1.cost=%s&tariffs-2.id=%s&tariffs-2.cost=%s&tariffs-3.id=%s&tariffs-3.cost=%s&tariffs-4.id=%s&tariffs-4.cost=%s" %(ids.dublin, ids.dublin_tariff1000, 21, ids.dublin_tariff2000, 64, ids.dublin_tariff3000, 14, ids.dublin_default, 75.01))

        ids.dublin_printer1 = self.getmaxid('Resource')

        result = self.get(server_url + "/create_resource?type=printer&place=%s&name=printer2&description=Resource+printer2+in+dublin&tariffs-1.id=%s&tariffs-1.cost=%s&tariffs-2.id=%s&tariffs-2.cost=%s&tariffs-3.id=%s&tariffs-3.cost=%s&tariffs-4.id=%s&tariffs-4.cost=%s" %(ids.dublin, ids.dublin_tariff1000, 14, ids.dublin_tariff2000, 44, ids.dublin_tariff3000, 23, ids.dublin_default, 55))


        ids.dublin_printer2 = self.getmaxid('Resource')

        result = self.get(server_url + "/create_resource?type=hotdesk&time_based=1&place=%s&name=hotdesk1&description=Resource+hotdesk1+in+dublin&tariffs-1.id=%s&tariffs-1.cost=%s&tariffs-2.id=%s&tariffs-2.cost=%s&tariffs-3.id=%s&tariffs-3.cost=%s&tariffs-4.id=%s&tariffs-4.cost=%s" %(ids.dublin, ids.dublin_tariff1000, 20.343, ids.dublin_tariff2000, 44.34, ids.dublin_tariff3000, 52, ids.dublin_default, 65))

        ids.dublin_hotdesk1 = self.getmaxid('Resource')

        result = self.get(server_url + "/create_resource?type=hotdesk&time_based=1&place=%s&name=hotdesk2&description=Resource+hotdesk2+in+dublin&tariffs-1.id=%s&tariffs-1.cost=%s&tariffs-2.id=%s&tariffs-2.cost=%s&tariffs-3.id=%s&tariffs-3.cost=%s&tariffs-4.id=%s&tariffs-4.cost=%s" %(ids.dublin, ids.dublin_tariff1000, 20, ids.dublin_tariff2000, 40, ids.dublin_tariff3000, 80, ids.dublin_default, 105))

        ids.dublin_hotdesk2 = self.getmaxid('Resource')

        result = self.get(server_url + "/create_resource?type=room&time_based=1&place=%s&name=room1&description=Resource+room1+in+dublin&tariffs-1.id=%s&tariffs-1.cost=%s&tariffs-2.id=%s&tariffs-2.cost=%s&tariffs-3.id=%s&tariffs-3.cost=%s&tariffs-4.id=%s&tariffs-4.cost=%s" %(ids.dublin, ids.dublin_tariff1000, 10, ids.dublin_tariff2000, 20, ids.dublin_tariff3000, 40, ids.dublin_default, 80))
        
        ids.room1id = self.getmaxid('Resource')
        ids.dublin_room1 = ids.room1id

        result = self.get(server_url + "/create_resource?type=room&time_based=1&place=%s&name=room2&description=Resource+room2+in+dublin&tariffs-1.id=%s&tariffs-1.cost=%s&tariffs-2.id=%s&tariffs-2.cost=%s&tariffs-3.id=%s&tariffs-3.cost=%s&tariffs-4.id=%s&tariffs-4.cost=%s" %(ids.dublin, ids.dublin_tariff1000, 1, ids.dublin_tariff2000, 2, ids.dublin_tariff3000, 4, ids.dublin_default, 5))

        ids.room2id = self.getmaxid('Resource')
        ids.dublin_room2 = ids.room2id

        result = self.get(server_url + "/add_requirement?resourceid=%s&requirementid=%s" % (ids.room1id,ids.room2id))


        self.get(server_url + "/save_tariffHistoryEdit?location=%s&id=%s&tariff.%s.%s=%s" % (ids.dublin, ids.dublin_member1, now.year, now.month, ids.dublin_tariff1000))
        
        self.get(server_url + "/save_tariffHistoryEdit?location=%s&id=%s&tariff.%s.%s=%s" % (ids.dublin, ids.dublin_member1, otherday.year, otherday.month, ids.dublin_tariff1000))

        self.get(server_url + "/save_tariffHistoryEdit?location=%s&id=%s&tariff.%s.%s=%s" % (ids.dublin, ids.dublin_member2, now.year, now.month, ids.dublin_tariff2000))

        self.get(server_url + "/save_tariffHistoryEdit?location=%s&id=%s&tariff.%s.%s=%s" % (ids.dublin, ids.dublin_member2, nextmonth.year, nextmonth.month, ids.dublin_tariff2000))

        result = self.get(server_url + "/book_resource",dict(start_datetime=gettime(0,9),
                                                             end_datetime=gettime(0,10),
                                                             location=ids.dublin,
                                                             resource_id=ids.dublin_hotdesk1,
                                                             user=ids.dublin_member1))

        result = self.get(server_url + "/book_resource",dict(start_datetime=gettime(0,12),
                                                             end_datetime=gettime(0,14),
                                                             location=ids.dublin,
                                                             resource_id=ids.dublin_room1,
                                                             user=ids.dublin_member1))
        result = self.get(server_url + "/book_resource",dict(start_datetime=gettime(0,8),
                                                    end_datetime=gettime(0,9),
                                                    location=ids.dublin,
                                                    resource_id=ids.dublin_hotdesk2,
                                                    user=ids.dublin_member1))
        result = self.get(server_url + "/book_resource",dict(start_datetime=gettime(0,9),
                                                    end_datetime=gettime(0,9),
                                                    location=ids.dublin,
                                                    resource_id=ids.dublin_printer1,
                                                    user=ids.dublin_member1))
        ids.rusage = self.getmaxid('RUsage')


        result = self.get(server_url + "/create_invoice?autocollect=True&userid=%s" % ids.dublin_member1)

        ids.invoice = self.getmaxid('Invoice')


        result = self.get(server_url + "/remove_rusage_from_invoice?invoiceid=%s&rusageid=%s" % (ids.invoice,
                                                                                                        ids.rusage))


        #self.get(server_url + "/book_resource?resource=8&user=5&invoice=2&location=3",
        #         description="")


        response = self.get(server_url + "/create_todo?createdby=%s&subject=Travel+to+Dublin&parent=1&body=by+train" % ids.dublin_host1)
        
    def test_0010_jhb_testing(self):
        return
        # The description should be set in the configuration file
        server_url = self.server_url

        response =self.get(server_url + "/dublin/jhb",
                           description="")
        assert(response.code==403)
    
    def test_0020_access_policies(self):
        self.setBasicAuth('jhb','test')
        #create a policy group
        #result = self.post(self.server_url + "/create_policy_group", params=[['name', 'Special Users'], ['loc_id',"1"]])
        result = self.get(self.server_url + "/create_policy_group?name=Special%20Users&loc_id=1")
        pol_group_id = self.getmaxid('PolicyGroup')
        user_id = self.getmaxid('User')
        #add an accesspolicy associated to the policy group
        ids.policy_resource_1 = 1
        ids.policy_resource_2 = 2
        self.get(self.server_url + "/add_accessPolicy2Proxy?policyResource_id=%s&policyProxy_id=%s&policyProxy_type=PolicyGroup&policyStartDate=%s&policyEndDate=%s&precedence=5" %(ids.policy_resource_1, pol_group_id, quote(dateconverter.from_python(datetime.now())), quote(dateconverter.from_python(datetime.now()+timedelta(days=30)))))
        #do it again to see that it fails
        try:
            self.get(self.server_url + "/add_accessPolicy2Proxy?policyResource_id=%s&policyProxy_id=%s&policyProxy_type=PolicyGroup&policyStartDate=%s&policyEndDate=%s" %(ids.policy_resource_1, pol_group_id, quote(dateconverter.from_python(datetime.now())), quote(dateconverter.from_python(datetime.now()+timedelta(days=30)))))
            raise "fail here, this shouldn't have worked"
        except AssertionError:
            pass
        
        
        #add a user to the policygroup
        self.get(self.server_url + "/add_user2policy_group?polgroup_id=%s&user_id=%s"%(str(pol_group_id), str(user_id)))

        # assert that the user has the access policy
        assert(self.getmaxid('AccessPolicy') in User.get(user_id).access_policies)
        
        self.get(self.server_url + "/add_accessPolicy2Proxy?policyResource_id=%s&policyProxy_id=%s&policyProxy_type=PolicyGroup&policyStartDate=%s&policyEndDate=%s" %(ids.policy_resource_2, pol_group_id, quote(dateconverter.from_python(datetime.now())), quote(dateconverter.from_python(datetime.now()+timedelta(days=30)))))
        # assert that the user has the access policy
        User._connection.cache.clear()
        assert(self.getmaxid('AccessPolicy') in User.get(user_id).access_policies)
        membership = UserPolicyGroup.select(AND(UserPolicyGroup.q.policygroupID==pol_group_id,
                                                UserPolicyGroup.q.userID==user_id))
        assert(membership.count()==1)
        
        # add some entry times to the access policy for door_2 in location 1
        pol_id = self.getmaxid('AccessPolicy')

        # specifically make it accessible on wednesdays from now on at 9.30am-5.15pm
        today = date.today()
        if today.weekday() <= 2:
            day_diff = 2 - today.weekday()
        else:
            day_diff = 9 - today.weekday() 
        next_wed_dtime = datetime.combine(today, time(0, 0)) + timedelta(days=day_diff)
        next_wed_d = next_wed_dtime.date()
            
        self.get(self.server_url + "/create_openTime?pol_id=%s&openTimeDay=2&openTimeStartDate=%s&openTimeStart=%s&openTimeEnd=%s" %(pol_id, quote(dateconverter.from_python(datetime.combine(today, time(0, 0)))), quote("9:30am"), quote("5:15pm")))
        #should enter door_2         
        # check we can enter on wednesday @ 10.15am
        access_pol = AccessPolicy.get(pol_id)
        allow = self.get(self.server_url + '/check_access?user_id=%s&loc_id=%s&policyResource_id=%s&check_datetime=%s' %(user_id, access_pol.location.id, access_pol.policy_resource.id, quote(datetimeconverter.from_python(datetime.combine(next_wed_d, time(10, 15))))))
        
        assert(allow.body=="Allowed")
        # override next wednesday on the policy, DD, MM, YYYY with 11.45am-5.15pm
        self.get(self.server_url + "/create_openTime?pol_id=%s&openTimeDate=%s&openTimeStart=%s&openTimeEnd=%s" %(pol_id, quote(dateconverter.from_python(next_wed_dtime)), quote("11:45am"), quote("5:15pm")))
        # door_2 can be opened on next_wed_day between 11.45am-5.15pm

        # check we cannot enter on wednesday @ 10.15am
        allow = self.get(self.server_url + '/check_access?user_id=%s&loc_id=%s&policyResource_id=%s&check_datetime=%s' %(user_id, access_pol.location.id, access_pol.policy_resource.id, quote(datetimeconverter.from_python(datetime.combine(next_wed_d, time(10, 15))))))
        assert(allow.body=='')

        # but can at 12.30pm
        allow = self.get(self.server_url + '/check_access?user_id=%s&loc_id=%s&policyResource_id=%s&check_datetime=%s' %(user_id, access_pol.location.id, access_pol.policy_resource.id, quote(datetimeconverter.from_python(datetime.combine(next_wed_d, time(12, 30))))))
        assert(allow.body=='Allowed')
        
        # test precedence of access policies (higher precedence policies should override lower precedence)
        # create a higher precedence policy on the member group/role, such that it overlap its times with those in the lower precedence policy
        # ...but first put the user in the member 'group/role'
        self.get(self.server_url + "/addUser2Group?user=15&group=1")

        self.get(self.server_url + "/add_accessPolicy2Proxy?policyResource_id=%s&policyProxy_id=1&policyProxy_type=Group&policyStartDate=%s&policyEndDate=%s&precedence=2" %(ids.policy_resource_2, quote(dateconverter.from_python(datetime.now())), quote(dateconverter.from_python(datetime.now()+timedelta(days=30)))))
        pol_id = self.getmaxid('AccessPolicy')
        self.get(self.server_url + "/create_openTime?pol_id=%s&openTimeDate=%s&openTimeStart=%s&openTimeEnd=%s" %(pol_id, quote(dateconverter.from_python(next_wed_dtime)), quote("3:00pm"), quote("4:30pm")))
        # door_2 can be opened on next_wed_day between 3pm-4.30pm
        
        # see that the new policy has overriden the old
        allow = self.get(self.server_url + '/check_access?user_id=%s&loc_id=%s&policyResource_id=%s&check_datetime=%s' %(user_id, access_pol.location.id, access_pol.policy_resource.id, quote(datetimeconverter.from_python(datetime.combine(next_wed_d, time(12, 30))))))
        assert(allow.body=="")

        allow = self.get(self.server_url + '/check_access?user_id=%s&loc_id=%s&policyResource_id=%s&check_datetime=%s' %(user_id, access_pol.location.id, access_pol.policy_resource.id, quote(datetimeconverter.from_python(datetime.combine(next_wed_d, time(16, 00))))))
        assert(allow.body=="Allowed")

        allow = self.get(self.server_url + '/check_access?user_id=%s&loc_id=%s&policyResource_id=%s&check_datetime=%s' %(user_id, access_pol.location.id, access_pol.policy_resource.id, quote(datetimeconverter.from_python(datetime.combine(next_wed_d, time(16, 45))))))

        assert(allow.body=="")

        #remove the most recently added access policy
        self.get(self.server_url + "/remove_accessPolicy2Proxy?id=%s" %(self.getmaxid('AccessPolicy')))
        # door_2 can be opened on next_wed_day between 11.45am-5.15pm
        
        allow = self.get(self.server_url + '/check_access?user_id=%s&loc_id=%s&policyResource_id=%s&check_datetime=%s' %(user_id, access_pol.location.id, access_pol.policy_resource.id, quote(datetimeconverter.from_python(datetime.combine(next_wed_d, time(17, 00))))))

        assert(allow.body=="Allowed")

        allow = self.get(self.server_url + '/check_access?user_id=%s&loc_id=%s&policyResource_id=%s&check_datetime=%s' %(user_id, access_pol.location.id, access_pol.policy_resource.id, quote(datetimeconverter.from_python(datetime.combine(next_wed_d, time(17, 30))))))

        assert(allow.body=="")

        # test access policies with same precedence (should be additive)
        # create another "precedence 5" policy,  this time associated with 'host' group/role. See that the user can come in when either policy applies.
        self.get(self.server_url + "/add_accessPolicy2Proxy?policyResource_id=%s&policyProxy_id=2&policyProxy_type=Group&policyStartDate=%s&policyEndDate=%s&precedence=5" %(ids.policy_resource_2, quote(dateconverter.from_python(datetime.now())), quote(dateconverter.from_python(datetime.now()+timedelta(days=30)))))
        self.get(self.server_url + "/addUser2Group?user=15&group=2")

        pol_id = self.getmaxid('AccessPolicy')
        
        self.get(self.server_url + "/create_openTime?pol_id=%s&openTimeDate=%s&openTimeStart=%s&openTimeEnd=%s" %(pol_id, quote(dateconverter.from_python(next_wed_dtime)), quote("10:00am"), quote("11:15am")))
        # door_2 can be opened on next_wed_day between 10am-11.15pm and 11.45am-5.15pm
        allow = self.get(self.server_url + '/check_access?user_id=%s&loc_id=%s&policyResource_id=%s&check_datetime=%s' %(user_id, access_pol.location.id, access_pol.policy_resource.id, quote(datetimeconverter.from_python(datetime.combine(next_wed_d, time(10, 45))))))
        assert(allow.body=="Allowed")

        allow = self.get(self.server_url + '/check_access?user_id=%s&loc_id=%s&policyResource_id=%s&check_datetime=%s' %(user_id, access_pol.location.id, access_pol.policy_resource.id, quote(datetimeconverter.from_python(datetime.combine(next_wed_d, time(11, 35))))))
        assert(allow.body=="")

        allow = self.get(self.server_url + '/check_access?user_id=%s&loc_id=%s&policyResource_id=%s&check_datetime=%s' %(user_id, access_pol.location.id, access_pol.policy_resource.id, quote(datetimeconverter.from_python(datetime.combine(next_wed_d, time(12, 00))))))
        assert(allow.body=="Allowed")
            
        self.get(self.server_url + "/delete_openTime?id=%s" %(self.getmaxid('Open')))
        
        self.get(self.server_url + "/create_openTime?pol_id=%s&openTimeDate=%s&openTimeStart=%s&openTimeEnd=%s" %(pol_id, quote(dateconverter.from_python(next_wed_dtime)), quote("10:00am"), quote("1:00pm")))
        allow = self.get(self.server_url + '/check_access?user_id=%s&loc_id=%s&policyResource_id=%s&check_datetime=%s' %(user_id, access_pol.location.id, access_pol.policy_resource.id, quote(datetimeconverter.from_python(datetime.combine(next_wed_d, time(11, 35))))))
        assert(allow.body=="Allowed")

        # door_2 can be opened on next_wed_day between 10am-5.15pm
        allow = self.get(self.server_url + '/check_access?user_id=%s&loc_id=%s&policyResource_id=%s&check_datetime=%s' %(user_id, access_pol.location.id, access_pol.policy_resource.id, quote(datetimeconverter.from_python(datetime.combine(next_wed_d, time(11, 35))))))
        assert(allow.body=="Allowed")
        allow = self.get(self.server_url + '/check_access?user_id=%s&loc_id=%s&policyResource_id=%s&check_datetime=%s' %(user_id, access_pol.location.id, access_pol.policy_resource.id, quote(datetimeconverter.from_python(datetime.combine(next_wed_d, time(17, 15))))))
        assert(allow.body=="Allowed")
        allow = self.get(self.server_url + '/check_access?user_id=%s&loc_id=%s&policyResource_id=%s&check_datetime=%s' %(user_id, access_pol.location.id, access_pol.policy_resource.id, quote(datetimeconverter.from_python(datetime.combine(next_wed_d, time(18, 00))))))
        assert(allow.body=="")
        
        self.get(self.server_url + "/create_openTime?pol_id=%s&openTimeDate=%s&openTimeStart=%s&openTimeEnd=%s" %(pol_id, quote(dateconverter.from_python(next_wed_dtime)), quote("5:00pm"), quote("6:00pm")))
        # door_2 can be opened on next_wed_day between 10am-6pm
        allow = self.get(self.server_url + '/check_access?user_id=%s&loc_id=%s&policyResource_id=%s&check_datetime=%s' %(user_id, access_pol.location.id, access_pol.policy_resource.id, quote(datetimeconverter.from_python(datetime.combine(next_wed_d, time(18, 00))))))
        assert(allow.body=="Allowed")

        
        # create and test tariff policies
        # this tariff access_policy should override all other access_policies for door_2 since it has precedence 1. Our dublin_director2 (user.id=15) should have it.
        ids.london = 1
        ids.london_tariff1000 = 4
        ids.london_tariff2000 = 5
        self.get(self.server_url + "/add_accessPolicy2Proxy?policyResource_id=%s&policyProxy_id=%s&policyProxy_type=Resource&precedence=1" %(ids.policy_resource_2, ids.london_tariff1000))
        pol_id = self.getmaxid("AccessPolicy")
        self.get(self.server_url + "/create_openTime?pol_id=%s&openTimeDate=%s&openTimeStart=%s&openTimeEnd=%s" %(pol_id, quote(dateconverter.from_python(next_wed_dtime)), quote("11:00am"), quote("1:15pm")))
        self.get(self.server_url + "/save_tariffHistoryEdit?location=%s&id=%s&tariff.%s.%s=%s" % (ids.london, ids.dublin_director2, now.year, now.month, ids.london_tariff1000))

        # door_2 can be opened be opened next_wed_day between 11:00-13:15
        allow = self.get(self.server_url + '/check_access?user_id=%s&loc_id=%s&policyResource_id=%s&check_datetime=%s' %(user_id, access_pol.location.id, access_pol.policy_resource.id, quote(datetimeconverter.from_python(datetime.combine(next_wed_d, time(11, 30))))))
        assert(allow.body=="Allowed")
                 
        allow = self.get(self.server_url + '/check_access?user_id=%s&loc_id=%s&policyResource_id=%s&check_datetime=%s' %(user_id, access_pol.location.id, access_pol.policy_resource.id, quote(datetimeconverter.from_python(datetime.combine(next_wed_d, time(13, 30))))))
        assert(allow.body=="")
                 
        allow = self.get(self.server_url + '/check_access?user_id=%s&loc_id=%s&policyResource_id=%s&check_datetime=%s' %(user_id, access_pol.location.id, access_pol.policy_resource.id, quote(datetimeconverter.from_python(datetime.combine(next_wed_d, time(10, 10))))))
        assert(allow.body=="")


        # now on changing the tariff to dublin_tariff2000 we should revert to the previous situation 10am-6pm
        self.get(self.server_url + "/save_tariffHistoryEdit?location=%s&id=%s&tariff.%s.%s=%s" % (ids.london, ids.dublin_director2, now.year, now.month, ids.london_tariff2000))

        allow = self.get(self.server_url + '/check_access?user_id=%s&loc_id=%s&policyResource_id=%s&check_datetime=%s' %(ids.dublin_director2, ids.london, access_pol.policy_resource.id, quote(datetimeconverter.from_python(datetime.combine(next_wed_d, time(10, 10))))))
        assert(allow.body=="Allowed")

        # add a new accessPolicy associated with the user's new tariff this should be additive with the existing 10-6
        self.get(self.server_url + "/add_accessPolicy2Proxy?policyResource_id=%s&policyProxy_id=%s&policyProxy_type=Resource&precedence=5" %(ids.policy_resource_2, ids.london_tariff2000))
        pol_id = self.getmaxid("AccessPolicy")
        self.get(self.server_url + "/create_openTime?pol_id=%s&openTimeDate=%s&openTimeStart=%s&openTimeEnd=%s" %(pol_id, quote(dateconverter.from_python(next_wed_dtime)), quote("9:00am"), quote("12:15pm")))
        self.get(self.server_url + "/create_openTime?pol_id=%s&openTimeDate=%s&openTimeStart=%s&openTimeEnd=%s" %(pol_id, quote(dateconverter.from_python(next_wed_dtime)), quote("6:00pm"), quote("7:15pm")))

        allow = self.get(self.server_url + '/check_access?user_id=%s&loc_id=%s&policyResource_id=%s&check_datetime=%s' %(user_id, access_pol.location.id, access_pol.policy_resource.id, quote(datetimeconverter.from_python(datetime.combine(next_wed_d, time(18, 10))))))
        assert(allow.body=="Allowed")

        allow = self.get(self.server_url + '/check_access?user_id=%s&loc_id=%s&policyResource_id=%s&check_datetime=%s' %(user_id, access_pol.location.id, access_pol.policy_resource.id, quote(datetimeconverter.from_python(datetime.combine(next_wed_d, time(19, 20))))))
        assert(allow.body=="")
                 
        allow = self.get(self.server_url + '/check_access?user_id=%s&loc_id=%s&policyResource_id=%s&check_datetime=%s' %(user_id, access_pol.location.id, access_pol.policy_resource.id, quote(datetimeconverter.from_python(datetime.combine(next_wed_d, time(9, 10))))))
        assert(allow.body=="Allowed")

        # XXX test making users inactive and active again
        # XXX find a way to test the reassignment of tariffs on the turbn of the month

        #remove an access policy
        self.get(self.server_url + "/remove_accessPolicy2Proxy?id=%s" %(self.getmaxid('AccessPolicy')))
        self.get(self.server_url + "/remove_accessPolicy2Proxy?id=%s" %(self.getmaxid('AccessPolicy')))
        self.get(self.server_url + "/remove_accessPolicy2Proxy?id=%s" %(self.getmaxid('AccessPolicy')))        
        #check that the user now only has the first two access policies
        User._connection.cache.clear()
        assert(User.get(user_id).access_policies==[1, 3, 4, 5])


        #check that the user can't access at the times made possible by the removed access_policy
        allow = self.get(self.server_url + '/check_access?user_id=%s&loc_id=%s&policyResource_id=%s&check_datetime=%s' %(user_id, access_pol.location.id, access_pol.policy_resource.id, quote(datetimeconverter.from_python(datetime.combine(next_wed_d, time(11, 35))))))
        assert(allow.body=="")

        
        self.get(self.server_url + "/remove_user2policy_group?polgroup_id=%s&user_id=%s"%(str(pol_group_id), str(user_id)))

        membership = UserPolicyGroup.select(AND(UserPolicyGroup.q.policygroupID==pol_group_id,
                                                UserPolicyGroup.q.userID==user_id))
        assert(membership.count()==0)
        
        result = self.get(self.server_url + "/remove_policy_group?id="+str(pol_group_id))
        assert(PolicyGroup.select().count()==0)
    

    def test_0030_simple_invoice(self):
        # The description should be set in the configuration file
        server_url = self.server_url
        self.setBasicAuth('jhb','test')
        #resource 8 is printer1
        #resource 9 is printer2
        #resource 10 is hotdesk1

        #5 member1
        #6 member2
        #and now member3
        print 'ids', `ids.__dict__`
        self.get(server_url + "/create_user?billto=%s&homeplace=%s&first_name=member&last_name=3&user_name=member3&password2=test1&password=test1&email_address=member3%%40test.com&active=1" % (ids.dublin_member1,ids.dublin))

        ids.dublin_member3 = self.getmaxid('User')


        self.get(server_url + "/save_tariffHistoryEdit?location=%s&id=%s&tariff.%s.%s=%s" % (ids.dublin, ids.dublin_member3, year, month, ids.dublin_tariff1000))

        self.get(server_url + "/save_tariffHistoryEdit?location=%s&id=%s&tariff.%s.%s=%s" % (ids.dublin, ids.dublin_member3, otherday.year, otherday.month, ids.dublin_tariff1000))

        bookprinter = server_url + "/book_resource?resource_id=%s&user=%s&location=%s" % (ids.dublin_printer1, ids.dublin_member3, ids.dublin)
        self.get(bookprinter)
        self.get(bookprinter)
        self.get(bookprinter)
        self.get(bookprinter)
        self.get(bookprinter)
        
        bookprinter = server_url + "/book_resource?resource_id=%s&user=%s&location=%s" % (ids.dublin_printer2,
                                                                                       ids.dublin_member3,
                                                                                       ids.dublin)
        self.get(bookprinter)

        self.get(server_url + "/book_resource",dict(resource_id=ids.dublin_hotdesk1,
                                                    user=ids.dublin_member3,
                                                    location=ids.dublin,
                                                    start_datetime=gettime(2,10),
                                                    end_datetime=gettime(2,11)))

        self.get(server_url + "/book_resource",dict(resource_id=ids.dublin_room1,
                                                    user=ids.dublin_member3,
                                                    location=ids.dublin,
                                                    start_datetime=gettime(2,10),
                                                    end_datetime=gettime(2,11)))
 

        #create invoice - we expect to see also user 9's usage to appear on the invoice on user 5
        result = self.get(server_url + "/create_invoice?autocollect=True&userid=%s" % ids.dublin_member1)
        ids.invoice = self.getmaxid('Invoice')
        #from hubspace.model import RUsage
        #raise `[rus for rus in RUsage.select(RUsage.q.invoiceID==3)]`

        #sent an invoice, old one: 2
        result = self.get(server_url + "/send_invoice?invoiceid=%s" % (ids.invoice-1))
        
        


    def test_0040_hosting(self):
        server_url = self.server_url
        self.setBasicAuth('jhb','test')
        
        result = self.get(server_url + "/create_todo?createdby=%s&subject=My+lovely+parent+bar&parent=&foruser=3&body=" % ids.dublin_host1)

        ids.todo2 = self.getmaxid('Todo')

        result = self.get(server_url + "/create_todo",dict(createdby=ids.dublin_host1,
                                                          subject='first child',
                                                          parent=ids.todo2,
                                                          body=""))

        result = self.get(server_url + "/create_todo",dict(createdby=ids.dublin_host1,
                                                          subject='second child',
                                                          parent=ids.todo2,
                                                          body=""))

        result = self.get(server_url + "/create_todo",dict(createdby=ids.dublin_host1,
                                                          subject='something urgent',
                                                          parent=ids.todo2,
                                                          body="",
                                                          due=datetimeconverter.from_python(now-timedelta(hours=5))))

    def test_0050_booking_conflicts(self):
        server_url = self.server_url
        self.setBasicAuth('jhb','test')
        #book a resource which has dependencies

        oneday = timedelta(days=1)
        morning = datetime.combine(now + oneday,time(8)) 

        future1 = now + oneday
        future2 = nowplus1h + oneday
        future3 = future1 + oneday
        future4 = future2 + oneday

        #now book the resource
        result = self.get(server_url + "/book_resource", dict(resource_id=ids.dublin_room1,
                                                              location=ids.dublin,
                                                              user=ids.dublin_member1,
                                                              start_datetime=gettime(1,8),
                                                              end_datetime=gettime(1,9)))
        #check with a booking being present
        response = self.get(server_url + "/booking_conflicts", dict(resourceid = ids.dublin_room1,
                                                                    start=gettime(1,8),
                                                                    end=gettime(1,9)))
        assert(response.body!='')
        


        #now book a dependeny resource
        result = self.get(server_url + "/book_resource", dict(resource_id=ids.dublin_room2,
                                                              location=ids.dublin,
                                                              user=ids.dublin_member1,
                                                              start_datetime=gettime(1,10),
                                                              end_datetime=gettime(1,11)))

        #check with a booking of a dependency booking being present
        response = self.get(server_url + "/booking_conflicts", dict(resourceid = ids.dublin_room1,
                                                                    start=gettime(1,10),
                                                                    end=gettime(1,11)))
        assert(response.body!='')



    def test_0060_user_image(self):
        server_url = self.server_url
        self.setBasicAuth('jhb','test')
        return 
        #self.post(server_url + "/uploadImage", dict(image=Upload("/home/joerg/projects/hubspace/hubspace/hubspace/tests/images/jhb.jpg"),
        #                                            userid=2))
        
        self.post(server_url + "/uploadImage",params=[['image',Upload("/home/joerg/projects/hubspace/hubspace/hubspace/tests/images/jhb.jpg")]])


    def test_0070_user_page_edits(self):
        userid = ids.dublin_member2
        domids = ['memberProfile_%sEdit' % userid,
                  'memberDescription_%sEdit' % userid,
                  'memberServices_%sEdit' % userid,
                  'tariffHistory-%sEdit' % userid]
        for id in domids:
            #hidden = "re.findall(r'display:none.*%s',response.body)" % id
            #nottest = "re.findall(r'visibility:hidden.*%s',response.body)" % id
            #visible  = 'not ' + hidden
            visible = '''re.findall('id="%s"', response.body)''' % id
            hidden = 'not ' + visible
            self.assert_mass('/load_tab?section=mainProfile&object_type=User&object_id=%s' % ids.dublin_member2,
                             assertions=dict(jhb=visible, member1=hidden, webapi=hidden), printresults=True)



    def test_0080_save_memberProfileEdit(self):
        self.assert_mass('/save_memberProfileEdit?id=%s&value=undefined&user_name=jhb&password=&password2=&first_name=Joerg&last_name=Baach&title=God&organisation=Universe&mobile=7777777777&work=777777777&home=77777777&fax=&email_address=mail%%40baach.de&email2=&email3=&website=&address=lala%%20land&sip_id=&skype_id=LordBaach&homeplace=1&active=1' % ids.jhb,
                         assertions=dict(jhb=200,member1=403))

    def test_0090_save_memberDescriptionEdit(self):
        self.assert_mass('/save_memberDescriptionEdit?id=%s&value=undefined&description=foobar&_=' % ids.jhb,
                         assertions=dict(jhb=200,member1=403))

    def test_0100_save_memberCommunitiesEdit(self):
        self.assert_mass('/save_memberCommunitiesEdit?id=%s&value=undefined&Designing%%20places%%20and%%20spaces=on&_=' % ids.jhb,
                         assertions=dict(jhb=200,member1=403))

    def test_0110_save_memberServicesEdit(self):
        self.assert_mass('/save_memberServicesEdit?id=%s&value=undefined&handset=&ext=&frank_pin=1234&gb_storage=&os=&storage_loc=&_=' % ids.jhb, assertions=dict(jhb=200,member1=403))
    
    def test_0120_save_tariffHistoryEdit(self):
        plus1 = addmonth(now,1)
        plus2 = addmonth(now,2)
        print 'dates', now, plus1, plus2

        self.assert_mass('/save_tariffHistoryEdit?id=%s&value=undefined&location=1&tariff.%s.%s=4&tariff.%s.%s=4&tariff.%s.%s=4&_=' % (ids.jhb, now.year,now.month, plus1.year,plus1.month,plus2.year,plus2.month),
        #self.assert_mass('/save_tariffHistoryEdit?id=2&value=undefined&location=1',
                          assertions=dict(jhb=200,member1=403))
        
    def test_0130_updateUserOutstanding(self):
        self.assert_mass('/updateUserOutstanding?userid=%s&amount=20' % ids.dublin_member1,
                         assertions = dict(jhb=200,member1=403))

    def test_0140_userList(self):
        self.assert_mass('/user_list?place=%s' % ids.dublin,
                         assertions = dict(jhb=200,webapi=403,member1=403))
    def test_0142_sageUserList(self):
        self.assert_mass('/sage_user_list?place=%s' %ids.dublin,
                         assertions = dict(jhb=200,webapi=403,member1=403))

    def test_0144_invoiceList(self):
        url = '/invoice_list/'+str(ids.dublin)+'/'+dateconverter.from_python(datetime.now()-timedelta(days=30))+'/'+dateconverter.from_python(datetime.now())+'/'
        url = url.replace(' ','%20')
        self.assert_mass(url,
                         assertions = dict(jhb=200,webapi=403,member1=403))

    def test_0150_apiBooking(self):
        self.assert_mass('/book_resource?user=%s&resource_id=%s&quantity=5' % (ids.dublin_member1,ids.dublin_printer1),
                         assertions = dict(jhb=200,webapi=403,member1=200))

        self.assert_mass('/book_resource?user=%s&resource_id=%s' % (ids.dublin_member2,ids.dublin_printer1),
                         assertions = dict(jhb=200,webapi=403))

    def test_0160_meetingBooking(self):
        self.get(self.server_url + "/create_user?billto=&homeplace=1&first_name=member4&last_name=m4ln&user_name=member4&password2=test4&password=test4&email_address=member4%%40test.com&active=1")
        
        logins = [('member1','test1',200),('foo','bar',403),('member4','test4',200)]
        i = 8
        for l,p,code in logins:
            t = gettime(16,i,'date').replace(' ','+')
            url = '/add_booking?resource_id=%s&date=%s&notes=test_0160&start.hour=%s&start.minute=00&end.hour=%s&end.minute=30&_' % (ids.dublin_room1,t,i,i)
            self.assert_one(url,'response.code == %s' % code,l,p)
            if l == 'member1':
                id = self.getmaxid('RUsage')
            i+=1
        
        i = 8
        for l,p,code in logins:
            url = '/save_meetingBookingEdit?id=%s&value=undefined&resource_id=%s&date=%s&number_of_people=1&meeting_name=&notes=&start.hour=%s&start.minute=00&end.hour=%s&end.minute=45' % (id,ids.dublin_room1,t,i,i)
            self.assert_one(url,'response.code == %s' % code,l,p)
            if l == 'member1':  #RUsages get deleted when changed
                id = self.getmaxid('RUsage') 
            i+=1

    def test_0170_host_todos(self):
        url = '/load_tab?object_type=User&object_id=2&section=host&_='
        visible = "re.findall(r'addTodoBar',response.body)"
        hidden = 'not ' + visible
        #hidden = "re.findall(r'display:none.*add todo',response.body)"
        #visible  = 'not ' + hidden
        self.assert_mass(url,assertions=dict(jhb=visible,member1=hidden,webapi=hidden))

    def test_0175_host_addnewlist(self):
        url = '/create_todo?subject=foobar&foruser=1&body=blablub&_='
        #params = dict(subject='foobar',foruser=ids.dublin_member1,body='blablub')
        self.assert_mass(url,assertions=dict(jhb=200))


    def test_0180_networking_tab(self):
        url = '/load_tab?section=network&object_id=%s&object_type=User&_=' % ids.dublin_member1
        #hidden = "re.findall(r'display:none.*Add new member',response.body)"
        #visible  = 'not ' + hidden
        visible = '"Add new member" in response.body'
        hidden = 'not ' + visible
        self.assert_mass(url,assertions=dict(jhb=visible,member1=hidden,webapi=hidden))


    def test_0185_networking_billing(self):
        url = '/load_tab?section=network&object_id=%s&object_type=User&_=' % ids.dublin_member1
        #hidden = "re.findall(r'display:none.*Add new member',response.body)"
        #visible  = 'not ' + hidden
        visible = '"Billing" in response.body'
        hidden = 'not ' + visible
        self.assert_mass(url,assertions=dict(jhb=visible,member1=hidden,webapi=hidden))

    def test_0190_addnewmemberlink(self):
        url = '/'
        hidden = "re.findall(r'display:none.*Hosting',response.body)"
        visible  = 'not ' + hidden
        self.assert_mass(url,assertions=dict(jhb=visible,member1=hidden,webapi=hidden))

    def test_0200_usage_report_csv(self):
        self.assert_mass('/usage_report_csv/'+ str(ids.dublin),
                         assertions = dict(jhb=200,webapi=403,member1=403))
    
    def test_0210_save_tariffHistoryEdit(self):

        self.assert_mass("/save_tariffHistoryEdit?location=%s&id=%s&tariff.%s.%s=%s" % (ids.dublin, ids.dublin_member1, now.year+1, now.month, ids.dublin_tariff1000),
                         assertions = dict(jhb=200,webapi=403,member1=403))

    def test_0220_create_note(self):
        self.assert_mass("/create_note?title=testnote&onuser=%s&body=bla&_=" % ids.dublin_member1,
                         assertions = dict(jhb=200,webapi=403,member1=403))

        self.clearBasicAuth()
        self.setBasicAuth('jhb','test')
        ids.note1 = self.getmaxid('Note')

    def test_0230_save_noteEdit(self):
        self.assert_mass("/save_noteEdit?id=%s&value=undefined&title=newtestnote&body=new&_=" % ids.note1,
                         assertions = dict(jhb=200,webapi=403,member1=403))

    def test_0240_save_todoEdit(self):
        self.assert_mass("/save_todoEdit?id=%s&value=undefined&subject=thesub&action=edit&due=&body=thebod&_" % ids.todo2,
                         assertions = dict(jhb=200,webapi=403,member1=403))

    def test_0250_create_user(self):
        self.assert_mass("/create_user?billto=&homeplace=%s&first_name=MrTestuser&last_name=foobar&user_name=mrtestuser&password2=test1&password=test1&email_address=testuser@test.com&active=1" % ids.dublin,
                         assertions = dict(jhb=200,webapi=403,member1=403))

    def test_0260_add_requirement(self):
        self.assert_mass("/add_requirement?resourceid=%s&requirementid=%s" % (ids.room1id,ids.room2id),
                         assertions = dict(jhb=200,webapi=403,member1=403))


    def test_0270_pdf_invoice(self):
        self.assert_mass("/pdf_invoice?invoiceid=%s" % ids.invoice,
                             assertions = dict(jhb=200,webapi=403,member1=200),
                             printresults=0)
        
    def test_0280_remove_rusage_from_invoice(self):
        
        self.assert_mass("/remove_rusage_from_invoice?invoiceid=%s&rusageid=%s" % (ids.invoice,ids.rusage),
                             assertions = dict(webapi=403,member1=403,jhb=200),
                             printresults=0)
    
    def test_0290_add_rusage_to_invoice(self):
        
        self.assert_mass("/add_rusage_to_invoice?invoiceid=%s&rusageid=%s" % (ids.invoice,ids.rusage),
                             assertions = dict(webapi=403,member1=403,jhb=200),
                             printresults=0)

    def test_0300_ignore_remind(self):
        
        self.assert_mass("/ignore_remind?user_id=%s" % (ids.dublin_member1),
                             assertions = dict(webapi=403,member1=403,jhb=200),
                             printresults=0)

    def test_0310_send_reminder(self):
        
        self.assert_mass("/send_reminder?id=%s&subject=testreminer&body=thebody" % (ids.dublin_member1),
                             assertions = dict(webapi=403,member1=403,jhb=200),
                             printresults=0)
 
    def test_0320_send_invoice(self):
        
        self.assert_mass("/send_invoice?invoiceid=%s&subject=testinvoice&body=thebody" % (ids.invoice),
                             assertions = dict(webapi=403,member1=403,jhb=200),
                             printresults=0) # why member1 and webapi are able to send?

    def test_0330_create_todo_testbar(self):
        self.assert_mass("/create_todo?subject=testbar&foruser=%s" % ids.dublin_host1,
                             assertions = dict(webapi=403,member1=403,jhb=200),
                             printresults=0)

        self.clearBasicAuth()
        self.setBasicAuth('jhb','test')
        ids.testbar = self.getmaxid('Todo')

    def test_0340_toggle_closed_todos(self):
        
        self.assert_mass("/toggle_closed_todos?bar_id=%s&show=True" % (ids.testbar),
                             assertions = dict(webapi=403,member1=403,jhb=200),
                             printresults=0)

    def test_0350_delete_todo_bar(self):
        
        self.assert_mass("/delete_todo_bar?bar_id=%s" % (ids.testbar),
                             assertions = dict(webapi=403,member1=403,jhb=200),
                             printresults=0)

    def test_0360_display_invoice(self):
        
        self.assert_mass("/display_invoice?invoiceid=%s" % (ids.invoice),
                             assertions = dict(webapi=403,member1=200,jhb=200),
                             printresults=0)

    def test_0370_update_resource_table(self):
        
        self.assert_mass("/update_resource_table?invoiceid=%s" % (ids.invoice),
                             assertions = dict(webapi=403,member1=200,jhb=200),
                             printresults=0)

    def test_0380_save_costEdit(self):
        
        self.assert_mass("/save_costEdit?id=%s&customcost=23" % (ids.rusage),
                             assertions = dict(webapi=403,member1=403,jhb=200),
                             printresults=0)

    def test_0390_create_invoice(self):
        
        self.assert_mass("/create_invoice?userid=%s" % (ids.dublin_member1),
                             assertions = dict(webapi=403,member1=403,jhb=200),
                             printresults=0)

        self.clearBasicAuth()
        self.setBasicAuth('jhb','test')
        ids.invoice = self.getmaxid('Invoice')
        ids.testinvoice = self.getmaxid('Invoice')

    def test_0400_remove_invoice(self):
        passwords = dict(standardlogins)
        for user,code in dict(webapi=403,member1=403,jhb=200).items():
            response = self.assert_one("/create_invoice?userid=%s" % (ids.dublin_member1),
                                       "response.code == 200",
                                       "jhb")
            ids.tmpinvoice = self.getmaxid('Invoice')
            self.assert_one("/remove_invoice?invoiceid=%s" % (ids.tmpinvoice),
                                       "response.code == %s" % code,
                                       user,
                                       passwords[user])
            try:
                self.assert_one("/remove_invoice?invoiceid=%s" % (ids.tmpinvoice),
                                "response.code == 200",
                                "jhb",
                                passwords['jhb'])
            except:
                pass



    #def test_410_upload_outstanding(self):        
    #    r = self.post(#self.server_url + "/upload_outstanding", 
    #                  'http://localhost:8081/upload_outstanding',
    #                  #params = [['csvfile','bla']]
    #                  params=[['csvfile', Upload("hubspace/tests/outstanding.csv")]]
    #                 )
    #    print r.body

    #XXX should be tested
    #def test_0420_delete_rusage(self):
    #    
    #    self.assert_mass("/delete_rusage?rusage=%s" % (ids.rusage),
    #                         assertions = dict(webapi=403,member1=403,jhb=200),
    #                         printresults=0)
    def test_0420_delete_rusage(self):
        passwords = dict(standardlogins)
        then = gettime(15,8,'timeobject')

        self.assert_one("/save_tariffHistoryEdit?location=%s&id=%s&tariff.%s.%s=%s" % (ids.dublin, ids.dublin_member1, then.year, then.month, ids.dublin_tariff1000), "response.code == 200", "jhb", passwords['jhb'])



        for user,code in dict(webapi=403,member1=200,jhb=200).items():
            response = self.assert_one("/book_resource?resource_id=%s&user=%s&start_datetime=%s" % (ids.dublin_printer1,
                                                                                               ids.dublin_member1,
                                                                                               gettime(15,8).replace(' ','+')),
                                       "response.code == 200",
                                       "member1",
                                       passwords['member1'])




            self.clearBasicAuth()
            self.setBasicAuth('jhb',passwords['jhb'])
            ids.tmprusage = self.getmaxid('RUsage')
            print 'tmprusage: ', ids.tmprusage

            self.assert_one("/delete_rusage?rusage=%s" % (ids.tmprusage),
                                       "response.code == %s" % code,
                                       user,
                                       passwords[user])
            try:
                self.assert_one("/delete_rusage?rusage=%s" % (ids.tmprusage),
                                "response.code == 200",
                                "jhb",
                                passwords['jhb'])
            except:
                pass

    def test_0430_update_invoice_amount(self):
        
        self.assert_mass("/update_invoice_amount?invoiceid=%s" % (ids.invoice),
                             assertions = dict(webapi=403,member1=200,jhb=200),
                             printresults=0)

    def test_0430_addUser2Group(self):
        
        self.assert_mass("/addUser2Group?user=%s&group=%s" % (ids.dublin_member1,ids.dublin_member),
                             assertions = dict(webapi=403,member1=403,jhb=200),
                             printresults=0)

    def test_0440_create_resource(self):
        
        self.assert_mass("/create_resource?type=hotdesk&time_based=1&place=%s&name=hotdesktest&description=testhotdesk&tariffs-1.id=%s&tariffs-1.cost=%s&tariffs-2.id=%s&tariffs-2.cost=%s&tariffs-3.id=%s&tariffs-3.cost=%s&tariffs-4.id=%s&tariffs-4.cost=%s" %(ids.dublin, ids.dublin_tariff1000, 0.5, ids.dublin_tariff2000, 52.5, ids.dublin_tariff3000, 23.4, ids.dublin_default, 72), assertions = dict(webapi=403,member1=403,jhb=200), printresults=0)
        self.clearBasicAuth()
        self.setBasicAuth('jhb','test')
        ids.testhotdesk = self.getmaxid('Resource')

    def test_0450_create_tariff(self):
        
        self.assert_mass("/create_tariff?active=True&place=%s&name=testtariff&description=testtariff&tariff_cost=23&resources-1.id=%s&resources-1.cost=23&resources-2.id=%s&resources-2.cost=23&resources-3.id=%s&resources-3.cost=23&resources-4.id=%s&resources-4.cost=23&resources-5.id=%s&resources-5.cost=23&resources-6.id=%s&resources-6.cost=23&resources-7.id=%s&resources-7.cost=23" % (ids.dublin, ids.testhotdesk,  ids.dublin_hotdesk1,  ids.dublin_hotdesk2,  ids.dublin_printer1,  ids.dublin_printer2, ids.dublin_room1, ids.dublin_room2),
                             assertions = dict(webapi=403,member1=403,jhb=200),
                             printresults=0)
        self.clearBasicAuth()
        self.setBasicAuth('jhb','test')
        ids.testtariff = self.getmaxid('Resource')

    def test_0450_save_resource_property(self):
        
        self.assert_mass("/save_resource_property?id=%s&name=testhotdesk2&description=test2" % (ids.testhotdesk),
                             assertions = dict(webapi=403,member1=403,jhb=200),
                             printresults=0)
    
    def test_0460_toggle_resource_activate(self):
        
        self.assert_mass("/toggle_resource_activate?resourceid=%s" % (ids.testhotdesk),
                             assertions = dict(webapi=403,member1=403,jhb=200),
                             printresults=0)

    def test_0470_add_requirement(self):
        
        self.assert_mass("/add_requirement?resourceid=%s&requirementid=%s" % (ids.testhotdesk,ids.dublin_hotdesk1),
                             assertions = dict(webapi=403,member1=403,jhb=200),
                             printresults=0)

    def test_0480_add_suggestion(self):
        
        self.assert_mass("/add_suggestion?resourceid=%s&suggestionid=%s" % (ids.testhotdesk,ids.dublin_hotdesk2),
                             assertions = dict(webapi=403,member1=403,jhb=200),
                             printresults=0)

    def test_0485_remove_suggestion(self):
        
        self.assert_mass("/remove_suggestion?resourceid=%s&suggestionid=%s" % (ids.testhotdesk,ids.dublin_hotdesk2),
                             assertions = dict(webapi=403,member1=403,jhb=200),
                             printresults=0)


    def test_0490_create_group(self):
        """Is it really sane to create a second group of the same level in the same location?
        I think that this could screw the permissions structure of the system and would have made this impossible if it didnt break so many tests!! 
        """
        self.assert_mass("/create_group?place=%s&level=member&display_name=testgroup&group_name=testgroup_member" % (ids.dublin),
                         assertions = dict(webapi=403,member1=403,jhb=200), 
                         printresults=0)
        
    #def test_0500_create_pricing(self):
        
    #    self.assert_mass("/create_pricing?cost=23&tariff=%s&resources=%s" % (ids.testtariff,ids.testhotdesk),
    #                         assertions = dict(webapi=403,member1=403,jhb=200),
    #                         printresults=0)

    def test_0510_get_id(self):
        
        self.assert_mass("/get_id/Group/display_name/testgroup",
                             assertions = dict(webapi=200,member1=200,jhb=200),
                             printresults=0)
    def xtest_9999_users(self):
        import csv
        server_url = self.server_url
        self.setBasicAuth('jhb','test')
        r = csv.reader(open('hubspace/tests/user_list.csv'),delimiter=',')
        for line in r:
            display_name = line[1]
            try:
                first_name, last_name = display_name.split(" ", 1)
            except:
                try:
                    first_name, last_name = display_name.split(".", 1)
                except:
                    first_name = display_name
                    last_name = display_name
                    
            data = dict(user_name=line[0],
                        display_name = display_name,
                        first_name= first_name,
                        last_name = last_name,
                        password='test1',
                        password2='test1',
                        email_address='%s@the-hub.net' % line[0],
                        billto="",
                        homeplace=2,
                        active=1)
            result = self.get(server_url + '/create_user',data)

    
    def tearDown(self):
        """Setting up test."""
        self.logd("tearDown.\n")



if __name__ in ('main', '__main__'):
    unittest.main()
