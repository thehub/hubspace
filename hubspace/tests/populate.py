import hubspace.model
from hubspace.model import *

from datetime import datetime
class Population (object):
  pass

def populate ():
  objs = Population()
 
#  #Currencies
#  objs.eur = Currency(name='eur',
#                      longname='continental Euro',
#                      exchangerate=1)
#  
#  objs.gbp = Currency(name='gbp',
#                      longname='island Dollar',
#                      exchangerate=1.6)
#
#  objs.usd = Currency(name='usd',
#                      longname='thin air',
#                      exchangerate=0.8)

  #Locations
  objs.london = Location(name='Londoninium',
                         currency='GBP')
  objs.bielefeld = Location(name='Bielefeld',
                       currency='GBP')

  hubspace.model.hub.commit()
  User._connection.cache.clear()
  objs.hubspaceadmin = User.selectBy(user_name="hubspaceadmin")[0]
  #Groups
  from hubspace.utilities.permissions import new_group
  
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


  objs.bielefeld_member = new_group(group_name='bielefeld_member',
                                    display_name='bielefeld member',
                                    place = objs.bielefeld.id,
                                    level = 'member')
  
  objs.bielefeld_host = new_group(group_name='bielefeld_host',
                                  display_name='bielefeld host',
                                  place = objs.bielefeld.id,
                                  level = 'host')

  objs.bielefeld_director = new_group(group_name='bielefeld_director',
                                      display_name='bielefeld director',
                                      place = objs.bielefeld.id,
                                      level = 'director')


  hubspace.model.hub.commit()
  Group._connection.cache.clear()


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
                  email_address='tomdoesntexist@opendoesntexist.coop',
                  password='boo',
                  address = '60 Heaven Mansions',
                  skype_id = 'tomsalfield',
                  email2='tom@ud.com',
                  billingaddress='Tower Bridge',
                  billto=None,
                  outstanding=500,
                  homeplace=objs.london.id,
                  active=1)

  objs.tom.save_image('image', open('hubspace/tests/images/tom.jpg').read(),'image/jpeg')
  objs.tom.billto = objs.tom.id
  
  objs.jhb = User(user_name='jhb',
                  display_name='Joerg Baach',
                  first_name='Joerg',
                  last_name = 'Baach',
                  title = 'God',
                  organisation = 'Universe',
                  mobile = '7777777777',
                  work = '777777777',
                  home = '77777777',
                  fax = '',
                  email_address='mail@baachdosesntexist.de',
                  password='test',
                  skype_id = 'LordBaach',
                  address = 'lala land',
                  billingaddress='Nowhere really',
                  billto=objs.tom.id,
                  homeplace=objs.london.id,
                  active=1) 


  objs.jhb.save_image('image', open('hubspace/tests/images/jhb.jpg').read(),'image/jpeg')
  objs.jhb.billto = objs.jhb.id
  
  objs.maria = User(user_name='maria',
                    display_name='Maria Glauser',
                    first_name='Maria',
                    last_name = 'Glauser',
                    title = 'Boss',
                    organisation = 'London Hub',
                    mobile = '',
                    work = '',
                    home = '',
                    fax = '',
                    email_address='maria.glauser@the-hubdoesntexist.net',
                    password='test',
                    skype_id = 'mariamaria',
                    address = '',
                    billingaddress='Nowhere really',
                    billto=None,
                    homeplace=objs.london.id,
                    active=1)

  objs.maria.save_image('image', open('hubspace/tests/images/maria.jpg').read(),'image/jpeg')
  objs.maria.billto = objs.maria.id
  
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
                  email_address='jonathan.robinson@the-hubdoesntexist.net',
                  password='test',
                  skype_id = 'jonathanjonathan',
                  address = '',
                  billingaddress='Nowhere really',
                  billto=None,
                  homeplace=objs.london.id,
                  active=1)


  objs.jonathan.save_image('image', open('hubspace/tests/images/jonathan.jpg').read(),'image/jpeg')
  objs.jonathan.billto = objs.jonathan.id
  
  objs.james = User(user_name='james',
                  display_name='James Hurrell',
                  first_name='James',
                  last_name = 'Hurrel',
                  title = 'Boss',
                  organisation = 'London Hub',
                  mobile = '',
                  work = '',
                  home = '',
                  fax = '',
                  email_address='james@the-hubdoesntexist.net',
                  password='test',
                  skype_id = 'jamesjames',
                  address = '',
                  billingaddress='Nowhere really',
                  billto=None,
                  homeplace=objs.london.id,
                  active=1)

  objs.james.billto = objs.james.id

  objs.ben = User(user_name='bjpirt',
                  display_name='Ben Pirt',
                  first_name='Ben',
                  last_name = 'Pirt',
                  title = 'Boss',
                  organisation = 'London Hub',
                  mobile = '',
                  work = '',
                  home = '',
                  fax = '',
                  email_address='ben@moreassociatesdoesntexist.com',
                  password='test',
                  skype_id = '',
                  address = '',
                  billingaddress='more',
                  billto=None,
                  homeplace=objs.london.id,
                  active=1)

  objs.ben.save_image('image', open('hubspace/tests/images/ben.jpg').read(),'image/jpeg')
  objs.ben.billto = objs.ben.id
  
  
  objs.ida = User(user_name='ida',
                  display_name='Ida Norheim Hagtun',
                  first_name='Ida',
                  last_name = 'Norheim Hagtun',
                  title = 'Boss',
                  organisation = 'London Hub',
                  mobile = '',
                  work = '',
                  home = '',
                  fax = '',
                  email_address='ida@the-hubdoesntexist.net',
                  password='test',
                  skype_id = '',
                  address = '',
                  billingaddress='Nowhere really',
                  billto=None,
                  homeplace=objs.london.id,
                  active=1)

  objs.ida.save_image('image', open('hubspace/tests/images/ida.jpg').read(),'image/jpeg')
  objs.ida.billto = objs.ida.id

  objs.menka = User(user_name='menka',
                  display_name='Menka Parekh',
                  first_name='Menka',
                  last_name = 'Parekh',
                  title = 'Boss',
                  organisation = 'London Hub',
                  mobile = '',
                  work = '',
                  home = '',
                  fax = '',
                  email_address='menka@the-hubdoesntexist.net',
                  password='test',
                  skype_id = '',
                  address = '',
                  billingaddress='Nowhere really',
                  billto=None,
                  homeplace=objs.london.id,
                  active=1)


  objs.menka.save_image('image', open('hubspace/tests/images/menka.jpg').read(),'image/jpeg')
  objs.menka.billto = objs.menka.id


  objs.ida.billto = objs.ida.id

  #Resources
  objs.london_room1 = Resource(place=objs.london.id,
                               type='room',
                               name='london_room1',
                               time_based=1,
                               description='London meeting room 1')

  objs.london_room2 = Resource(place=objs.london.id,
                               type='room',
                               name='london_room2',
                               time_based=1,
                               description='London meeting room 2')

  objs.london_custom= Resource(place=objs.london.id,
                               type='other',
                               name='london_custom',
                               description='London custom item')

  #Tariffs
  tariffnames = ['london_tariff1000','london_tariff2000','london_tariff3000']
  for t in tariffnames:
    tariff = Resource(place=objs.london.id,
                      name=t,
                      description=t.replace('_',' ').capitalize(),
                      type='tariff')
    setattr(objs,t,tariff)

  #objs.london_tariff1 = Resource(place=objs.london.id,
  #                               name='london_tariff1',
  #                               description='London Tariff 1',
  #                               type='tariff')


  #Prices

  prices = dict(london_tariff1000 = dict(tariff1000=30,room1=30,room2=20,custom=1),
                london_tariff2000 = dict(tariff2000=60,room1=20,room2=10,custom=1),
                london_tariff3000 = dict(tariff3000=100,room1=10,room2=4,custom=1))

  for t,prices in prices.items():
      for resource,cost in prices.items():
          pricing = Pricing(tariff = getattr(objs,t).id,
                            cost = cost,
                            resource = getattr(objs,'london_' + resource).id)
          
