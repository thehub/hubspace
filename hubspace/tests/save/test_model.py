# If your project uses a database, you can set up database tests
# similar to what you see below. Be sure to set the db_uri to
# an appropriate uri for your testing database. sqlite is a good
# choice for testing, because you can use an in-memory database
# which is very fast.

from turbogears import testutil, database, config, startup
from hubspace import model
from hubspace.model import *
from populate import populate
from hubspace.controllers import Root
import cherrypy
import inspect, sqlobject
from sqlobject.inheritance import InheritableSQLObject

config.update({
    'visit.on': True,
    'identity.on': True,
    'identity.failure_url': '/login',
})

cherrypy.root = Root()
#work on the dev database, so that we don't have to repopulate all the time
#and can also check on the results of the tests
base = '/'.join(model.__file__.split('/')[:-2])
#database.set_db_uri("sqlite:///%s/devdata.sqlite" % base)
database.set_db_uri("sqlite:///%s/devdata.sqlite" % base)
#Have our own testclass so that we destroy data at the beginning of the tests
class Hubspacetest(testutil.DBTest):
    def setUp(self):
        print "asdfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
        for item in model.__dict__.values():
            if inspect.isclass(item) and issubclass(item,
                sqlobject.SQLObject) and item != sqlobject.SQLObject \
                and item != InheritableSQLObject:
                item.dropTable(ifExists=True)
        testutil.DBTest.setUp(self)
        self.objs = populate()

    def tearDown(self):
        startup.stopTurboGears()
        pass
        #database.rollback_all()


