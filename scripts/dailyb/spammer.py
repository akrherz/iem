"""
 Generate the dailyb spam, run from RUN_12Z.sh
"""
import subprocess
import smtplib
import os
import datetime
import time
import psycopg2.extras
import json
import urllib2
import pytz
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import wwa


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
    uri = "https://api.github.com/repos/akrherz/iem/commits?since=%s" % (iso,)

    txt = "> IEM Code Development on Github\n\n"
    html = "<h3>IEM Code Development on Github</h3><ul>\n"

    try:
        jdata = json.loads(urllib2.urlopen(uri).read())
    except:
        txt += "    An Error Occurred downloading changelog!\n"
        html += "<li>An Error Occurred</li></ul>"
        return txt, html

    res = {}
    for commit in jdata:
        timestring = commit['commit']['author']['date']
        utcvalid = datetime.datetime.strptime(timestring, '%Y-%m-%dT%H:%M:%SZ')
        valid = (utcvalid.replace(tzinfo=pytz.timezone("UTC"))).astimezone(
                                            pytz.timezone("America/Chicago"))
        res[valid] = commit

    keys = res.keys()
    keys.sort()
    for valid in keys:
        commit = res[valid]
        msg = commit['commit']['message']
        txt += "    %s %s\n" % (valid.strftime("%-m/%-d %-2I:%M %p"),
                              msg.split("\n")[0])
        html += "<li><a href=\"%s\">%s</a> %s</li>\n" % (commit['html_url'],
                                            valid.strftime("%-m/%-d %I:%M %p"), 
                            msg.replace("\n\n","<br />"))
    
    if len(keys) == 0:
        txt += "    No code commits found in previous 24 Hours\n"
        html += "<li>No code commits found in previous 24 Hours</li>"
    
    return txt+"\n", html+"</ul>"


def cowreport():
    """ Generate something from the Cow, moooo! """
    proc = subprocess.Popen('php cowreport.php', shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    data = proc.stdout.read()
    html = "<h3>IEM Cow Report</h3><pre>"+ data +"</pre>"
    txt = '> IEM Cow Report\n'+ data +'\n'
    return txt, html


def feature():
    """ Print the feature for yesterday """
    mesosite = psycopg2.connect(database='mesosite', host='iemdb',
                                user='nobody')
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
        row2['link'] = ("http://mesonet.agron.iastate.edu/onsite/features/"
                        "cat.php?day=%s"
                        ) % (lastts.strftime("%Y-%m-%d"),)
        row2['imgurl'] = ("http://mesonet.agron.iastate.edu/onsite/features/"
                          "%s/%02i/%s.png"
                          ) % (row['valid'].year, row['valid'].month,
                               row['valid'].strftime("%y%m%d"))
        txt += textfmt % row2
        html += htmlfmt % row2
    if mcursor.rowcount == 0:
        txt += "\n    No feature posted\n\n"
        html += "<strong>No feature posted</strong>"

    return txt, html


def news():
    """ Print the news that is fit to print """
    mesosite = psycopg2.connect(database='mesosite', host='iemdb',
                                user='nobody')
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
    htmlfmt = """
<hr />
<br /><strong>Title:</strong>
<a href="https://mesonet.agron.iastate.edu/onsite/news.phtml?id=%(id)s">%(title)s</a>
<br /><strong>Date:</strong> %(nicedate)s
<br /><strong>Author:</strong> %(author)s
<br /><a href="%(url)s">link</a>

<p>%(body)s

"""
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
        msg['To'] = 'dailyb@mesonet.agron.iastate.edu'

    text = """Iowa Environmental Mesonet Daily Bulletin for %s\n\n""" % (
                                                now.strftime("%d %B %Y"), )
    html = """
    <h3>Iowa Environmental Mesonet Daily Bulletin for %s</h3>
    """ % (now.strftime("%d %B %Y"), )

    t, h = news()
    text += t
    html += h
    t, h = get_github_commits()
    text += t.encode('ascii', 'ignore')
    html += "%s" % (h.encode('ascii', 'ignore'),)
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

    try:
        s = smtplib.SMTP('mailhub.iastate.edu')
    except:
        time.sleep(57)
        s = smtplib.SMTP('mailhub.iastate.edu')
    s.sendmail(msg['From'], [msg['To']], msg.as_string())
    s.quit()

    # Send forth LDM
    o = open("tmp.txt", 'w')
    o.write(text)
    o.close()
    subprocess.call(('/home/ldm/bin/pqinsert -p "plot c 000000000000 '
                     'iemdb.txt bogus txt" tmp.txt'), shell=True)
    o = open("tmp.txt", 'w')
    o.write(html)
    o.close()
    subprocess.call(('/home/ldm/bin/pqinsert -p "plot c 000000000000 '
                     'iemdb.html bogus txt" tmp.txt'), shell=True)
    os.unlink("tmp.txt")

if __name__ == '__main__':
    main()
