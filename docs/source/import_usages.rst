===========================
API: Bulk usages import API
===========================

Importing bulk usages in Hubspace using APIs is two stage process.

Authenticate and create a session
---------------------------------

API: verify_credentials

Patameters: username, password

Usage: :doc:`Find documentation here </connect>`

Importing usages in hubspace
----------------------------


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

    import sys
    import requests
    
    domain = 'https://members.the-hub.net/'
    auth_url = domain + 'verify_credentials'
    import_url = domain + 'import_usages'
    
    creds = dict(username='clarkkent', password='secret')
    s = requests.session()
    r = s.post(auth_url, creds)
    authenticated = r.json['authenticated']
    
    if not authenticated:
        print ('Login failed')
        sys.exit(1)
    else:
        print ('Login successful')
    
    usages_data = [
        dict(member=1209, resource=103, start='2012-04-01 09:30:00', quantity=10),
        dict(member=1589, resource=107, start='2012-04-07 11:00:00', end='2012-04-01 12:30:00')
    ]
    
    s.post(import_url, usages_data)

