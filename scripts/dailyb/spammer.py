"""
 Generate the dailyb spam
"""
import subprocess
import smtplib
import os
import iemdb
import mx.DateTime
import time
import psycopg2.extras
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import wwa

def cowreport():
    """ Generate something from the Cow, moooo! """
    proc = subprocess.Popen('php cowreport.php', shell=True, 
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    data = proc.stdout.read()
    html = "<h3>IEM Cow Report</h3><pre>"+ data +"</pre>"
    txt  = '> IEM Cow Report\n'+ data +'\n'
    return txt, html

def feature():
    """ Print the feature for yesterday """
    mesosite = iemdb.connect('mesosite', bypass=True)
    mcursor = mesosite.cursor(cursor_factory=psycopg2.extras.DictCursor)
    lastts = mx.DateTime.now() + mx.DateTime.RelativeDateTime(days=-1)
    # Query
    mcursor.execute("""
      SELECT *, to_char(valid, 'DD Mon HH:MI AM') as nicedate 
      from feature WHERE date(valid) = 'YESTERDAY'""")
    textfmt = """
 +----------------------------------------------
%(link)s
 | Title : %(title)s
 | Date  : %(nicedate)s
 | Votes : Good: %(good)s   Bad: %(bad)s
 +----------------------------------------------

%(story)s

"""
    htmlfmt = """
<p><a href="%(link)s">%(title)s</a>
<br /><strong>Date:</strong> %(nicedate)s
<br /><strong>Votes:</strong> Good: %(good)s &nbsp;  Bad: %(bad)s

<p>%(story)s

"""
    txt = "> Daily Feature\n"
    html = "<h3>Daily Feature</h3>"

    for row in mcursor:
        row2 = row.copy()
        row2['link']  = "http://mesonet.agron.iastate.edu/onsite/features/cat.php?day=%s" % (lastts.strftime("%Y-%m-%d"),)
        txt  += textfmt % row2
        html += htmlfmt % row2
    if mcursor.rowcount == 0:
        txt += "\n    No feature posted\n\n"
        html += "<strong>No feature posted</strong>"

    return txt, html

def news():
    """ Print the news that is fit to print """
    mesosite = iemdb.connect('mesosite', bypass=True)
    mcursor = mesosite.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # Last dailyb delivery
    lastts = mx.DateTime.now() + mx.DateTime.RelativeDateTime(hour=11, days=-1)
    mcursor.execute("""
      SELECT *, to_char(entered, 'DD Mon HH:MI AM') as nicedate 
      from news WHERE entered > '%s' 
      ORDER by entered DESC""" % (
      lastts.strftime("%Y-%m-%d %H:%M"),) )

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
<br /><strong>Title:</strong> <a href="http://mesonet.agron.iastate.edu/onsite/news.phtml?id=%(id)s">%(title)s</a>
<br /><strong>Date:</strong> %(nicedate)s
<br /><strong>Author:</strong> %(author)s
<br /><a href="%(url)s">link</a>

<p>%(body)s

"""
    txt = "> News\n"
    html = "<h3>News</h3>"

    for row in mcursor:
        txt  += textfmt % row
        html += htmlfmt % row
    if mcursor.rowcount == 0:
        txt += "\n    No news is good news\n\n"
        html += "<strong>No news is good news</strong>"

    return txt, html

msg = MIMEMultipart('alternative')
msg['Subject'] = 'IEM Daily Bulletin'
msg['From'] = 'daryl herzmann <akrherz@iastate.edu>'
if os.environ['USER'] == 'akrherz':
    msg['To'] = 'akrherz@iastate.edu'
else:
    msg['To'] = 'dailyb@mesonet.agron.iastate.edu'

now = mx.DateTime.now() 
text = """
Iowa Environmental Mesonet Daily Bulletin for %s

""" % (now.strftime("%d %B %Y"), )
html = """
<h3>Iowa Environmental Mesonet Daily Bulletin for %s</h3>
""" % (now.strftime("%d %B %Y"), )

t,h = news()
text += t
html += h
t,h = feature()
text += t
html += h
t,h = wwa.run()
text += t
html += h
t,h = cowreport()
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
o.write( text )
o.close()
subprocess.call("""/home/ldm/bin/pqinsert -p "plot c 000000000000 iemdb.txt bogus txt" tmp.txt""", shell=True)
o = open("tmp.txt", 'w')
o.write( html )
o.close()
subprocess.call("""/home/ldm/bin/pqinsert -p "plot c 000000000000 iemdb.html bogus txt" tmp.txt""", shell=True)
os.unlink("tmp.txt")
