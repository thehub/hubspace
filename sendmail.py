import smtplib, os
from email import Encoders
from email.Message import Message
from email.MIMEAudio import MIMEAudio
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEImage import MIMEImage
from email.MIMEText import MIMEText
from cStringIO import StringIO
from email.Generator import Generator
import sys
from turbogears import config

def sendmail(to,sender,subject,body,attachments=None, cc=None):
    '''Sends away a mail with optional attachments using smtplib. This should be fired off in a new process / thread to avoid waiting for mail server
       attachments: [('filename','content of first attachment','mime/type'),...]'''
    if not attachments:
        attachments = []

    outer = MIMEMultipart()
    outer.set_charset('utf-8')

    if cc is None:
        cc = ''
    outer['To'] = to
    outer['From'] = sender    
    outer['Cc'] = cc
    outer['Subject'] = subject.encode('utf-8')
    outer.preamble = 'the holy preamble'
    attachments.insert(0,['',body,'text/plain'])
    for filename,content,mimetype in attachments:
        maintype, subtype = mimetype.split('/', 1)
        if maintype == 'text':
            # Note: we should handle calculating the charset
            try:
	        content = content.encode('utf-8')
            except UnicodeDecodeError:
                #the incoming content might already encoded at utf-8
                pass
            msg = MIMEText(content, _subtype=subtype)
            msg.set_charset('utf-8')
        elif maintype == 'image':
            msg = MIMEImage(content, _subtype=subtype)
        elif maintype == 'audio':
            msg = MIMEAudio(content, _subtype=subtype)
        else:
            msg = MIMEBase(maintype, subtype)
            msg.set_payload(content)
            # Encode the payload using Base64
            Encoders.encode_base64(msg)
        # Set the filename parameter
        if filename:
	    msg.add_header('Content-Disposition', 'attachment', filename=filename)
        outer.attach(msg)
    mail_server = config.get('hubspace.mail')

    if mail_server:
        server = smtplib.SMTP(mail_server) #this bit should actually fire off 
    else:
        return
    fp = StringIO()
    g = Generator(fp)
    g.flatten(outer)
    final = fp.getvalue()
    to = [to]
    if cc:
	to.append(cc)
    try:
        server.sendmail(sender, to, final)
    except smtplib.SMTPRecipientsRefused:
        print "SMTP RECIPIENT REFUSED"
    server.quit()
