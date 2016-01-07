"""
  My purpose in life is to send an email each day with changes found
  on the Google Drive
"""
import ConfigParser
import sys
import util
import os
import datetime
import pytz
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

FMIME = 'application/vnd.google-apps.folder'
CFG = {'cscap': dict(emails=['labend@iastate.edu', 'akrherz@iastate.edu',
                             'lokhande@iastate.edu', 'gio@iastate.edu'],
                     title="Sustainable Corn"
                     ),
       'td': dict(emails=['labend@iastate.edu', 'akrherz@iastate.edu',
                          'breinhar@purdue.edu', 'gio@iastate.edu'],
                  title='Transforming Drainage'
                  )
       }


def sites_changelog(regime, yesterday, html):
    html += """
    <h4>%s Internal Website Changes</h4>
    <table border="1" cellpadding="3" cellspacing="0">
    <thead><tr><th>Time</th><th>Activity</th></tr></thead>
    <tbody>""" % (CFG[regime]['title'],)

    config = ConfigParser.ConfigParser()
    config.read('mytokens.cfg')

    site = 'sustainablecorn' if regime == 'cscap' else 'transformingdrainage'
    s = util.get_sites_client(config, site)
    # Fetch more results for sites activity feed
    opt = {'max-results': 999}
    feed = s.get_activity_feed(**opt)
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


def drive_changelog(regime, yesterday, html):
    """ Do something """
    drive = util.get_driveclient()
    folders = util.get_folders(drive)
    start_change_id = util.CONFIG.get("changestamp_"+regime, "1")

    html += """<p><table border="1" cellpadding="3" cellspacing="0">
<thead>
<tr><th>Folder</th><th>Resource</th></tr>
</thead>
<tbody>"""

    largestChangeId = -1
    hits = 0
    page_token = None
    param = {'includeDeleted': False, 'maxResults': 1000}
    while True:
        if start_change_id:
            param['startChangeId'] = start_change_id
        if page_token:
            param['pageToken'] = page_token
        print(("[%s] start_change_id: %s largestChangeId: %s page_token: %s"
               ) % (regime, start_change_id, largestChangeId, page_token))
        response = drive.changes().list(**param).execute()
        largestChangeId = response['largestChangeId']
        page_token = response.get('nextPageToken')
        for item in response['items']:
            changestamp = item['id']
            if item['deleted']:
                continue
            # don't do more work when this file actually did not change
            modifiedDate = datetime.datetime.strptime(
                item['file']['modifiedDate'][:19], '%Y-%m-%dT%H:%M:%S')
            modifiedDate = modifiedDate.replace(tzinfo=pytz.timezone("UTC"))
            if modifiedDate < yesterday:
                continue
            # Need to see which base folder this file is in!
            isproject = False
            for parent in item['file']['parents']:
                if parent['id'] not in folders:
                    print(('[%s] file: %s has unknown parent: %s'
                           ) % (regime, item['id'], parent['id']))
                    continue
                if (folders[parent['id']]['basefolder'] ==
                        util.CONFIG[regime]['basefolder']):
                    isproject = True
            if not isproject:
                print(('[%s] %s skipped'
                       ) % (regime, repr(item['file']['title'])))
                continue
            uri = item['file']['alternateLink']
            title = item['file']['title'].encode('ascii', 'ignore')
            localts = modifiedDate.astimezone(pytz.timezone("America/Chicago"))
            hits += 1
            pfolder = item['file']['parents'][0]['id']
            html += """
<tr>
<td><a href="https://docs.google.com/folderview?id=%s&usp=drivesdk">%s</a></td>
<td><a href="%s">%s</a></td></tr>
            """ % (pfolder, folders[pfolder]['title'], uri, title)
            hit = False
            if 'version' in item['file'] and item['file']['mimeType'] != FMIME:
                lastmsg = ""
                try:
                    revisions = drive.revisions().list(
                        fileId=item['file']['id']).execute()
                except:
                    print(('[%s] file %s (%s) failed revisions'
                           ) % (regime, title, item['file']['mimeType']))
                    revisions = {'items': []}
                for item2 in revisions['items']:
                    md = datetime.datetime.strptime(
                                                    item2['modifiedDate'][:19],
                                                    '%Y-%m-%dT%H:%M:%S')
                    md = md.replace(tzinfo=pytz.timezone("UTC"))
                    if md < yesterday:
                        continue
                    localts = md.astimezone(pytz.timezone("America/Chicago"))
                    if 'lastModifyingUser' not in item2:
                        print(('[%s] file: %s has no User? %s'
                               ) % (regime, title, item2))
                        continue
                    luser = item2['lastModifyingUser']
                    hit = True
                    thismsg = """
    <tr><td colspan="2"><img src="%s" style="height:25px;"/> %s by
     %s (%s)</td></tr>
                    """ % ((luser['picture']['url']
                            if 'picture' in luser else ''),
                           localts.strftime("%-d %b %-I:%M %p"),
                           luser['displayName'], luser['emailAddress'])
                    if thismsg != lastmsg:
                        html += thismsg
                    lastmsg = thismsg
            # Now we check revisions
            if not hit:
                luser = item['file']['lastModifyingUser']
                html += """
<tr><td colspan="2"><img src="%s" style="height:25px;"/> %s by
 %s (%s)</td></tr>
                """ % (luser['picture']['url'] if 'picture' in luser else '',
                       localts.strftime("%-d %b %-I:%M %p"),
                       luser['displayName'], luser.get('emailAddress', 'n/a'))
        if not page_token:
            break

    util.CONFIG['changestamp_'+regime] = changestamp
    if hits == 0:
        html += """<tr><td colspan="5">No Changes Found...</td></tr>\n"""

    html += """</tbody></table>"""

    util.save_config()
    return html


def main(argv):
    """Do Fun things"""
    regime = "cscap" if argv[1] == 'cscap' else 'td'
    if os.environ.get('HOSTNAME', '') == 'laptop.local':
        CFG[regime]['emails'] = ['akrherz@iastate.edu', ]

    today = datetime.datetime.utcnow()
    today = today.replace(tzinfo=pytz.timezone("UTC"), hour=12,
                          minute=0, second=0, microsecond=0)
    yesterday = today - datetime.timedelta(days=1)
    localts = yesterday.astimezone(pytz.timezone("America/Chicago"))
    html = """
<h3>%s Cloud Data Changes</h3>
<br />
<p>Period: %s - %s

<h4>Google Drive File Changes</h4>
""" % (CFG[regime]['title'],
       (localts - datetime.timedelta(hours=24)).strftime("%-I %p %-d %B %Y"),
       localts.strftime("%-I %p %-d %B %Y"))

    html = drive_changelog(regime, yesterday, html)
    html = sites_changelog(regime, yesterday, html)

    html += """<p>That is all...</p>"""
    # debugging
    if len(sys.argv) == 3:
        o = open('/tmp/out.html', 'w')
        o.write(html)
        o.close()
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "%s %s Data ChangeLog" % (yesterday.strftime("%-d %b"),
                                               CFG[regime]['title'])
    msg['From'] = 'mesonet@mesonet.agron.iastate.edu'
    msg['To'] = ','.join(CFG[regime]['emails'])

    part2 = MIMEText(html, 'html')

    msg.attach(part2)

    s = smtplib.SMTP('mailhub.iastate.edu')
    s.sendmail(msg['From'], CFG[regime]['emails'], msg.as_string())
    s.quit()

if __name__ == '__main__':
    main(sys.argv)
