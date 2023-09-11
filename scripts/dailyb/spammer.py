"""
 Generate the dailyb spam, run from RUN_12Z.sh
"""
import datetime
import os
import re
import smtplib
import subprocess
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from zoneinfo import ZoneInfo

import requests
import wwa  # @UnresolvedImport
from pyiem.util import (
    exponential_backoff,
    get_dbconnc,
    logger,
    utc,
)

LOG = logger()
IEM_BRANCHES = "https://api.github.com/repos/akrherz/iem/branches"
URLS = re.compile(r"(https?://[\w\d:#@%/;$()~_?\+-=\\\.&]*)", re.M)


def mywrap(text):
    """Make text pretty, my friends"""
    text = text.replace("\n\n", "\n").replace("\n", "\n    ").rstrip()
    return text


def htmlize(msg):
    """Convert things into html."""
    for token in URLS.findall(msg):
        msg = msg.replace(token, f'<a href="{token}">{token}</a>')
    return msg


def get_github_commits():
    """Get the recent day's worth of github code commits

    Returns:
      txt (str): text variant result
      html (str): html variant result
    """
    utcnow = datetime.datetime.utcnow()
    yesterday = utcnow - datetime.timedelta(hours=24)
    yesterday = yesterday.replace(hour=12, minute=0, second=0)
    iso = yesterday.strftime("%Y-%m-%dT%H:%M:%SZ")

    txt = ["> IEM Code Pushes <to branch> on Github\n"]
    html = ["<h3>IEM Code Pushes &lt;to branch&gt; on Github</h3>"]

    # get branches, main is first!
    branches = ["main"]
    req = exponential_backoff(requests.get, IEM_BRANCHES, timeout=30)
    for branch in req.json():
        if branch["name"] == "main":
            continue
        branches.append(branch["name"])

    hashes = []
    links = []
    for branch in branches:
        uri = (
            f"https://api.github.com/repos/akrherz/iem/commits?since={iso}&"
            f"sha={branch}"
        )
        req2 = exponential_backoff(requests.get, uri, timeout=30)
        # commits are in reverse order
        for commit in req2.json()[::-1]:
            if commit["sha"] in hashes:
                continue
            hashes.append(commit["sha"])
            timestring = commit["commit"]["author"]["date"]
            utcvalid = datetime.datetime.strptime(
                timestring, "%Y-%m-%dT%H:%M:%SZ"
            )
            valid = utcvalid.replace(tzinfo=ZoneInfo("UTC")).astimezone(
                ZoneInfo("America/Chicago")
            )
            data = {
                "stamp": valid.strftime("%b %-d %-2I:%M %p"),
                "msg": commit["commit"]["message"],
                "htmlmsg": htmlize(commit["commit"]["message"])
                .replace("\n\n", "\n")
                .replace("\n", "<br />\n"),
                "branch": branch,
                "url": commit["html_url"][:-20],  # chomp to make shorter
                "i": len(links) + 1,
            }
            links.append("[%(i)s] %(url)s" % data)
            txt.append(
                mywrap("  %(stamp)s[%(i)s] <%(branch)s> %(msg)s" % data)
            )
            html.append(
                (
                    '<li><a href="%(url)s">%(stamp)s</a> '
                    "&lt;%(branch)s&gt; %(htmlmsg)s</li>\n"
                )
                % data
            )

    if len(txt) == 1:
        txt = txt[0] + "    No code commits found in previous 24 Hours"
        html = html[0] + (
            "<strong>No code commits found " "in previous 24 Hours</strong>"
        )
    else:
        txt = "\n".join(txt) + "\n\n" + "\n".join(links)
        html = html[0] + "<ul>" + "\n".join(html[1:]) + "</ul>"

    return txt + "\n\n", html + "<br /><br />"


