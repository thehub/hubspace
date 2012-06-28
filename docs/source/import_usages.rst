===========================
API: Bulk usages import
===========================

Importing bulk usages in Hubspace using APIs is two stage process.

API: import_usages

Patameters:
    usages: List of usage objects

    Usage object fields
    
    - start: Usage start time
    - end: Usage end time. Optional in case of quantity based resources.
    - resource: Resource ID
    - cost: Optional field. Data type: float.
    -     Specify custom cost if any. Omit this field if you want serve to calculate the cost
    - member: Member id
    - quantity: Optional. Data type integer.

Data Example::

    [
        {'member': 1209, 'resource': 103, 'start': '2012-04-01 09:30:00', quantity: 10},
        {'member': 1589, 'resource': 107, 'start': '2012-04-07 11:00:00', 'end': '2012-04-01 12:30:00'}
    ]

Full Python example
-------------------

::

    import requests
    
    domain = 'https://members.the-hub.net/'
    auth_url = domain + 'authenticate'
    import_url = domain + 'import_usages'
    
    # 1. Authenticate and create a session
    creds = dict(username='clarkkent', password='secret')
    s = requests.session()
    r = s.post(auth_url, creds) # HTTP POST
    authenticated = r.json['authenticated']
    
    # 2. Importing usages in hubspace
    usages_data = [
        dict(member=1209, resource=103, start='2012-04-01 09:30:00', quantity=10),
        dict(member=1589, resource=107, start='2012-04-07 11:00:00', end='2012-04-01 12:30:00')
    ]
    
    r = s.post(import_url, usages_data) # HTTP POST
    print r.json
