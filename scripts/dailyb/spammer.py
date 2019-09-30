"""
 Generate the dailyb spam, run from RUN_12Z.sh
"""
from __future__ import print_function
import subprocess
import smtplib
import os
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import psycopg2.extras
import requests
import pytz
from pyiem.util import exponential_backoff, get_dbconn
import wwa  # @UnresolvedImport

IEM_BRANCHES = "https://api.github.com/repos/akrherz/iem/branches"


def mywrap(text):
    """Make text pretty, my friends"""
    text = text.replace("\n\n", "\n").replace("\n", "\n    ").rstrip()
    return text


def get_github_commits():
    """ Get the recent day's worth of github code commits

    Returns:
      txt (str): text variant result
      html (str): html variant result
    """
    utcnow = datetime.datetime.utcnow()
    yesterday = utcnow - datetime.timedelta(hours=24)
    yesterday = yesterday.replace(hour=12, minute=0, second=0)
    iso = yesterday.strftime("%Y-%m-%dT%H:%M:%SZ")

    txt = ["> IEM Code Pushes <to branch> on Github\n", ]
    html = ["<h3>IEM Code Pushes &lt;to branch&gt; on Github</h3>", ]

    # get branches, master is first!
    branches = ['master']
    req = exponential_backoff(requests.get, IEM_BRANCHES, timeout=30)
    for branch in req.json():
        if branch['name'] == 'master':
            continue
        branches.append(branch['name'])

    hashes = []
    links = []
    for branch in branches:
        uri = ("https://api.github.com/repos/akrherz/iem/commits?since=%s&"
               "sha=%s") % (iso, branch)
        req2 = exponential_backoff(requests.get, uri, timeout=30)
        # commits are in reverse order
        for commit in req2.json()[::-1]:
            if commit['sha'] in hashes:
                continue
            hashes.append(commit['sha'])
            timestring = commit['commit']['author']['date']
            utcvalid = datetime.datetime.strptime(timestring,
                                                  '%Y-%m-%dT%H:%M:%SZ')
            valid = utcvalid.replace(tzinfo=pytz.utc).astimezone(
                                            pytz.timezone("America/Chicago"))
            data = {
                'stamp': valid.strftime("%b %-d %-2I:%M %p"),
                'msg': commit['commit']['message'],
                'htmlmsg': commit['commit'][
                    'message'].replace("\n\n", "\n").replace("\n", "<br />\n"),
                'branch': branch,
                'url': commit['html_url'][:-20],  # chomp to make shorter
                'i': len(links) + 1,
            }
            links.append("[%(i)s] %(url)s" % data)
            txt.append(
                mywrap("  %(stamp)s[%(i)s] <%(branch)s> %(msg)s" % data))
            html.append(("<li><a href=\"%(url)s\">%(stamp)s</a> "
                        "&lt;%(branch)s&gt; %(htmlmsg)s</li>\n") % data)

    if len(txt) == 1:
        txt = txt[0] + "    No code commits found in previous 24 Hours"
        html = html[0] + ("<strong>No code commits found "
                          "in previous 24 Hours</strong>")
    else:
        txt = "\n".join(txt) + "\n\n" + "\n".join(links)
        html = html[0] + "<ul>" + "\n".join(html[1:]) + "</ul>"

    return txt+"\n\n", html + "<br /><br />"


