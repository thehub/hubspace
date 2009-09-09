from pyjamas.JSONService import JSONProxy

class LocalhostProxy(JSONProxy):
    def __init__(self):
        JSONProxy.__init__(self, "/rpc/", ["get_messagecustdata", "customize_message", "get_messagesdata_for_cust"])

server = LocalhostProxy()


