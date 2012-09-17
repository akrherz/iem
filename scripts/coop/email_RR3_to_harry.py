"""
Run at Friday afternoon and email harry 
"""
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
import mx.DateTime
import os
import iemdb
AFOS = iemdb.connect('afos', bypass=True)
acursor = AFOS.cursor()

now = mx.DateTime.now()
sts = now + mx.DateTime.RelativeDateTime(days=-7,hour=0)

acursor.execute("""
  SELECT data, source from products where pil in ('RR3DMX','RR3DVN','RR3ARX','RR3FSD',
  'RR3OAX','RR1FSD') and entered > '%s' ORDER by entered ASC
""" % (sts.strftime("%Y-%m-%d %H:%M"), ))

WFOS = ['KDMX', 'KARX', 'KDVN', 'KFSD', 'KOAX']
files = {}
for wfo in WFOS:
    files[wfo] = open('/tmp/%sRR3.txt' % (wfo,), 'w')

for row in acursor:
    files[row[1]].write( row[0].replace("\001", "") )
    files[row[1]].write("\n")

for wfo in WFOS:
    files[wfo].close()

msg = MIMEMultipart()
msg['Subject'] = 'NWS RR3 Data for %s - %s' % (sts.strftime("%d %b %Y"), 
                                               now.strftime("%d %b %Y"))
msg['From'] = 'akrherz@iastate.edu'
msg['To'] = 'Harry.Hillaker@iowaagriculture.gov'
#msg['To'] = 'akrherz@localhost'
msg.preamble = 'RR3 Report'

fn = "RR3-%s-%s.txt" % (sts.strftime("%Y%m%d"), now.strftime("%Y%m%d"))

for wfo in WFOS:
    fp = open('/tmp/%sRR3.txt' % (wfo,), 'rb')
    b = MIMEBase('Text', 'Plain')
    b.set_payload(fp.read())
    encoders.encode_base64(b)
    fp.close()
    b.add_header('Content-Disposition', 'attachment; filename="%s-%s"' % (wfo,
                                                                          fn))
    msg.attach(b)
    os.unlink('/tmp/%sRR3.txt' % (wfo,))

# Send the email via our own SMTP server.
s = smtplib.SMTP('localhost')
s.sendmail(msg['From'], msg['To'], msg.as_string())
s.quit()
