===================
API: List Resources
===================

List resources for specified Hub

API: list_resources

Parameters:

    - place_id: ID for Hub <int>

Return:
    
    Return value is an object containing key `result`.
    Value of result is an array of resource objects.
    Resource object contains following keys
    - id <int>
    - active <int 1|0>
    - name <string>

Python Example::
    
    import requests
    
    domain = 'https://members.the-hub.net/'
    auth_url = domain + 'authenticate'
    list_url = domain + 'list_resources'
    place_id = 12
    
    creds = dict(username='clarkkent', password='secret')
    s = requests.session()
    r = s.post(auth_url, creds) # HTTP POST
    authenticated = r.json['authenticated']
    
    params = dict(place_id=place_id)
    r = s.post(list_url, params) # HTTP POST
    print r.json
