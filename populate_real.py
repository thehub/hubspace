from hubspace.model import *

from datetime import datetime
import popen2
class Population (object):
  pass

def populate ():
  objs = Population()

  classes = ['Visit','VisitIdentity','Group','User','Permission','Location',
            'Resource','RUsage','Pricing','Todo','Invoice','Note']
  for c in classes:
       for prefix in ['manage']:
           pname = prefix + '_' +  c.lower() + 's'
           setattr(objs,'permission_%s' % pname,Permission(permission_name=pname))

  level = ['member', 'host', 'director']
  for c in level:
    for prefix in ['add']:
      pname = prefix + '_' +  c.lower() + 's'
      setattr(objs,'permission_%s' % pname,Permission(permission_name=pname))
      
  objs.permission_superuser = Permission(permission_name='superuser')
  objs.permission_superuser = Permission(permission_name='webapi')

  objs.london = Location(name='London',
                         currency='GBP')

  from hubspace.controllers import new_group
  
  objs.london_member = new_group(group_name='london_member',
                                 display_name='London member',
                                 place = objs.london.id,
                                 level = 'member')
   
  objs.london_host = new_group(group_name='london_host',
                               display_name='London host',
                               place = objs.london.id,
                               level = 'host')
  

  objs.london_director = new_group(group_name='london_director',
                                   display_name='London director',
                                   place = objs.london.id,
                                   level = 'director')


  objs.group_superuser  = Group(group_name='superuser',
                             display_name='Superuser',
                             place = None,
                             level = 'director')

  objs.group_webapi  = Group(group_name='webapi',
                             display_name='webapi',
                             place = None,
                             level = 'host')
  #Users
  objs.tom = User(user_name='salfield',
                  display_name='Tom Salfield',
                  first_name='Tom',
                  last_name = 'Salfield',
                  title = 'Mr',
                  organisation = 'Open Coop',
                  mobile = '07967 099480',
                  work = '02073576407',
                  home = '02073576407',
                  fax = '',
                  email_address='tom@open.coop',
                  password='boo',
                  address = '60 Heaven Mansions',
                  skype_id = 'tomsalfield',
                  email2='tom@ud.com',
                  billingaddress='Tower Bridge',
                  billto=None,
                  outstanding=500,
                  homeplace=objs.london.id)

  objs.tom.save_image(open('hubspace/tests/images/tom.jpg').read(),'image/jpeg')
  objs.tom.billto = objs.tom.id
      
  objs.jonathan = User(user_name='jonathan',
                  display_name='Jonathan Robinson',
                  first_name='Jonathan',
                  last_name = 'Robinson',
                  title = 'Boss',
                  organisation = 'London Hub',
                  mobile = '',
                  work = '',
                  home = '',
                  fax = '',
                  email_address='jonathan.robinson@the-hub.net',
                  password='test',
                  skype_id = 'jonathanjonathan',
                  address = '',
                  billingaddress='Nowhere really',
                  billto=None,
                  homeplace=objs.london.id)


  objs.jonathan.save_image(open('hubspace/tests/images/jonathan.jpg').read(),'image/jpeg')
  objs.jonathan.billto = objs.jonathan.id
  

  objs.webapi   = User(user_name='webapi',
                  display_name='Mr. Webapi',
                  first_name='web',
                  last_name = 'api',
                  title = 'Api slave',
                  organisation = 'London Hub',
                  mobile = '',
                  work = '',
                  home = '',
                  fax = '',
                  email_address='api@the-hub.net',
                  password='test',
                  skype_id = '',
                  address = '',
                  billingaddress='Nowhere really',
                  billto=None,
                  homeplace=objs.london.id)


  #Permissions and Groups
  
  su = Permission.by_permission_name('superuser')
  objs.group_superuser.addPermission(su)

  wa = Permission.by_permission_name('webapi')
  objs.group_webapi.addPermission(wa)

  objs.group_superuser.addUser(objs.tom)
  objs.group_webapi.addUser(objs.webapi)

  for u in ['tom','jonathan']:
        objs.london_host.addUser(getattr(objs,u))
  for u in ['tom','jonathan']:
        objs.london_member.addUser(getattr(objs,u))
  for u in ['tom','jonathan']:
        objs.london_director.addUser(getattr(objs,u))
        
  return objs

