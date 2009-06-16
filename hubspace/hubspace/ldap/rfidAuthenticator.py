import ldap
import datetime

uri = "ldap://ldap.the-hub.net"
#uri = "ldap://localhost"
localuserdn = "uid=%(uid)s,ou=users,hubId=%(hubId)s,ou=hubs,o=the-hub.net"
basedn = "o=the-hub.net"
hubdn = "hubId=%(hubId)s,ou=hubs," + basedn
leveldn = "level=%(level)s,ou=roles," + hubdn
accesspolicydn = "policyId=%(policyId)s,ou=policies," + hubdn
opentimedn = "openTimeId=%(openTimeId)s," + accesspolicydn
policiesbase = "ou=policies" + hubdn

class LDAPAttrs2Obj(object):
    def __init__(self, d):
        assert isinstance(d, dict), "just dict please"
        new_d = dict ()
        for (k,v) in d.items():
            if isinstance(v, list) and len(v) == 1:
                v = v[0]
            if isinstance(v, str) and v.isdigit():
                v = int(v)
            new_d[k] = v
        self.__dict__.update(new_d)
    def __str__(self):
        ret = getattr(self, "dn")
        if not ret:
            ret = str(dict([(k,v) for (k,v) in self.__dict__.items() if k[0] is not "_"]))
        return ret
    def __repr__(self):
        return self.__str__()
    def __getattr__(self, attr):
        return

class MyDateTime(datetime.datetime):
    def __str__(self):
        return self.strftime("%Y%m%d%H%M%S") + '+0000'
    def date(self):
        return MyDateTime(*datetime.datetime.date(self).timetuple()[:3])

def ldapSafe(x):
    if isinstance(x, unicode):
        x = x.encode('utf-8') # http://www.mail-archive.com/python-ldap-dev@lists.sourceforge.net/msg00040.html
    elif isinstance(x, (bool, int, long)):
        x = str(int(x))
    elif x == None:
        x = ''
    elif isinstance(x, (datetime.date, datetime.time)):
        try:
            x = x.strftime("%Y%m%d%H%M%S") + '+0000'
        except ValueError:
            if isinstance(x, datetime.date):
                x = "%s%s%s000000+0000" % (str(x.year).zfill(4), str(x.month).zfill(2), str(x.day).zfill(2))
            elif isinstance(x, datetime.time):
                x = "00000000%s%s%s+0000" % (str(x.hour).zfill(2), str(x.minute).zfill(2), str(x.second).zfill(2))
            else:
                raise
    elif isinstance(x, (list, tuple)):
        x = [ldapSafe(i) for i in x if i]
    return x

def getLDAPObj(conn, dn):
    rdn, basedn = dn.split(',', 1)
    d = conn.search_s(basedn, ldap.SCOPE_ONELEVEL, '(%s)' % rdn, ['*'])[0][1]
    d['dn'] = dn
    return LDAPAttrs2Obj(d)

