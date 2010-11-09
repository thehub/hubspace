Hub Connect
===========

Hub connect exposes basic hubspace credential check to verify against hubspace user database. And thus allows possible integration for third party utilities.

It's a http call that returns following in json format. The return value contains a key "tg_flash" which is safe to ignore.

Success
    {"authenticated": true, "tg_flash": null}

Failure
    {"authenticated": false, "tg_flash": null}


Example code
------------

Python::

    import urllib2, urllib
    
    url = "https://members.the-hub.net/verify_credentials"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = dict (username = "shon", password = "secret" )
    req = urllib2.Request(url, headers=headers,  urllib.urlencode(data))
    response = urllib2.urlopen(req)
    print response.read()

