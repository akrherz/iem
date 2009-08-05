# Make sure the database server is up!

import pg, smtplib
from email.mime.text import MIMEText

try:
  pgconn = pg.connect('postgis', 'iemdb')
except:
  msg = MIMEText("IEMDB DOWN!")
  msg['From'] = 'akrherz@iastate.edu'
  msg['To'] = '5154519249@messaging.sprintpcs.com'
  s = smtplib.SMTP('mailhub.iastate.edu')
  s.sendmail(msg['From'], [msg['To']], msg.as_string())
  s.quit()