class TestUser(Hubspacetest):
 
    def calldefault(self,*args,**kwargs):
        import urllib
        args = list(args)
        location = args[0]
        method = args[1]
        parameters=urllib.urlencode(kwargs)
        print parameters 
        url = 'URL: /%s/%s?%s' % (location,method,parameters)
        print url
        return testutil.call(cherrypy.root.default,*args,**kwargs)

    def dorequest(self,location,method,*args,**kwargs):
        for arg in args:
            kwargs[arg]=None
        if 'user_name' in kwargs.keys() and 'password' in kwargs.keys():
            kwargs.setdefault('login','Login')
        import urllib
        parameters=urllib.urlencode(kwargs)
        print parameters 
        url = '/%s/%s?%s' % (location,method,parameters)
        print url
        url = '/dublin/jhb?user_name=member1&password=test&login=Login'
        return testutil.createRequest(url)
        #return testutil.call(cherrypy.root.default,location,method,*args,**kwargs)


    def xtest_00010_setup_location(self):
        'Set up location Dublin'
        result = self.calldefault('london','create_location',name='dublin',currency='EUR')
        assert 'dublin' in testutil.call(cherrypy.root.listlocations)


    def test_yyy(self):
        '''Running the whole application. The output can be found in devdata.sqlite for 
        further use'''

        #create Location
        result = self.calldefault('london','create_location',name='dublin')
        assert 'dublin' in testutil.call(cherrypy.root.listlocations)
        
        dublin = Location.byName('dublin')

        #create Groups
        for g in ['member','host','director']:
            result = self.calldefault('dublin',
                                      'create_group',
                                      group_name='dublin_' + g,
                                      display_name='Dublin ' +g,
                                      place=dublin.id,
                                      level = g)

        assert 'dublin_host' in  [l.group_name for l in Group.select()]
        
        #create Users
        users = ['host1','host2','member1','member2','director1','director2']
        for name in users:
            level = name[:-1]
            result = self.calldefault('dublin',
                                      'create_user',
                                      user_name=name,
                                      email_address='%s@test.com' % name,
                                      display_name=name,
                                      password = 'test',
                                      #groups = [Group.by_group_name('dublin_' + level).id],
                                      homeplace=dublin.id,
                                      billto=None)
            user = User.by_user_name(name)
            user.addGroup(Group.by_group_name('dublin_'+level))
        print 'Groups: ',user.groups
        assert 'member1' in [r.user_name for r in User.select()]

        

        #create Tariffs

        tariffs = ['tariff1000','tariff2000','tariff3000']
        for tariff in tariffs:
            result = self.calldefault('dublin',
                                      'create_resource',
                                      place = dublin.id,
                                      name=tariff,
                                      description='Tariff %s in dublin' % tariff,
                                      type='tariff')
         
        assert 'tariff2000' in [r.name for r in Resource.select()]


        #create Resources

        resources = ['printer1','printer2','hotdesk1','hotdesk2','room1','room2']
        for resource in resources:
            result = self.calldefault('dublin',
                                      'create_resource',
                                      place = dublin.id,
                                      name=resource,
                                      description='Resource %s in dublin' % resource,
                                      type=resource[:-1])
        assert 'printer2' in [r.name for r in Resource.select()]

        #create Prices
        
        pricestructure = [[3,2,1],[4,3,2],[5,4,3],[5,4,3],[10,9,8],[13,12,11]]
        
        for i in range(0,6):
            resourcename = resources[i]
            resource=Resource.selectBy(name=resourcename)[0]
            for j in range(0,3):
                self.calldefault('dublin',
                                 'create_pricing',
                                 tariff=Resource.selectBy(name=tariffs[j])[0].id,
                                 cost = pricestructure[i][j],
                                 resources=resource.id,
                                 time_based=resourcename.startswith('room'))


        #create Prices for tariffs

        for tariffname in tariffs:
            tariff = Resource.selectBy(name=tariffname)[0]
            self.calldefault('dublin',
                             'create_pricing',
                             tariff=tariff.id,
                             cost = int(tariffname[-4:-1])/3,
                             resources=tariff.id)

        #We are working with this user only at this time
        user = User.selectBy(user_name='member1')[0]


        from datetime import datetime
        now = datetime.now()
        #Book a tariff
        tariff = Resource.selectBy(name='tariff1000',place=dublin)[0]
        print 'Book a tariff for ', `user`
        print `tariff`
        result = self.calldefault('dublin',
                                 'book_tariff',
                                 userid=user.id,
                                 tariffid=tariff.id,
                                 year=now.year,
                                 month=now.month)


        #create Usage
       
        resource = Resource.selectBy(name='room1')[0]
        fmt = '%m/%d/%Y %H:%M:%S'
        result = self.calldefault('dublin',
                                    'create_rusage',
                                    user = user.id,
                                    resource=resource.id,
                                    start = datetime(now.year,now.month,20,10).strftime(fmt),
                                    end = datetime(now.year,now.month,20,12,30).strftime(fmt))

        resource = Resource.selectBy(name='printer1')[0]
        result = self.calldefault('dublin',
                                    'create_rusage',
                                    user = user.id,
                                    resource=resource.id,
                                    start = datetime(now.year,now.month,20,10).strftime(fmt),
                                    end = datetime(now.year,now.month,20,12,30).strftime(fmt))
        result = self.calldefault('dublin',
                                  'create_rusage',
                                  user = user.id,
                                  resource=resource.id,
                                  start = datetime(now.year,now.month,20,10).strftime(fmt),
                                  end = datetime(now.year, now.month,20,12,30).strftime(fmt))
        
        rusage = RUsage.get(result['id'])
        #rusage.cost = calculate_cost('dublin',rusage)
        #print `rusage`



        #result = self.calldefault('dublin',
        #                          'create_rusage',
        #                          user = user.id,
        #                          resource=tariff.id)

        


        #create new Invoice with unbilled invoices

        result = self.calldefault('dublin',
                                  'create_invoice',
                                  user = user.id,
                                  autocollect=True)

        invoice = Invoice.get(result['id'])
        
        print 'Invoice', `invoice.rusages`
        
        #Remove an rusage from an invoice

        result = self.calldefault('dublin',
                                  'remove_rusage_from_invoice',
                                  invoiceid=invoice.id,
                                  rusageid=rusage.id)

        print 'Invoice2', `invoice.rusages`

        #Add an rusage directly to the invoice

        result = self.calldefault('dublin',
                                  'create_rusage',
                                  user = user.id,
                                  resource = resource.id,
                                  invoice = invoice.id)
        print invoice.id
        print `RUsage.get(result['id'])`

        print 'Invoice3', `invoice.rusages`

        #create Todos
        result = self.calldefault('dublin',
                                  'create_todo',
                                  createdby=user.id,
                                  subject='Travel to Dublin')
        print `Todo.get(result['id'])`

        #costs
        #print 'Calculate costs'
        #rusage = invoice.rusages[0]
        #result = self.calldefault('dublin',
        #                          'calculate_cost',
        #                          rusage.id)
        #print result
        #print calculate_cost(rusage)
        #
        #self.dorequest('dublin','jhb',user_name='member3',password='test')
        #print cherrypy.response.body
        
        #testutil.createRequest('/dublin/jhb?login=Login&password=test&user_name=member1')
        #print cherrypy.response.body[0]

    def xtest_tom(self):
        print 'foo'
        assert self.objs.tom.display_name == 'Tom Salfield'

    def xtest_basic_relation(self):
        assert self.objs.london_price1 in self.objs.london_room1.prices
    
    def xtest_paid_default(self):
        assert not self.objs.invoice1.paid
    
    def xtest_indextitle(self):
        "The mainpage should have the right title"
        testutil.createRequest("/")
        assert "<TITLE>Welcome to TurboGears</TITLE>" in cherrypy.response.body[0]
 
    def test_berlin(self):
        "Create berlin"
        testutil.createRequest("/london/create_location?name=berlin")
        #print cherrypy.response.body[0]
#        assert 1
    
#    def test_zzzlistlocations(self):
#        "List locations"
#        objs = populate()
#        result = testutil.call(cherrypy.root.listlocations)
#        print result
#        assert 1

    def test_vienna2(self):
        "Create vienna2"
        result = self.calldefault('london','create_location',name='vienna2')
        locations = testutil.call(cherrypy.root.listlocations)
        assert 'vienna2' in locations

    def test_vienna3(self):
        'Test within test'
        self.test_vienna2()
        locations = testutil.call(cherrypy.root.listlocations)
        print locations
        assert 1
    
    
#         def get_model(self):
#                 return User
#
#         def test_creation(self):
#                 "Object creation should set the name"
#                 obj = User(user_name = "creosote",
#                                             email_address = "spam@python.not",
#                                             display_name = "Mr Creosote",
#                                             password = "Wafer-thin Mint")
#                 assert obj.display_name == "Mr Creosote"

