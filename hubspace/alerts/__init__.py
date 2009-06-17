import os.path
import string
import compiler
import sendmail
import logging

applogger = logging.getLogger("hubspace")
tmpl_dir = "%s/templates" % (os.path.abspath(os.path.dirname(__file__)))

def sendTextEmail(to, tmpl_name, data, cc=None, sender=None, notifydevonfailure=True):
    tmpl_path = os.path.join(tmpl_dir, tmpl_name)
    if os.path.isfile(tmpl_path):
        tmpls = readConfigSafe(tmpl_path)
        body = string.Template(tmpls['body']).safe_substitute(data)
        sender = sender or tmpls['sender']
        try:
            sendmail.sendmail(to, sender=sender, subject=tmpls['subject'], body=body)
        except Exception, err:
            applogger.exception("alertslib failure")
    else:
        applogger.error("Template not found: %s" % tmpl_name)
        # TODO
        #if notifydevonfailure:
        #    sendTextEmailAlert("notify_dev", False)

def readConfigSafe(path):
    ast = compiler.parseFile(path)
    d = dict()
    for x in ast.asList()[1].asList():
        name = x.asList()[0].name
        if hasattr(x.asList()[1], "value"): value = x.asList()[1].value
        else: value = [n.value for n in x.asList()[1].nodes]
        d[name] = value
    return d

if __name__ == '__main__':
    sendTextEmail("shon@localhost", "booking_cancellation", dict(resource_name="some room"))
