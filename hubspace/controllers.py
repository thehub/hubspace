import sys
import traceback
import logging
import re
import itertools
import string
import cStringIO
import ho.pisa as pisa

import cherrypy
from cgi import FieldStorage, escape
import turbogears, sendmail
from hubspace import inplace_i18n
from turbogears import controllers, expose, validate, redirect, exception_handler, validators as v, identity, widgets as tg_widgets, config, error_handler
from turbogears.identity.exceptions import *
from turbogears.i18n.utils import get_locale
from formencode import All, Any, ForEach, Schema
from docutils.core import publish_parts
from hubspace.openTimes import add_policy_group, add_users2policy_group, remove_users2policy_group, remove_policy_group, add_accessPolicy2Proxy, remove_accessPolicy2Proxy, create_openTime, delete_openTime, edit_openTime, opening_times, check_access, user_acquires_policyProxy, user_loses_policyProxy, recalculate_tariff_accessPolicies, create_default_open_times
 
from hubspace import json
import hubspace.model
model = hubspace.model
from hubspace.model import *
import hubspace.bookinglib as bookinglib
import hubspace.alerts
import hubspace.errors
from datetime import datetime,timedelta, time, date
from hubspace.utilities.object import create_object, get_attribute_names, modify_attribute, modify_attributes, get_attribute
from hubspace.utilities.templates import try_render
from hubspace.utilities.login import login_args
from hubspace.feeds import get_updates_data, cached_updates, clear_cache
from hubspace.invoice import *

from datetime import datetime, timedelta, time, date
from time import ctime, mktime
import calendar
import compat
from sqlobject import AND, OR, DESC
from sqlobject.sqlbuilder import IN, Select
log = logging.getLogger("hubspace.controllers")

import turbogears.scheduler
from hubspace.utilities.autoreload import autoreload
from hubspace.utilities.dicts import AttrDict
from hubspace.utilities.image_preview import create_image_preview
from hubspace.utilities.static_files import hubspace_compile
from hubspace.utilities.uiutils import c2s, inv_currency, unsent_for_user, get_multiselected, set_multiselected, set_freetext_metadata, get_freetext_metadata, set_singleselected, get_singleselected, now
from hubspace.utilities.permissions import user_locations, addUser2Group
from hubspace.utilities.users import filter_members
from hubspace.tariff import get_tariff

import hubspace.sync.core as sync
import hubspace.search

from hubspace.validators import *
from turbogears.validators import Money
from hubspace import reportutils

import inspect, sqlobject, md5,random
from sqlobject.inheritance import InheritableSQLObject
from sqlobject import *
from hubspace.tests.populate import populate
import csv, StringIO

import os
from os.path import exists
from commands import getoutput
from glob import glob

from decimal import Decimal
#add for feed generation
from turbofeeds import FeedController
import mechanize

from turbogears.database import PackageHub, commit_all, end_all
hub = PackageHub("turbogears.visit")
__connection__ = hub

dtc = v.DateTimeConverter("%Y-%m-%d %H:%M:%S")
print_dtc = v.DateTimeConverter("%m/%d/%Y %H:%M:%S")

applogger = logging.getLogger("hubspace")

from hubspace.configuration import site_default_lang,  site_folders, title, new_or_old


####SCHEDULED
from cherrypy._cphttptools import Request
import urllib2

def update_tariff_bookings():
    """get the last month for which tariffs have been booked anywhere in the system
    then for every active user in every location, find the tariff for that month and book the same tariff into the next month
    - should be run on the turn of the month
    """
    for location in Location.select():
        try:
            loc_last_tariff = RUsage.select(AND(RUsage.q.resourceID==Resource.q.id,
                                                Resource.q.type=='tariff',
                                                Resource.q.placeID==location.id)).orderBy("start")[-1]
        except:
            continue
        loc_last_tariff_date = loc_last_tariff.start
        group = Group.select(AND(Group.q.level=='member',
                                 Group.q.placeID==location.id))[0]
        group_users = [user for user in group.users if user.active]
        for user in group_users:
            last_tariff = get_tariff(location.id, user.id, loc_last_tariff_date, default=False)
            if last_tariff:
                next_tariff_date = loc_last_tariff_date + timedelta(days=calendar.monthrange(loc_last_tariff_date.year, loc_last_tariff_date.month)[1])
                tariff_booking = book_tariff(user, last_tariff, next_tariff_date.year, next_tariff_date.month, recalculate=False)
                model.hub.commit()
                model.hub.begin()
    model.hub.commit()
    print "finish"

def book_tariff(user, tariff, year, month, recalculate=True):
    lastday = calendar.monthrange(year, month)[1]
    tariff_booking = create_rusage(start=datetime(year,month,1,0,0,1),
                                   end_time=datetime(year,month,lastday,0,0,0)+timedelta(days=1),
                                   resource=tariff.id,
                                   user=user.id)
    if recalculate:
        tariff_booking_changed_recalculate(user, tariff, tariff_booking.start, tariff_booking.end_time)

    return tariff_booking



def send_unknown_aliases():
    try:
        no_alias_users = open('printing/unknown_aliases.txt', 'rb')
        no_alias_jobs = open('printing/alias_failure.log', 'rb')
    except:
        fail_text = "no unknown_aliases to send"
        print fail_text
        return fail_text
    if len(no_alias_users.readlines())>1:
        no_alias_users.seek(0)
        sendmail.sendmail('islington.hosts@the-hub.net', 'islington.hosts@the-hub.net', 'Hubspace has unknown aliases', "Attached is a list of unknown aliases and corresponding unregistered jobs. Please add them to the appropriate users\n\n All the best, \n\n Mr Hubspace", [["alias_log.txt", no_alias_users.read(), "text/plain; charset=utf-8"], ["failed_jobs_log_.txt", no_alias_jobs.read(), "test/plain; charset=utf-8"]])
    no_alias_users.close()
    no_alias_jobs.close()
    model.hub.commit()


from hubspace.scheduler import _start_scheduler, add_oneoff_task, add_weekday_task, add_weekday_task, _get_scheduler, add_monthday_task, add_interval_task

def startup():
    config.update({'i18n.get_locale':get_hubspace_locale})
    #hubspace.search.populate()
    hubspace_compile()
    for location in Location.select():
        get_updates_data(location)
    start_scheduler()

class schedSafe(object):
    """
    a. may not be safe, make sure you test the transactions are executed correctly.
    b. strictly for non long running tasks
    """
    def __init__(self, f):
        self.f = f
    def __call__(self, *args, **kw):
        applogger.debug("schedSafe: begin")
        from sqlobject.util.threadinglocal import local as threading_local
        hub.threadingLocal = threading_local()
        hub.begin()
        try:
            ret = self.f(*args, **kw)
            applogger.debug("schedSafe: %s returned %s" % (self.f.__name__, ret))
        finally:
            commit_all()
            end_all()
        applogger.debug("schedSafe: done")

def start_scheduler():
    """start the scheduler and add the timed jobs. These jobs must be sure to do model.hub.commit() in all cases EVEN IF THEY ONLY READ - otherwise they will hold onto database transaction in postgres forever! Its often wise to break them down into smaller transactions, by committing and then beginning new transactions using model.hub.begin().
    """
    #turbogears.scheduler.add_interval_task(action=parse_print_file, taskname='parse the print log', initialdelay=0, interval=600)
    add_interval_task(schedSafe(bookinglib.requestBookingConfirmations), taskname="Request booking confirmations", initialdelay=60 * 60, interval=60 * 60)
    add_weekday_task(send_unknown_aliases, [1], (0,0))
    add_monthday_task(update_tariff_bookings, [1], (0,0))
    add_monthday_task(schedule_access_policy_updates, [3], (0,0))
    add_interval_task(reportutils.do_report_maintainance, taskname="Report generation routine tasks", initialdelay=30*60, interval=24*60*60)
    if datetime.now() > datetime(datetime.today().year, datetime.today().month, 3):
        schedule_access_policy_updates()

turbogears.startup.call_on_startup.append(startup)

from pytz import timezone

def schedule_access_policy_updates():
    """make sure that each location is has its
    """
    right_now = now()
    month = right_now.month
    year = right_now.year
    last_day_of_the_month = calendar.monthrange(year, month)[1]
    next_month_start = (right_now + timedelta(days=(last_day_of_the_month + 1 - right_now.day)))
    for loc in Location.select():
        #execute "recalculate_tariff_accessPolicies" for each location at the time which is the turn of the month in their timezone.  
        zone_name = loc.timezone
        if not zone_name:
            zone_name = 'UTC'
        time_zone = timezone(zone_name)
        recalc_time = datetime(next_month_start.year, next_month_start.month, 1, tzinfo=time_zone).astimezone(timezone('UTC'))
        #recalc_time = datetime.now() + timedelta(seconds=10) #uncomment this to test 
        add_oneoff_task(recalculate_tariff_accessPolicies, recalc_time.date(), recalc_time.timetuple()[3:5], kw=dict(location=loc))
    model.hub.commit()

def recreate_tables(force=False):
    # careful ;)
    if force or config.get('server.testing', False):
        print "Test setup: recreate_tables"
        for item in model.__dict__.values():
            if inspect.isclass(item) and issubclass(item, sqlobject.SQLObject) and item != sqlobject.SQLObject \
                and item != InheritableSQLObject:
                item.dropTable(ifExists=True, cascade=True)
                item.createTable(ifNotExists=True)

def create_permissions():
    classes = ['Visit','VisitIdentity','Group','User','Permission','Location',
               'Resource','RUsage','Pricing','Todo','Invoice','Note']
    existing_perms = [p.permission_name for p in model.Permission.select()]
    for c in classes:
        for prefix in ['manage']:
            pname = prefix + '_' +  c.lower() + 's'
            if pname not in existing_perms:
                Permission(permission_name=pname)
    level = ['member', 'host', 'director']
    for c in level:
        for prefix in ['add']:
            pname = prefix + '_' +  c.lower() + 's'
            if pname not in existing_perms:
                Permission(permission_name=pname)

def create_su():
    su_perm = Permission(permission_name='superuser')

    su_grp = Group(group_name='superuser',
                             display_name='Superuser',
                             place = None,
                             level = 'director')

    su_usr = model.User(user_name=turbogears.config.config.configs['syncer']['hubspaceadminuid'],
                      display_name='Hubspace App Admin',
                      password=turbogears.config.config.configs['syncer']['hubspaceadminpass'],
                      email_address="world.tech.space@the-hub.net",
                      active=1)

    su_perm = Permission.by_permission_name('superuser')
    su_grp.addPermission(su_perm)
    addUser2Group(su_usr, su_grp)

def create_wa():
    if model.User.selectBy(user_name="webapi").count():
        return

    wa = Permission(permission_name='webapi')

    wa_usr = User(user_name='webapi',
                  display_name='Mr. Webapi',
                  first_name='web',
                  last_name = 'api',
                  title = 'Api slave',
                  organisation = 'London Hub',
                  email_address='api@the-hubdoesntexist.net',
                  password='test',
                  skype_id = '',
                  address = '',
                  billingaddress='Nowhere really',
                  billto=None,
                  active=1)

    loc_id = model.Location.select()[0].id
    webapi_group  = Group(group_name='webapi',
                          display_name='webapi',
                          place = loc_id,
                          level = 'host')

    wa = Permission.by_permission_name('webapi')
    webapi_group.addPermission(wa)

def setup():
    # Before we call setup and populate (while testing), we need to login to syncer to make sure that all the object would
    # get created to LDAP as well. In order to login and create objects we need a user with superuser rights.
    if config.get('server.testing', False):
        recreate_tables()
    if not model.User.select().count():
        print "setup: Adding initial user/group(s)"
        create_su()
        model.hub.commit()
        print "setup: Done"

if not model.User.select().count():
    setup()

sync.setupLDAPSync()

################## TurboLucene ##################

def make_document(user):
    """Turn user into a TurboLucene document for full-text indexing.
    """
    document = Document()
    document.add(Field('id', str(user.id), STORE, UN_TOKENIZED))

    username = unicode(user.user_name.strip())
    if not isinstance(username, basestring):
        username = None
    if username:
        document.add(Field('user_name', username, STORE, UN_TOKENIZED))

    display_name = user.display_name
    if not isinstance(display_name, basestring):
        display_name = None
    if display_name:
        document.add(Field('display_name', display_name, STORE, TOKENIZED))

    description = user.description
    if not isinstance(description, basestring):
        description = None
    if description:
        document.add(Field('description', description, COMPRESS, TOKENIZED))

    org = user.organisation
    if not isinstance(org, basestring):
        org = None
    if org:
        document.add(Field('organisation', org, STORE, TOKENIZED))

    biz_type =  get_freetext_metadata(user, 'biz_type')
    if not isinstance(biz_type, basestring):
        biz_type = None
    if biz_type:
        document.add(Field('biz_type', biz_type, STORE, TOKENIZED))
    
    return document



def results_formatter(results):
    """Return the users that match the ids provided by TurboLucene"""
    if results:
        return User.select(IN(User.q.id, [int(id) for id in results])).orderBy("display_name")


def fulltext_index_users():
    import time
    for user in User.select():
        time.sleep(1)
        hubspace.search.update(user)
    return "success"



##################  Helpers  ####################

from hubspace.utilities.cache import strongly_expire
from turbogears.identity.conditions import Predicate, IdentityPredicateHelper

class not_anonymous(Predicate, IdentityPredicateHelper):
    '''
    Predicate for checking whether current visitor is anonymous.
    '''
    error_message= "Anonymous access denied"

    def eval_with_object(self, ident, errors=None):
	if identity.current.anonymous or identity.current.user.active==False:
		self.append_error_message( errors )
		return False

        return True


def alias_map(location=1):

    users = get_users_for_location(location)
    alias_map = {}
    for user in users:
        for alias in user.aliases:
            alias_map[alias.alias_name] = user.id
    return alias_map


################## Deletion Errors ##############
class NoSuchObject(Exception):
    pass

class LocationHasUsers(Exception):
    pass

class LocationHasRUsages(Exception):
    pass

class ResourceHasRUsages(Exception):
    pass

from hubspace.utilities.permissions import *

def can_delete_rusage(rusage):
    if (is_owner(rusage) and rusage.start>(now(rusage.resource.place)+timedelta(days=14))) or permission_or_owner(rusage.resource.place, None, 'manage_resources'):
        return True
        #if rusage.invoice==None:
        #    return True
    if identity.has_permission("superuser"):
	return True
    return False

###role assignment################

def roles_grantable(location):
    roles = []
    for group in location.groups:
        if permission_or_owner(location, None, 'add_'+ group.level + 's'):
            roles.append(group.level)
    return roles





#########################Search for users who need invoicing##############


def uninvoiced_users(location, resource_type, search_from_date):
    if len(resource_type)==2:
        users = User.select(AND(User.q.id==RUsage.q.userID,
                                RUsage.q.invoiceID==None,
                                RUsage.q.end_time<=search_from_date,
                                RUsage.q.resourceID==Resource.q.id,
                                Resource.q.placeID==location),
                            distinct=True)
    elif resource_type[0]=='tariff':
        users = User.select(AND(User.q.id==RUsage.q.userID,
                                RUsage.q.invoiceID==None,
                                RUsage.q.end_time<=search_from_date,
                                RUsage.q.resourceID==Resource.q.id,
                                Resource.q.type=='tariff',
                                Resource.q.placeID==location),
                            distinct=True)
    elif resource_type[0]=='resources':        
        users = User.select(AND(User.q.id==RUsage.q.userID,
                                RUsage.q.invoiceID==None,
                                RUsage.q.end_time<=search_from_date,
                                RUsage.q.resourceID==Resource.q.id,
                                Resource.q.type!='tariff',
                                Resource.q.placeID==location),
                            distinct=True)
    else:
        users = []
    
    users = [user.billto for user in users]
    unique_users = []
    for user in users:
	if user not in unique_users:
            unique_users.append(user)
    return unique_users


##################  Users  ####################

def get_users_for_location(place=None):
    """get all the users who are a member of a specific hub
    """
    if place:
        location = Location.get(place)
        users = []
        for group in location.groups:
            for user in group.users:
                if user not in users:
                    users.append(user)
    else:
        users = User.select()
    return users




##################  RUsage  ####################
    
booking_confirmation_text =  """Dear %(name)s,\n\nThank you for your booking at The Hub %(location)s.\n\nYou have booked %(resource)s from %(start)s to %(end)s on %(date)s. The expected cost of this usage is %(currency)s %(cost)s.\n\n%(options)sIn the event of a cancellation, the individual or organization booking the space will be charged 50%% of the total cost, unless it is cancelled more than two weeks prior to the event.\n\nIf you have any questions or further requirements please contact The Hub's hosting team at %(hosts_email)s or call us on %(telephone)s.\n\nWe look forward to seeing you.\n\nThe Hosting Team"""  

def create_rusage(**kwargs):
    '''Creates an RUsage, the use of an resource. It will also determine
    the cost of this usage at creation time, because the booked resource
    could later be removed, rendering the rusage otherwise useless. This
    implies that a tariff has to be booked for the starting time of the
    rusage'''
    if isinstance(kwargs['resource'], Resource):
        resource = kwargs['resource']
    else:
        resource = Resource.get(int(kwargs['resource']))

    if not kwargs['start']:
        kwargs['start'] = now(resource.place)
    if not kwargs['end_time']:
        kwargs['end_time'] = now(resource.place)
        
        
    if 'customname' in kwargs and kwargs['customname']:
	kwargs['resource_name'] = kwargs['customname']
	del kwargs['customname']
    if 'resource_name' not in kwargs:
        kwargs['resource_name'] = resource.name
    if 'resource_description' not in kwargs:
        kwargs['resource_description'] = resource.description
    kwargs.setdefault('invoice',None)
    tariff = get_tariff(resource.place.id, kwargs['user'], kwargs['start'])
    if not tariff and resource.type != 'tariff':
	raise NoTariffForUser(User.get(kwargs['user']).display_name, kwargs['start'], resource.place.name)

    kwargs['date_booked'] = now(resource.place)
    try:
        kwargs['bookedby'] = identity.current.user
    except RequestRequiredException:
        pass


    if 'customcost' in kwargs and not isinstance(kwargs['customcost'], float):
        if kwargs['customcost'] != None:
            kwargs['customcost'] = Money.to_python(str(kwargs['customcost']))
    if 'cost' in kwargs and not isinstance(kwargs['cost'], float):
        if kwargs['cost'] != None:
            kwargs['cost'] = Money.to_python(str(kwargs['cost']))

    rusage = create_object('RUsage',**kwargs)

    if not hasattr(rusage, 'customcost'):
        rusage.customcost = None
    
    if resource.type == 'tariff':
        # have we just created a tariff booking which will recursively price itself
	tariff = get_tariff(resource.place.id, kwargs['user'], kwargs['start'])
    #we need to calculate the cost at creation time
    #in case the resource the rusage is for gets deleted`
    rusage.tariff = tariff.id
    rusage.cost = calculate_cost(rusage)
    if 'usagesuggestedby' not in kwargs:
        options_text = ""
        if 'options' in kwargs:
            options = [Resource.get(option).name for option in kwargs['options']]
            if options:
                options_text = "You have also booked: " + ', '.join(options) +"."
        
        try:
            request = cherrypy.request.headers
        except AttributeError:
            request = None
        if rusage.resource.type != 'tariff' and rusage.resource.time_based and request:
            #validators.Money.from_python and therefore c2s does not work outside a request - which it needs to for some scheduled jobs
            location = rusage.resource.place
            data = dict ( rusage = rusage, user = rusage.user, location = location )
            msg_name = rusage.confirmed and "booking_confirmation" or "t_booking_made"
            hubspace.alerts.sendTextEmail(msg_name, location, data)
    return rusage
           
def user_stats(users):
    totals = {}
    totals['users'] = users.count()
    totals['profiles'] = 0
    totals['profile_images'] = 0
    totals['profile_and_image'] = 0
    for user in users:
        if user.description:
            totals['profiles'] += 1
        if user.image:
            totals['profile_images'] += 1
        if user.image and user.description:
            totals['profile_and_image'] += 1
    return totals


def genReportTitle(graph=None, params=None):
    if params:
        rname = params.get("r_name", None) or params.get("r_type", None)
        grpby = params["grpby"]
        g_type = params["g_type"]
        title = "%s usage grouped by %s (%s)" % (rname, grpby, g_type.title())
    if graph:
        rname = graph.records_filter.get("r_name", None) or graph.records_filter.get("r_type", None)
        grpby = graph.grpby
        g_type = graph.rtype
        title = "%s usage grouped by %s (%s)" % (rname, grpby, g_type.title())
    return title

def listSavedReports():
    return [(g.id, genReportTitle(graph=g), str(g.generated_on)) for g in model.Report.selectBy(owner=identity.current.user.id)]
    
##################  Invoice  ####################
class NoTariffForUser(Exception):
    def __init__(self, user, start, location):
        self.user = user
        self.start = start
        self.location = location
    def __str__(self):
        return 'There is no tariff booked for the user %s at the time of resource usage starting on %s in location %s' %(self.user, dateconverter.from_python(self.start), self.location)

def get_ordered_pricings(tariff, resource):
    return Pricing.select(AND(Pricing.q.tariffID == tariff.id,
                              Pricing.q.resourceID == resource.id)).orderBy("periodstarts")
              

def get_pricing(tariff, resource, month_datetime=None):
    """get the price of the resources during month
    """
    if month_datetime == None:
        month_datetime = now(resource.place)

    start = datetime(month_datetime.year, month_datetime.month, 1,0,0,1)
    end = datetime(month_datetime.year, month_datetime.month, 1,0,0,0)+ timedelta(calendar.monthrange(month_datetime.year, month_datetime.month)[1])

    if resource.type == 'tariff': tariff = resource # tariff change is happening

    try:
        pricing = Pricing.select(AND(Pricing.q.tariffID == tariff.id,
                                     Pricing.q.resourceID == resource.id,
                                     Pricing.q.periodstarts <= start,
                                     Pricing.q.periodends >= end))[0]
        return pricing.cost
    except:
        return None


def calculate_cost(rusage):
    """Calculate the cost for an rusage, taking user, tariffs and pricings into consideration
    ...and the location of the user :p
    """

    try:
        rusage = RUsage.get(int(rusage))
    except:
        pass

    price = get_pricing(rusage.tariff, rusage.resource, rusage.start)

    if rusage.resource.time_based and rusage.end_time:
        delta = rusage.end_time - rusage.start
        quantity = delta.seconds / 3600.0
        price = Decimal(str(quantity)) * Decimal(str(price))
    elif rusage.quantity and not rusage.resource.time_based:
        quantity = rusage.quantity
        price = Decimal(str(quantity)) * Decimal(str(price))
    else:
        raise NotBillable(rusage)

    TWOPLACES = Decimal(10) ** -2
    #use a different exponent to round to say 5 eurocents
    rounded = price.quantize(TWOPLACES) #for decimal    
    #price = round(price,2) #for floats
    return price


def pricing_changed_recalculate(new_pricing):
    """recalculate costs for usage because the price of a resource in a tariff has changed
    """    
    #get all rusages which are contained in the new time frame
    #are on the resource and tariff which are referred to in the price object
    #have not already been invoiced for

    rusages = RUsage.select(AND(RUsage.q.end_time <= new_pricing.periodends, 
                                RUsage.q.start >= new_pricing.periodstarts,
                                RUsage.q.resourceID == new_pricing.resource.id,
                                RUsage.q.tariffID == new_pricing.tariff.id,
                                RUsage.q.invoiceID == None))

    #if this selects a few extra rusages (which it does in some unusual situations) then not to worry since calculate costs shouldn't make any mistakes anyway
    for rusage in rusages:
        rusage.cost = calculate_cost(rusage)
   
def tariff_booking_changed_recalculate(user=None, tariff=None, start=None, end=None, catch_invoiced=False):
    """recalculate costs for usage: because a user changes tariff.
    Find all the rusages affected by that tariffbooking and not the tariffbooking itself
    """     
    sql = """rusage.user_id = %s AND
             rusage.start >= '%s' AND
             rusage.end_time <= '%s' AND
             rusage.resource_id != %s AND
             rusage.resource_id = pricing.resource_id AND
             pricing.tariff_id = %s""" % (user.id,
                                          dtc.from_python(start),
                                          dtc.from_python(end),
                                          tariff.id,
                                          tariff.id)
    
    rusages = RUsage.select(sql, clauseTables=['pricing', 'rusage'])

    rusages_invoiced = []
    for rusage in rusages:
        if catch_invoiced and rusage.invoiced:
            applogger.warn("tariff_booking_changed_recalculate: skipping rusage %s as it's already invoiced" % rusage.id)
            if rusage.tariff != tariff:
                rusages_invoiced.append(rusage)
            continue
        rusage.tariff = tariff.id
        rusage.cost = calculate_cost(rusage)
    return rusages_invoiced


