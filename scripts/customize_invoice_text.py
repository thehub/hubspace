import os.path
import glob
import polib

import hubspace.utilities.i18n as i18n
import hubspace.model as model

invoice_mail_text =  """
Dear %(first_name)s,

Please find your Hub invoice attached.

If you have any questions, please don't hesitate to contact The Hub's hosting team on %(location_name)s.hosts@the-hub.net or %(telephone)s.

We would always welcome your feedback and ideas on how we can improve your experience here.

Thank you for being part of The Hub.

The Hosting Team
"""

def make_location_po_map():
    return ((i18n.get_po_path(location), location) for location in model.Location.select())

def make_cust_map():
    d = {}
    for pofile, location in make_location_po_map():
        if os.path.exists(pofile):
            po = polib.pofile(pofile)
            entry = po.find(invoice_mail_text)
            if entry.msgstr:
                d[location] = entry.msgstr
    return d

def send_cust_to_db(location, text):
    msgname = "invoice_mail"
    model.MessageCustomization(message=msgname, location=location, lang=location.locale, text=text)

def run():
    macros_map = {
            '%(first_name)s': '${MEMBER_FIRST_NAME}',
             '%(last_name)s': '${MEMBER_LAST_NAME}',
             '%(location_name)s': '${LOCATION}',
             '%(telephone)s': '${LOCATION_PHONE}' }
    cust_map = make_cust_map()
    for location, text in cust_map.items():
        print "Sending customization to db: ", location.name
        for old, new in macros_map.items():
            text = text.replace(old, new)
        send_cust_to_db(location, text)

run()