class AccessChecker(object):
    def __init__(self, u, p):
        self.conn = ldap.ldapobject.ReconnectLDAPObject(uri)
        self.conn.simple_bind_s(u, p)
    
    def reinitialize(self, u, p):
        self.__init__(u, p)

    def check_from_token(self, token, hubId, resourceId, check_datetime):#
        # TODO make this use the rfid token, instead of user id
        check_datetime = MyDateTime( *check_datetime.timetuple()[:7] )
        base = "ou=users," + basedn
        searchfilter = '(&(objectClass=hubGlobalUser)(hubUserRFID=%s))' % token
        uid = self.conn.search_s(base, ldap.SCOPE_ONELEVEL, searchfilter, ['uid'])[0][1]['uid'][0]

        if not uid:
            return "unknown_token"

        if self.check(uid, hubId, resourceId, check_datetime):
            return "succes"
        else:
            return "failure"

    def check(self, uid, hubId, resource_id, check_datetime):
        check_datetime = MyDateTime( *check_datetime.timetuple()[:7] )
        userdn = localuserdn % locals()
        user = getLDAPObj(self.conn, userdn)
        times = self.get_times(resource_id, hubId, check_datetime.date(), user)
        for time in times:
            if ldapSafe(check_datetime.time()) >= time[0] and ldapSafe(check_datetime.time()) <= time[1]:
                return True
        return False
    
    def get_times(self, resource_id, hubId, check_date, user=None, role=None, combined=True):
        if user:
            available_policies = user.policyReference
        elif role:
            available_policies = role.policyReference
        available_policies = [p.split(",")[0].split('=')[1] for p in available_policies]
    
        policies = self.get_applicable_accessPolicies(resource_id, hubId, check_date, available_policies)
        policies = self.filter_policy_precedence(policies)
        times = self.get_times_from_policies(hubId, policies)
        if combined:
            times = self.combine_times(times)
        if not times:
            #ensure that if the user doesn't have any access policies the calendar can still be rendered but the user cannot book
            times.append((datetime.time(9,00), datetime.time(8,59)))
        return times
       
    def get_applicable_accessPolicies(self, resource_id, hubId, check_date, available_policies):
        """Get all the access_policies which apply (in the location, for the domain, at the specified datetime).
        """            
        day_code = check_date.weekday()
        holiday = 8 #day 8 doesn't exist
        place = getLDAPObj(self.conn, hubdn % locals())
        if place.holidays and check_date in place.holidays:
            holiday = 7
        basedn = policiesbase % locals()

        # Search 1
        available_policies = "".join("(policyId=%s)" % p for p in available_policies)
        policy_filter = """
        (&
            (objectClass=hubLocalPolicy)
            (policyResource=%(resource_id)s)
            (policyStartDate<=%(check_date)s)
            (policyEndDate>=%(check_date)s)
            (| %(available_policies)s )
        )
        """ % locals()
        searchfilter = policy_filter.replace("\n","").strip()
        search = self.conn.search_s("ou=hubs,o=the-hub.net", ldap.SCOPE_SUBTREE, searchfilter,['policyId'])
        policyref_filters = "".join(["(policyReference=%s)" % s[0] for s in search])

        # Search 2
        open_filter = """
        (&
            (objectClass=hubLocalOpenTime)
            (| %(policyref_filters)s )
            (|
                (&
                    (|
                        (openTimeDay=%(holiday)s)
                        (openTimeDay=%(day_code)s)
                    )
                    (openTimeStartDate<=%(check_date)s)
                )
                (openTimeStartDate=%(check_date)s)
            )
        )
        """ % locals()
        searchfilter = open_filter.replace("\n","").strip()

        search = self.conn.search_s("ou=hubs,o=the-hub.net", ldap.SCOPE_SUBTREE, searchfilter,['policyReference'])
        applicable_policies = [res[1].values()[0][0] for res in search]

        ret = [getLDAPObj(self.conn, dn) for dn in applicable_policies]
        return ret
        
    def filter_policy_precedence(self, policies):
        """We throw away any AccessPolicies which are not of the highest precendence present.
        """
        max_precendence = 11 #max precedence is 1 min precedence is 10
        new_policies = []
        for pol in policies:
            pol_precedence = int(pol.policyPrecedence)
            if pol_precedence < max_precendence:
                max_precendence = pol_precedence
                new_policies = [pol]
            elif pol_precedence == max_precendence:
                new_policies.append(pol)
            else:
                pass
        return new_policies
    
    def get_times_from_policies(self, hubId, policies):
        """Evaluate the times from each AccessPolicy (of equal precedence). Within an AccessPolicy a date entry, will override a holiday, will override a day entry. Filter out any day entries which are not the newest for their policy.  
        """
        policy_times = {}
        for pol in policies:
            date_times = []
            holiday_times = []
            day_times = []
            dn = pol.dn
            searchfilter = "(&(objectClass=hubLocalOpenTime)(policyReference=%s))" % dn
            open_times = [LDAPAttrs2Obj(res[1]) for res in self.conn.search_s(dn, ldap.SCOPE_SUBTREE, searchfilter,['*'])]
            for time in open_times:
                if time.openTimeDay in range(0,7):
                    day_times.append(time)
                elif time.openTimeDay == 7:
                    holiday_times.append(time)
                elif isinstance(time.openTimeDate, datetime.date):
                    date_times.append(time)
                else:
                    pass
                
            if date_times:
                policy_times[pol.policyId] = date_times
            elif holiday_times:
                policy_times[pol.policyId] = holiday_times
            elif day_times:
                min_date = ldapSafe(datetime.date.min)
                filtered_day_times = []
                for time in day_times:
                    if time.openTimeStartDate > min_date:
                        min_date = time.openTimeStartDate
                        filtered_day_times = [time]
                    elif time.openTimeStartDate == min_date:
                        filtered_day_times.append(time)
                policy_times[pol.policyId] = filtered_day_times
            else:
                pass
        return policy_times

    def combine_times(self, policy_times):
        """We now combine times from all access_policies additively.
        """
        all_times = []
        for pol, times in policy_times.iteritems():
            all_times.extend(times)
        all_times.sort(lambda x, y: cmp(x.openTimeStart, y.openTimeStart))
        new_times = []
        for time in all_times:
            start_time = time.openTimeStart
            end_time = time.openTimeEnd
            if new_times==[] or start_time > new_times[-1][1]:
                new_times.append([start_time, end_time])
            elif start_time <= new_times[-1][1] and end_time > new_times[-1][1]:
                new_times[-1][1] = end_time
            else:
                pass
        return new_times


if __name__ == '__main__':
    checker = AccessChecker("uid=ldapadmin,o=the-hub.net", 'secret')
    hub = getLDAPObj(checker.conn, hubdn % dict(hubId="1"))
    user = getLDAPObj(checker.conn, localuserdn % dict(uid="salfield", hubId="1"))
    guser = getLDAPObj(checker.conn, user.hubUserReference)
    check_date = datetime.datetime(2008, 10, 15, 17, 22, 22)
    print checker.check("salfield", 1, 268, check_date)
    print checker.check_from_token("123", 1, 268, check_date)