class NotBillable(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
def get_collected_invoice_data(user=None, invoice=None, earliest=None, latest=None):
    empty = True
    if not user and not invoice:
        raise 'CantWorkLikeThis', 'You need to supply an userid or an invoiceid'
    elif invoice:
        inv_id = invoice
        collected = get_invoice_rusages(invoice.id)
    else:
        users = [u for u in user.billed_for]
        if user.billto==None and user not in users:
            users.append(user)
        inv_id = "no"
        collected = {}
        for user in users:
            collected[user] = show_rusages(get_rusages(user, invoice, earliest, latest))
            if len(collected[user][0])>1:
                empty = False
            
    return (collected, inv_id, empty)

def get_invoice_rusages(invoice):
    rusages = RUsage.select(AND(RUsage.q.invoiceID==invoice)).orderBy('start')
    collected = {}
    for rusage in rusages:
        if rusage.user not in collected:
            collected[rusage.user] = [rusage]
        else:
            collected[rusage.user].append(rusage)
    for user in collected:
        collected[user] = show_rusages(collected[user])    
        
    return collected
    

def get_rusages(user=None, invoice=None, earliest=None, latest=None):
    if user:
        user = user.id
    if invoice:
        invoice = invoice.id
    if earliest==None or latest==None:
        rusages = RUsage.selectBy(user=user,invoice=invoice)
    else:
        earliest = datetime(earliest.year, earliest.month, earliest.day, 0, 0, 0, 0)
        latest = datetime(latest.year, latest.month, latest.day, 0, 0, 0, 0)+timedelta(days=1)
        rusages = RUsage.select(AND(RUsage.q.userID==user,
                                    RUsage.q.confirmed==1,
                                    RUsage.q.invoiceID==invoice,
                                    RUsage.q.end_time>=earliest,
                                    RUsage.q.end_time<=latest)).orderBy('start')
    return rusages

from hubspace.utilities.dicts import ODict

def show_rusages(rusages):
    """If invoiceid=None, we get the uninvoiced resources for the specified time range;
    If this is an invoice, and earliest and latest are None we get the resources associated with a given invoice;
    
    """
    resources = ODict()
    sums = dict()

    for rusage in rusages:
        #would be good to use an ordered dict here to preserve the rusages start-date order
        resources.setdefault(rusage.resource, []).append(rusage)

    for resource in resources:
        if len(resources[resource])>1:
            if resource.time_based:
                sums[resource] = timedelta(0)
            else:
                sums[resource] = 0
                
            for rusage in resources[resource]:
                if rusage.refund:
                    sums[resource] -= quantity_or_duration(rusage) 
                else:
                    sums[resource] += quantity_or_duration(rusage) 

    return (resources, sums)


def sum_resource_costs(rusages):
    amount = 0
    for rusage in rusages:
        amount += [rusage.customcost,rusage.cost][rusage.customcost == None]
    return amount

def format_time_delta(time_delta):
    hours = time_delta.seconds/3600
    mins = time_delta.seconds%3600/60
    return str(hours) + " hours " + str(mins) + " mins"  

def quantity_or_duration(rusage):
    if rusage.resource.time_based:
        return rusage.end_time - rusage.start #duration in seconds and days
    else:
        return rusage.quantity


def show_quantity_or_duration(rusage):
    q = rusage
    if isinstance(rusage, RUsage):
        q = quantity_or_duration(rusage)
    if isinstance(q, int):
        return q
    return format_time_delta(q)

def display_resource_table(user=None, invoice=None, earliest=None, latest=None):
    if invoice:
        invoice_data = get_collected_invoice_data(invoice=invoice)
        user = invoice.user
        invoice = invoice.id
    elif user:
        invoice_data = get_collected_invoice_data(user=user, earliest=earliest, latest=latest)
        invoice = None

    ourdata = dict(invoice=invoice,
                   invoice_data=invoice_data,
                   mainuser=user)
    return try_render(ourdata, template='hubspace.templates.resourcetable', format='xhtml', headers={'content-type':'text/html'}, fragment=True)


def send_welcome_mail(user, password):
    if not password:
        password = md5.new(str(random.random())).hexdigest()[:8]
    location = user.homeplace
    data = dict ( location = location,
                  user = user,
                  password = password, )

    hubspace.alerts.sendTextEmail("member_welcome", location, data)

    user.welcome_sent = 1
    

def send_mail(to=None,sender='hubspace@members.the-hub.net',subject="",body="", attachment=None, attachment_name="attachment", attachment_content_type='application/pdf', cc=None):
    if attachment:
        sendmail.sendmail(to,sender,subject,body,[[attachment_name, attachment, attachment_content_type]], cc=cc)
        return True
    else:
        sendmail.sendmail(to,sender,subject,body, cc=cc)
        return True


##Resource Groups

def resource_groups(location):
    """Return the Resourcegroup objects associated with a location
    """
    ungrouped_resources = Resource.select(AND(Resource.q.placeID==location.id,
                                              Resource.q.resgroupID==None,
                                              Resource.q.type!='tariff',
                                              Resource.q.type!='calendar')) 
    ungrouped = AttrDict(name="Ungrouped",
                         description="Ungrouped-resources",
                         location=location,
                         resources=ungrouped_resources,
                         group_type='miscellaneous',
                         resources_order=[res.id for res in ungrouped_resources],
                         id=0)
    
    groups = Resourcegroup.select(Resourcegroup.q.locationID==location.id)
    ordered_groups = []
    group_order = location.resourcegroup_order
    if not group_order:
        group_order = [0]
    
    for group in group_order:
        if group and Resourcegroup.get(group) in groups:
            ordered_groups.append(Resourcegroup.get(group))
        elif group==0:
            ordered_groups.append(ungrouped)
    return ordered_groups



####Make Bookings ############

def make_booking(**kwargs):
    resource = Resource.get(kwargs['resource'])
    
    if resource.time_based and unavailable_for_booking(kwargs['resource'],
                                                       kwargs['start'],
                                                       kwargs['end_time'],
                                                       kwargs['rusage']).count():
        raise 'BookingConflict', 'Resource %s cannot be booked between %s and %s' % (resource.id,
                                                                                     kwargs['start'],
                                                                                     kwargs['end_time'])

    rusage = create_rusage(**kwargs)

    if 'options' in kwargs:
        book_suggested_resources(kwargs['options'], rusage, kwargs['user'], kwargs['start'], kwargs['end_time'])

    return rusage

def book_suggested_resources(resource_ids, booking, user, start, end_time):
    for resource in resource_ids:
        end_time = Resource.get(resource).time_based and end_time or start
        create_rusage(usagesuggestedby=booking.id, resource=resource, user=user, start=start, end_time=end_time, quantity=1)


def printer_resources(loc_id):
    resource_types = {'A4': {'colour': 'A4Colour',
                             'bw': 'A4BW'},
                      'Letter': {'colour': 'A4Colour',
                                 'bw': 'A4BW'},
                      'Other(0)': {'colour': 'A4Colour',
                                   'bw': 'A4BW'},
                      'A3': {'colour': 'A3Colour',
                             'bw': 'A3BW'}}
    

    for size in resource_types:
        for col in resource_types[size]:
            resource_types[size][col] = get_resource_id_by_name(resource_types[size][col], loc_id)
            if int(resource_types[size][col]) == -1:
                raise "problem getting printing resources"
    return resource_types


def parse_print_file(file_name="printing/jobs.csv", loc_id=1):
    """Parse the print file and enter corresponding usages.
    - we keep a processed to date. Usages in the master log before this are ignored
    - if usages fail due to any reason they get put in the failure log and reprocessed
    - hopefully that is due to their having missing aliases and once the aliases are entered they will be processed through
    """
    #use the log_file later
    #we need a remote way of accessing the logs.
    #we can periodically download the logs to london.the-hub.net from log_file = 'http://hublondon:hublondon\@192.168.1.238/jobacct.dat';
    #we then upload them from there into the print directory of hubspace
    #and run this every 10 minutes to parse new logs
    model.hub.begin()
    aliases = alias_map(loc_id)
    print_file = open(file_name, 'r')
    csv_file = csv.reader(print_file, csv.excel_tab)
    try:
        failure_log = open('printing/alias_failure.log', 'r')
        csv_failure = csv.reader(failure_log, csv.excel_tab)
    except:
        failure_log = None
        csv_failure = []
    try:
        processed_to = open('printing/processed_to', 'r')
        processed_to_date = print_dtc.to_python(processed_to.readline())
    except:
        processed_to = open('printing/processed_to', 'w')
        processed_to_date = None
    processed_to.close()
    if not processed_to_date:
        processed_to_date = datetime(1970, 1, 1)
    resource_types = printer_resources(loc_id)
    alias_failures = []
    other_failures = []
    unknown_aliases = []
    complete = 0
    date_string = None
    while not complete:
        #try:
            for job in csv_file:
                if job[0] == 'Job Index':
                    continue
                alias = job[2].strip()+'@'+job[3].strip()
                date_string = job[8].strip()
                try:
                    date = print_dtc.to_python(date_string)
                except:
                    date_string += ':00'
                    date_string = date_string.split('/')
                    date_string[2] = '20' + date_string[2]
                    date_string = '/'.join(date_string)
                    date = print_dtc.to_python(date_string)


                if date <= processed_to_date:
                    continue
                else:            
                    code = process_entry(job, alias, date, aliases, resource_types)
                    print "processed " + `code`
                    if code=='2':
                        if [alias] not in unknown_aliases:
                            unknown_aliases.append([alias])
                        alias_failures.append(job)
                    elif code=='1':
                        pass
                    elif code=='3':
                        other_failures.append(job)
                    elif code=='0':
                        print "duplicate"
            complete=1
 
        #except:

        #    pass 
    print_file.close()
    processed_to_date_string = None
    if date_string:
        processed_to_date_string = date_string
        print `processed_to_date_string`
        
    for job in csv_failure:
        alias = job[2].strip()+'@'+job[3].strip()
        date_string = job[8].strip()

        try:
            date = print_dtc.to_python(date_string)
        except:
            date_string += ':00'
            date_string = date_string.split('/')
            date_string[2] = '20' + date_string[2]
            date_string = '/'.join(date_string)
            date = print_dtc.to_python(date_string)

        code = process_entry(job, alias, date, aliases, resource_types)
        print "previous_failure " +  `code`
        if code=='2':
            if [alias] not in unknown_aliases:
                unknown_aliases.append([alias])
            alias_failures.append(job)
        elif code=='1':
            pass
        elif code=='0':
            other_failures.append(job)

    if failure_log:
        failure_log.close()

    model.hub.commit()

    if processed_to_date_string:
        processed_to = open('printing/processed_to', 'w')        
        processed_to.write(processed_to_date_string)
        processed_to.close()
    
    no_alias_log = open('printing/unknown_aliases.txt', 'w')
    no_aliases_csv = csv.writer(no_alias_log, csv.excel_tab)
    no_aliases_csv.writerows(unknown_aliases)
    no_alias_log.close()
        
    alias_failures_log = open('printing/alias_failure.log', 'w')
    csv_alias_failures = csv.writer(alias_failures_log, csv.excel_tab)
    csv_alias_failures.writerows(alias_failures)
    alias_failures_log.close()

    #assumed to be duplicate entries
    other_failures_log = open('printing/other_failure.log', 'a')
    csv_other_failures = csv.writer(other_failures_log, csv.excel_tab)
    csv_other_failures.writerows(other_failures)
    other_failures_log.close()

    return 'success'


def get_resource_id_by_name(name=None, location=None):
    resource = Resource.select(AND(Resource.q.active==1,
                                   Resource.q.name==name,
                                       Resource.q.placeID==location))
    if len(list(resource))==1:
        return str(resource[0].id)
    return str(-1)


def process_entry(job, alias, start_date, aliases, resource_types):
    try:
        user_id = aliases[alias]
    except:
        return '2'

    end_date = job[9].strip()
    try:
        end_date = print_dtc.to_python(end_date)
    except:
        end_date += ':00'
        end_date = end_date.split('/')
        end_date[2] = '20' + end_date[2]
        end_date = '/'.join(end_date)
        end_date = print_dtc.to_python(end_date)
  
    job_name = job[5].strip()
    pages = int(job[7].strip())
    page_size = job[12].strip()
    print page_size
    try:
        resource_size = resource_types[page_size]
    except:
        resource_size = resource_types['A4']
    print `resource_size`
    c = job[13].strip()
    m = job[14].strip()
    y = job[15].strip()
    k = job[16].strip()
    if c=="0.000000%" and m=="0.000000%" and y=="0.000000%":
        col = 'bw'
    else:
        col = 'colour'
    resource_id = resource_size[col]
    print `resource_id`
    hash_description = job_name +" - Job ID:"+ md5.new(job_name + alias + print_dtc.from_python(start_date)).hexdigest()
    code = book_print_resource(resource_id, resource_description=hash_description, quantity=pages, start=start_date, end_time=end_date, user=user_id)
    return code



def book_print_resource(resource_id, resource_description, tg_errors=None, **kwargs):
    """
    """
    resource_description = resource_description.decode('utf-8', 'replace')
    resource_description = resource_description.encode('utf-8')
    rusages = RUsage.select(AND(RUsage.q.resourceID==resource_id,
                                RUsage.q.resource_description==resource_description))

    try:
        rusages[0]

        #this is a duplicate since the hash in the description is the same
        print "already_done"
        return "0"
    except:
        pass
    try:
        kwargs['resource_description'] = resource_description
        kwargs['resource'] = resource_id
        make_booking(**kwargs)
        return "1"
    except Exception, e:
        print `e`
        return "3"


def get_rusage_bookings(resource, start, end):
    rusages = RUsage.select(AND(RUsage.q.resourceID == resource.id,
                                RUsage.q.start>=start,
                                RUsage.q.end_time<=end,
                                RUsage.q.cancelled == 0))
    return rusages

def unavailable_for_booking(resourceid, start, end, rusage_id=None, ignore_current_res=False):
    '''Checks if there are conflicts if the given resourcid would be booked at 
    the given time. It also checks for dependencies. Should also check for opening times.
    With rusage_id it avoids seeing the booking that is being edited as a conflict'''
       
    resource = Resource.get(resourceid)
    requires = [resourceid]
    requiredby = [resourceid]
    
    requiredby = res_requiredby(resource, requiredby)
    requires = res_requires(resource, requires)

    if ignore_current_res:
        requires.remove(resourceid)
        requiredby.remove(resourceid)

    for res in requires:
        if res not in requiredby:
            requiredby.append(res)
    
    return booked(requiredby, start, end, rusage_id=rusage_id)
     
def res_requires(resource, requires):
    """warning!! non-tail recursion like this may have a negative effect on your stack size
    and memory usage but seems to be necessary to stop cycles in this case. Anyway we are
    probably dealing with relatively low depth recursion
    """
    for r in resource.requires:
        if r.id not in requires:
            requires.append(r.id)
            res_requires(r, requires)
    return requires
    
def res_requiredby(resource, requiredby):
    for r in resource.requiredby:
        if r.id not in requiredby:
            requiredby.append(r.id)
            res_requiredby(r, requiredby)      
    return requiredby

def booked(requirements, start, end, rusage_id=None):
    #        <-- event1 -->           conflicting event
    #     <-- e2 -->                  before
    #               <-- e3 --->       after
    #    <-- e4             ->        containing
    #          <-- e5 -->             contained
    #        <-- event6->             starting same
    #              <-ev7-->           ending same
    # but 
    #<-- e7-->                        no problem (start and end == same)
    #
    if not requirements:
        return []
    return RUsage.select(AND(IN(RUsage.q.resourceID, requirements),
                             RUsage.q.cancelled == 0,
                             RUsage.q.id != rusage_id,
                             OR(AND(RUsage.q.start <= start,
                                    RUsage.q.end_time > start),
                                AND(RUsage.q.start > start,
                                    RUsage.q.end_time < end),
                                AND(RUsage.q.start < end,
                                    RUsage.q.end_time >= end))))



class NoBooking(Exception):
    def __init__(self, resourceid, datetime):
        self.resourceid = resourceid
        self.start = datetime 
    def __str__(self):
        return repr("no booking for %s at time %s" %(str(self.resourceid), datetimeconverter.from_python(self.start)))








################### Hosting ####################

def todo_to_AttrDict(todo):
    return AttrDict(createdby=todo.createdby.display_name,
                    opened=todo.opened,
                    due=todo.due,
                    subject=todo.subject,
                    body=todo.body,
                    foruser=todo.foruser,
                    action=todo.action,
                    action_id=todo.action_id,
                    closed=todo.closed,
                    id=todo.id)

def ascending_dates(todo1, todo2):
    if todo1.due and todo2.due:
        if todo1.due <= todo2.due:
            return -1
        else:
            return 1
    elif todo1.due and not todo2.due:
        return -1
    elif not todo1.due and todo2.due:
        return 1
    else:
        if todo1.opened <= todo2.opened:
            return -1
        else:
            return 1 

def ascending_evt_dates(ev1, ev2):
    if ev1.start and ev2.start:
	if ev1.start <= ev2.start:
	    return -1
        else:
	    return 1

def urgent(user):
    urgent = (Todo.select(AND(Todo.q.due<=now(user.homeplace),
			      Todo.q.closed==None,
			      Todo.q.foruserID==user.id)))
    urgent_list = [todo_to_AttrDict(todo) for todo in urgent]
    for urgent in urgent_list:
        action = urgent.action and urgent.action or "edit"
        urgent.action = action + '_urgent'
    urgent_list.sort(ascending_dates)
    return urgent_list

def events(user, date):
    locations = user_locations(user, ['host'])
    evs_date = RUsage.select(AND(RUsage.q.start>=date,
				 RUsage.q.start<=date+timedelta(hours=24)))
    evs = []
    for ev in evs_date:
	if ev.resource.place in locations and ev.resource.time_based:
	    evs.append(ev)
    ev_time = v.DateTimeConverter("%H:%M").from_python 
    evs.sort(ascending_evt_dates)
    return [AttrDict(createdby=ev.bookedby.display_name,
		     opened=ev.date_booked,
		     subject= ev_time(ev.start) + ' to ' + ev_time(ev.end_time),
                     due=None,
                     foruser=ev.user,
                     body=ev.user.display_name + ' has booked ' + ev.resource.name,
                     action='event',
                     closed=None,
                     action_id=ev.user.id,
                     id=ev.id) for ev in evs]


def todos(bar, user):
    todo_list = [todo_to_AttrDict(todo) for todo in bar.children if todo.foruser==user]
    todo_list.sort(ascending_dates)
    return todo_list

def invoices_to_create(user):
    """Suggest creating invoices where there are uninvoiced resource usages ending in the previous month or before (in the hosts location). Creation date should be the 1st day of the month after the earliest ending resource usage.  
    """
    locations = user_locations(user, ['host'])
    
    right_now = now(user.homeplace)
    month_begin = datetime(right_now.year, right_now.month, 1)

    uninvoiced = RUsage.select(AND(RUsage.q.invoiceID==None,
                                   RUsage.q.end_time<=month_begin))
    
    uninvoiced_in_place = [RUse for RUse in uninvoiced if RUse.resource.place in locations]
    uninvoiced_in_place.sort(min_end_date)

    users = []
    create_date = {}
    for RUse in uninvoiced_in_place:
        user = RUse.user.billto
        if user==None:
            user=RUse.user 
        if user not in users:
            users.append(user)
            create_date[user.id] = create_invoice_date(RUse)
            users.sort(sort_alpha(create_date))

    return [AttrDict(createdby="hubspace",
                     opened=create_date[user.id],
                     subject='Create an invoice for %s' % (user.display_name),
                     due=None,
                     foruser=None,
                     body=None,
                     action='invoice',
                     closed=None,
                     action_id=user.id,
                     id=user.id) for user in users]


def sort_alpha(create_date):
    def sort_it(a, b):
        if create_date[a.id]>create_date[b.id]:
            return 1
        elif create_date[a.id]==create_date[b.id]:
            if a.display_name>b.display_name:
                return 1
            else:
                return -1
        else:
            return -1
    return sort_it

def min_end_date(a, b):
    if a.end_time>b.end_time:
        return 1
    return -1

def create_invoice_date(RUse):
    month_create = RUse.start.month%12 + 1
    year_create = RUse.start.year + RUse.start.month/12
    return datetime(year_create, month_create, 1)


def invoices_unsent(user):
    """invoice created and not sent which include rusage on resources in the location where the current user is a host 
    """
    unsent = Invoice.select(AND(Invoice.q.sent==None))
    invoices = []

    locations = user_locations(user, ['host'])
    for invoice in unsent:
        for rusage in invoice.rusages:
            if rusage.resource.place in locations:
                invoices.append(invoice)
                break
    
    unsent= [AttrDict(createdby="hubspace",
                     opened=invoice.created,
                     subject='Send Invoice to %s' %(invoice.user.display_name),
                     body='For %s from %s to %s: %s %s' % (invoice.user.display_name,
                                                           datetimeconverter.from_python(invoice.start),
                                                           datetimeconverter.from_python(invoice.end_time),
                                                           invoice.location.currency,
                                                           c2s(invoice.amount)),
                      due=None,
                      foruser=None,
                      action='send',
                      closed=None,
                      id = invoice.id,
                      action_id=invoice.user.id) for invoice in invoices]
    unsent.sort(ascending_dates)
    return unsent

def reminders(user):
    locations = user_locations(user, ['host'])
    locations = [location.id for location in locations]
            
    reminders = User.select(AND(User.q.outstanding!=0,
                                User.q.homeplaceID in locations,
                                OR(User.q.last_reminder<now(user.homeplace)-timedelta(days=30),
                                   User.q.last_reminder==None)))

    return [AttrDict(createdby="hubspace",
                 subject='Remind %s' %(user.display_name),
                 body=reminder_body(user),
                 due=None,
                 foruser=None,
                 opened= None,
                 action='remind',
                 extra_action = 'ignore',
                 closed=None,
                 action_id=user.id,
                 id=user.id)
                 for user in reminders]
                 

def reminder_body(user):
    if user.last_reminder:
        date =  datetimeconverter.from_python(user.last_reminder+timedelta(days=30))
        return "%s has %s outstanding and has been sent %s reminders. Last reminder was sent on %s" % (user.display_name, c2s(user.outstanding), user.reminder_counter, date) 
    return "%s has %s %s outstanding. No reminders sent" %(user.display_name, user.homeplace.currency, c2s(user.outstanding))



################## Feed ##################
        
class Feed(FeedController):
    @validate(validators={'type':v.UnicodeString(), 'location':v.Int()})    
    def get_feed_data(self, type="profiles", location=0):
        if location == 0:
            data = cached_updates[type]['global']
        else:
            data = cached_updates[type][location]
        try:
            location = Location.get(location)
        except:
            location = None
        title = "Empty feed from The Hub"
        if len(list(data)):
            if isinstance(data[0], User):
                data = [{'title':entry.display_name,
                         'author': dict(name = entry.display_name),
                         'summary': entry.description,
                         'published': entry.created,
                         'updated': entry.modified or entry.created,
                         'link': '%s/profiles/%s' %(cherrypy.request.base, entry.user_name)} for entry in data]
                for item in data:
                    print `item['updated']`
                if location:
                    title = "%s Profile Updates" %(location.name)
                else:
                    title = "Hub Network Profile Updates"
            if isinstance(data[0], RUsage):
                data = [{'title':"%s  Location: %s - %s"%(entry.meeting_name,  entry.resource.place.name, entry.resource.name),
                         'author': dict(name = entry.user.display_name),
                         'summary': "%s" %(entry.meeting_description),
                         'published': entry.date_booked,
                         'link': '%s/events/%s' %(cherrypy.request.base, entry.id)} for entry in data]
                if location:
                    title = "%s Events Updates" %(location.name)
                else:
                    title = "Hub Network Events Updates"
        return {'entries':data, 'title':title}
          

################RFID Controllers#########################
def get_user_from_rfid(rfid):
    try:
        user = User.select(User.q.rfid==rfid)[0]
    except IndexError:
        user = None
    return user

class RFID(controllers.Controller):
    @expose(template="hubspace.templates.memberRFID")
    @validate(validators={'user_id':real_int})
    def unregister_card(self, user_id, reason=None):
        """delete rfid attribute and log the reason and rfid
        """
        user = User.get(user_id)
        if not permission_or_owner(user_locations(user, ["member"]), None, 'manage_users'):
            raise IdentityFailure('what about not hacking the system')

        user.rfid = None
        return {'object':user}

    @expose(template="hubspace.templates.memberRFID")
    @validate(validators={'user_id':real_int, 'rfid':valid_rfid})
    def add_card(self, user_id=None, rfid=None, tg_errors=None):
        """associate the rfid with the user
        """
        if tg_errors:
            for tg_error in tg_errors:
                return str(tg_errors[tg_error])
        # does the user already have an rfid
        user = User.get(user_id)
        if not permission_or_owner(user_locations(user, ["member"]), None, 'manage_users'):
            raise IdentityFailure('what about not hacking the system')

        if user.rfid:
            return "This user already has an rfid card assigned"
        user.rfid = rfid
        return {'object':user}

    @expose()
    @validate(validators={'rfid':valid_rfid})
    def find_user_from_rfid(self, rfid):
        if not permission_or_owner(None, None, 'manage_users'):
            raise IdentityFailure('what about not hacking the system')

        user = get_user_from_rfid(rfid)
        return user


def make_superuser(user):
    super_group = Group.select(AND(Group.q.group_name=='superuser', 
                                   Group.q.placeID==None))[0]
    super_group.addUser(user)

##################Members SubController############
class Members(controllers.Controller):
    @expose()
    def index(self):
        return "Not Available"

    @expose()
    def default(self, username, subsection="mainProfile"):
        # redirect to front page
        user = User.by_user_name(username)
        if not identity.current.user:
            raise redirect(cherrypy.request.base + "/login")
        if user.id != identity.current.user.id:
            template = "hubspace.templates.network"
            area = 'network'
        else:
            template = "hubspace.templates.profile"
            area = 'profile'
        return try_render({'object':user, 'area':area, 'subsection':subsection, 'tg_css':[], 'tg_js_head':[], 'tg_js_bodytop':[], 'tg_js_bodybottom':[]}, template=template, format='xhtml', headers={'content-type':'text/html'})



from hubspace.utilities.booking import booking_offset_plus_height, default_booking_params
from hubspace.utilities.i18n import get_hubspace_locale, get_location_from_base_url, get_po_path
from hubspace.microSite import Sites
##################  Root  ####################

def expose_as_csv(f):
    @expose()
    @strongly_expire
    def wrap(*args, **kw):
        rows = f(*args, **kw)
        out = StringIO.StringIO()
        writer = csv.writer(out, lineterminator='\n', quoting=csv.QUOTE_ALL)
        writer.writerows(rows)
        cherrypy.response.headerMap["Content-Type"] = "text/csv"
        cherrypy.response.headerMap["Content-Length"] = out.len
        return out.getvalue()
    return wrap


import simplejson

class RPC(controllers.Controller):

    #@expose(format="json")
    def rpc_error_handler(self, *args, **kw):
        if 'tg_errors' in kw:
            return dict(errors = kw['tg_errors'])

    @expose(format="json")
    @error_handler(rpc_error_handler)
    def default(self, *args, **kw):
        jsonin = simplejson.loads(cherrypy.request.body.read())
        rpcver=jsonin.get("jsonrpc","1.0")
        methodname=jsonin["method"]
        params = jsonin['params']
        _id = jsonin['id']
        f = getattr(self, methodname)
        if isinstance(params, dict):
            ret = f(**params)
        else:
            ret = f(*params)
        return dict(error=None, result=ret, id=_id)

    @identity.require(not_anonymous())
    def get_messagesdata_for_cust(self):
        messages = dict( [(name, dict(label=o.label)) for (name, o) in hubspace.alerts.messages.bag.items() if o.can_be_customized] )
        locations = sorted([(loc.id, loc.name) for loc in user_locations(identity.current.user)], key=lambda x:x[1])
        return dict (messages=messages, locations=locations)

    @identity.require(not_anonymous())
    def get_messagecustdata(self, msg_name, loc_id):
        loc = model.Location.get(loc_id)
        msg = hubspace.alerts.messages.bag[msg_name]
        return dict( text = msg.getTemplates(loc)['body'],
                         macros = [dict(label=m.label, name=m.name) for m in msg.available_macros] )
    
    @identity.require(not_anonymous())
    @error_handler(rpc_error_handler)
    @validate(validators=MessageCustSchema)
    def customize_message(self, loc_id, msg_name, msg_cust, lang=None):
        loc = model.Location.get(loc_id)
        msg = hubspace.alerts.messages.bag[msg_name]
        lang = lang or loc.locale
        return msg.addNewCustomization(loc, msg_cust, lang)

class Root(controllers.RootController):
    members = Members()
    rfid = RFID()
    feed = Feed()
    sites = Sites()
    rpc = RPC()

    @expose("hubspace.templates.managementReport")
    def generate_report(self, locations, report_types, period=None, start=None, end=None,format="web"):
        if not isinstance(locations, list): locations = [locations]
        if not isinstance(report_types, list): report_types = [report_types]
        locations = [int(loc) for loc in locations]
        if not set(locations).issubset(tuple(loc.id for loc in user_locations(identity.current.user))):
            raise IdentityFailure('what about not hacking the system')
        if start and end:
            start, end = dateconverter.to_python(start), dateconverter.to_python(end)
        mode = len(locations) > 1 and "comparison" or "onelocation"
        stats = dict(((Location.get(loc).name, {}) for loc in locations))
        for location in locations:
            lstats = reportutils.LocationStats(location, period, start, end)
            loc_name = Location.get(location).name
            for report_type in report_types:
                data = getattr(lstats, 'get_' + report_type)()
                if report_type in ('members_by_tariff', 'revenue_by_resource', 'revenue_by_resourcetype', 'revenue_by_tariff'):
                    data = tuple((name, ((0, number),)) for name, number in data)
                    stats[loc_name][report_type] = reportutils.Report(data)
                elif report_type == 'summary':
                    stats[loc_name][report_type] = data
                elif report_type == 'revenue_stats':
                    options = dict ( axis = dict(x = dict(
                                                ticks = [dict(v=i, label=cell[0]) for i, cell in enumerate(data)],
                                                label = 'Months', rotate = 25),
                                                y = dict(label='Revenue', tickCount=5)),)
                    data = [('months', tuple((i, cell[1]) for i,cell in enumerate(data)))]
                    stats[loc_name][report_type] = reportutils.Report(data, options)
                elif report_type == 'churn_stats':
                    options = dict ( axis = dict(x = dict(
                                                ticks = [dict(v=i, label=cell[0]) for i, cell in enumerate(data)],
                                                label = 'Months', rotate = 25) ),
                                     title = "Churn rate" )
                    left_data = tuple((i, cell[1][0]) for i,cell in enumerate(data))
                    back_data = tuple((i, cell[1][1]) for i,cell in enumerate(data))
                    data = [('Members left', left_data), ('Members came back', back_data)]
                    stats[loc_name][report_type] = reportutils.Report(data, options)
                elif report_type == 'usage_by_tariff':
                    stats[loc_name][report_type] = dict()
                    for r_type, rt_data in data.items():
                        tariffs_iter = list(enumerate(set(itertools.chain(*(t_dict.keys() for t_dict in rt_data.values())))))
                        tariffs_dict = dict(tariffs_iter)
                        data = [(r_name, tuple((i, r_data.get(t,0)) for i,t in tariffs_iter)) for r_name, r_data in rt_data.items()]
                        options = dict ( axis = dict(x = dict(label='Tariffs', ticks = [dict(v=i, label=Resource.get(t).name) for i,t in tariffs_iter], ),
                                                     y = dict(tickCount=5, rotate = -25, label="Usage hours/quantity")),
                                         padding = dict(left = 150, bottom = 75, top = len (data) * 20))
                        stats[loc_name][report_type][r_type] = reportutils.Report(data, options)

        d =dict(stats=stats, report_types=report_types, start=lstats.start, end=lstats.end)
        if format == 'web':
            return d
        elif format == 'pdf':
            html =  try_render(d, template='hubspace.templates.managementReport', format='html', headers={'content-type':'text/html'})
            html = html.replace("NEXTPAGEHACK", "<div> <pdf:nextpage/> </div> ")
            src = cStringIO.StringIO(html)
            dst = cStringIO.StringIO()
            pdf = pisa.CreatePDF(src, dst, default_css=file("hubspace/static/css/micro/blueprint/screen.css").read(), encoding='utf-8')
            dst.seek(0)
            cherrypy.response.headers['Content-type'] = 'application/pdf'
            return dst.read()

    @identity.require(not_anonymous())
    @expose()
    def report_image(self, *path):
        mimetype = "image/png"
        cherrypy.response.headerMap["Content-Type"] = str(mimetype)
        path = os.sep.join(path)
        return file(path).read()

   
    @identity.require(not_anonymous())
    @expose()
    def download_messages_po(self, *args, **kw):
        po_path = get_po_path()
        out = file(po_path).read()
        cherrypy.response.headerMap["Content-Type"] = "application/x-gettext"
        cherrypy.response.headerMap["Content-Length"] = len(out)
        return out
   
    @expose("hubspace.templates.flexigrid")
    def users_grid(self, *args, **kw):
        return kw

    def _export_users(self, location, sortname, sortorder, fields, start, end):
        from hubspace.utilities.users import fields as user_fields
        fields = [f for f in user_fields if f in fields]
        sortname = (sortname in fields and sortname) or "display_name" in fields and "display_name" or fields[0]
        if location == "all":
            select = model.User.select()
        else:
            select = model.User.select(AND(model.User.q.homeplaceID==int(location)))
        total = select.count()
        if sortname not in [c.name for c in User.sqlmeta.columnList]:
            block = sorted(select, key=lambda u: getattr(u, sortname))
            if sortorder == 'desc':
                block = block[::-1][start:end]
        else:
            if sortorder == 'desc':
                block = select.orderBy(DESC(getattr(model.User.q, sortname)))[start:end]
            else:
                block = select.orderBy(sortname)[start:end]
        return total, [[getattr(u, k) for k in user_fields if k in fields] for u in block]

    @expose_as_csv
    @validate(validators=ExportUsersCSVSchema)
    @identity.require(not_anonymous())
    def export_users_csv(self, location, sortname, usercols_selction, sortorder="asc"):
        start, end = 0, -1
        total, rows = self._export_users(location, sortname, sortorder, usercols_selction, start, end)
        return rows

    @expose(format="json")
    @validate(validators=ExportUsersJSONSchema)
    def export_users_json(self, location, page=1, rp=25, sortname=None, sortorder='asc', qtype=None, query=None, **fields):
        end = page * rp
        start = end - rp
        total, block = self._export_users(location, sortname, sortorder, fields, start, end)
        rows = [dict(cell=cell) for cell in block]
        return dict(page=page, total=total, rows=rows)

    @expose()
    @identity.require(identity.has_permission('superuser'))
    def regenerate_all(self):
        for site_name in self.sites.__class__.__dict__:
            site = getattr(self.sites, site_name)
            try:
                site.regenerate_all()
            except:
                pass
        return "done"

    _cp_filters = sync._cp_filters

    def _cpOnError(self):
        """log the error and give the user a trac page to submit the bug
        We should give the error a UID so that we can find the error associated more easily
        """
        # If syncer transaction fails the syncer daemon takes care of rolling back the changes also
        # syncerclient then raises SyncerError effectively stops TG transaction from commiting
        # changes to native database.
        # For all other errors we should call syncer rollback here.
        # And finally if there is no error, we send transaction complete signal to syncer. Which is
        # handled by TransactionCompleter filter.
        if config.get('server.testing', False):
            cherrypy.response.status = 500
        else:
            cherrypy.response.status = 200
        e_info = sys.exc_info()
        e_id = str(datetime.now())
        e_path = cherrypy.request.path
        _v = lambda v: str(v)[:20]
        e_params = dict([(k, _v(v)) for (k, v) in cherrypy.request.paramMap.items()])
        e_hdr = cherrypy.request.headerMap
        applogger.error("%(e_id)s: Path:%(e_path)s" % locals())
        applogger.error("%(e_id)s: Params:%(e_params)s" % locals())
        applogger.exception("%(e_id)s:" % locals())
        if isinstance(e_info[1], sync.SyncerError):
            applogger.error("%(e_id)s: LDAP sync error" % locals())
        else:
            sync.sendRollbackSignal()
        tb = sys.exc_info()[2]
        e_str = traceback.format_exc(tb)
        if isinstance(e_info[1], hubspace.errors.ErrorWithHint):
            e_hint = e_info[1].hint
        else:
            e_hint = ""
        d = dict(e_id=e_id, e_path=e_path, e_str=e_str, e_hint=e_hint)
        cherrypy.response.body = try_render(d, template='hubspace.templates.issue', format='xhtml', headers={'content-type':'text/html'}, fragment=True)

    @expose_as_csv
    @identity.require(not_anonymous())
    def members_csv(self):
        l = [(u.active, u.homeplace.name, u.first_name.encode('utf-8'), u.last_name.encode('utf-8'), u.email_address, u.email2, u.email3) for u in model.User.select()]
        l = sorted(l, key=lambda x: x[1])
        l.insert(0, ("Active", "Home Hub", "First Name", "Last Name", "Email", "Email2", "Email3"))
        return l

    @expose()
    @identity.require(not_anonymous())
    def submitTicket(self, e_id, e_path, e_str, u_summary, u_desc=""):
        homeplace = identity.current.user.homeplace.name
        reporter = identity.current.user.display_name
        email = identity.current.user.email_address
        summary = u_summary.encode('utf-8')
        description = """
Location: %(homeplace)s

Error ID: %(e_id)s

URL: %(e_path)s

User Description:

Exception: 
{{{
%(e_str)s
}}}
""" % locals()


        baseurl = turbogears.config.config.configs['trac']['baseurl']
        loginurl = baseurl + turbogears.config.config.configs['trac']['loginpath']
        newticketurl = baseurl + turbogears.config.config.configs['trac']['newticketpath']
        try:
            b = mechanize.Browser()
            b.open(loginurl)
            forms = list(b.forms())
            for form in forms:
                if set(["user", "password"]).issubset(set([c.name for c in form.controls])):
                    nr = forms.index(form)
                    b.select_form(nr=nr)
                    break
            # else: no form ?
            b['user'] = turbogears.config.config.configs['trac']['user']
            b['password'] = turbogears.config.config.configs['trac']['password']
            b.submit()

            b.open(newticketurl)
            forms = list(b.forms())
            for form in forms:
                if set(["field_reporter", "field_summary"]).issubset(set([c.name for c in form.controls])):
                    nr = forms.index(form)
                    b.select_form(nr=nr)
                    break
            # else: no form ?
            b["field_reporter"] = "%(reporter)s <%(email)s>" % locals()
            b["field_summary"] = summary
            b["field_description"] = description
            b["field_type"] = ["defect"]
            b["field_priority"] = ["major"]
            #if component:
            #    b["field_component"] = component
            b.submit('submit')
            links = b.links()
            defect_url = [lnk for lnk in b.links() if lnk.text == 'View'][0].absolute_url
            return "Thank you, %s, you can further followup the defect at <a href=%s>Hubspace Trac</a>" % (reporter, defect_url)
        except Exception, err:
            applogger.exception("Trac submission error:")
            data = dict ( user=identity.current.user, tb=sys.exc_info()[2] )
            extra_data = dict ( e_id=e_id, summary=summary, description=description, url=newticketurl )
            hubspace.alerts.sendTextEmail("trac_submission_failed", data=data, extra_data=extra_data)
        return "Thank you, %s!" % reporter

    @expose(allow_json=True)
    @validate(validators={'start':dateconverter, 'end':dateconverter})
    def saveUsageReport(self, start, end, grpby, r_name, r_type, user_id, rtype, tg_errors=None):
        if r_type == 'all': r_type = None 
        if r_name == 'all': r_name = None 
        if user_id == 'all': user_id = None 
        if start == 'all': start = None 
        if end == 'all': end = None 
        now = datetime.now()
        model.Report(owner=identity.current.user.id, generated_on=now, rtype=rtype,
            start_date=start, end_date=end, grpby=grpby, records_filter=dict(r_name=r_name, r_type=r_type, user_id=user_id))
        return dict (ret = True)

    @expose(allow_json=True)
    @validate(validators={'g_id':real_int})
    def deleteUsageReport(self, g_id):
        g = model.Report.get(g_id)
        ret = False
        if g.owner.id == identity.current.user.id:
            g.destroySelf()
            ret = True
        return dict (ret = ret)

    @expose()
    @validate(validators={'g_id':real_int})
    def rerenderSavedReport(self, g_id, format, fname=None):
        data = model.Report.get(g_id)
        location_id = get_location_from_base_url().id
        start = data.start_date
        end = data.end_date
        g_type = data.rtype
        records_filter = data.records_filter
        if not records_filter: records_filter = {}
        r_name = records_filter.get('r_name', None)
        r_type = records_filter.get('r_type', None)
        user_id = records_filter.get('user_id', None)
        grpby = data.grpby
        if r_type == "tariff":
            if format == "csv":
                return self.get_tariff_usage_csv(start, end)
            else:
                return self.get_tariff_usage(location_id, start, end)
        else:
            if format == "csv":
                return self.get_usage_csv(location_id, r_type, r_name, user_id, start, end, grpby, g_type)
            else:
                return self.get_usage_graph(location_id, r_type, r_name, user_id, start, end, grpby, g_type)

    def index(self):
        return self.default()

    def get_rusage_entries(self, location_id, r_type=None, r_name=None, user_id=None, start=None, end=None):
        location_id = int(location_id)
        select_crit = []
        if user_id:
            user_id = int(user_id)
            select_crit.append(RUsage.q.userID == user_id)
        if r_name:
            r_name = int(r_name)
            select_crit.append(RUsage.q.resource == r_name)
        if r_type:
            select_crit.append(IN(RUsage.q.resource_name, Select(Resource.q.name, where=(AND(Resource.q.type == r_type, Resource.q.place == location_id)))))
        else:
            select_crit.append(IN(RUsage.q.resource_name, Select(Resource.q.name, where=(Resource.q.place == location_id))))

        if start:
            select_crit.append(RUsage.q.start > start)
        if end:
            select_crit.append(RUsage.q.end_time <= end)

        select = RUsage.select(AND(*select_crit))

        return list(select)

    @expose_as_csv
    def get_tariff_usage_csv(self, location_id, fname=None):
        rows = self.get_rusage_entries(location_id, "tariff", None , None, None, None)
        grouped_tariffs = []
        month_helper = reportutils.Month(rows[0].resource)
        all_tariffs = set([r.name for r in Location.get(location_id).resources if r.type == 'tariff'])
        weighted_tariffs = [r[1] for r in sorted([(len(list(grp)), r_name) for (r_name, grp) in reportutils.sortAndGrpby(rows, lambda ru: ru.resource_name)], reverse=True)] # readable ?
        tariff_no_entries = all_tariffs.difference(weighted_tariffs)
        weighted_tariffs.extend(tariff_no_entries)

        date_grouper = lambda ru: ru.start
        rows.sort(key=date_grouper, reverse=True)
        rname_grouper = lambda ru: ru.resource_name
        for (start, grp) in itertools.groupby(rows, date_grouper):
            usages = dict ([(r_name, len(list(grp))) for (r_name, grp) in reportutils.sortAndGrpby(grp, rname_grouper)])
            grouped_tariffs.append((start.strftime("%B %Y"), usages))

        out = [["Month"] + weighted_tariffs]
        for (start, usages) in grouped_tariffs:
            out_row = [start]
            for t in weighted_tariffs:
                out_row.append(usages.get(t, 0))
            out.append(out_row)
        
        return out

    @expose_as_csv
    @identity.require(not_anonymous())
    @validate(validators={'start':dateconverter, 'end':dateconverter})
    def get_usage_csv(self, location_id, r_type=None, r_name=None, user_id=None, start=None, end=None, grpby=None, g_type="pattern", fname=None):
        """
        fname is only to form a url that adds right extension to our file
        """
        title, rows = self.get_usage_data(location_id, r_type, r_name, user_id, start, end, grpby, g_type, "strf")
        if g_type == "timeseries":
            rows_new = []
            for i in rows:
                if isinstance(i[0], datetime):
                    i = (str(i[0]), i[1])
                rows_new.append(i)
            return rows_new
        return rows
    
    @expose()
    @identity.require(not_anonymous())
    def get_quick_usage(self, loc_id, r_type=None, r_name=None, user_id=None, period=None, g_type=None, format="csv", fname=None):
        if r_type == 'tariff': # special case
            return self.get_tariff_usage(loc_id)
        today = date.today()
        d2dts = lambda d: d.strftime("%a, %d %B %Y")
        if period == "lastweek":
            lastweek = [today - timedelta(i) for i in range(1,8)]
            end, start = d2dts(lastweek[0]), d2dts(lastweek[-1])
            grpby = "hour"
        elif period == "curmonth":
            curmonth = compat.Calendar().monthdatescalendar(today.year, today.month)
            start = d2dts([d for d in curmonth[0] if d.month == today.month][0])
            end = d2dts([d for d in curmonth[-1] if d.month == today.month][-1])
            grpby = "day"
        else:
            start = end = grpby = None
        if format == "csv":
            return self.get_usage_csv(loc_id, r_type, r_name, user_id, start, end, grpby, g_type)
        else:
            return self.get_usage_graph(loc_id, r_type, r_name, user_id, start, end, grpby, g_type)

    @expose("hubspace.templates.plotGraph")
    @identity.require(not_anonymous())
    @validate(validators={'start':dateconverter, 'end':dateconverter})
    def get_usage_graph(self, location_id, r_type=None, r_name=None, user_id=None, start=None, end=None, grpby="week", g_type="pattern", size="small"):
        title, rows = self.get_usage_data(location_id, r_type, r_name, user_id, start, end, grpby, g_type, "epoch")
        data = []
        x_ticks_str = ""
        x_len = 500
        if size == "small":
            y_len = 300
            max_canv_width = 700
        else:
            y_len = 900
            max_canv_width = (2 ** 13 ) # my browser supports (2 ** 15) - 1
        x_label = rows[0][0]
        y_label = rows[0][1]

        if g_type == 'pattern':
            x_ticks = []
            for i, row in enumerate(rows):
                data.append([i, row[1]])
                x_ticks.append([i, str(row[0])])
            x_ticks_str = str(x_ticks)
            x_len = len(x_ticks_str) * 5
            x_len = min(x_len, max_canv_width)
            data_str = str(data[1:])
            options_str = '{ xaxis: { ticks: %s } }' % x_ticks_str
        else:
            data_str = str(rows)
            data_str = re.sub("([0-9]+)L, ", r"\g<1>, ", data_str) # flot's timestamps are in microsecods vs seconds in python
            options_str = '{ xaxis: { mode: "time" } }'

        save_params = dict(owner=identity.current.user.id, title=title, rtype=g_type,
            start=start.strftime("%a, %d %B %Y"), end=end.strftime("%a, %d %B %Y"), grpby=grpby,
            r_name=r_name, r_type=r_type, user_id=user_id)

        template_args = dict (
            title = title,
            data_str = "[%s]" % data_str,
            options_str = options_str,
            x_len = x_len,
            y_len = y_len,
            x_label = x_label,
            y_label = y_label,
            save_params = save_params)
        return template_args

    @expose("hubspace.templates.plotGraph")
    @identity.require(not_anonymous())
    def get_tariff_usage(self, location_id, start=None, end=None):
        #XXX we need to use the location from the selection at the top of the page (not the base_url) - need to pass in the location to the request
        rows = self.get_rusage_entries(location_id, "tariff", None, None,  start, end)
        grouper = lambda row: row.resource_name
        grouped_tariffs = []
        month_helper = reportutils.Month(rows[0].resource)

        for (t_name, grp) in reportutils.sortAndGrpby(rows, grouper):
            grp = list(grp)
            grouper = lambda ru: ru.start
            grouped_tariffs.append( dict (
                label = str(t_name),
                data = [[month_helper.toEpochSecs(ru_start) * 1000, len(list(grp))] for (ru_start, grp) in reportutils.sortAndGrpby(grp, grouper)]) )
        data_str = str(grouped_tariffs)
        data_str = re.sub("([0-9]+)L, ", r"\g<1>, ", data_str) # flot's timestamps are in microsecods vs seconds in python
        options_str = '{ xaxis: { mode: "time", tickSize: [4, "month"] }, legend: {backgroundOpacity: 0.0 }}'
        x_ticks_str = ""
        x_len = 900

        title = "Tariff usage grouped by month (Timeseries)"

        save_params = dict(owner=identity.current.user.id, title=title, rtype="pattern",
                        start=start, end=end, grpby="month", r_name=None, r_type="tariff", user_id=None)

        template_args = dict (
            title = title,
            data_str = data_str,
            options_str = options_str,
            x_len = x_len,
            y_len = 600, # y_len = len(rows) * 50,
            x_label = "Time",
            y_label = "Tariff bookings",
            save_params = save_params)
        return template_args

    def get_usage_data(self, location_id, r_type, r_name, user_id, start, end, grpby, g_type, timeformat):
        if r_type == 'all': r_type = None 
        if r_name == 'all': r_name = None 
        if user_id == 'all': user_id = None 
        if start == 'all': start = None 
        if end == 'all': end = None 
        if start and end:
            time_range = (start, end)
        else:
            time_range = None

        entries = self.get_rusage_entries(location_id, r_type, r_name, user_id, start, end)

        groupers = dict (
            hour = reportutils.Hour,
            day = reportutils.Day,
            week = reportutils.Weekday,
            month = reportutils.Month )

        if entries:
            resource = entries[0].resource
        else:
            if r_name: resource = Resource.get(r_name)[0]
            elif r_type: resource = Resource.selectBy(type=r_type)[0]
        grouper = groupers[grpby](resource)

        if g_type == 'pattern':
            data = grouper.groupAndAverage(entries)
            t_range_labeled = [grouper.getLabel(t) for t in grouper.getRange()]
            data_d = dict(data)
            data = [[t, data_d.get(t, 0)] for t in t_range_labeled]
        else:
            data = grouper.getUsageSums(entries)
            if timeformat == "epoch":
                data = [[int(mktime(i[0].timetuple())) * 1000, i[1]] for i in data]
                start_s = int(mktime(start.timetuple())) * 1000
                end_s = int(mktime(end.timetuple())) * 1000
            else:
                data = [[grouper.dt2strf(i[0]), i[1]] for i in data]
                start_s = grouper.dt2strf(start)
                end_s = grouper.dt2strf(end)
            dates_in_data = [i[0] for i in data]
            if not start_s in data:
                data.insert(0, [start_s, 0])
            if not end_s in data:
                data.insert(len(data) + 1, [end_s, 0])

        data = grouper.addTitlerow(data)

        rname = r_name or r_type
        title = genReportTitle(params=locals())

        return title, data

    ################## Public Pages ##################
    ################## TO BE REMOVED #################

    @expose(template="hubspace.templates.publicEvent")
    @validate(validators={'rusage_id':v.Int()})
    def events(self, rusage_id, tg_errors=None, **kwargs):
        if 'forward_url' in kwargs:
            #we are trying to login so redirect to root of the site
            redirect(cherrypy.request.base)
        loc = get_location_from_base_url()
        event_args = self.login_args()
        event_args['updates'] = get_updates_data(loc)
        rusage = RUsage.get(rusage_id)
        if not rusage.public_field:
            redirect(cherrypy.request.base)
        event_args['rusage'] = rusage
        return event_args

    @expose(template="hubspace.templates.publicProfile")
    @validate(validators={'username':v.UnicodeString()})
    def profiles(self, username, tg_errors=None, **kwargs):
        if 'forward_url' in kwargs:
            #we are trying to login so redirect to root of the site
            redirect(cherrypy.request.base)
        user = User.by_user_name(username)
        if not user.public_field:
            redirect(cherrypy.request.base)
        loc = get_location_from_base_url()
        profile_args = self.login_args()
        profile_args['updates'] = get_updates_data(loc)
        profile_args['user'] = user
        
        return profile_args
    
    ##################  Location  ####################

    @expose()
    @identity.require(identity.has_permission('superuser'))
    @validate(validators={'name':no_ws_ne_cp, 'currency':All(v.UnicodeString(), v.MaxLength(3)), 'with_groups':BoolInt(if_empty=1)})
    def create_region(self, name, currency='GBP', with_groups=True):
        region = self.create_location(name, currency, with_groups, is_region=1)
        return "region created"

    @expose()
    @identity.require(identity.has_permission('superuser'))
    @validate(validators={'region_id':real_int, 'hub_id':real_int})
    def add_location_to_region(self, region_id, hub_id):
        region = Location.get(region_id)
        if not region.is_region:
            return region.name + "is not a region"
        hub = Location.get(hub_id)
        hub.in_region = region
        return "Hub " + hub.name + "has been added to " + region.name


    @expose()
    @identity.require(identity.has_permission('superuser'))
    def correct_group_names(self):
        for group in Group.select():
            if group.place:
                group.group_name = group.place.name + '_' + group.level
        return "done"

    @expose()
    @identity.require(identity.has_permission('superuser'))
    @validate(validators={'name':no_ws_ne_cp, 'currency':All(v.UnicodeString(), v.MaxLength(3)), 'with_groups':BoolInt(if_empty=1)})
    def create_location(self, name, currency='GBP', with_groups=True, is_region=0):
        """Creates a location and all the necessary groups with standard permissions
        """
        location = Location(name=name, currency=currency, city="", is_region=is_region)
        self.create_tariff(active=1, place=location.id, name="Guest Membership "+ name, description="", tariff_cost=0, default=True)

        #create a dummy resource called calendar which will be used for access_policies to arbitrate access to the calendar
        
        cal = create_object('Resource', type='calendar', time_based=1, active=0, place=location.id, name='calendar', description='calendar', )
        location.calendar = cal

        if with_groups:
            for level in ['member', 'host', 'director']:
                group = new_group(place=location.id, level=level, display_name=location.name+" "+level, group_name=location.name.lower() + "_" + level)
                access_policy = add_accessPolicy2Proxy(cal, group.id, 'Group', 5, None, None)
                create_default_open_times(access_policy)
	        locations = location.select() 
        if locations.count() == 1:
            super_users = User.select(AND(Group.q.group_name == 'superuser',
                                          UserGroup.q.groupID == Group.q.id,
                                          User.q.id == UserGroup.q.userID
                                          ))
            for user in super_users:
                user.homeplace = locations[0]

        homeless_users = [u for u in model.User.select() if not u.homeplace]
        home_for_homeless = model.Location.select()[0]
        for u in homeless_users:
            u.homeplace = home_for_homeless

        return ''

    def print_exception(self, tg_exceptions=None):
        hub.rollback()
        return str(tg_exceptions)


    @expose()
    @exception_handler(print_exception, "isinstance(tg_exceptions, LocationHasUsers)")
    @exception_handler(print_exception, "isinstance(tg_exceptions, NoSuchObject)")
    @identity.require(identity.has_permission('superuser'))
    @validate(validators={'name':v.UnicodeString()})
    def delete_location(self, name):
        message = ""
        try:
            location = Location.byName(name)
        except:
            
            raise NoSuchObject("No such location as " + name)
        
        for group in location.groups:
            self.delete_group(group.group_name)
       
        if len(location.homemembers)>0:
            raise LocationHasUsers("Could not delete location " + location.name + ". Location is the homeplace of 1 or more users")
        for resource in location.resources:
            res_message = self.delete_resource(resource.name)
            if res_message == "":
                raise LocationHasRUsages("Could not delete location "+ location.name + ". "+ resource.place.name+" has resource usages.")
            else:
                message += res_message

        location.destroySelf()
        message  += "Location "+ name + " deleted!"
        return message


    @expose()
    @identity.require(identity.has_permission('superuser'))
    def delete_user(self, name, id=None):
        if id:
	    user = User.get(id)
        else:
            user = User.selectBy(user_name=name)
            if user.count()==1:
                user=user[0]
            else:
                raise NoSuchObject("There is no user with the username " + name)
        #for group in user.groups:
            #group.removeUser(user)
        user_group_memberships = UserGroup.select(AND(UserGroup.q.userID==user.id))
        for entry in user_group_memberships:
            entry.destroySelf()
        for invoice in user.invoices:
            invoice.destroySelf()
            
        for booked_by in user.booked_by:
            booked_by.destroySelf()
        for rusage in user.rusages:
            rusage.destroySelf()

        for other_user in user.billed_for:
            other_user.billto = other_user.id

        for alias in user.aliases:
            alias.destroySelf()
        for note_on in user.notes_on:
            note_on.destroySelf()
        for note_by in user.notes_by:
            note_by.destroySelf()
        for metadata in user.metadata:
            metadata.destroySelf()
        for selection in user.selections:
            selection.destroySelf()
        user.destroySelf()
        return "user '"+name+"' deleted"
            

    @expose(template="hubspace.templates.locationProfile")
    @identity.require(not_anonymous())
    @validate(validators=EditLocationSchema)
    def save_locationProfileEdit(self, id, tg_errors=None, **kwargs):
        if tg_errors:
            location = AttrDict(id=id, **kwargs)
            cherrypy.response.headers['X-JSON'] = 'error'
            return self.error_template('locationProfileEdit', {'object':location, 'tg_errors':tg_errors})

        location = Location.get(id)
        if 'name' in kwargs:
            #mv locale paths appropriately
            for locale_path in glob('locales/*_'+location.name.lower().replace(' ', '')):
                os.rename(locale_path, os.path.join(os.path.dirname(locale_path), os.path.basename(locale_path).split('_')[0] + '_' + kwargs['name'].lower().replace(' ', '')))
        
        if not identity.has_permission("superuser"):
            del kwargs['vat_included']
            del kwargs['rfid_enabled']
            del kwargs['microsite_active']
            del kwargs['url']
        for kwarg in kwargs:
            modify_attribute(location, kwarg, kwargs[kwarg])
        cherrypy.response.headers['X-JSON'] = 'success'
        return {'object':location}


    #=====================data fix scripts =====================================

    @expose()
    @identity.require(identity.has_permission('superuser'))
    def fulltext_index_users(self):
        return fulltext_index_users()

    #@expose()
    @identity.require(identity.has_permission('superuser'))
    def reset_passwords(self):
        for user in User.select():
            user.password = user.password
        return ''


    #@expose()
    @identity.require(identity.has_permission('superuser'))
    def upgrade_data(self):
        for group in Group.select():
            if group.level == 'member':
                for user in User.select():
                    if user.homeplace.id != group.place.id: 
                        if user in group.users:
                            group.removeUser(user)

        for user in User.select():
            for attr in ['mobile', 'work', 'fax', 'home']:
                attrib = getattr(user, attr)
                if not attrib:
                    continue
                if attrib.startswith('00'):
                    attrib = '+'+attrib[2:]
                attrib = ")".join("(".join(attrib.split('.', 1)).split('.',1))
                modify_attribute(user, attr, attrib)
                    
        for pricing in Pricing.select():
            pricing.periodends 
        for rusage in RUsage.select():
            rusage.tariff = rusage.resource.place.defaulttariff.id
            calculate_cost(rusage)
            
        return ''


    #@expose()
    def unicode_descriptions(self):
        rusages = RUsage.select()
        for ruse in rusages:
            try:
                ruse.new_resource_description = v.UnicodeString.to_python(ruse.resource_description)
            except:
                new = ""
                for ch in ruse.resource_description:
                    try:
                        new += v.UnicodeString.to_python(ch)
                    except:
                        pass
                ruse.new_resource_description = new
            ruse.resource_description = ""
        return ''

    #@expose()
    def after_change_unicode_descriptions(self):
        rusages = RUsage.select()
        for ruse in rusages:
            ruse.resource_description = ruse.new_resource_description
        return ''

    #@expose()
    @identity.require(identity.has_permission('superuser'))
    def remove_all_print_jobs_from_16_march(self):
        date = print_dtc.to_python("3/16/2007 12:44:15")
        for res_type in ['A4Colour', 'A4BW', 'A3Colour', 'A3BW']:
            resource = get_resource_id_by_name(res_type, 1)
            for rusage in RUsage.select(AND(RUsage.q.resourceID == int(resource),
                                            RUsage.q.start>date)):
                rusage.destroySelf()
        return ''
            

    @expose()
    @identity.require(identity.has_permission('superuser'))
    def user_from_id(self, id):
         return User.get(id).user_name

    #@expose()
    @identity.require(identity.has_permission('superuser'))
    def zero_ids_to_none(self):
        users = []
        for user in User.select():
            try:
                user.signedby
            except:
                user.signedby = None
                users.append(user.display_name)
            try:
                user.hostcontact
            except:
                user.hostcontact = None
                users.append(user.display_name)
	return `users`


    @expose()
    @identity.require(identity.has_permission('superuser'))
    def remove_identical_print_jobs(self):
        for size, printer_size in printer_resources(1).items():
            for quality, resource_id in printer_size.items():
                rusages =  RUsage.select(AND(RUsage.q.resourceID==resource_id,
                                         CONTAINSSTRING(RUsage.q.resource_description, 'identical_entry')))
                for rusage in rusages:
                    print `rusage.start`
                    if rusage.start > datetime(2008,1,1):
                        print 'destroy'
                        rusage.destroySelf()
        return 'success'
                

    ####################Space Booking#####################


    @expose(template="hubspace.templates.booking")
    @strongly_expire
    @identity.require(not_anonymous())
    @validate(validators={'location':real_int, 'date':Any(dateconverter, DateRange), 'res_group':real_int, 'view':v.Int(if_empty=0), 'rooms_displayed':ForEach(v.Int()), 'room_selected':v.Int(), 'only_my_bookings':v.Int(if_empty=0), 'switch':v.UnicodeString()})
    def load_make_booking(self, location=None, date=None, res_group=None, view=0, rooms_displayed=None, room_selected=None, only_my_bookings=0, switch=None, tg_errors=None, **kwargs):
        """reload the booking area
        """
        if not rooms_displayed:
            rooms_displayed = []
        loc = Location.get(location)
	if isinstance(date, tuple):
            today = datetime.today()
            if view==0 and date[0] <= today and today <= date[1]:
                date = today
            else:
                date = date[0]
        try:
            res_group = Resourcegroup.get(res_group)
            if res_group not in loc.resourcegroups:
                res_group = None
        except:
            res_group = None

        if switch == "location":
            rooms_displayed, room_selected, res_group = default_booking_params(loc)
        elif switch == "res_group":
            rooms_displayed, room_selected, res_group = default_booking_params(loc, res_group)

        return {'location':loc, 'date':date, 'res_group':res_group, 'view':view, 'rooms_displayed':rooms_displayed, 'room_selected':room_selected, 'only_my_bookings':only_my_bookings}


    @expose()
    @identity.require(not_anonymous())
    @validate(validators=CreateBookingSchema())
    def add_booking(self, tg_errors=None, **kwargs):
        """add a booking through the web with the special time/date input format
        """        
        resource = Resource.get(kwargs['resource_id'])
        date = kwargs['date']
        start = kwargs['start']
        if kwargs.get('customcost') == '':
            kwargs['customcost'] = None


        if resource.time_based:
            end = kwargs['end']
        else:
            end = start
        if not end:
            raise "no end time for resource booking"

        kwargs['start_datetime'] = datetime.combine(dateconverter.to_python(date), time(int(start['hour']), int(start['minute']))) 
        kwargs['end_datetime'] = datetime.combine(dateconverter.to_python(date), time(int(end['hour']), int(end['minute'])))

        if tg_errors:
            rusage = AttrDict(**kwargs)
            rusage.time_based = resource.time_based
            rusage.start = kwargs['start_datetime']
            rusage.end_time = kwargs['end_datetime']
            rusage.public_field = 'public_field' in kwargs and kwargs['public_field'] or 0
            rusage.confirmed = 1
            if 'user' in kwargs:
                rusage.user = User.get(kwargs['user'])
            cherrypy.response.headers['X-JSON'] = 'error'
            if "customcost" in tg_errors:
                rusage.customcost = kwargs.get('customcost', '')
                tg_errors['customcost'] = tg_errors['customcost'] + _(" (Hint: You should not include currency signs)")
            if 'pagetype' in kwargs and kwargs['pagetype']=='billing':
                return self.error_template('addRusage', {'object':rusage, 'user':kwargs['pageuser'], 'tg_errors':tg_errors})
            else:
                return self.error_template('addBooking', {'object':rusage, 'resource':resource, 'tg_errors':tg_errors})        

        del kwargs['end']
        del kwargs['start']
        if kwargs['public_field']==1:
            clear_cache('events', resource.place)

        if resource.place.tentative_booking_enabled:
            kwargs['confirmed'] = int(not kwargs.get('tentative', 0))
        else:
            kwargs['confirmed'] = 1
        del kwargs['tentative']

        return  self.book_resource(**kwargs)


    
    @expose()
    @identity.require(not_anonymous())
    @validate(validators=CreateUsageByNameSchema())
    def book_resource_by_name(self, resource_name, location, tg_errors=None, **kwargs):
        """get a resource by the active one of its name. used for getting the id of automated resources such as 'A4Colour Print' To customise the resource description on the rusage, pass in kwarg: 'resource_description=foo'.

        e.g. http://localhost:8080/book_resource_by_name/london_custom/1?start_datetime=23%20February%202007%2011%3A30%3A00&quantity=10&user=1

        """
        if tg_errors:
            for e in tg_errors:
                raise e, `tg_errors`
        kwargs['resource_id'] = int(get_resource_id_by_name(resource_name, location=location))
        if kwargs['resource_id']==-1:
            return "name_error"
        if not Resource.get(kwargs['resource_id']).time_based:
            self.book_resource(**kwargs)
            return "success"
        else:
            return "resource_is_time_based"
        
        

    @expose()
    @identity.require(not_anonymous())
    @validate(validators=CreateUsageSchema())
    def book_resource(self,tg_errors=None, **kwargs):
        """book a resource using the standard datetime format
        """
        resource = Resource.get(kwargs['resource_id'])     
        if 'user' not in kwargs or not kwargs['user']:
            kwargs['user'] = identity.current.user.id
        
        if  kwargs['user']!=identity.current.user.id and not (permission_or_owner(resource.place, None, "manage_resources") or permission_or_owner(None, None, "webapi")):
            raise IdentityFailure('what about not hacking the system')

 
        if not kwargs['start_datetime'] and not resource.time_based:
            start_datetime = now(resource.place)
        else:       
            start_datetime = kwargs['start_datetime']
        if ('end_datetime' not in kwargs or not kwargs['end_datetime']) and not resource.time_based:
            end_datetime = start_datetime
        else:
            end_datetime = kwargs['end_datetime']
       	     
        if 'quantity' not in kwargs and not resource.time_based:
            kwargs['quantity'] = 1
            

        kwargs['temp_id'] = kwargs['resource_id']
        del kwargs['resource_id']
        if tg_errors:
            rusage = AttrDict(**kwargs)
            rusage.time_based = resource.time_based
            rusage.start = start_datetime
            rusage.end_time = end_datetime
            rusage.user = User.get(kwargs['user'])
            rusage.customcost = kwargs.get('customcost', "")
            cherrypy.response.headers['X-JSON'] = 'error'
            if 'pagetype' in kwargs and kwargs['pagetype']=='billing':
                return self.error_template('addRusage', {'object':rusage, 'pageuser':kwargs['user'], 'tg_errors':tg_errors})
            else:
                return self.error_template('addBooking', {'object':rusage, 'resource':resource, 'tg_errors':tg_errors})
    
        try:
            new_rusage = make_booking(resource=resource.id, start=start_datetime, end_time=end_datetime, rusage=None, **kwargs)
        except NoTariffForUser, e:
            cherrypy.response.headers['X-JSON'] = 'error'
            return '<div class="errorMessage">'+ str(e)+ '</div>'
        if 'customcost' in kwargs and kwargs['customcost']:
            new_rusage.customcost = kwargs['customcost']
        cherrypy.response.headers['X-JSON'] = 'success'
        if 'pagetype' in kwargs and kwargs['pagetype']=='billing':
            return try_render({'user':User.get(kwargs['pageuser']), 'invoice':None}, template='hubspace.templates.invoicesnippet', format='xhtml', headers={'content-type':'text/html'}, fragment=True)
        else:
            return try_render({'rusage':new_rusage}, template='hubspace.templates.meetingBooking', format='xhtml', headers={'content-type':'text/html'}, fragment=True)

    
    
    @expose()
    @identity.require(not_anonymous())
    @validate(validators=EditBookingSchema())
    def save_meetingBookingEdit(self, tg_errors=None, **kwargs):
        """validators could look ahead and check if the tariff can actually be changed here
        If rusage is already invoiced, it has to be cancelled as we should not change an rusage which is invoiced.
        If it is not invoiced, better modify the same rusage instance and recaculate cost.
        """
        date = kwargs['date']
        start = kwargs['start']
        end = kwargs['end']
        rusage = model.RUsage.get(kwargs['id'])
        resource = Resource.get(kwargs['resource_id'])

        if not permission_or_owner(resource.place,rusage,'manage_rusages') and can_delete_rusage(rusage):
            raise IdentityFailure('what about not hacking the system')


        kwargs['start'] = datetime.combine(dateconverter.to_python(date), time(int(start['hour']), int(start['minute'])))
        kwargs['end_time'] = datetime.combine(dateconverter.to_python(date), time(int(end['hour']), int(end['minute'])))
        kwargs['rusage'] = rusage
        kwargs['resource'] = resource
        kwargs['user'] = kwargs.get('user', None) and model.User.get(int(kwargs['user'])) or identity.current.user
        if tg_errors and tg_errors.get('customcost'):
            tg_errors['customcost'] = tg_errors['customcost'] + _(" (Hint: You should not include currency signs)")
        else:
            kwargs['customcost'] = kwargs.get('customcost', None)
        if resource.place.tentative_booking_enabled:
            kwargs['confirmed'] = int(not kwargs.get('tentative', 0))
        else:
            kwargs['confirmed'] = 1

        kwargs['public_field'] = kwargs.get('public_field', 0) and 1
        if 'tentative' in kwargs:
            del kwargs['tentative']

        if tg_errors:
            cherrypy.response.headers['X-JSON'] = 'error'
            return self.error_template('meetingBookingEdit', {'object':hubspace.utilities.dicts.AttrDict(kwargs), 'resource':resource, 'tg_errors':tg_errors})

        old_values = hubspace.utilities.dicts.ObjDict(rusage)
        keys_just_cant_change = ('id',)
        keys_can_change_if_same_type = ('resource', 'meeting_name', 'description', 'public_field', 'meeting_name', 'meeting_description', \
            'number_of_people', 'notes')
        keys_cant_change_if_invoiced = model.RUsage.keys_cant_change_if_invoiced
        keys_affect_cost = ('start', 'end_time', 'tariff', 'customcost', 'resource', 'quantity')

        change = dict([(k,v) for (k, v) in kwargs.items() if k in old_values and v != old_values[k] and k not in keys_just_cant_change])
        #if 'customcost' in change and float(rusage.customcost) == change['customcost']:
        #    del change['customcost'] # this was part of commit for #480 but is responsible for #511. I don't think we
        #    need this check anyways. Commenting out for now.

        old_options = [ru.resource.id for ru in rusage.suggested_usages]
        new_options = kwargs.get('options', [])

        options_changed = sorted(old_options) != sorted(kwargs.get('options', []))
        if options_changed:
            options_to_cancel = [option for option in old_options if option not in new_options]
            options_to_add = [option for option in new_options if option not in old_options]
            applogger.debug("options to cancel/delete: %s" % str(options_to_cancel))
            applogger.debug("options to add: %s" % str(options_to_add))

            for option in options_to_cancel:
                ousage = [ru for ru in rusage.suggested_usages if ru.resource.id == option][0]
                if rusage.invoiced:
                    applogger.debug("cancelling: %s" % ousage.id)
                    self.cancel_rusage(ousage.id)
                else:
                    applogger.debug("deleting: %s" % ousage.id)
                    self.delete_rusage(ousage.id)

            for option in options_to_add:
                applogger.debug("adding: %s" % option)
                book_suggested_resources(options_to_add, rusage, kwargs.get('user', rusage.user.user_name), kwargs['start'], kwargs['end_time'])

        if rusage.resource.type != resource.type:
            for k in keys_can_change_if_same_type:
                if k in change: del change[k]

        cancellation_needed = rusage.invoiced and set(change.keys()).intersection(keys_cant_change_if_invoiced)
        cost_recalculation_needed = set(change.keys()).intersection(keys_affect_cost)

        if not cancellation_needed:
            for (k, v) in change.items():
                setattr(rusage, k, v)
            if cost_recalculation_needed:
                new_cost = calculate_cost(rusage) # recalculate the cost
                if not new_cost == rusage.cost:
                    rusage.cost = new_cost
                    if rusage.invoice:
                        self.update_invoice_amount(rusage.invoice.id)
        else:
            # old rusage is cancelled and new instace created for refund purpose
            # refund will be reflected in the next invoice
            rusage_id = self.cancel_rusage(rusage.id)
            kwargs['resource'] = kwargs['resource_id']
            rusage = create_rusage(**kwargs)


        cherrypy.response.headers['X-JSON'] = 'success'
        return {'render':try_render({'rusage':rusage}, template="hubspace.templates.viewBooking", format='xhtml', headers={'content-type':'text/html'}, fragment=True), 'rusage_id':rusage.id}

   
    @expose(template="hubspace.templates.addBooking")
    @strongly_expire
    @identity.require(not_anonymous())
    @validate(validators=StartBookingSchema)
    def start_booking(self, resource_id=None, start_datetime=None, end_datetime=None, tg_errors=None, **kwargs):
        for k in ('start', 'end', 'date', 'customcost'):
            if k in kwargs: del kwargs[k]
        if 'user' in kwargs:
            kwargs['user'] = model.User.get(int(kwargs['user']))
        resource = Resource.get(resource_id)
        location = resource.place
        userid = identity.current.user.id
        tariff = get_tariff(location.id, userid, start_datetime)
        start_datetime = datetimeconverter.to_python(start_datetime)
        end_datetime = datetimeconverter.to_python(end_datetime)
        if end_datetime < start_datetime:
            end_datetime = start_datetime
        rusage_d = {'start':start_datetime,
                           'end_time':end_datetime,
                           'number_of_people':1,
                           'meeting_name':"",
                           'meeting_description':"",
                           'notes':"",
                           'customcost':None,
                           'cost':None,
                           'confirmed': 1,
                           'public_field':0}
        if tg_errors:
            rusage_d.update(kwargs)
            return {'object':AttrDict(rusage_d), 'resource':resource, 'tg_errors':tg_errors}
        
        if not tariff:
            message = "You do not have a tariff for the Hub in " + location.name + " for the month of " + dateconverter.from_python(start_datetime)[3:-5] + ". Please arrange to book one before booking resources."
            return {'message':message}
                
        return {'object':AttrDict(rusage_d), 'resource':resource}
        message = "<p>The resource " + escape(Resource.get(resourceid).name) + " in " + escape(location.name) + " can not be booked at "+ escape(datetimeconverter.from_python(datetime)) + " because it requires:</p><ul>"
        message = "<p>The resource " + escape(Resource.get(resourceid).name) + " in " + escape(location.name) + " can not be booked at "+ escape(datetimeconverter.from_python(datetime)) + " because it requires:</p><ul>"


    @expose(template="hubspace.templates.meetingBookingEdit")
    @strongly_expire
    @identity.require(not_anonymous())
    @validate(validators=EditBookingSchema())
    def edit_booking(self, tg_errors=None, **kwargs):
        resource = Resource.get(kwargs['resource_id'])
        location = resource.place
        userid = identity.current.user.id
        tariff = get_tariff(location.id, userid, datetime)
        start = datetime.combine(dateconverter.to_python(kwargs['date']), time(int(kwargs['start']['hour']), int(kwargs['start']['minute'])))
        end = datetime.combine(dateconverter.to_python(kwargs['date']), time(int(kwargs['end']['hour']), int(kwargs['end']['minute'])))

        rusage = AttrDict(**kwargs)
        rusage.public_field = kwargs.get('public_field', 0)
        rusage.meeting_name = kwargs.get('meeting_name', "")
        rusage.meeting_description = kwargs.get('meeting_description', "")
        rusage.number_of_people = kwargs.get('number_of_people', 1)
        rusage.start = start
        rusage.end_time = end
        if kwargs['user'] == None:
            rusage.user = model.RUsage.get(int(kwargs['id'])).user.id
        else:
            rusage.user = User.get(kwargs['user'])
        if resource.place.tentative_booking_enabled:
            kwargs['confirmed'] = int(not kwargs.get('tentative', 0))
        else:
            kwargs['confirmed'] = 1

        rusage.customcost = kwargs.get('customcost', None) and Money.to_python(str(kwargs['customcost'])) or None
        rusage.notes = kwargs['notes']

        if tg_errors:
            cherrypy.response.headers['X-JSON'] = 'error'
            return self.error_template('meetingBookingEdit', {'object':rusage, 'resource':resource, 'tg_errors':tg_errors})

        
        if not tariff:
            message = "You do not have a tariff for the Hub in " + location.name + " for the month of " + dateconverter.from_python(datetime)[3:-5] + ". Please arrange to book one before booking resources."
            return {'message':message}

        return {'object':rusage, 'resource':resource}
    

    #########tariffs
    @validate(validators={'userid':real_int, 'tariffid':real_int, 'month':real_int, 'year':real_int})
    def book_tariff(self, userid=None, tariffid=None, year=None, month=None, recalculate=True, tg_errors=None, **kwargs):
        "book a tariff for a user in a given year's month"

        if tariffid==0:
            return ""
        
        tariff = Resource.get(tariffid)       
        user = User.get(userid)
        
        if not permission_or_owner(tariff.place,None,'manage_users'):
            raise IdentityFailure('what about not hacking the system')
            
        if tg_errors:
            for tg_error in tg_errors:
                raise str(tg_errors[tg_error])

        return book_tariff(user, tariff, year, month, recalculate)


    @expose(template="hubspace.templates.tariffHistory")
    @identity.require(not_anonymous())
    @validate(validators={'id':real_int, 'location':real_int})
    def save_tariffHistoryEdit(self, tg_errors=None, **kwargs):
        """validators could look ahead and check if the tariff can actually be changed here
           Once there are rusages connected to a tariff booking, this function only allows
           changing to another tariff, but not removing the booking completely.
        """
        user = User.get(kwargs['id'])
        location = Location.get(kwargs['location'])

        #for calculating changes in access policies
        original_current_tariff = get_tariff(location.id, user.id, now(location.id))
        
        if tg_errors:
            cherrypy.response.headers['X-JSON'] = 'error'
            return self.error_template('tariffHistoryEdit', {'object':user, 'location':kwargs['location'], 'tg_errors':tg_errors})

        if not permission_or_owner(Location.get(kwargs['location']), None, 'manage_users'):
            raise IdentityFailure('what about not hacking the system')

        tariffs = kwargs['tariff']
        already_invoiced = []
        for year in tariffs:
            for month in tariffs[year]:
                tariffid=int(tariffs[year][month])
                start = datetime(int(year),int(month),1, 0,0,1)
                lastday = calendar.monthrange(int(year),int(month))[1]
                end=datetime(int(year),int(month),lastday,0,0,0)+timedelta(days=1)

                #we could optimise by doing this once for a year getting all tariff bookings
                # then sorting and iterating
                current_tariff_booking = RUsage.select(AND(RUsage.q.resourceID == Resource.q.id,
                                                           Resource.q.type=='tariff', 
                                                           RUsage.q.userID==user.id,
                                                           Resource.q.placeID==location.id,
                                                           RUsage.q.start == start,
                                                           RUsage.q.end_time == end))
                # TODO ^ why not sort on some column and specify a limit (slice)

                if current_tariff_booking.count()==0:
                    current_tariff_booking = None
                else:
                    current_tariff_booking = current_tariff_booking[0]

                #did we move back to the guest tariff - if so destroy old booking and recalculate costs
                if current_tariff_booking and not tariffid:
                    self.delete_rusage(current_tariff_booking.id)
                    invoiced_usages = tariff_booking_changed_recalculate(user, location.defaulttariff, \
                        current_tariff_booking.start, current_tariff_booking.end_time, True)
                    already_invoiced += invoiced_usages
                                      
                #Do we have a change in tariffs or move onto a tariff? if so book the new tariff (recalculate any related bookings)
                if tariffid and (current_tariff_booking==None or current_tariff_booking.tariff.id != tariffid):
                    if current_tariff_booking:
                        self.delete_rusage(current_tariff_booking.id)
                    tariff_booking = self.book_tariff(userid=user.id, tariffid=tariffid, year=int(year), month=int(month), recalculate=False)
                    invoiced_usages = tariff_booking_changed_recalculate(user, tariff_booking.resource, tariff_booking.start, tariff_booking.end_time, True)
                    already_invoiced += invoiced_usages

        final_current_tariff = get_tariff(location.id, user.id, now(location.id))
        if original_current_tariff != final_current_tariff:
            if final_current_tariff:
                user_acquires_policyProxy(user, final_current_tariff)
            if original_current_tariff:
                user_loses_policyProxy(user, original_current_tariff)

        cherrypy.response.headers['X-JSON'] = 'success'
        return {'user':user, 'location':Location.get(kwargs['location']), 'already_invoiced':already_invoiced}
        

    ###########tabs an forms#################

    @expose()
    @strongly_expire
    @identity.require(not_anonymous())
    def load_tab(self, object_type="User", object_id=1, section='profile', **kwargs):
        theclass = getattr(hubspace.model, object_type)
        obj = theclass.get(object_id)
        return try_render({'object':obj, 'ajax':'1', 'tg_css':[], 'tg_js_head':[], 'tg_js_bodytop':[], 'tg_js_bodybottom':[]}, template='hubspace.templates.' + str(section), format='xhtml', headers={'content-type':'text/html'}, fragment=True)
        
  
    @expose(template="hubspace.templates.memberCommunitiesEdit")
    @identity.require(not_anonymous())
    def error_memberCommunitiesEdit(self, id, tg_errors=None, **kwargs):
        return dict
    
    @expose(template="hubspace.templates.memberCommunities")
    @identity.require(not_anonymous())
    def save_memberCommunitiesEdit(self, id, tg_errors=None, **kwargs):
        if tg_errors:
            object = AttrDict(id=id, **kwargs)
            cherrypy.response.headers['X-JSON'] = 'error'
            return self.error_memberDescriptionEdit({'object':object, 'tg_errors':tg_errors})

        user = User.get(id)
        if not permission_or_owner(user.homeplace,user,'manage_users'):
            raise IdentityFailure('what about not hacking the system')

        current_cops = user.cops
        for cop in current_cops:
            index = current_cops.index(cop)
            if cop[0] in kwargs:
                current_cops[index] = (cop[0], 1)
            else:
                current_cops[index] = (cop[0], 0)
        user.cops = current_cops
        cherrypy.response.headers['X-JSON'] = 'success'
        return {'object':user}

    @expose(template="hubspace.templates.memberDescriptionEdit")
    @identity.require(not_anonymous())
    def error_memberDescriptionEdit(self, id, tg_errors=None, **kwargs):
        return dict
    
    @expose(template="hubspace.templates.memberDescription")
    @identity.require(not_anonymous())
    @validate(validators={'description':v.UnicodeString()})
    def save_memberDescriptionEdit(self, id, tg_errors=None, **kwargs):
        
        if tg_errors:
            object = AttrDict(id=id, **kwargs)
            cherrypy.response.headers['X-JSON'] = 'error'
            return self.error_memberDescriptionEdit({'object':object, 'tg_errors':tg_errors})

 
        user = User.get(id)
        if not permission_or_owner(user.homeplace,user,'manage_users'):
            raise IdentityFailure('what about not hacking the system')

        kwargs['modified'] = now(user.homeplace)    
        modify_attribute(user, 'description', kwargs['description'])
        modify_attribute(user, 'modified', datetime.now())
        if user.public_field == 1:
            location = user.homeplace
            clear_cache('profiles', location)
    
        hubspace.search.update(user)
        cherrypy.response.headers['X-JSON'] = 'success'
        return {'object':user}


            
    @expose(template="hubspace.templates.memberProfileEdit")
    @identity.require(not_anonymous())
    def error_memberProfileEdit(self, dict):
        return dict
 

    @expose()
    @identity.require(not_anonymous())
    @validate(validators={'q':v.UnicodeString()})
    def complete_biz_type(self, q="", **kwargs):
        biz_type = q.strip()
        biz_typ = u" ".join([word+u"*" for word in biz_type.split(u" ")])
        biz_typ = 'biz_type:'+biz_typ
        results = hubspace.search.do_search(biz_typ)
        
        suggestions = [res['biz_type'] for res in results]
        return '\n'.join(suggestions)


    @expose()
    @identity.require(not_anonymous())
    def usage_stats(self):
        users = User.select()
        all_users = user_stats(users)
        active = User.select(AND(User.q.active==1))
        active_users = user_stats(active)
        return "Of all users: " + `all_users` + '\n\nOf active users' + `active_users`
 

    @expose(template="hubspace.templates.memberProfile")
    @identity.require(not_anonymous())
    @validate(validators=ProfileSchema())
    def save_memberProfileEdit(self, id=None, tg_errors=None, **kwargs): 
        user = User.get(id)
        if "username" in kwargs: kwargs["username"] = user.username # quick n dirty hack to prevent username
        # modification, if we can handle corresponding ldap uid change then ^ line is not reqd
        if permission_or_owner(user.homeplace, None, 'manage_users') and 'active' not in kwargs:
            kwargs['active'] = 0
        elif not permission_or_owner(user.homeplace, None, 'manage_users'):
            kwargs['active'] = 1

        if tg_errors:
            if 'public_field' not in kwargs:
                kwargs['public_field'] = 0
            obj = User.get(id)
            aliases = []
            if 'aliases' in kwargs:
                for alias in kwargs['aliases']:
                    aliases.append(AttrDict(alias))
            kwargs['aliases'] = aliases
            cherrypy.response.headers['X-JSON'] = 'error'
            return self.error_memberProfileEdit({'object':obj, 'tg_errors':tg_errors})

        if not permission_or_owner(user.homeplace,user,'manage_users'):
            raise IdentityFailure('what about not hacking the system')

        if permission_or_owner(user.homeplace,None,'manage_users') and 'active' not in kwargs:
            kwargs['active'] = 0
        elif not permission_or_owner(user.homeplace,None,'manage_users'):
            kwargs['active'] = 1
        if kwargs['active'] and not user.welcome_sent:
            send_welcome_mail(user, kwargs['password'])

        if 'password' in kwargs and kwargs['password'] in ["", None]:
            del kwargs['password']

        if not kwargs['email_address']:
            kwargs['email_address'] = kwargs['user_name']

        metadata = ['postcode', 'biz_type']
        changed_attrs = []
        for kwarg in kwargs:
            if kwarg in metadata:
                set_freetext_metadata(user, kwarg, unicode(kwargs[kwarg]))
            else:
                changed = modify_attribute(user, kwarg, kwargs[kwarg])
                if changed:
                    changed_attrs.append(kwarg)

        singleselected = []
        for attr_name in singleselected:
            set_singleselected(attr_name, user, kwargs[attr_name])
            del kwargs[attr_name]

        model.hub.commit() # this is rather dangerous
        model.hub.begin()
        hubspace.search.update(user)

        location = user.homeplace # this will have to do changed once its possible to have users with no homeplace
        try:
            home_group = Group.selectBy(level='member', place=location)[0]
        except:
            home_group = None

        if location and ('homeplace' in changed_attrs or 'organisation' in changed_attrs) and user.public_field == 1:
            user.modified = datetime.now()
            clear_cache('profiles', location)

        groups = {}
        if 'groups' in kwargs:
            groups = kwargs['groups']

        for alias_name in kwargs.get('new_alias'):
            if alias_name: create_object('Alias', user = id, alias_name=alias_name)
            
        if 'aliases' in kwargs:
            for alias in kwargs['aliases']:
                if alias['alias_name'] != Alias.get(alias['id']).alias_name:
                    al = Alias.get(alias['id'])
                    al.alias_name = alias['alias_name']
                    if len(al.alias_name)==0:
                        al.destroySelf()
                
        
        locations = user_locations(user, ['member', 'host', 'director'])
        for location_id in groups:
            locations.append(Location.get(location_id))

        for location in locations:
            if str(location.id) not in groups: 
                groups[str(location.id)] = {}
   
        for location in locations:
            for role in roles_grantable(location):
                group = Group.selectBy(level=role, place=location)[0]
                if role in groups[str(location.id)]:
                    self.addUser2Group(user, group)
                elif role not in groups[str(location.id)] and group in user.groups:
                    user_group = UserGroup.select(AND(UserGroup.q.userID==user.id,
                                                      UserGroup.q.groupID==group.id))
                    for membership in user_group:
                        membership.destroySelf()

        if home_group and 'homeplace' in changed_attrs:        
            self.addUser2Group(user, home_group)
                  
        cherrypy.response.headers['X-JSON'] = 'success'
        return {'object':user} 


    def error_template(self, widget_name, dict):
        return try_render(dict, template='hubspace.templates.'+str(widget_name), format='xhtml', headers={'content-type':'text/html'}, fragment=True)   


    @expose(template="hubspace.templates.relationshipStatus")
    @identity.require(not_anonymous())
    @validate(validators={'id':real_int, 'signedby':IntOrNone(), 'hostcontact':IntOrNone(), 'introduced':v.UnicodeString()})
    def save_relationshipStatusEdit(self, id, tg_errors=None, **kwargs):
        if tg_errors:
            obj = AttrDict(id=id, **kwargs)
            cherrypy.response.headers['X-JSON'] = 'error'
            return self.error_template('relationshipStatusEdit', {'object':obj, 'tg_errors':tg_errors})

        user = User.get(id)
        
        metadata = ['introduced_by']
        for kwarg in kwargs:
            if kwarg in metadata:
                set_freetext_metadata(user, kwarg, unicode(kwargs[kwarg]))
            else:
                modify_attribute(user, kwarg, kwargs[kwarg])

        if not permission_or_owner(user.homeplace, None, 'manage_users'):
            raise IdentityFailure('what about not hacking the system')
        for kwarg in kwargs:
            modify_attribute(user, kwarg, kwargs[kwarg])
            
        cherrypy.response.headers['X-JSON'] = 'success'
        return {'object':user}

        
    @expose(template="hubspace.templates.memberServices")
    @identity.require(not_anonymous())
    @validate(validators=MemberServiceSchema())
    def save_memberServicesEdit(self, id, tg_errors=None, **kwargs):
        
        if tg_errors:
            obj = AttrDict(id=id, **kwargs)
            cherrypy.response.headers['X-JSON'] = 'error'
            return self.error_template('memberServicesEdit', {'object':obj, 'tg_errors':tg_errors})

        user = User.get(id)
        if not permission_or_owner(user.homeplace, None, 'manage_users'):
            raise IdentityFailure('what about not hacking the system')
        for kwarg in kwargs:
            modify_attribute(user, kwarg, kwargs[kwarg])
            
        cherrypy.response.headers['X-JSON'] = 'success'
        return {'object':user}


    @expose(template="hubspace.templates.bristolData")
    @identity.require(not_anonymous())
    @validate(validators=BristolDataSchema())
    def save_bristolDataEdit(self, id, tg_errors=None, **kwargs):
        user = User.get(id)
        if tg_errors:
            cherrypy.response.headers['X-JSON'] = 'error'
            return self.error_template('bristolDataEdit', {'object':AttrDict(**kwargs), 'tg_errors':tg_errors})

        user.bristol_metadata = kwargs
        cherrypy.response.headers['X-JSON'] = 'success'
        return {'object':AttrDict(user.bristol_metadata), 'user':user}


    @expose(template="hubspace.templates.billingDetails")
    @identity.require(not_anonymous())
    @validate(validators=BillingDetailsSchema())
    def save_billingDetailsEdit(self, id, tg_errors=None, **kwargs):
	user = User.get(id)
	if not permission_or_owner(user.homeplace, user,'manage_invoices'):
		raise IdentityFailure('what about not hacking the system')

        if kwargs['billto'] and not permission_or_owner(user.homeplace, None,'manage_invoices'):
		raise IdentityFailure('what about not hacking the system')
        
        
        if tg_errors:
            obj = AttrDict(id=id, **kwargs)
            attrs =  get_attribute_names(User)
            for attr in attrs:
                if attr not in obj:
                    obj[attr] = getattr(user, attr) 

            cherrypy.response.headers['X-JSON'] = 'error'
            return self.error_template('billingDetailsEdit', {'object':obj, 'tg_errors':tg_errors})


        user = User.get(id)
        for kwarg in kwargs:
            #if kwargs[kwarg] or kwarg in ['billto', 'bill_to_profile']:
                modify_attribute(user, kwarg, kwargs[kwarg])
            
        cherrypy.response.headers['X-JSON'] = 'success'
        return {'object':user}



        

    @expose(template="hubspace.templates.notes")
    @identity.require(not_anonymous())
    @validate(validators=AddAction())
    def add_action(self, tg_errors=None, **kwargs):
        if tg_errors:
            obj = AttrDict(id=id, **kwargs)
            cherrypy.response.headers['X-JSON'] = 'error'
            return self.error_template('notes', {'object':obj, 'tg_errors':tg_errors})

        note = Note.get(kwargs['note'])
        user = note.onuser
        kwargs['subject'] = "Follow-up with " + user.display_name  
        kwargs['createdby'] = identity.current.user.id
        kwargs['opened'] = now(identity.current.user.homeplace)
        kwargs['action'] = 'followup'
        kwargs['action_id'] = user.id
        parent = Todo.select(AND(Todo.q.foruserID==kwargs['foruser'],
                                 Todo.q.parentID==None,
                                 Todo.q.subject=="Follow-ups",
                                 ))
        if parent.count()==0:
            parent = create_object('Todo',
                                   parent=None,
                                   subject="Follow-ups",
                                   foruser=kwargs['foruser'],
                                   createdby=kwargs['createdby'],
                                   opened=kwargs['opened'],
                                   action="followups")
        else:
            parent = parent[0]
        kwargs['parent'] = parent.id
        todo = create_object('Todo', **kwargs)
        note.action = todo.id

        cherrypy.response.headers['X-JSON'] = 'success'
        return {'note':note}

        

    @expose(template="hubspace.templates.notes")
    @identity.require(not_anonymous())
    @validate(validators=EditNoteSchema())
    def save_noteEdit(self, id, tg_errors=None, **kwargs):
        if tg_errors:
            obj = AttrDict(id=id, **kwargs)
            cherrypy.response.headers['X-JSON'] = 'error'
            return self.error_template('noteEdit', {'object':obj, 'tg_errors':tg_errors})

        del kwargs['onuser']
        note = Note.get(id)
        user = User.get(note.onuser.id)
        kwargs['date'] = now(user.homeplace)

        if not permission_or_owner(user.homeplace,None,'manage_notes'):
            raise IdentityFailure('what about not hacking the system')
        
        kwargs['byuser'] = identity.current.user.id
        for kwarg in kwargs:
            modify_attribute(note, kwarg, kwargs[kwarg])

        cherrypy.response.headers['X-JSON'] = 'success'
        return {'note':note}

    @expose(template="hubspace.templates.host")
    @identity.require(not_anonymous())
    @validate(validators=EditTodoSchema())
    def save_todoEdit(self, id, tg_errors=None, **kwargs):

        if tg_errors:
            if 'closed' not in kwargs:
                kwargs['closed'] = 0
            obj = AttrDict(id=id, **kwargs)
            cherrypy.response.headers['X-JSON'] = 'error'
            return self.error_template('todoEdit', {'object':obj, 'action':kwargs['action'], 'tg_errors':tg_errors})
        
        todo = Todo.get(id)

        user = User.get(todo.foruser.id)
        if not permission_or_owner(user.homeplace,None,'manage_todos'):
            raise IdentityFailure('what about not hacking the system')


        if 'closed' in kwargs and kwargs['closed']==1:
            kwargs['closed'] = now(user.homeplace)
        for kwarg in kwargs:
            modify_attribute(todo, kwarg, kwargs[kwarg])

        cherrypy.response.headers['X-JSON'] = 'success'
        return {'todo':todo_to_AttrDict(todo)}


    
    @expose(template="hubspace.templates.mini_details")
    @strongly_expire
    @identity.require(not_anonymous())
    @validate(validators={'id':real_int})
    def mini_user_detail(self, id=1, **kwargs):
        return {'user':User.get(id)}
    
    @expose()
    @strongly_expire
    @validate(validators={'id':v.Int(if_empty=0), 'type':v.UnicodeString(), 'attr':v.UnicodeString()})
    def display_image(self, type, id=0, attr="", **kwargs):
        theclass = getattr(hubspace.model, type)
        if theclass == Location and id==0:
            try:
                obj = get_location_from_base_url()
            except:
                return ""
        else:
            obj = theclass.get(id)

        #the object image is private if it has a public_field and the public_field is False
        #otherwise its public.
        allowed = True
        if hasattr(obj,'public_field'):
            allowed = getattr(obj, 'public_field')
            
        if identity.current.anonymous and not allowed:
            raise IdentityFailure('what about not hacking the system')

        image = getattr(obj, attr)
        try:
            mimetype = getattr(obj, attr +'_mimetype')
        except:
            mimetype = "image/png"
        cherrypy.response.headerMap["Content-Type"] = str(mimetype)
        if isinstance(image, basestring) and isinstance(mimetype, basestring): 
            return image
        return ""

    @identity.require(identity.has_permission('superuser'))
    @expose()
    @validate(validators={'user_name': username})
    def make_superuser(self, user_name=""):
        """to create a new superuser call '/make_superuser?user_name=$username'
        """
        user = User.by_user_name(user_name)
        if not user_name and not user:
            return ""
        make_superuser(user)
        return  user_name + " is now a superuser"

    @expose(template="hubspace.templates.createSuperUser")
    def setup_form(self, name, currency='GBP'):
        self.create_location(name, currency)
        return {}

    @expose()
    def default(self, *args, **kwargs):
        version = new_or_old[cherrypy.request.base]
        if version == 'old':
            default_method = self.default_old
        else:
            default_method = self.default_new
        try:
            return default_method(*args, **kwargs)
        except AttributeError, err:
            print err
            if identity.current.anonymous:
                cherrypy.response.status = 404
                return "404"
            else:
                raise

    ############################TO BE REMOVED LATER#########################################################
    def default_old(self, *args, **kwargs):
        locale = get_locale()
        site_folder_paths = ['hubspace.templates.']

        #if not model.Location.select().count():
        #    return self.setup_form()

        if len(args)>0 and args[0]=='failed':
            cherrypy.response.status=403
            return try_render(self.login_args(*args, **kwargs), template='login', format='xhtml', headers={'content-type':'text/html'}, fragment=False, folder_paths=site_folder_paths)

        if not identity.current.anonymous \
            and identity.was_login_attempted() \
            and not identity.get_identity_errors() \
            and cherrypy.request.path != "/":
            raise redirect(cherrypy.request.base)
        
        if identity.current.anonymous or not identity.current.user.active:
            if cherrypy.request.base in site_folders:
                site_folder_paths.insert(0, site_folders[cherrypy.request.base])

            if len(args)==0 or args[0] in ['home', '']:
                return try_render(self.login_args(*args, **kwargs), template='login', format='xhtml',  headers={'content-type':'text/html'}, fragment=False, folder_paths=site_folder_paths)
            elif args[0]=='login':
                return try_render(self.login_args(*args, **kwargs), template='login', format='xhtml',  headers={'content-type':'text/html'}, fragment=False, folder_paths=site_folder_paths)
            elif args[0]=='requestPassword':
                req_pass_args = self.login_args(*args, **kwargs)
                req_pass_args.update(self.requestPassword(*args, **kwargs))
                return try_render(req_pass_args,  template='password', format='xhtml', headers={'content-type':'text/html'}, fragment=False, folder_paths=site_folder_paths)
            elif args[0]=='resetPassword':
                reset_pass_args = self.login_args(*args, **kwargs)
                reset_pass_args.update(self.resetPassword(*args, **kwargs))
                return try_render(reset_pass_args,  template='password', format='xhtml', headers={'content-type':'text/html'}, fragment=False, folder_paths=site_folder_paths)
   
        if '_'in kwargs:
            del kwargs['_']
        return self.application()


    def login_args(self, previous_url=None, *args, **kwargs):
        forward_url=None
        if 'forward_url' in kwargs:
            forward_url = kwargs['forward_url']
        if identity.was_login_attempted():
            cherrypy.response.status=403
            msg=_("Your username or password were incorrect. "
                  "Please try again.")
        elif identity.get_identity_errors():
            msg=_("Please log in.")
        else:
            msg=_("Please log in.")
            forward_url=cherrypy.request.headers.get("Referer", "/")
        try:    
            location = get_location_from_base_url()
            updates = get_updates_data(location)
        except:
            location = None
            updates = None
        return dict(login_message=msg, previous_url=previous_url, logging_in=True,
                    original_parameters=cherrypy.request.params,
                    forward_url=forward_url, updates=updates, location=location)
    

    def requestPassword(self, *args, **kwargs):
        try:
            if args[1]=='username':
                mode = "uname"
            else:
                mode = "pword"
        except:
            mode = "pword"
            
        email = None
        if 'email' in kwargs:
            email = kwargs['email']
        showform = True
        if not email:
            return dict(message=_("Please enter the email address associated with your account"),
                        showform=True)
        result = User.select(User.q.email_address==email)
            
        try:
            if mode == "uname":
                user = result[0]
                mailtext = "Dear %(first_name)s,\n\nYour username is: %(user_name)s\n\nYou can login at:\n\n%(request_url)s\n\nIf you have any questions, please contact The Hub's hosting team at %(location_name)s.hosts@the-hub.net or phone %(telephone)s.\n\nThank you very much.\n\nThe Hosting Team" %({'first_name':user.first_name, 'request_url':cherrypy.request.base, 'user_name':user.user_name, 'location_name':user.homeplace.name.lower().replace(' ', ''), 'telephone':user.homeplace.telephone})
            
                sendmail.sendmail(email, user.homeplace.name.lower().replace(' ', '') +'.hosts@the-hub.net','The Hub | username reminder',mailtext,[])
                return dict(message=_("""A confirmation email was sent to you. """),
                        showform=False)
            else:
                user = result[0]
                reminderkey = md5.new(str(random.random())).hexdigest()
                user.reminderkey = reminderkey
                mailtext = "Dear %(first_name)s,\n\nPlease click the link to reset your password:\n\n %(request_url)s/resetPassword?key=%(reminderkey)s\n\nIf you have any questions, please contact The Hub's hosting team at %(location_name)s.hosts@the-hub.net or phone %(telephone)s.\n\nThank you very much.\n\nThe Hosting Team" %({'first_name':user.first_name, 'request_url':cherrypy.request.base, 'reminderkey':reminderkey, 'location_name':user.homeplace.name.lower().replace(' ', ''), 'telephone':user.homeplace.telephone})
            
                sendmail.sendmail(email, user.homeplace.name.lower().replace(' ', '') +'.hosts@the-hub.net','The Hub | password reminder',mailtext,[])
                return dict(message=_("""A confirmation email was sent to you. """),
                        showform=False)
        except:            
            return dict(message=_("The email was not correct"),
                        showform=True)


    def resetPassword(self, *args,**kwargs):
        key=kwargs['key']
        result = User.selectBy(reminderkey=key)
        if result.count()==0:
            return dict(message=_("The confirmation key is wrong - maybe you need to check your email?"),
                        showform=False)

        else:
            user=result[0]
            user.reminderkey = md5.new(str(random.random())).hexdigest()	    
            newpassword = md5.new(str(random.random())).hexdigest()[:8]
            user.password = newpassword 
            mailtext = """
Dear Member,

Your new password for The Hub is: %(newpassword)s

For your convenience and security please login and change the password at the earliest possible opportunity. To do so click 'edit' on the top section of your profile page and enter a new password in the 'password' and 'confirm password' fields.

You can login at:
%(url)s

The Hub Team
"""%({'newpassword':newpassword, 'url':user.homeplace.url})
            sendmail.sendmail(user.email_address, user.homeplace.name.lower().replace(' ', '') +'.hosts@the-hub.net','The Hub | new password',mailtext,[])
            return dict(message=_("""The new password was sent to you."""),
                        showform=False)



    ####################################################################################
   
    def default_new(self, *args, **kwargs):
        if cherrypy.request.path.endswith('public'):
            print cherrypy.request.path, "endswith public"
            redirect(cherrypy.request.base + cherrypy.request.path + '/') 

        #if not identity.current.user.active and cherrypy.request.path == '/':
        #    print "path: " + cherrypy.request.path
        #    redirect(cherrypy.request.base + '/public/login')

        locale = get_locale()
        site_folder_paths = ['hubspace.templates.']

        #if not model.Location.select().count():
        #    return self.setup_form()

        if len(args)>0 and args[0]=='failed':
            cherrypy.response.status=403
            return try_render(login_args(*args, **kwargs), template='microSiteLogin', format='xhtml', headers={'content-type':'text/html'}, fragment=False, folder_paths=site_folder_paths)

        
        if identity.current.anonymous or not identity.current.user.active:
            login_dict = login_args(*args, **kwargs)
            if cherrypy.request.base in site_folders:
                site_folder_paths.insert(0, site_folders[cherrypy.request.base])

            if not args:
                path = ''
            else:
                path = '/'.join(args)
            if 'public' not in cherrypy.request.browser_url and not cherrypy.request.base in ['http://the-hub.net', 'http://new.the-hub.net']:
                
                redirect(cherrypy.request.base + '/public/' + path)

        if not identity.current.anonymous \
            and identity.was_login_attempted() \
            and not identity.get_identity_errors() \
            and cherrypy.request.path != "/":
            raise redirect(cherrypy.request.base)
   
        if '_'in kwargs:
            del kwargs['_']
        return self.application()


    @expose('hubspace.templates.profile')
    def application(self):
        return {'area':'profile', 'object':identity.current.user}

    @expose()
    @identity.require(not_anonymous())
    def listlocations(self):
        names = []
        return [h.name for h in Location.select()]

    @expose()
    def setUp(self):
        os.system('./bin/kidc hubspace/templates')
        print "setup: Templates compiled!"
        create_permissions()
        if config.get('server.testing', False):
            populate()
            create_wa() # This user is not required at LDAP side, but rightnow we are creating it solely to make all the
                        # tests pass
            print "populate done"
        return 'done'
    
    @expose()
    @identity.require(not_anonymous())
    def logout(self):
        cherrypy.session['locale'] = ""
        identity.current.logout()
        #if ldap_sync_enabled:
        #    syncerclient.onSignoff()
        raise redirect(cherrypy.request.base + "/login")

    @expose()
    @identity.require(not_anonymous())
    @validate(validators=CreateTodoSchema())
    def create_todo(self,tg_errors=None,**kwargs):
        '''create a todo
        permission: manage_todos'''

        if kwargs['parent']:
            kwargs['foruser'] = Todo.get(kwargs['parent']).foruser.id
        elif not kwargs['action']:
            kwargs['action'] = 'edit'
            
        foruser = User.get(kwargs['foruser'])
        
        create_todo = False
        locations = user_locations(foruser, ['host', 'director', 'superuser'])
        for location in locations:
            if permission_or_owner(location, None, 'manage_todos'):
                create_todo = True
        
        if create_todo==False:
            raise IdentityFailure("What about not hacking the system")
            
        kwargs.setdefault('parent', None)
        kwargs.setdefault('due', None)

        if tg_errors:
            object = None
            if kwargs['parent']:
                object = Todo.get(kwargs['parent'])
                template = "hubspace.templates.addTodo"
            elif kwargs['foruser']:
                object = User.get(kwargs['foruser'])
                template = "hubspace.templates.addTodoBar"
            todo = AttrDict(kwargs)
            cherrypy.response.headers['X-JSON'] = 'error'
            return try_render({'object':object, 'todo':todo, 'tg_errors':tg_errors}, template=template, format='xhtml', headers={'content-type':'text/html'}, fragment=True)

        

        kwargs['createdby'] = identity.current.user.id
        kwargs.setdefault('opened', now(foruser.homeplace))

        todo = create_object('Todo',**kwargs)
        cherrypy.response.headers['X-JSON'] = 'success'
        return try_render({'object':User.get(kwargs['foruser'])}, template='hubspace.templates.host', format='xhtml', headers={'content-type':'text/html'}, fragment=True)


    @expose(template="hubspace.templates.addMember")
    @identity.require(not_anonymous())
    @validate(validators=AddMemberSchema())
    def create_user(self, tg_errors=None, **kwargs):
        home_group = None
        if 'homeplace' in kwargs:
            location = Location.get(int(kwargs['homeplace']))
            ##add user to member group for this location
            home_group = Group.selectBy(level='member', place=location.id)[0]
        else:
            location = Location.get(1)

        if not permission_or_owner(None,None,'manage_users'):
            raise IdentityFailure('what about not hacking the system')

        if 'active' not in kwargs or not kwargs['active']:
            kwargs['active'] = 0
            
        if tg_errors:
            #log the error
            cherrypy.response.headers['X-JSON'] = ['failure']
            if 'public_field' not in kwargs:
                kwargs['public_field'] = 0
            groups = []
            if 'groups' in kwargs:
                for loc in kwargs['groups']:
                    for level in kwargs['groups'][loc]:
                        group = Group.select(AND(Group.q.placeID==loc,
                                                 Group.q.level==level))
                        if group and group not in groups:
                            groups.append(group[0])
                            
                kwargs['groups'] = groups

            if 'homeplace' in kwargs:
                kwargs['homeplace'] = Location.get(kwargs['homeplace'])
            
            obj = AttrDict(**kwargs)
            return {'new_user':obj, 'tg_errors':tg_errors}


        if 'new_alias' in kwargs and kwargs['new_alias']:
            aliases = kwargs['new_alias'].split(',')
        else:
            aliases = []
            
        if 'password' in kwargs and kwargs['password'] in ["", None]:
            del kwargs['password']

        user = create_object('User',**kwargs)
        for alias in aliases:
            create_object('Alias', user=user.id, alias_name=alias.strip())
       
        user.billto = user.id
        if home_group:
            self.addUser2Group(user, home_group)

        if 'groups' in kwargs:
            to_groups = []
            for loc in kwargs['groups']:
                for level in kwargs['groups'][loc]:
                    group = Group.select(AND(Group.q.placeID==loc, Group.q.level==level))
                    if group and group[0]:
                        to_groups.append(group[0])

            for grp in to_groups:
                self.addUser2Group(user, grp)

        if user.active:
            send_welcome_mail(user, kwargs['password'])
        model.hub.commit()
        hubspace.search.update(user)
        if kwargs['public_field']==1:
            clear_cache('profiles', location)
        cherrypy.response.headers['X-JSON'] = 'success'
        return str(user.id)

    @expose()
    @strongly_expire
    @identity.require(not_anonymous())
    def maxid(self,objecttype):
        theclass = getattr(hubspace.model,objecttype)
        return str(theclass.select().max('id'))

    @expose(template="hubspace.templates.notes")
    @identity.require(not_anonymous())
    @validate(validators={'id':v.Int()})
    def delete_note(self, id=None, **kwargs):
        try:
            n = Note.get(id)
            if n.action:
                n.action.destroySelf()
            n.destroySelf()
            return ''
        except:
            n = Note.get(id)
            return {'note':n}

    @expose(template="hubspace.templates.notes")
    @identity.require(not_anonymous())
    @validate(validators=AddNoteSchema())
    def create_note(self, tg_errors=None, **kwargs):

        if tg_errors:
            obj = AttrDict(**kwargs)
            return {'user':obj, 'tg_errors':tg_errors}

        user = User.get(kwargs['onuser'])
        if not permission_or_owner(user.homeplace,None,'manage_notes'):
            raise IdentityFailure('what about not hacking the system')

        kwargs['date'] = now(user.homeplace)     
        kwargs['byuser'] = identity.current.user.id
        note = create_object('Note',**kwargs)

        return {'user': note.onuser}
    
    @expose(template='hubspace.templates.uploadImage')
    @identity.require(not_anonymous())
    def uploadImageIframe(self, id, type, attr, **kwargs):
        return {'id':id, 'type':type, 'attr':attr}


    @expose()
    @identity.require(not_anonymous())
    @validate(validators={'object_id':real_int, 'object_type':v.UnicodeString(), 'attr':v.UnicodeString()})
    def uploadImage(self, object_id, object_type, attr, image):
        if not image.file:
            raise 'NoFile', 'You need to upload a fifle'
        theclass = getattr(hubspace.model, object_type)
        obj = theclass.get(object_id)
        if not permission_or_owner(get_place(obj), obj, 'manage_'+object_type.lower()+'s'):
            raise IdentityFailure('what about not hacking the system')
        
        if "image/" in image.type:
            #try:
            save = getattr(obj, "save_" + attr)
            save(attr, image.file.read(), 'image/png')
            if isinstance(obj, User) and obj.public_field == 1:
                clear_cache('profiles', obj.homeplace)
            #except:
            #    raise "error during upload"
        else:
            raise "unexpected content type" + `image.type`

        return "<div id='new_image_src'>/display_image/" + object_type + '/' + str(object_id) + '/' + attr + "</div>"

    @expose()
    @identity.require(identity.has_any_permission("webapi","superuser"))
    def upload_printer_log(self, log=''):
        new_jobs_file = open("printing/jobs.csv", 'wb')
        new_jobs_file.write(log.file.read())
        print "print uploaded succeeded!"
        return "success"

        
    @expose()
    @strongly_expire
    @identity.require(not_anonymous())
    def get_widget(self, widget_name, object_id="", object_type="User", **kwargs):
        """dynamically get a preset widget from the server side for inplace editing
        """
        theclass = getattr(hubspace.model, object_type)
        obj = theclass.get(object_id)

        template_args = {}
        if obj:
            template_args['object'] = obj
        for kwarg in kwargs:
            if kwarg in ['location', 'action', 'user', 'tariff', 'res_or_tariff']:
                template_args[kwarg] = kwargs[kwarg]

        return try_render(template_args, template='hubspace.templates.'+str(widget_name), format='xhtml', headers={'content-type':'text/html'}, fragment=True) 


    @expose()
    @strongly_expire
    @identity.require(not_anonymous())
    @validate(validators={'q':v.UnicodeString()})
    def filter_book_for(self, q, timestamp, **kwargs):
        members = filter_members(0, q, 'member_search', False, 0, 10)
        members = [member.display_name +'|'+ str(member.id) for member in members]
        return '\n'.join(members)
    
    @expose()
    @strongly_expire
    @identity.require(not_anonymous())
    @validate(validators={'location':real_int, 'text_filter':v.UnicodeString(), 'type':v.UnicodeString(), 'start':real_int, 'end':real_int})
    def filter_members(self, location, text_filter, type, start, end, **kwargs):
        if location:
            location = Location.get(location)        
        is_host_in_locs = user_locations(identity.current.user, levels=['host'])
        if len(is_host_in_locs)==0:
            active_only = True
        else:
            active_only = False
        users = filter_members(location, text_filter, type, active_only, start, end)
        
        if type == 'member_search':
            return try_render({'members':users}, template='hubspace.templates.memberslist', format='xhtml', headers={'content-type':'text/html'}, fragment=True)
        elif type == 'fulltext_member_search':
            return try_render({'results':users, 'query':text_filter}, template='hubspace.templates.fulltextsearch', format='xhtml', headers={'content-type':'text/html'}, fragment=True)
        elif type == 'rfid_member_search':
            if not permission_or_owner(None, None, 'manage_users'):
                raise IdentityFailure('what about not hacking the system')
            if not text_filter:
                users = []
            try:
                user = users[0]
                return `user.id`
                #return try_render({'object':user}, template='hubspace.templates.mainProfile', format='xhtml', headers={'content-type':'text/html'}, fragment=True)
            except:
                return "<p>No user is associated with this card</p>"



    ####################### Resource Tariff Search #########
    @expose()
    @strongly_expire
    @identity.require(not_anonymous())
    @validate(validators={'location':real_int, 'resource_type':ForEach(v.UnicodeString()), 'search_from_date':dateconverter})
    def uninvoiced_users(self, location, resource_type, search_from_date, **kwargs):
        users=uninvoiced_users(location, resource_type, search_from_date)
        return try_render({'results':users, 'query':'', 'subsection':'billing'}, template='hubspace.templates.fulltextsearch', format='xhtml', headers={'content-type':'text/html'}, fragment=True) 


    ##################Invoices###############################
    @expose()
    @identity.require(not_anonymous())
    @validate(validators={'userid':real_int,'amount':real_int})
    def updateUserOutstanding(self,userid,amount):
        user = User.get(userid)
        if not permission_or_owner(user.homeplace,None,'manage_users'):
            raise IdentityFailure('what about not hacking the system')
        user.outstanding = amount
        return `user.outstanding`

    @expose()
    @strongly_expire
    @identity.require(identity.has_any_permission("webapi","superuser"))
    @validate(validators={'place':real_int})
    def user_list(self, place=None):
        if not permission_or_owner(Location.get(place), None, 'manage_users'):
            raise IdentityFailure('what about not hacking the system')
        out = StringIO.StringIO()
        writer = csv.writer(out,quoting=csv.QUOTE_ALL)
        users = get_users_for_location(place)
        for user in users:
            row = (user.user_name,
                   user.display_name.encode('utf-8'),
                   500 + int(user.id),
                   user.unix_hash,
                   user.lanman_hash,
                   user.nt_hash)
            writer.writerow(row)
        return out.getvalue()

    @expose()
    @strongly_expire
    @identity.require(not_anonymous())
    def all_user_org_website(self, file_name=None):
        if not permission_or_owner(None, None, 'manage_locations'):
            raise IdentityFailure('what about not hacking the system')

        out = StringIO.StringIO()  
        writer = csv.writer(out, quoting=csv.QUOTE_ALL)
        users = User.select()
        for user in users:
             row = (user.display_name and user.display_name.encode('utf-8') or "",
                    user.organisation and user.organisation.encode('utf-8') or "",
                    user.website and user.website.encode('utf-8') or "")
             writer.writerow(row)
        cherrypy.response.headerMap["Content-Type"] = "text/csv"
        cherrypy.response.headerMap["Content-Length"] = out.len
        return out.getvalue()
        
    @expose()
    @strongly_expire
    @identity.require(not_anonymous())
    #@identity.require(identity.has_any_permission("webapi","superuser"))
    @validate(validators={'place':real_int})
    def sage_user_list(self, place=None, file_name=None):
        """Please do check docs/sage_export.txt"""
        if not permission_or_owner(Location.get(place), None, 'manage_users'):
            raise IdentityFailure('what about not hacking the system')

        out = StringIO.StringIO()
        writer = csv.writer(out, quoting=csv.QUOTE_ALL)
        users = User.select("""homeplace_id=%s"""%(place))
        for user in users:
            address = user.address.encode('utf-8')
            if not address:
                address = ""
            addresslines = address.split('\n',5)
            row = (user.id,
                   user.display_name.encode('utf-8'),
                   addresslines[0],
                   len(addresslines) > 1 and addresslines[1] or '',
                   len(addresslines) > 2 and addresslines[2] or '',
                   len(addresslines) > 3 and addresslines[3] or '',
                   len(addresslines) > 4 and addresslines[4] or '',
                   user.display_name.encode('utf-8'),
                   user.work and user.work or user.home,
                   user.fax,
                   '',
                   '',
                   '',
                   user.homeplace.id,
                   user.bill_vat_no,
                   0,
                   0,
                   0,
                   0,
                   '',
                   0,
                   0,
                   '',
                   0, #Default Tax Code
                   '',
                   '',
                   user.email_address and user.email_address.encode('utf-8') or "",
                   user.website and user.website.encode('utf-8') or "",
                   0,
                   0,
                   1)
            writer.writerow(row)

        cherrypy.response.headerMap["Content-Type"] = "text/csv"
        cherrypy.response.headerMap["Content-Length"] = out.len
        return out.getvalue()


    @expose()
    @strongly_expire
    @identity.require(not_anonymous())
    @validate(validators={'place':real_int, 'start':dateconverter, 'end':dateconverter})
    def invoice_list(self, place=None, start=None, end=None, file_name=None):
      
        '''This is for sage
        "SI","2","4000","1","07/01/2007","H1","no details","210.00","T1","26.75","1", "1", "Jonathan Robinson"
        "SI", "userid", "4000", "1", "date", "invoice_id", "some details", "net amount", "T1", "vat", "exchange_rate", "extra info", "user name"

        if invoice amounts are -ve switch SI (invoice) to SC (credit) and put +ve values in export
        '''
        if not permission_or_owner(Location.get(place), None, 'manage_users'):
            raise IdentityFailure('what about not hacking the system')

        out = StringIO.StringIO()
        writer = csv.writer(out,quoting=csv.QUOTE_ALL)
        invoices = Invoice.select(AND(Invoice.q.sent>=start,
                                      Invoice.q.sent<(end + timedelta(days=1)),
                                      Invoice.q.locationID==place))
        for invoice in invoices:
            excluding_vat = Decimal(str(invoice.amount)) - invoice.total_tax
            
            if invoice.amount>0:
                code = 'SI'
            elif invoice.amount<0:
                code = 'SC'
            else:
                continue
                
            row = (code,
                   invoice.user.id,
                   4000,
                   1,
                   invoice.sent.strftime('%d/%m/%Y'),
                   'H'+str(invoice.id),
                   'Invoice with id %s for period %s to %s' %(invoice.id, invoice.start.strftime('%d/%m/%Y'), invoice.end_time.strftime('%d/%m/%Y')),
                   str(abs(excluding_vat)), #net amount
                   "T1",
                   str(abs(invoice.total_tax)), #tax amount
                   1,
                   1,
                   invoice.user.display_name.encode('utf-8'))
            writer.writerow(row)
        cherrypy.response.headerMap["Content-Type"] = "text/csv"
        cherrypy.response.headerMap["Content-Length"] = out.len
        return out.getvalue()

    
    @expose()
    @strongly_expire
    @identity.require(not_anonymous())
    @validate(validators={'invoiceid':real_int})
    def pdf_invoice(self, invoiceid, filename=None, html2ps=None):
        invoice = Invoice.get(invoiceid)
        if not permission_or_owner(invoice.user.homeplace, invoice, 'manage_invoices'):
            raise IdentityFailure('what about not hacking the system')
        pdf = self.create_pdf_invoice(invoiceid=invoiceid,html2ps=html2ps)
        #cherrypy.response.headers['Content-type'] = 'application/pdf'
        return pdf
    
    @expose()
    @identity.require(not_anonymous())
    def new_invoices(self):
        invoice_ids = (inv.id for inv in model.Invoice.selectBy(location = identity.current.user.homeplace)[:10])
        invoice_urls = ("<a href=/show_newinvoice/%s> %s </a>" % (invoice_id, invoice_id) for invoice_id in invoice_ids)
        return "<br/>".join(invoice_urls)

    @expose()
    @identity.require(not_anonymous())
    def show_newinvoice(self, invoiceid):
        invoice=model.Invoice.get(int(invoiceid))
        if not permission_or_owner(invoice.user.homeplace, invoice, 'manage_invoices'):
            raise IdentityFailure('what about not hacking the system')
        MCust = model.MessageCustomization
        try:
            freetext1 = MCust.select(AND(MCust.q.message=="invoice_freetext_1", MCust.q.location==invoice.location))[0].text
        except:
            freetext1 = ""

        try:
            freetext2 = MCust.select(AND(MCust.q.message=="invoice_freetext_2", MCust.q.location==invoice.location))[0].text
        except:
            freetext2 = ""
        d = dict(invoice=invoice, freetext1=freetext1, freetext2=freetext2)
        html =  try_render(d, template='hubspace.templates.newinvoice', format='html', headers={'content-type':'text/html'})
        html = html.replace("NEXTPAGEHACK", "<div> <pdf:nextpage/> </div> ")
        src = cStringIO.StringIO(html)
        dst = cStringIO.StringIO()
        pdf = pisa.CreatePDF(src, dst, encoding='utf-8')
        dst.seek(0)
        cherrypy.response.headers['Content-type'] = 'application/pdf'
        return dst.read()

    def create_pdf_invoice(self, invoiceid, html2ps=None):
        invoiceid = int(invoiceid)
        invoice = Invoice.get(invoiceid)
        return self.show_newinvoice(invoiceid)

    @expose()
    @identity.require(not_anonymous())
    def old_invoice(self, invoice_no, html2ps=None):
        try:
            invoice = Invoice.selectBy(number=invoice_no)[0]
        except:
            invoice = Invoice.get(int(invoice_no))
        if not permission_or_owner(invoice.user.homeplace, invoice, 'manage_invoices'):
            raise IdentityFailure('what about not hacking the system')
        html =  try_render(dict(invoice=invoice),template='hubspace.templates.invoice', format='html', headers={'content-type':'text/html'})
        if html2ps:
            command = 'html2ps | ps2pdf13 - -'
        else:
            command = 'htmldoc --webpage -t pdf --top 0 --left 10mm --right 10mm --bottom 0 --footer . -'
        stdin, stdout, stderr = os.popen3(command)
        try:
            html = html.decode('utf-8').encode('iso-8859-1')
        except UnicodeEncodeError:
            pass # try w/o decode encode now
        stdin.write(html)
        stdin.close()
        pdf = stdout.read()
        stdout.close()
        cherrypy.response.headers['Content-type'] = 'application/pdf'
        return pdf


    @expose()
    @identity.require(not_anonymous())
    @validate(validators={'invoiceid':real_int, 'rusageid':real_int})
    def remove_rusage_from_invoice(self, invoiceid=None, rusageid=None, **kwargs):
        
        invoice = Invoice.get(invoiceid)
        if invoice.sent:
            raise ValueError
        rusage = RUsage.get(rusageid)

        if not permission_or_owner(invoice.user.homeplace, None, 'manage_invoices'):
            raise IdentityFailure('what about not hacking the system')

        if rusage in invoice.rusages:
            rusage.invoice = None
            self.update_invoice_amount(invoice.id)
        return ''

    @expose()
    @identity.require(not_anonymous())
    @validate(validators={'invoiceid':real_int, 'rusageid':real_int})
    def add_rusage_to_invoice(self, invoiceid=None, rusageid=None, **kwargs):
        invoice = Invoice.get(invoiceid)
        if invoice.sent:
            raise ValueError
        rusage = RUsage.get(rusageid)

        if not permission_or_owner(invoice.user.homeplace, None, 'manage_invoices'):
            raise IdentityFailure('what about not hacking the system')

        if rusage not in invoice.rusages:
            rusage.invoice = invoice
            self.update_invoice_amount(invoice.id)
        return ''



    @expose()
    @identity.require(not_anonymous())
    @validate(validators={'user_id':real_int})
    def ignore_remind(self, user_id, **kwargs):
        user = User.get(user_id)
        
        if not permission_or_owner(user.homeplace, None, 'manage_users'):
            raise IdentityFailure('what about not hacking the system')
        
        user.last_reminder = now(user.homeplace)
        return ''
        
    @expose()
    @identity.require(not_anonymous())
    @validate(validators={'id':real_int, 'subject':All(v.String(), v.NotEmpty()), 'body':All(v.String(), v.NotEmpty())})
    def send_reminder(self, tg_errors=None, **kwargs):
        user = User.get(kwargs['id'])
        
        if not permission_or_owner(user.homeplace, None, 'manage_users'):
            raise IdentityFailure('what about not hacking the system') 
        
        if tg_errors:
            object = AttrDict(**kwargs)
            object.outstanding = user.outstanding
            object.first_name = user.first_name
            cherrypy.response.headers['X-JSON'] = 'error'
            return self.error_template("sendReminder", {'object':object, 'tg_errors':tg_errors})
        subject = kwargs['subject']
        body = kwargs['body']
       
        sent = send_mail(to=user.email_address, sender=user.homeplace.name.lower().replace(' ', '_') + ".hosts@the-hub.net",subject=subject,body=body)
        if sent:
            cherrypy.response.headers['X-JSON'] = 'success'
            user.reminder_counter += 1
            user.last_reminder = now(user.homeplace)
            return ''
        else:
            cherrypy.response.headers['X-JSON'] = 'error'
            return 'could not send mail'



    @expose()
    @identity.require(not_anonymous())
    def send_invoice(self, invoiceid=None, subject="", body="", **kwargs):
        try:
            invoiceid=int(invoiceid)
            invoice = Invoice.get(invoiceid)
        except:
            return "problem sending invoice"
 
        if not permission_or_owner(invoice.user.homeplace, None, 'manage_invoices'):
            raise IdentityFailure('what about not hacking the system')          

        if not invoice.sent:
            self.update_invoice_amount(invoiceid)

        to = invoice.user.bill_to_profile and invoice.user.email_address or invoice.user.bill_email
        if not to:
            if not invoice.user.bill_to_profile and not invoice.user.bill_email:
                return _("Problem sending the invoice: Member's billing preferences are set to not to use profile details and billing preferences has no email address specified. You may want visit member's 'Billing Details' section.")
            return "user has no email address"

        pdf = self.create_pdf_invoice(invoiceid=invoiceid)

        if not kwargs.get('send_it'):
            return "Invoice not sent by email not sent!"
        host_mail = invoice.user.homeplace.name.lower().replace(' ', '') + '.hosts@the-hub.net'
        value = send_mail(to=to, sender=host_mail, subject=subject, body=body, attachment=pdf, cc=host_mail, attachment_name="Invoice%s.pdf"%invoice.id)
        if value:
            if not invoice.sent:
                invoice.sent = now(invoice.location)
                applogger.info("Invoice: Invoice (id: %s number: %s) sent successfully" % (invoice.id, invoice.number))
            return 'Invoice was sent successfully'
        else:
            applogger.error("Invoice: Failed sending Invoice (id: %s number: %s)" % (invoice.id, invoice.number))
            return 'There was a problem sending the invoice'

    @expose(template="hubspace.templates.todos")
    @strongly_expire
    @identity.require(identity.has_any_permission('manage_todos','superuser'))
    #@identity.require(not_anonymous())
    @validate(validators={'bar_id':real_int, 'show':BoolInt()})
    def toggle_closed_todos(self, bar_id, show=True, **kwargs):
        todobar = Todo.get(bar_id)
        return {'show_closed':show, 'bar':todobar, 'object':todobar.foruser}

    @expose()
    @identity.require(identity.has_any_permission('manage_todos','superuser'))
    @validate(validators={'bar_id':real_int})
    def delete_todo_bar(self, bar_id, **kwargs):
        todobar = Todo.get(bar_id)
        todobar.closed = now(todobar.foruser.homeplace)
        for todo in todobar.children:
            if not todo.closed:
                todo.closed= now(todobar.foruser.homeplace)
        return ""

  

    @expose()
    @strongly_expire
    @identity.require(not_anonymous())
    def display_invoice(self, userid=None, invoiceid=None, **kwargs):
        user = None
        invoice = None
        if userid:
            user = User.get(userid)            
        if invoiceid:
            invoice = Invoice.get(invoiceid)
            user = invoice.user

        if not permission_or_owner(user.homeplace, invoice, 'manage_invoices'):
            raise IdentityFailure('what about not hacking the system')
        
        if not user:
            user = invoice.user
        return try_render({'user':user, 'invoice':invoice}, template='hubspace.templates.invoicesnippet', format='xhtml', headers={'content-type':'text/html'}, fragment=True)

    @expose()
    @strongly_expire
    @identity.require(not_anonymous())
    @validate(validators={'userid':v.Int(), 'invoiceid':v.Int(), 'start':dateconverter, 'end_time':dateconverter})
    def update_resource_table(self, tg_errors=None, userid=None, invoiceid=None, start=None, end_time=None, **kwargs):
        print tg_errors
        if tg_errors:
            raise `str(tg_errors.get('invoiceid') or tg_errors)`
        user=None
        invoice = None
        if userid:
            user =User.get(userid)
        if invoiceid:
            invoice = Invoice.get(invoiceid)
            if not user:
                user = invoice.user

	#user is used as the object here because we want to allow the user to update the resource table when invoice=None (ie. to look through uninvoiced items)
        if not permission_or_owner(user.homeplace, user, 'manage_invoices'):
            raise IdentityFailure('what about not hacking the system')

        return display_resource_table(user=user, invoice=invoice, earliest=start, latest=end_time)


    @expose(format="json")
    @strongly_expire
    @identity.require(not_anonymous())
    @validate(validators={'billed_user_id':real_int, 'ruse_user_id':real_int, 'invoice_id':real_int, 'resource_id':real_int, 'earliest':dateconverter, 'latest':dateconverter})
    def insert_sub_usages(self, tg_errors=None, billed_user_id=None, ruse_user_id=None, invoice_id=None, resource_id=None, earliest=None, latest=None, **kwargs):

        if tg_errors:
            for x in tg_errors:
                raise `str(tg_errors[x])`
        
        billed_user = User.get(billed_user_id)
        
        if not permission_or_owner(billed_user.homeplace, billed_user, 'manage_invoices'):
            raise IdentityFailure('what about not hacking the system')

        ruse_user = User.get(ruse_user_id)
        if invoice_id:
            invoice = Invoice.get(invoice_id)
            earliest = None
            latest = None
        else:
            invoice = None
            invoice_id = None
        resource = Resource.get(resource_id)
        rusages = get_collected_invoice_data(user=billed_user, invoice=invoice, earliest=earliest, latest=latest)[0][ruse_user][0][resource]

        json = {'rows':[]}
        for ruse in rusages:
            json['rows'].append(self.list_of_cell_values(ruse, billed_user, invoice_id))
        return json

    format_date = datetimeconverter.from_python

    def list_of_cell_values(self, rusage, billed_user, invoice):
        if rusage.refund:
            title = "Refund"
        elif rusage.cancelled:
            title = "Cancelled"
        else:
            title = ""
        values = [title,
                  self.format_date(rusage.start),
                  self.format_date(rusage.end_time),
                  show_quantity_or_duration(rusage),
                  rusage.resource.place.name
                  ]
        if invoice:
            values.append(inv_currency(invoice, billed_user) +" "+ c2s([rusage.customcost,rusage.cost][rusage.customcost == None]))
            if unsent_for_user(billed_user) and unsent_for_user(billed_user).id==invoice and permission_or_owner(billed_user.homeplace, None, 'manage_invoices'):
                values.append(try_render({'remove_from_invoice':True, 'rusage':rusage}, template='hubspace.templates.subresourcetable', format='xhtml', headers={'content-type':'text/html'}, fragment=True))
        else:
            values.append(try_render({'cost':True, 'rusage':rusage, 'billed_user':billed_user, 'invoice':invoice}, template='hubspace.templates.subresourcetable', format='xhtml', headers={'content-type':'text/html'}, fragment=True))
            if permission_or_owner(billed_user.homeplace, None, 'manage_invoices'):
                if unsent_for_user(billed_user):
                    values.append(try_render({'add_to_invoice':True, 'rusage':rusage}, template='hubspace.templates.subresourcetable', format='xhtml', headers={'content-type':'text/html'}, fragment=True))
                values.append(try_render({'delrusage':True, 'rusage':rusage}, template='hubspace.templates.subresourcetable', format='xhtml', headers={'content-type':'text/html'}, fragment=True))
        # fix for #210 and #224. This might not be reqd if default encoding is utf-8.
        # Problem is while jsonifying if the basestring object is string containing encoded unicode chars (nor ascii
        # string or unicode ) the encoder that is used for jsonification could not handle and fails. So we take care of
        # such situation here. This happens typically when template translation replaces "change" with "\xc3\xa4ndra"
        def fix_chunk(s):
            if isinstance(s, basestring) and not isinstance(s, unicode):
                try:
                    s = s.decode('utf-8')
                except:
                    pass
            return s
        return [fix_chunk(v) for v in values]
            

    @expose()
    @identity.require(not_anonymous())
    @validate(validators={'id':real_int, 'customcost':v.Money(not_empty=True)})
    def save_costEdit(self, id, tg_errors=None, **kwargs):
        if tg_errors:
            kwargs['cost']=kwargs['customcost']
            object = AttrDict(id=id, **kwargs)
            cherrypy.response.headers['X-JSON'] = 'error'
            return self.error_template('costEdit', {'object':object, 'tg_errors':tg_errors})

        rusage = RUsage.get(id)

        if not permission_or_owner(rusage.user.homeplace, None, 'manage_rusages'):
            raise IdentityFailure('what about not hacking the system')

        rusage.customcost = kwargs['customcost']
        cherrypy.response.headers['X-JSON'] = 'success'
        return inv_currency(None, rusage.user) +" "+ c2s(rusage.customcost)

    @expose(template="hubspace.templates.billing")
    @identity.require(not_anonymous())
    @validate(validators={'start':dateconverter, 'end_time':dateconverter, 'userid':real_int})
    def create_invoice(self, autocollect=True,**kwargs):
        amount = 0
        kwargs.setdefault('user', kwargs['userid'])        
        user = User.get(kwargs['user'])
        
        if not permission_or_owner(user.homeplace, None, 'manage_invoices'):
            raise IdentityFailure('what about not hacking the system')

        users = [u for u in user.billed_for]
        if user.billto==None and user not in users:
            users.append(user)
        if len(users)<1:
            raise 'Cant invoice this user directly - this user %s bills to user %s - %s' % (user.id,user.billto.id,user.billto.user_name)
        kwargs.setdefault('billingaddress',user.billingaddress)
        if not kwargs['start']:
            kwargs['start']=datetime(1970,1,1)
        if not kwargs['end_time']:
            kwargs['end_time']= now(user.homeplace)
        kwargs.setdefault('location',user.homeplace)
        invoice = create_object('Invoice',**kwargs)

        if autocollect:
            for u in users:                
                for rusage in get_rusages(u, None, kwargs['start'], kwargs['end_time']):
                    rusage.invoice = invoice.id
        
        self.update_invoice_amount(invoice.id)
        return {'object':user}

    @expose()
    @strongly_expire
    @identity.require(not_anonymous())
    def update_invoice_amount(self, invoiceid, force=False):
        """Called whenever an invoice is created or updated.
        Calculates the amount of the invoice -- including vat.
        Calculates the tax on the invoice
        """
        invoice = Invoice.get(invoiceid)
        if not permission_or_owner(invoice.user.homeplace, invoice, 'manage_invoices'):
            raise IdentityFailure('what about not hacking the system')
        
        if invoice.sent and force and permission_or_owner(None, None, 'superuser'):
            tmp = invoice.sent
            invoice.sent = None
            calculate_tax_and_amount(invoice)
            invoice.sent = tmp
        else:
            calculate_tax_and_amount(invoice)
        return ''

    @expose()
    @identity.require(not_anonymous())
    @validate(validators={"invoiceid":real_int})
    def remove_invoice(self, invoiceid, **kwargs):
        inv = Invoice.get(invoiceid)        
        
        if not permission_or_owner(inv.user.homeplace, None, 'manage_invoices'):
            raise IdentityFailure('what about not hacking the system')
        
        if inv.sent != None:
            raise "you cant delete sent invoices"

        for rusage in RUsage.select(AND(RUsage.q.invoiceID==invoiceid)):
            rusage.invoice = None
        inv.destroySelf()
        return "" 

    @expose()
    @strongly_expire
    @identity.require(not_anonymous())
    @validate(validators={'rusage_id':real_int, 'resource_id':real_int, 'date':dateconverter})
    def explain_unavailable(self, rusage_id=None, resource_id=None, date=None, tg_errors=None, **kwargs):
        rusage = RUsage.get(rusage_id)
        resource = Resource.get(resource_id)
        location = resource.place
        message = "<p>The resource <em>" + escape(resource.name) + "</em> in " + escape(location.name) + " can not be booked between <em>"+ escape(datetimeconverter2.from_python(rusage.start)) + "</em> and <em>" + escape(datetimeconverter2.from_python(rusage.end_time)) + "</em> since it requires resource <em>" + escape(rusage.resource.name) + "</em> which is booked between these times</p>"
        times = opening_times(location.calendar, date)
        start = times[0][0]
        height = booking_offset_plus_height(rusage, start)    
        return {'render':try_render({'message':message}, template="hubspace.templates.viewBooking", format='xhtml', headers={'content-type':'text/html'}, fragment=True),'height':height, 'rusage_id':rusage.id}

    @expose(format="json")
    @strongly_expire
    @identity.require(not_anonymous())
    @validate(validators={"rusage":real_int, 'date':dateconverter})
    def get_rusage(self, rusage, date, **kwargs):
        """
        return the rusage interface and also the start time/offset in json
        """
        rusage = RUsage.get(rusage)
        times = opening_times(rusage.resource.place.calendar, date)
        start = times[0][0]
        height = booking_offset_plus_height(rusage, start)
        return {'render':try_render({'rusage':rusage}, template="hubspace.templates.viewBooking", format='xhtml', headers={'content-type':'text/html'}, fragment=True).decode('utf-8'),'height':height, 'start_time':datetimeconverter.from_python(rusage.start), 'end_hour':datetimeconverter.from_python(rusage.end_time.hour), 'end_minute':datetimeconverter.from_python(rusage.end_time.minute), 'date':dateconverter.from_python(date), 'rusage_id':rusage.id}


    @expose()
    @identity.require(not_anonymous())
    @validate(validators={"rusage":real_int})
    def delete_rusage(self, rusage, **kwargs):
        """
        rusage can be deleted till it's not invoiced. If it's on invoice which is not send, it can still be deleted with
        invoice recalculation. If invoice is sent, then rusage can only be cancelled (i.e a refund would be created)
        """
        rusage = RUsage.get(rusage)

        if not can_delete_rusage(rusage):
            raise IdentityFailure("You can't delete that booking")

        if rusage.invoiced:
            return self.cancel_rusage(rusage.id)

        invoice_updt_reqd = bool(rusage.invoice)
        invoice = rusage.invoice

        for suggestion in rusage.suggested_usages:
            suggestion.destroySelf()
        if not rusage.confirmed:
            bookinglib.notifyTentativeBookingRelease(rusage)
        applogger.info("Deleting RUsage %s" % rusage)
        rusage.destroySelf()

        if invoice_updt_reqd:
            self.update_invoice_amount(invoice.id)

        return ''
 
    @expose()
    @identity.require(not_anonymous())
    @validate(validators={"rusage":real_int})
    def cancel_rusage(self, rusage):
        rusage = model.RUsage.get(rusage)
        if can_delete_rusage(rusage):
            rusage.cancelled = 1
            rusage.public_field = 0
            # copy rusage
            d = dict ([ (col.name, getattr(rusage, col.name)) for col in rusage.sqlmeta.columnList ])
            d['refund'] = 1
            d['refund_for'] = rusage.id
            d['cost'] = (- d['cost'])
            d['quantity'] = (- d['quantity'])
            if d['customcost']:
                d['customcost'] = (-d['customcost'])
            else:
                d['customcost'] = None
            del d['invoiceID']
            new_rusage = model.RUsage(**d)
            location = rusage.resource.place
            to = rusage.resource.place.hosts_email
            data = dict ( rusage = rusage, user = rusage.user, location = location )
            if not rusage.resource.type == 'tariff':
                hubspace.alerts.sendTextEmail("booking_cancellation", data=data)
            applogger.info("Rusage cancellation: %s" % rusage)
            applogger.info("Rusage refund: %s" % new_rusage)
            if not rusage.confirmed:
                bookinglib.notifyTentativeBookingRelease(rusage)
            return str(new_rusage.id)
        raise IdentityFailure("You can't cancel that booking")

       
    @expose()
    @identity.require(not_anonymous())
    @validate(validators={"rusage_id":real_int})
    def addToResourceQueue(self, rusage_id):
        rusage = RUsage.get(rusage_id)
        model.ResourceQueue(foruser=identity.current.user.id, rusage=rusage_id)
        return ""

    @expose()
    @identity.require(not_anonymous())
    @validate(validators={"rusage_id":real_int})
    def confirmBooking(self, rusage_id):
        rusage = RUsage.get(rusage_id)
        if bookinglib.canConfirm(rusage):
            rusage.confirmed = 1
            bookinglib.onBookingConfirmation(rusage)
        return ""
       
    @expose()
    @identity.require(not_anonymous())
    def addUser2Group(self, user=None, group=None):
        if not isinstance(user, User):
            user = User.get(user)
        if not isinstance(group, Group):
            group = Group.get(group)

        if not permission_or_owner(group.place, None, 'manage_users'):
            raise IdentityFailure('what about not hacking the system')

        return addUser2Group(user, group)

    @expose_as_csv
    @strongly_expire
    @identity.require(not_anonymous())
    @validate(validators={'place':real_int})
    def usage_report_csv(self, place, filename=None, columns_selection=['resourcetype', 'resourceid', 'total', 'invoiced']):
        place = Location.get(place)
        if not permission_or_owner(place, None, 'manage_users'):
            raise IdentityFailure('what about not hacking the system')

        must_columns = ['location','resourcename']
        if isinstance(columns_selection, basestring): columns_selection = [columns_selection]
        columns = must_columns + columns_selection
        include_total = "total" in columns
        if include_total:
            columns.remove("total")
        include_invoiced = "invoiced" in columns
        if include_invoiced:
            columns.remove("invoiced")
        
        rusages = [rusage for rusage in RUsage.select() if rusage.resource.place==place]
        sums = dict()
        keys = []
        resources = {}

        for rusage in rusages:
            resourceid = rusage.resource.id
            resources[resourceid] = rusage.resource
            year = rusage.start.year
            month = rusage.start.month
            key = datetime(year,month,1)
            if key not in keys:
                keys.append(key)
            cost = [rusage.customcost,rusage.cost][rusage.customcost == None]
            old = sums.setdefault(resourceid,{}).setdefault(key,{})
            if include_invoiced:
                old.setdefault('invoiced', 0)
                if rusage.invoice:
                    sums[resourceid][key]['invoiced'] = old['invoiced'] + cost
            if include_total:
                old.setdefault('total', 0)
                sums[resourceid][key]['total'] = old['total'] + cost
        sums = sums.items()
        sums.sort()
        keys.sort()

        titlerow = columns
        for key in keys:
            if include_total: titlerow.append(key.strftime('%B, %Y') + ' - total')
            if include_invoiced: titlerow.append(key.strftime('%B, %Y') + ' - invoiced')
                       
        rows_ungrouped = []

        for id,monthlysum in sums:
            resource = resources[id]
            row = [resource.place.name, resource.name]
            if 'resourcetype' in columns_selection:
                row.append(resource.type)
            if 'resourceid' in columns_selection:
                row.append(resource.id)
            for key in keys:
                amounts = monthlysum.get(key, {'total':0, 'invoiced':0})
                if include_total: row.append(amounts.get('total', 0))
                if include_invoiced: row.append(amounts.get('invoiced', 0))
            rows_ungrouped.append(row)
        
        grouper = lambda row: row[2]

        rows = []

        for (rtype, grp) in reportutils.sortAndGrpby(rows_ungrouped, grouper):
            rows += list(grp)

        rows.insert(0, titlerow)

        return rows


    ##################  Resource  ####################
    @expose()
    @strongly_expire
    @identity.require(not_anonymous())
    @validate(validators={'object_id':real_int, 'res_or_tariff':v.UnicodeString(not_empty=True)})
    def load_management_page(self, tg_error=None, **kwargs):
        kwargs['section'] = "manage"+kwargs['res_or_tariff']
        return self.load_tab(**kwargs)
                
    @expose(template="hubspace.templates.manageResources")
    @identity.require(not_anonymous())
    @validate(validators={'type':v.UnicodeString(not_empty=True), 'time_based':BoolInt(if_empty=0), 'active':BoolInt(if_empty=0), 'place':real_int, 'name':v.UnicodeString(not_empty=True), 'description':v.UnicodeString(not_empty=True), 'tariffs':ForEach(Schema(cost=v.Money(not_empty=True), id=real_int))})
    def create_resource(self, tg_errors=None, **kwargs):
        """
        """
        #should have a special validator to ensure that there aren't resources without a price
        #though this should not occur unless someone is tampering with the interface


        
        if tg_errors:
            cherrypy.response.headers['X-JSON'] = 'error'
            object = Location.get(kwargs['place'])
            args = AttrDict(**kwargs)
            return self.error_template("addResource", {'object':object, 'args':args, 'tg_errors':tg_errors})
        
        if not permission_or_owner(Location.get(kwargs['place']), None, 'manage_resources'):
            raise IdentityFailure('what about not hacking the system')

        resource = create_object('Resource', **kwargs)

        if kwargs.get('tariffs'):
            for tariff in kwargs['tariffs']:
                self.create_pricing(resource=resource.id, cost=tariff['cost'], tariff=tariff['id'])
        tariffs =  Resource.select(AND(Resource.q.placeID==kwargs['place'],
                                       Resource.q.type=='tariff'))
        for tariff in tariffs:
            pricing = get_pricing(tariff, resource)
            if pricing==None:
                raise `tariff` + "  " +`resource`#"not all tariffs have prices!!"

        cherrypy.response.headers['X-JSON'] = 'success'
        return {'object': resource.place}

    @exception_handler(print_exception, "isinstance(tg_exceptions, NoSuchObject)")
    @exception_handler(print_exception, "isinstance(tg_exceptions, ResourceHasRUsages)")
    @identity.require(not_anonymous())
    @validate(validators={'name':v.UnicodeString(not_empty=True)})
    def delete_resource(self, name):
        resource = Resource.selectBy(name=name)
        if resource.count()==0:
            return NoSuchObject("No such resource as "+ name +" exists")
        resource = resource[0]
        if not permission_or_owner(resource.place,None,'manage_resources'):
            raise IdentityFailure('what about not hacking the system')

        if len(resource.usages)>0:
            raise ResourceHasUsages("Could not delete resource %(name)s. %(name)s has usages." %({'name':name}))
        for pricing in resource.prices:
            pricing.destroySelf()
        for pricing in resource.tariff_for:
            pricing.destroySelf()
        for sugg in resource.suggestions:
            resource.removeSuggestions(sugg)
        for req in resource.requires:
            resource.removeRequires(req)
        for sugg in resource.suggestedby:
            resource.removeSuggestedby(sugg)
        for req in resource.requiredby:
            resource.removeRequiredby(req)
        
        resource.destroySelf()
        return "Resource '%(name)s' has been deleted" %({'name':name})

    ##################RESOURCE GROUPS##################################

    @expose(template="hubspace.templates.manageResources")
    @strongly_expire
    @identity.require(not_anonymous())
    @validate(validators={'name':NoHyphen(not_empty=True), 'description':v.UnicodeString(not_empty=True), 'location':real_int, 'group_type':v.UnicodeString(not_empty=True)})
    def create_resource_group(self, tg_errors=None, **kwargs):

        if tg_errors:
            return self.error_template("addResourceGroup", {'kwargs':AttrDict(kwargs), 'tg_errors':tg_errors})
         
        loc = Location.get(kwargs['location'])
        if not permission_or_owner(loc, None, 'manage_resources'):
            raise IdentityFailure('what about not hacking the system')
        cherrypy.response.headers['X-JSON'] = 'success'
        group = create_object('Resourcegroup', **kwargs)
        group_order = loc.resourcegroup_order
        if not group_order:
            group_order = [0]
        group_order.append(group.id)
        loc.resourcegroup_order = group_order
        return {'object':loc}

    @expose(template="hubspace.templates.manageResources")
    @strongly_expire
    @identity.require(not_anonymous())
    @validate(validators={'group_id':real_int})
    def delete_resource_group(self, tg_errors=None, **kwargs):
        if tg_errors:
            raise "cannot delete"
        group = Resourcegroup.get(kwargs['group_id'])
        loc = group.location
        if not permission_or_owner(loc, None, 'manage_resources'):
            raise IdentityFailure('what about not hacking the system')
        for res in group.resources:
            res.resgroup = None
        group.destroySelf()
        group_order = loc.resourcegroup_order
        group_order.remove(group.id)
        loc.resourcegroup_order = group_order
        return {'object':loc}

    @expose()
    @identity.require(not_anonymous())
    @validate(validators={'group':ForEach(real_int), 'loc':real_int})
    def save_res_groups(self, tg_errors=None, **kwargs):
        loc = Location.get(kwargs['loc'])
        if not permission_or_owner(loc, None, 'manage_resources'):
            raise IdentityFailure('what about not hacking the system')
        res_group = kwargs['res_group']
        loc.resourcegroup_order = kwargs['group']
        for gr in kwargs['group']:
            if gr:
                group = Resourcegroup.get(gr)
                resource_order = str(gr) in res_group and res_group[str(gr)] or []
                group.resources_order = [int(res_id) for res_id in resource_order]
                for res in group.resources_order:
                    Resource.get(res).resgroup = group
                    
                
        return "success"
        

    @expose(template="hubspace.templates.manageTariffs") 
    @identity.require(not_anonymous())
    @validate(validators={'tariff_id':real_int})
    def set_default_tariff(self, tariff_id=None, **kwargs):

        tariff = Resource.get(tariff_id)
        if not permission_or_owner(tariff.place, None, 'manage_resources'):
            raise IdentityFailure('what about not hacking the system')
        location = tariff.place
        location.defaulttariff = tariff_id
        
        return {'object': tariff.place}
    

    @expose(template="hubspace.templates.manageTariffs") 
    @identity.require(not_anonymous())
    @validate(validators={'active':BoolInt(if_empty=0), 'place':real_int, 'name':v.UnicodeString(not_empty=True), 'description':v.UnicodeString(not_empty=True), 'tariff_cost':v.Money(not_empty=True), 'resources':ForEach(Schema(cost=v.Money(not_empty=True), id=real_int)), 'default':BoolInt(default=0)})
    def create_tariff(self, tg_errors=None, **kwargs):
        if tg_errors:
            cherrypy.response.headers['X-JSON'] = 'error'
            object = Location.get(kwargs['place'])
            args = AttrDict(**kwargs)
            return self.error_template("addTariff", {'object':object, 'args':args, 'tg_errors':tg_errors})

        if not permission_or_owner(Location.get(kwargs['place']), None, 'manage_resources'):
            raise IdentityFailure('what about not hacking the system')

        kwargs['type'] = 'tariff'
        tariff = create_object('Resource', **kwargs)
        self.create_pricing(resource=tariff.id, cost=kwargs['tariff_cost'], tariff=tariff.id)
        if kwargs['default']:
            tariff.place.defaulttariff=tariff.id
        
        if 'resources' in kwargs and kwargs['resources']:
            for resource in kwargs['resources']:
                self.create_pricing(resource=resource['id'], cost=resource['cost'], tariff=tariff.id)

        resources = Resource.select(AND(Resource.q.placeID==kwargs['place'],
                                        Resource.q.type!='tariff',
                                        Resource.q.type!='calendar'))
        for resource in resources:
            pricing = get_pricing(tariff, resource)
            if pricing==None:
                raise `tariff` + "  " +`resource`#"not all resources have prices in the tariff!!"
        cherrypy.response.headers['X-JSON'] = 'success'
        return {'object': tariff.place}


    @expose()
    @identity.require(not_anonymous())
    @validate(validators={'id':real_int, 'name':v.UnicodeString(), 'description':v.UnicodeString()})
    def save_resource_group_property(self, tg_errors=None, **kwargs):

        group = Resourcegroup.get(kwargs['id'])
        if tg_errors:
            cherrypy.response.headers['X-JSON'] = 'error'              
            return ''

        if not permission_or_owner(group.location, None, 'manage_resources'):
            raise IdentityFailure('what about not hacking the system')

        if kwargs['name']:
            prop = group.name = kwargs['name']
        elif kwargs['description']:
            group.description = kwargs['description']
            prop = publish_parts(kwargs['description'], writer_name="html")["html_body"]
            
        cherrypy.response.headers['X-JSON'] = 'success'
        return prop

    @expose()
    @identity.require(not_anonymous())
    @validate(validators={'id':real_int, 'name':v.UnicodeString(), 'description':v.UnicodeString(), 'vat':FloatInRange()})
    def save_resource_property(self, tg_errors=None, **kwargs):

        resource = Resource.get(kwargs['id'])

        if tg_errors:
            cherrypy.response.headers['X-JSON'] = 'error'
            if 'vat' in tg_errors:
                error = "<input type='text' name='vat' id='resourceVAT_%s_widget'  value='%s' /><span class='errorMessage'>%s</span>" %(kwargs['id'], kwargs['vat'], str(tg_errors['vat']))
                return resource.vat and str(resource.vat)+error or str(resource.place.vat_default) + error
                                                                       
            return ''

        if not permission_or_owner(resource.place, None, 'manage_resources'):
            raise IdentityFailure('what about not hacking the system')

        if kwargs['name']:
            prop = resource.name = kwargs['name']
        elif kwargs['description']:
            prop = resource.description = kwargs['description']
        elif 'type' in kwargs and kwargs['type']:
            prop = resource.type = kwargs['type']
        elif 'vat' in kwargs:
            resource.vat = kwargs['vat']
            prop = str(kwargs['vat'])
        
        cherrypy.response.headers['X-JSON'] = 'success'
        return prop

    @expose()
    @strongly_expire
    @identity.require(not_anonymous())
    @validate(validators={'id':real_int, 'object_type':v.UnicodeString(), 'prop_name':v.UnicodeString()})
    def load_prop(self, id, object_type, prop_name, tg_errors=None, **kwargs):
        theclass = getattr(hubspace.model, object_type)
        obj = theclass.get(id)
        return getattr(obj, prop_name)
        
    @expose()
    @identity.require(not_anonymous())
    @validate(validators={'resourceid':real_int})
    def toggle_resource_activate(self, resourceid, **kwargs):
        resource = Resource.get(resourceid)
        
        if not permission_or_owner(resource.place, None, 'manage_resources'):
            raise IdentityFailure('what about not hacking the system')

        if resource.active:
            resource.active = 0
            return """Inactive <a class="button activate" id="activeness-%s">activate</a>
                   """ %(resourceid)
        else:
            resource.active = 1
            return """Active <a class="button activate" id="activeness-%s">de-activate</a>
                   """ %(resourceid)
     
    @expose(template="hubspace.templates.moreResDetails")        
    @identity.require(not_anonymous())
    @validate(validators={'resourceid':real_int, 'requirementid':real_int})
    def add_requirement(self, resourceid, requirementid, **kwargs):
        resource = Resource.get(resourceid) 
        if not permission_or_owner(resource.place,None,'manage_resources'):
            raise IdentityFailure('what about not hacking the system')
        requirement = Resource.get(requirementid)
        if requirement not in resource.requires:
            resource.addRequirement(requirement)
        return {'resource':resource, 'requirement':requirement}

  
    @expose(template="hubspace.templates.moreResDetails")
    @validate(validators={'resourceid':real_int, 'suggestionid':real_int})
    def add_suggestion(self, resourceid, suggestionid, **kwargs):
        resource = Resource.get(resourceid)

        if not permission_or_owner(resource.place,None,'manage_resources'):
            raise IdentityFailure('what about not hacking the system')

        suggestion = Resource.get(suggestionid)
        if suggestion not in resource.suggestions:
            resource.addSuggestion(suggestion)
        return {'resource':resource, 'suggestion':suggestion}

    #XXX test security!
    @expose()
    @validate(validators={'resourceid':real_int, 'suggestionid':real_int})
    def remove_suggestion(self, resourceid, suggestionid, **kwargs):
        resource = Resource.get(resourceid)

        if not permission_or_owner(resource.place,None,'manage_resources'):
            raise IdentityFailure('what about not hacking the system')

        suggestion = Resource.get(suggestionid)
        if suggestion in resource.suggestions:
            resource.removeSuggestion(suggestion)
        return "success"

    #XXX test permission
    @expose()
    @validate(validators={'resourceid':real_int, 'requirementid':real_int})
    def remove_requirement(self, resourceid, requirementid, **kwargs):
        resource = Resource.get(resourceid)
        if not permission_or_owner(resource.place,None,'manage_resources'):
            raise IdentityFailure('what about not hacking the system')

        requirement = Resource.get(requirementid)
        if requirement in resource.requires:
            resource.removeRequirement(requirement)
        return "success"
    
    
    ##################  Group  ####################

    @expose()
    @identity.require(not_anonymous())
    @validate(validators={'place':real_int, 'level':v.UnicodeString(), 'display_name':v.UnicodeString(), 'group_name':v.UnicodeString()})
    def create_group(self, **kwargs):
        if not permission_or_owner(kwargs['place'],None,'manage_groups'):
            raise IdentityFailure('what about not hacking the system')
        group = new_group(**kwargs)         
        return `group.group_name`

    @expose()
    @identity.require(not_anonymous())
    @validate(validators={'group_name':v.UnicodeString()})
    def delete_group(self, group_name, **kwargs):
        """One can always remove a group. inevitably if you remove a group you will also remove the memberships of users to that group and the permissions which were associated with it. 
        """
        group = Group.selectBy(group_name=group_name)
        if group.count()==0:
            return "Group not Found"
        group = group[0]
        if not permission_or_owner(group.place,None,'manage_groups'):
            raise IdentityFailure('what about not hacking the system')
        #for user in group.users:
        #    group.removeUser(user)
        group_users = UserGroup.select(AND(UserGroup.q.groupID==group.id))
        for gr in group_users:
            gr.destroySelf()
        for perm in group.permissions:
            group.removePermission(perm)
        group.destroySelf()
        return 'group "'+group_name+'" deleted'

    @expose()
    @identity.require(identity.has_permission('superuser'))
    @validate(validators={'level':v.UnicodeString(), 'perm_name':v.UnicodeString()})
    def add_permission_to_all_groups_of_level(self, level, perm_name, **kwargs):
        groups = Group.select(Group.q.level==level)
        for group in groups:
            add_perm_to_group(group, perm_name)
        return ''
        

    @expose()
    @identity.require(not_anonymous())
    @validate(validators={'level':v.UnicodeString(), 'location':real_int, 'perm_name':v.UnicodeString()})
    def add_permission_to_group(self, location, level, perm_name, **kwargs):
        if not permission_or_owner(location, None,'manage_groups'):
            raise IdentityFailure('what about not hacking the system')
        group = Group.select(AND(Group.q.placeID==location.id,
                                 Group.q.level==level))[0]
        add_perm_to_group(group, perm_name)
        return ''
        
    ##################  Pricing  ####################
    @expose(template="hubspace.templates.pricingSchedule")
    @identity.require(not_anonymous())
    @validate(validators=AddPricingSchema())
    def add_pricing(self, tg_errors=None, **kwargs):
        if tg_errors:
            cherrypy.response.headers['X-JSON'] = 'error'
            kwargs['tg_errors'] = tg_errors
            return self.error_template('pricingSchedule', {'cost':kwargs['cost'], 'month':kwargs['periodstarts']['month'], 'year':kwargs['periodstarts']['year'], 'tg_errors':tg_errors})

        kwargs['periodstarts'] = datetime(int(kwargs['periodstarts']['year']), int(kwargs['periodstarts']['month']), 1, 0, 0, 1)
        self.create_pricing(**kwargs)
        cherrypy.response.headers['X-JSON'] = 'success'
        return {'object':Resource.get(kwargs['resource']), 'tariff':kwargs['tariff']}


    @identity.require(not_anonymous())
    @validate(validators={'cost':v.Money(), 'tariff':real_int, 'resource':real_int, 'periodstarts':Any(datetimeconverter, v.Empty(if_empty=datetime(1970, 1, 1)))})
    def create_pricing(self, **kwargs):

        tariff=Resource.get(kwargs['tariff'])
        if not permission_or_owner(tariff.place, None, 'manage_pricings'):
            raise IdentityFailure('what about not hacking the system')

        price = create_object('Pricing', **kwargs)

        later_pricing = Pricing.select(AND(Pricing.q.periodstarts>price.periodstarts,
                                           Pricing.q.tariffID == tariff.id,
                                           Pricing.q.resourceID == kwargs['resource'])).orderBy('periodstarts')

        if later_pricing.count()==0:
            later_pricing = None
        else:
            later_pricing = later_pricing[0]
            
        price.nextperiod = later_pricing
        price.periodends
        print "current  pricing ends...." + `price.periodends`

        
        earlier_pricing = Pricing.select(AND(Pricing.q.periodstarts<price.periodstarts,
                                             Pricing.q.tariffID == tariff.id,
                                             Pricing.q.resourceID == kwargs['resource'])).orderBy('periodstarts')
        if earlier_pricing.count()>0:
            earlier_pricing[-1].nextperiod = price
            earlier_pricing[-1].periodends
            print "earlier pricing ends...." + `earlier_pricing[-1].periodends`        

        pricing_changed_recalculate(price)
        return price

    @expose(template="hubspace.templates.pricingSchedule") 
    @identity.require(not_anonymous())
    @validate(validators={'price_id':real_int})
    def delete_pricing(self, price_id, **kwargs):
        price = Pricing.get(price_id)
        resource = price.resource.id
        tariff = price.tariff.id
        next_price = price.nextperiod
        prev_price = Pricing.select(Pricing.q.nextperiodID==price.id)[0]
        if next_price:
            prev_price.nextperiod = next_price.id
        else:
            prev_price.nextperiod = None
        prev_price.periodends
        price.destroySelf()
        return {'object':Resource.get(resource), 'tariff':tariff}
        

    @expose() 
    @identity.require(not_anonymous())
    def get_id(self,objecttype,key,value):
        theclass = getattr(hubspace.model,objecttype)
        params = {str(key):str(value)}
        r = theclass.selectBy(**params)
        return str(r[0].id)
        if len(r):
            return r[0].id
        else:
            return False

    @identity.require(not_anonymous())
    @expose(template="hubspace.templates.upload_outstanding_form")
    def upload_outstanding_form(self):
        return dict()

    #XXX how can we test this?
    @expose()
    @identity.require(not_anonymous())
    def upload_outstanding(self,csvfile):
	if not permission_or_owner(None, None, 'manage_users'):
            raise IdentityFailure('what about not hacking the system')
        reader = csv.reader(csvfile.file)
        out=[]
        for row in reader:
            tmp,id,name,outstanding, ignore = row
            result = User.selectBy(id=id)
            if result.count():
                user = result[0]
                user.outstanding = float(outstanding)
                out.append('set user %s (%s) to %s' % (id,user.user_name,user.outstanding))
        return  'Updated!<br /><br />'+ '<br />'.join(out)
    
    @expose()
    @strongly_expire
    @identity.require(not_anonymous())
    def parse_print_file(self):
        if not permission_or_owner(None, None, 'manage_users'):
            raise IdentityFailure('what about not hacking the system')
        #try:
        parse_print_file()
        send_unknown_aliases()
        return 'success'
        #except:
        #    return 'failure'

    @expose()
    @strongly_expire
    @identity.require(not_anonymous())
    def send_unknown_aliases(self):
        if not permission_or_owner(None, None, 'manage_users'):
             raise IdentityFailure('what about not hacking the system')
        send_unknown_aliases()
        return 'success'

    @expose()
    @strongly_expire
    @identity.require(identity.has_permission("superuser"))
    def update_tariff_bookings(self):
        update_tariff_bookings()
        return "success"
        
    #######################Policy Groups############################    
    @expose(allow_json=True)
    @strongly_expire
    @validate(validators={'name':v.UnicodeString(), 'description':v.UnicodeString(), 'loc_id':real_int})
    def create_policy_group(self, name, description="", loc_id=None):
        try:
            location = Location.get(loc_id)
        except:
            raise "policy group can only exist in a location (non-given)"
        if not permission_or_owner(location, None, 'manage_users'):
            raise IdentityFailure('what about not hacking the system')
        policy_group = add_policy_group(name, description, location)
        return {'policy_group': policy_group}

    @expose(allow_json=True)
    @strongly_expire
    @validate(validators={'id':real_int})
    def remove_policy_group(self, id):
        pol_group = PolicyGroup.get(id)
        if not permission_or_owner(pol_group.place, None, 'manage_users'):
            raise IdentityFailure('what about not hacking the system')
        remove_policy_group(pol_group)
        return {'policy_group_removed': id}

    @expose(allow_json=True)
    @strongly_expire
    @validate(validators={'polgroup_id':real_int, 'user_id':real_int})
    def add_user2policy_group(self, polgroup_id, user_id):
        group = PolicyGroup.get(polgroup_id)
        if not permission_or_owner(group.place, None, 'manage_users'):
            raise IdentityFailure('what about not hacking the system')
        add_users2policy_group(group, [user_id])
        return str(user_id)

    @expose(allow_json=True)
    @strongly_expire
    @validate(validators={'polgroup_id':real_int, 'user_id':real_int})
    def remove_user2policy_group(self, polgroup_id, user_id):
        group = PolicyGroup.get(polgroup_id)
        if not permission_or_owner(group.place, None, 'manage_users'):
            raise IdentityFailure('what about not hacking the system')
        remove_users2policy_group(group, [user_id])
        return str(user_id)

    ###################### Access Policies ########
    @expose(allow_json=True)
    @strongly_expire
    @validate(validators={'policyResource_id':real_int, 'policyProxy_id':real_int, 'policyProxy_type':v.String(), 'policyStartDate':Any(dateconverter, v.Empty()), 'policyEndDate':Any(dateconverter, v.Empty()), 'precedence':v.Int(if_empty=5)})
    def add_accessPolicy2Proxy(self, policyResource_id=None, policyProxy_id=None, policyProxy_type=None, precedence=5, policyStartDate=None, policyEndDate=None):
        """a policy proxy is an object which can be referenced from an accesspolicy so that under certain conditions a user will be given access to it. e.g. if a user joins a group she would get the access policies associated with that group(proxy).
        The policy_resource is the resource to which access is controlled by the policy.
        """
        policyResource = Resource.get(policyResource_id)
        print "add policy 2 proxy" + `policyResource.name`
        return str(add_accessPolicy2Proxy(policyResource, policyProxy_id, policyProxy_type, precedence, policyStartDate, policyEndDate))

    @expose(allow_json=True)
    @strongly_expire
    @validate(validators={'id':real_int})
    def remove_accessPolicy2Proxy(self, id):
        return str(remove_accessPolicy2Proxy(id))

    ###################### Opening Times #################
    @expose()
    @strongly_expire
    @identity.require(not_anonymous())
    @validate(validators={'user_id':real_int, 'loc_id':real_int, 'policyResource_id':real_int, 'check_datetime':datetimeconverter})
    def check_access(self, user_id=None, loc_id=None, policyResource_id=None, check_datetime=None):
        """Mainly just for testing right now.
        """
        user = User.get(user_id)
        policy_resource = Resource.get(policyResource_id)
        allowed = check_access(user, policy_resource, check_datetime)
        if allowed:
            print "Allowed"
            return "Allowed"
        print "Not Allowed"
        return ""
        

    @expose()
    @strongly_expire
    @identity.require(not_anonymous())    
    @validate(validators={'pol_id':real_int, 'openTimeDay':Any(v.Int(), v.Empty()), 'openTimeStartDate':Any(dateconverter, v.Empty()), 'openTimeDate':Any(dateconverter, v.Empty()),  'openTimeStart':timeconverterAMPM, 'openTimeEnd':timeconverterAMPM})
    def create_openTime(self, pol_id, openTimeDay=None, openTimeStartDate=None, openTimeDate=None, openTimeStart=None, openTimeEnd=None):
        #XXX check for already existing duplicate opentimes on the access_policy e.g. same openTimeDate, or same openTimeStartDate and same openTimeDay
        if not permission_or_owner(AccessPolicy.get(pol_id).location, None, 'manage_users'):
            raise IdentityFailure('what about not hacking the system')
        open_time = create_openTime(pol_id, openTimeDay, openTimeStartDate, openTimeDate, openTimeStart, openTimeEnd)
        return `open_time.id`

    @expose()
    @strongly_expire
    @identity.require(not_anonymous())
    @validate(validators={'id':real_int})
    def delete_openTime(self, id=None):
        if not permission_or_owner(Open.get(id).policy.location, None, 'manage_users'):
            raise IdentityFailure('what about not hacking the system')
        return delete_openTime(id)
    
    @expose()
    @strongly_expire
    @identity.require(not_anonymous())    
    @validate(validators={'loc_id':real_int, 'date':dateconverter, 'cal_end':timeconverterAMPM, 'cal_start':timeconverterAMPM})
    def save_openTime(self, loc_id=None, date=None, cal_end=None, cal_start=None, value="", id=0):
        if not permission_or_owner(Location.get(loc_id), None, 'manage_users'):
            raise IdentityFailure('what about not hacking the system')
        edit_openTime()
        return `open_time`


    @expose()
    @strongly_expire
    @identity.require(not_anonymous())
    @validate(validators={'policy_id':real_int, 'date':dateconverter})
    def load_openTime(self, policy_id, date):
        policy = AccessPolicy.get(policy_id)
        if not permission_or_owner(policy.location, None, 'manage_users'):
            raise IdentityFailure('what about not hacking the system')
        times = get_times_from_policies([policy])

        # needs some work
        json_times = [[timeconverterAMPM.from_python(time), timeconverterAMPM.from_python(time.t_close)] for time in times]
        #our widgets aren't currently capable of dealing with json so we use a text-format instead
        text_times = ' + '.join(['-'.join(json) for json in json_times])
        #js and ui only deal with single opening time per date (so far)
        return text_times

