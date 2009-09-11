import sendmail
import logging
import messages

applogger = logging.getLogger("hubspace")

def sendTextEmail(message_name, location=None, data={}, extra_data={}, to=None, cc=None, sender=None, notifydevonfailure=True):
    message = messages.bag[message_name]
    message_dict = message.make(location, data, extra_data)
    sender = sender or message_dict['sender']
    to = to or message_dict['to']
    cc = cc or message_dict.get('cc')
    subject = message_dict['subject']
    body = message_dict['body']
    try:
        sendmail.sendmail(to, cc=cc, sender=sender, subject=subject, body=body)
    except Exception, err:
        applogger.exception("alertslib failure")
        # TODO
        #if notifydevonfailure:
        #    sendTextEmailAlert("notify_dev", False)

if __name__ == '__main__':
    sendTextEmail("shon@localhost", "booking_cancellation", dict(resource_name="some room"))