def cowreport():
    """Generate something from the Cow, moooo!"""
    central = ZoneInfo("America/Chicago")
    yesterday = (utc() - datetime.timedelta(days=1)).astimezone(central)
    midnight = yesterday.replace(hour=0, minute=0)
    midutc = midnight.astimezone(ZoneInfo("UTC"))
    begints = midutc.strftime("%Y-%m-%dT%H:%M")
    endts = (midutc + datetime.timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M")
    api = (
        f"http://iem.local/api/1/cow.json?begints={begints}&endts={endts}&"
        "phenomena=SV&phenomena=TO&lsrtype=SV&lsrtype=TO"
    )
    data = requests.get(api, timeout=60).json()
    st = data["stats"]
    if st["events_total"] == 0:
        text = "No SVR+TOR Warnings Issued."
        html = f"<h3>IEM Cow Report</h3><pre>{text}</pre>"
        txt = f"> IEM Cow Report\n{text}\n"
        return txt, html

    vp = st["events_verified"] / float(st["events_total"]) * 100.0
    text = (
        f"SVR+TOR Warnings Issued: {st['events_total']:3.0f} "
        f"Verified: {st['events_verified']:3.0f} [{vp:.1f}%]\n"
        "Polygon Size Versus County Size            "
        f"[{st['size_poly_vs_county[%]']:.1f}%]\n"
        "Average Perimeter Ratio                    "
        f"[{st['shared_border[%]']:.1f}%]\n"
        "Percentage of Warned Area Verified (15km)  "
        f"[{st['area_verify[%]']:.1f}%]\n"
        "Average Storm Based Warning Size           "
        f"[{st['avg_size[sq km]']:.0f} sq km]\n"
        f"Probability of Detection(higher is better) [{st['POD[1]']:.2f}]\n"
        f"False Alarm Ratio (lower is better)        [{st['FAR[1]']:.2f}]\n"
        f"Critical Success Index (higher is better)  [{st['CSI[1]']:.2f}]\n"
    )

    html = f"<h3>IEM Cow Report</h3><pre>{text}</pre>"
    txt = f"> IEM Cow Report\n{text}\n"

    return txt, html


def feature():
    """Print the feature for yesterday"""
    mesosite, mcursor = get_dbconnc("mesosite")
    lastts = datetime.datetime.now() + datetime.timedelta(days=-1)
    # Query
    mcursor.execute(
        "SELECT *, to_char(valid, 'DD Mon HH:MI AM') as nicedate "
        "from feature WHERE date(valid) = 'YESTERDAY'"
    )
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
<br />%(mediamarkup)s

<p>%(story)s</p>
"""
    txt = "> Daily Feature\n"
    html = "<h3>Daily Feature</h3>"

    for row in mcursor:
        row2 = row.copy()
        row2["link"] = (
            "https://mesonet.agron.iastate.edu/onsite/features/"
            f"cat.php?day={lastts:%Y-%m-%d}"
        )
        imgurl = (
            "https://mesonet.agron.iastate.edu/onsite/features/"
            f"{row['valid']:%Y/%m/%y%m%d}.{row['mediasuffix']}"
        )
        if row["mediasuffix"] in [
            "mp4",
        ]:
            row2["mediamarkup"] = (
                f'<video controls><source src="{imgurl}" type="video/mp4">'
                "Your email client does not support videos, please follow "
                "the link from the title of this feature to view.</video>"
            )
        else:
            row2["mediamarkup"] = f'<img src="{imgurl}">'
        if row2["appurl"] is not None:
            if not row2["appurl"].startswith("http"):
                row2["appurl"] = (
                    "https://mesonet.agron.iastate.edu" + row2["appurl"]
                )
            textfmt += (
                "\n\nThe featured media can be generated here: %(appurl)s"
            )
            htmlfmt += (
                "<p>The featured media can be generated on-demand "
                '<a href="%(appurl)s">here</a></p>.'
            )
        txt += textfmt % row2
        html += htmlfmt % row2
    if mcursor.rowcount == 0:
        txt += "\n    No feature posted\n\n"
        html += "<strong>No feature posted</strong>"

    return txt, html


def news():
    """Print the news that is fit to print"""
    mesosite, mcursor = get_dbconnc("mesosite")
    # Last dailyb delivery
    lastts = datetime.datetime.now() + datetime.timedelta(days=-1)
    mcursor.execute(
        "SELECT *, to_char(entered, 'DD Mon HH:MI AM') as nicedate "
        "from news WHERE entered > %s ORDER by entered DESC",
        (lastts,),
    )

    textfmt = """
 +----------------------------------------------
 | Title : %(title)s
 | Date  : %(nicedate)s
 | Author: %(author)s
 | URL   : %(url)s
 +----------------------------------------------

%(body)s

"""
    htmlfmt = (
        "<hr />\n"
        "<br /><strong>Title:</strong>\n"
        '<a href="https://mesonet.agron.iastate.edu/'
        'onsite/news.phtml?id=%(id)s">%(title)s</a>\n'
        "<br /><strong>Date:</strong> %(nicedate)s\n"
        "<br /><strong>Author:</strong> %(author)s\n"
        '<br /><a href="%(url)s">link</a>\n\n'
        "<p>%(body)s\n"
    )
    txt = "> News\n"
    html = "<h3>News</h3>"

    for row in mcursor:
        txt += textfmt % row
        html += htmlfmt % row
    if mcursor.rowcount == 0:
        txt += "\n    No news is good news\n\n"
        html += "<strong>No news is good news</strong>"

    return txt, html


def send_email(msg):
    """Send emails"""
    smtp = smtplib.SMTP("mailhub.iastate.edu")
    smtp.sendmail(msg["From"], [msg["To"]], msg.as_string())
    smtp.quit()


def main():
    """Go Main!"""
    msg = MIMEMultipart("alternative")
    now = datetime.datetime.now()
    msg["Subject"] = f"IEM Daily Bulletin for {now:%b %-d %Y}"
    msg["From"] = "daryl herzmann <akrherz@iastate.edu>"
    if os.environ["USER"] == "akrherz2":
        msg["To"] = "akrherz@iastate.edu"
    else:
        msg["To"] = "iem-dailyb@googlegroups.com"

    text = f"Iowa Environmental Mesonet Daily Bulletin for {now:%d %B %Y}\n\n"
    html = (
        f"<h3>Iowa Environmental Mesonet Daily Bulletin for {now:%d %B %Y}"
        "</h3>\n"
    )

    t, h = news()
    text += t
    html += h
    try:
        t, h = get_github_commits()
        text += t
        html += h
    except Exception as exp:
        LOG.info("get_github_commits failed with %s", exp)
        text += "\n(script failure fetching github activity\n"
        html += "<br />(script failure fetching github activity<br />"
    t, h = feature()
    text += t
    html += h
    t, h = wwa.run()
    text += t
    html += h
    try:
        t, h = cowreport()
        text += t
        html += h
    except Exception as exp:
        LOG.exception(exp)
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    msg.attach(part1)
    msg.attach(part2)

    exponential_backoff(send_email, msg)

    # Send forth LDM
    with open("tmp.txt", "w", encoding="utf-8") as fh:
        fh.write(text)
    subprocess.call(
        [
            "pqinsert",
            "-p",
            "plot c 000000000000 iemdb.txt bogus txt",
            "tmp.txt",
        ]
    )
    with open("tmp.txt", "w", encoding="utf-8") as fh:
        fh.write(html)
    subprocess.call(
        [
            "pqinsert",
            "-p",
            "plot c 000000000000 iemdb.html bogus txt",
            "tmp.txt",
        ]
    )
    os.unlink("tmp.txt")


if __name__ == "__main__":
    main()
