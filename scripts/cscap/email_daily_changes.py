"""
  My purpose in life is to send an email each day with changes found
  on the Google Drive
"""
import ConfigParser
import sys
import util
import datetime
import pytz
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

EMAILS = ['labend@iastate.edu', 'akrherz@iastate.edu',
          'lokhande@iastate.edu']
if len(sys.argv) == 2:
    EMAILS = ['akrherz@iastate.edu', ]


def sites_changelog(yesterday, html):
    html += """
    <h4>Sustainablecorn Internal Website Changes</h4>
    <table border="1" cellpadding="3" cellspacing="0">
    <thead><tr><th>Time</th><th>Activity</th></tr></thead>
    <tbody>"""

    config = ConfigParser.ConfigParser()
    config.read('mytokens.cfg')

    s = util.get_sites_client(config)
    feed = s.get_activity_feed()
    tablerows = []
    for entry in feed.entry:
        ts = datetime.datetime.strptime(entry.updated.text,
                                        '%Y-%m-%dT%H:%M:%S.%fZ')
        ts = ts.replace(tzinfo=pytz.timezone("UTC"))
        # print 'Sites ts: %s' % (ts,)
        if ts < yesterday:
            continue
        updated = ts.astimezone(pytz.timezone("America/Chicago"))
        elem = entry.summary.html
        elem.namespace = ''
        elem.children[0].namespace = ''
        tablerows.append(("<tr><td>%s</td><td>%s %s</td></tr>\n"
                          ) % (updated.strftime("%-d %b %-I:%M %P"),
                               elem.text, str(elem.children[0])))

    if len(tablerows) == 0:
        tablerows.append("<tr><td colspan='2'>No Changes Found</td></tr>")

    html += "".join(tablerows)
    html += """</tbody></table>"""
    return html


def drive_changelog(yesterday, html):
    """ Do something """
    drive = util.get_driveclient()

    start_change_id = util.CONFIG.get("changestamp", "1")

    html += """<p><table border="1" cellpadding="3" cellspacing="0">
<thead>
<tr><th>Changestamp</th><th>Time</th><th>Author</th><th>Resource</th></tr>
</thead>
<tbody>"""

    largestChangeId = -1
    hits = 0
    page_token = None
    while True:
        param = {}
        if start_change_id:
            param['startChangeId'] = start_change_id
        if page_token:
            param['pageToken'] = page_token
        print(("Requesting start_change_id: %s "
               "largestChangeId: %s page_token: %s"
               ) % (start_change_id, largestChangeId, page_token))
        response = drive.changes().list(**param).execute()
        largestChangeId = response['largestChangeId']
        page_token = response.get('nextPageToken')
        for item in response['items']:
            changestamp = item['id']
            if item['deleted']:
                continue
            modifiedDate = datetime.datetime.strptime(
                item['file']['modifiedDate'][:19], '%Y-%m-%dT%H:%M:%S')
            modifiedDate = modifiedDate.replace(tzinfo=pytz.timezone("UTC"))
            if modifiedDate < yesterday:
                continue
            uri = item['file']['alternateLink']
            title = item['file']['title']
            author = item['file']['lastModifyingUserName']
            localts = modifiedDate.astimezone(pytz.timezone("America/Chicago"))
            hits += 1
            html += """
<tr><td>%s</td><td>%s</td><td>%s</td><td><a href="%s">%s</a></td></tr>
            """ % (changestamp, localts.strftime("%-d %b %I:%M %P"),
                   author, uri, title)
        if not page_token:
            break

    util.CONFIG['changestamp'] = changestamp
    if hits == 0:
        html += """<tr><td colspan="4">No Changes Found...</td></tr>\n"""

    html += """</tbody></table>"""

    util.save_config()
    return html


def main():
    """Do Fun things"""
    today = datetime.datetime.utcnow()
    today = today.replace(tzinfo=pytz.timezone("UTC"), hour=12,
                          minute=0, second=0, microsecond=0)
    yesterday = today - datetime.timedelta(days=1)
    html = """
<h3>CSCAP Cloud Data Changes</h3>
<br />
<p>Period: 7 AM %s - 7 AM %s

<h4>Sustainablecorn Google Drive File Changes</h4>
""" % (yesterday.strftime("%-d %B %Y"), today.strftime("%-d %B %Y"))

    html = drive_changelog(yesterday, html)
    html = sites_changelog(yesterday, html)

    html += """<p>That is all...</p>"""
    # debugging
    if len(sys.argv) == 2:
        o = open('/tmp/out.html', 'w')
        o.write(html)
        o.close()
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "%s CSCAP Data ChangeLog" % (yesterday.strftime("%-d %b"),
                                                  )
    msg['From'] = 'mesonet@mesonet.agron.iastate.edu'
    msg['To'] = ','.join(EMAILS)

    part2 = MIMEText(html, 'html')

    msg.attach(part2)

    s = smtplib.SMTP('mailhub.iastate.edu')
    s.sendmail(msg['From'], EMAILS, msg.as_string())
    s.quit()

if __name__ == '__main__':
    main()
