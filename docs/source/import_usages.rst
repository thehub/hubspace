===========================
API: Bulk usages import
===========================

Importing bulk usages in Hubspace using APIs is two stage process.

API: import_usages

Patameters:
    usages: List of usage objects

    Usage object fields
    
    - start: Usage start time in ISO 8601 format. eg. 2012-04-01T09:30:00
    - end: Usage end time in ISO 8601 format. Optional in case of quantity based resources.
    - resource: Resource ID
    - cost: Optional field. Data type: float.
    -     Specify custom cost if any. Omit this field if you want serve to calculate the cost
    - member: Member id
    - quantity: Optional. Data type integer.

    Data Example::

        [
            {'member': 1209, 'resource': 103, 'start': '2012-04-01T09:30:00', 'quantity': 10},
            {'member': 1589, 'resource': 107, 'start': '2012-04-07T11:00:00', 'end': '2012-04-01T12:30:00'}
        ]

.. Note::
   HTTP header "Content-Type" should be set to 'application/json' while making the request.

Return:

    Return value is an object containing key `result`.

    Value of result is an array. Array element could be an integer or null. Integer represents id of usage created in the system. null indicates failure to import usage at same position in `usages` value.

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

    # Jsonify data
    data = simplejson.dumps(usages_data)
    
    r = s.post(import_url, data, headers={'Content-Type':'application/json'}) # HTTP POST
    print r.json
