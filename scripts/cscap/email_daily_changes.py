"""
 Print out changes feed
"""
import gdata.spreadsheets.client
import gdata.spreadsheets.data
import gdata.docs.data
import gdata.docs.client
import gdata.gauth
import re
import ConfigParser
import sys
import util
import mx.DateTime
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

today = mx.DateTime.now()
yesterday = today + mx.DateTime.RelativeDateTime(days=-1, hour=12, minute=0)

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

token = gdata.gauth.OAuth2Token(client_id=config.get('appauth','client_id'),
                                client_secret=config.get('appauth', 'app_secret'),
                                user_agent='daryl.testing',
                                scope=config.get('googleauth', 'scopes'),
                                #access_token=config.get('googleauth', 'access_token'),
                                refresh_token=config.get('googleauth', 'refresh_token'))

spr_client = gdata.spreadsheets.client.SpreadsheetsClient()
token.authorize(spr_client)

docs_client = gdata.docs.client.DocsClient()
token.authorize(docs_client)

changestamp = int(config.get('memory', 'changestamp'))
feed = docs_client.get_changes(expand_acl=True, changestamp=changestamp)

html = """
<h3>CSCAP Documents/Spreadsheet Changes</h3>
<br />
<p>Period: 7 AM %s - 7 AM %s

<p><table border="1" cellpadding="3" cellspacing="0">
<thead>
<tr><th>Time</th><th>Author</th><th>Resource</th></tr>
</thead>
<tbody>
""" % (yesterday.strftime("%d %B %Y"), today.strftime("%d %B %Y"))


for entry in feed.entry:
    uri = entry.get_html_link().href
    updated = mx.DateTime.strptime(entry.updated.text[:16], '%Y-%m-%dT%H:%M')
    if updated < yesterday:
        continue
    updated = updated.localtime()
    author = "N/A"
    if entry.last_modified_by:
        author = entry.last_modified_by.email.text
    changestamp = int(entry.changestamp.value)
    html += "<tr><td>%s</td><td>%s</td><td><a href=\"%s\">%s</a></td></tr>" % (
        updated.strftime("%-I:%M %P"), author, uri, entry.title.text)
    #if entry.filename:
    #    print entry.filename.text
    #print entry.changestamp.value

config.set('memory', 'changestamp', changestamp +1)
config.write( open('mytokens.cfg', 'w'))

html += """</tbody></table>

<p>That is all..."""

msg = MIMEMultipart('alternative')
msg['Subject'] = "CSCAP Data ChangeLog"
msg['From'] = 'mesonet@mesonet.agron.iastate.edu'
msg['To'] = 'labend@iastate.edu,akrherz@iastate.edu'


# Create the body of the message (a plain-text and an HTML version).
text = "See html variant"
# Record the MIME types of both parts - text/plain and text/html.
part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')

msg.attach(part1)
msg.attach(part2)

s = smtplib.SMTP('localhost')
s.sendmail(msg['From'], ['akrherz@localhost', 'akrherz2@localhost'], msg.as_string())
s.quit()