def cowreport():
    """ Generate something from the Cow, moooo! """
    proc = subprocess.Popen('php cowreport.php', shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    data = proc.stdout.read().decode('utf-8')
    html = "<h3>IEM Cow Report</h3><pre>" + data + "</pre>"
    txt = '> IEM Cow Report\n' + data + '\n'
    return txt, html


def feature():
    """ Print the feature for yesterday """
    mesosite = get_dbconn('mesosite', user='nobody')
    mcursor = mesosite.cursor(cursor_factory=psycopg2.extras.DictCursor)
    lastts = datetime.datetime.now() + datetime.timedelta(days=-1)
    # Query
    mcursor.execute("""
      SELECT *, to_char(valid, 'DD Mon HH:MI AM') as nicedate
      from feature WHERE date(valid) = 'YESTERDAY'""")
    textfmt = """
 +----------------------------------------------
%(link)s
 | Title : %(title)s
 | Date  : %(nicedate)s
 | Votes : Good: %(good)s   Bad: %(bad)s   Abstain: %(abstain)s
 +---------------------------------------------------------------

%(story)s

"""
    htmlfmt = """
<p><a href="%(link)s">%(title)s</a>
<br /><strong>Date:</strong> %(nicedate)s
<br /><strong>Votes:</strong> Good: %(good)s &nbsp;
Bad: %(bad)s  Abstain: %(abstain)s
<br /><img src="%(imgurl)s">

<p>%(story)s

"""
    txt = "> Daily Feature\n"
    html = "<h3>Daily Feature</h3>"

    for row in mcursor:
        row2 = row.copy()
        row2['link'] = ("https://mesonet.agron.iastate.edu/onsite/features/"
                        "cat.php?day=%s"
                        ) % (lastts.strftime("%Y-%m-%d"),)
        row2['imgurl'] = ("https://mesonet.agron.iastate.edu/onsite/features/"
                          "%s/%02i/%s.%s"
                          ) % (row['valid'].year, row['valid'].month,
                               row['valid'].strftime("%y%m%d"),
                               row['mediasuffix'])
        txt += textfmt % row2
        html += htmlfmt % row2
    if mcursor.rowcount == 0:
        txt += "\n    No feature posted\n\n"
        html += "<strong>No feature posted</strong>"

    return txt, html


def news():
    """ Print the news that is fit to print """
    mesosite = get_dbconn('mesosite', user='nobody')
    mcursor = mesosite.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # Last dailyb delivery
    lastts = datetime.datetime.now() + datetime.timedelta(days=-1)
    mcursor.execute("""
      SELECT *, to_char(entered, 'DD Mon HH:MI AM') as nicedate
      from news WHERE entered > '%s'
      ORDER by entered DESC
      """ % (lastts.strftime("%Y-%m-%d %H:%M"),))

    textfmt = """
 +----------------------------------------------
 | Title : %(title)s
 | Date  : %(nicedate)s
 | Author: %(author)s
 | URL   : %(url)s
 +----------------------------------------------

%(body)s

"""
    htmlfmt = ('<hr />\n'
               '<br /><strong>Title:</strong>\n'
               '<a href="https://mesonet.agron.iastate.edu/'
               'onsite/news.phtml?id=%(id)s">%(title)s</a>\n'
               '<br /><strong>Date:</strong> %(nicedate)s\n'
               '<br /><strong>Author:</strong> %(author)s\n'
               '<br /><a href="%(url)s">link</a>\n\n'
               '<p>%(body)s\n')
    txt = "> News\n"
    html = "<h3>News</h3>"

    for row in mcursor:
        txt += textfmt % row
        html += htmlfmt % row
    if mcursor.rowcount == 0:
        txt += "\n    No news is good news\n\n"
        html += "<strong>No news is good news</strong>"

    return txt, html


def main():
    """ Go Main! """
    msg = MIMEMultipart('alternative')
    now = datetime.datetime.now()
    msg['Subject'] = 'IEM Daily Bulletin for %s' % (now.strftime("%b %-d %Y"),)
    msg['From'] = 'daryl herzmann <akrherz@iastate.edu>'
    if os.environ['USER'] == 'akrherz':
        msg['To'] = 'akrherz@iastate.edu'
    else:
        msg['To'] = 'iem-dailyb@iastate.edu'

    text = """Iowa Environmental Mesonet Daily Bulletin for %s\n\n""" % (
                                                now.strftime("%d %B %Y"), )
    html = """
    <h3>Iowa Environmental Mesonet Daily Bulletin for %s</h3>
    """ % (now.strftime("%d %B %Y"), )

    t, h = news()
    text += t
    html += h
    try:
        t, h = get_github_commits()
        text += t
        html += h
    except Exception as exp:
        print("get_github_commits failed with %s" % (exp, ))
        text += "\n(script failure fetching github activity\n"
        html += "<br />(script failure fetching github activity<br />"
    t, h = feature()
    text += t
    html += h
    t, h = wwa.run()
    text += t
    html += h
    t, h = cowreport()
    text += t
    html += h

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)

    exponential_backoff(send_email, msg)

    # Send forth LDM
    fp = open("tmp.txt", 'w')
    fp.write(text)
    fp.close()
    subprocess.call(('/home/ldm/bin/pqinsert -p "plot c 000000000000 '
                     'iemdb.txt bogus txt" tmp.txt'), shell=True)
    fp = open("tmp.txt", 'w')
    fp.write(html)
    fp.close()
    subprocess.call(('/home/ldm/bin/pqinsert -p "plot c 000000000000 '
                     'iemdb.html bogus txt" tmp.txt'), shell=True)
    os.unlink("tmp.txt")


def send_email(msg):
    """Send emails"""
    smtp = smtplib.SMTP('mailhub.iastate.edu')
    smtp.sendmail(msg['From'], [msg['To']], msg.as_string())
    smtp.quit()


def tests():
    """Hacky means to test things"""
    text, html = get_github_commits()
    print("Text Variant")
    print(text)
    fp = open('/tmp/gh.html', 'w')
    fp.write(html)
    fp.close()
    subprocess.call("xdg-open /tmp/gh.html >& /dev/null", shell=True)


if __name__ == '__main__':
    main()
    # tests()
