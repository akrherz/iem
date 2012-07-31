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

EMAILS = ['labend@iastate.edu','akrherz@iastate.edu']
if len(sys.argv) == 2:
    EMAILS = ['akrherz@iastate.edu',]

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

html = """
<h3>CSCAP Documents/Spreadsheet Changes</h3>
<br />
<p>Period: 7 AM %s - 7 AM %s
<p>Changestamp In: %s

<p><table border="1" cellpadding="3" cellspacing="0">
<thead>
<tr><th>Time</th><th>Author</th><th>Resource</th></tr>
</thead>
<tbody>
""" % (yesterday.strftime("%d %B %Y"), today.strftime("%d %B %Y"), changestamp)

loopcount = 0
while 1:
    loopcount += 1
    print '%s Get Feed changestamp: %s' % (loopcount, changestamp)
    feed = docs_client.get_changes(expand_acl=True, changestamp=changestamp)
    count = 0
    for entry in feed.entry:
        count += 1
        link = entry.get_html_link()
        if link:
            uri = link.href
        else:
            uri = '#'
        updated = mx.DateTime.strptime(entry.updated.text[:16], '%Y-%m-%dT%H:%M')
        changestamp = max(int(entry.changestamp.value) +1, changestamp)
        if updated < yesterday:
            print 'Old changestamp of: %s thres: %s' % (updated, yesterday)
            continue
        updated = updated.localtime()
        author = "N/A"
        if entry.last_modified_by:
            author = entry.last_modified_by.email.text
        html += "<tr><td>%s</td><td>%s</td><td><a href=\"%s\">%s</a></td></tr>" % (
            updated.strftime("%-I:%M %P"), author, uri, entry.title.text)
        #if entry.filename:
        #    print entry.filename.text
        #print entry.changestamp.value
    if count == 0 or loopcount == 10:
        break

config.set('memory', 'changestamp', changestamp +1)
config.write( open('mytokens.cfg', 'w'))

html += """</tbody></table>

<p>Changestamp out: %s
<p>That is all...""" % (changestamp,)
msg = MIMEMultipart('alternative')
msg['Subject'] = "CSCAP Data ChangeLog"
msg['From'] = 'mesonet@mesonet.agron.iastate.edu'
msg['To'] = ','.join(EMAILS)


# Create the body of the message (a plain-text and an HTML version).
text = "See html variant"
# Record the MIME types of both parts - text/plain and text/html.
part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')

msg.attach(part1)
msg.attach(part2)

s = smtplib.SMTP('mailhub.iastate.edu')
s.sendmail(msg['From'], EMAILS, msg.as_string())
s.quit()