#  objs.london_price0 = Pricing(tariff=objs.london_tariff1.id,
#                               cost=30)
#  objs.london_price0.addResource(objs.london_tariff1.id)
#
#  objs.london_price1 = Pricing(tariff=objs.london_tariff1.id,
#                               cost=12.34)
#  objs.london_price1.addResource(objs.london_room1.id)

  #Usage
  res = objs.london_room1
  objs.usage1 = RUsage(resource_name=res.name,
                       resource_description=res.description,
                       resource=res.id,
                       user=objs.tom.id,
                       start=datetime(2006,9,20,13),
                       end_time=datetime(2006,9,20,15),
                       quantity=1,
                       customcost=50,
                       invoice=None)

  objs.usage2 = RUsage(resource_name=res.name,
                       resource_description=res.description,
                       resource=res.id,
                       user=objs.jhb.id,
                       start=datetime(2006,10,20,16),
                       end_time=datetime(2006,10,20,20),
                       quantity=1,
                       customcost=70,
                       invoice=None)
  
  objs.usage3 = RUsage(resource_name=objs.london_custom.name,
                       resource_description='Broke a glas',
                       resource=objs.london_custom.id,
                       user=objs.jhb.id,
                       start=datetime(2006,9,20,18),
                       end_time=datetime(2006,9,20,18),
                       quantity=1,
                       customcost=0.7,
                       invoice=None)



  #Invoice
  objs.invoice1 = Invoice(user=objs.tom.id,
                          billingaddress=objs.tom.billingaddress,
                          start=datetime(2006,9,10),
                          end_time=datetime(2006,9,30),
                          location=objs.tom.homeplace)
  #Put usage on invoice
  objs.usage1.invoice=objs.invoice1.id
  objs.usage2.invoice=objs.invoice1.id

  #Todos
  objs.todo1 = Todo(subject='Parent Bar',
                    body='whatever',
                    createdby = objs.jhb.id,
                    foruser = objs.tom.id,
                    opened=datetime.now(),
                    due=datetime(2006,10,1),
                    closed=None,
                    parent=None)

  objs.note1 = Note(title="no payment",
                   body="he is naughty boy!",
                   date=datetime.now(),
                   onuser = objs.tom.id,
                   byuser = objs.jhb.id)

  objs.note2 = Note(title="oi",
                    body="watch it...I got notes on you!",
                    date=datetime.now(),
                    onuser = objs.tom.id,
                    byuser = objs.jhb.id)
   
  
  su = Permission.by_permission_name('superuser')
  objs.group_superuser = hubspace.model.Group.by_group_name("superuser")


  objs.group_superuser.addUser(objs.tom)
  objs.group_superuser.addUser(objs.jhb)

  objs.london_director.addUser(objs.jonathan)

  for u in ['tom','jhb','maria','ida','menka']:
      objs.london_host.addUser(getattr(objs,u))

  for u in ['tom','jhb','maria','ida','menka','ben','james']:
      objs.london_member.addUser(getattr(objs,u))

  objs.bielefeld_director.addUser(objs.jonathan)  
  objs.bielefeld_host.addUser(objs.maria)

  return objs

