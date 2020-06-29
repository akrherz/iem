"""
Send Harry Hillaker a weekly email summarizing the past seven days worth of
RR3 products.
"""
import os
import datetime
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

from pyiem.util import get_dbconn

WFOS = ["KDMX", "KARX", "KDVN", "KFSD", "KOAX"]


def main():
    """Go Main Go"""
    pgconn = get_dbconn("afos", user="nobody")
    acursor = pgconn.cursor()

    now = datetime.datetime.now()
    sts = now + datetime.timedelta(days=-7)
    sts = sts.replace(hour=0)

    acursor.execute(
        "SELECT data, source from products where "
        "pil in ('RR3DMX','RR3DVN','RR3ARX','RR3FSD','RR3OAX','RR1FSD') "
        "and entered > %s ORDER by entered ASC",
        (sts,),
    )

    files = {}
    for wfo in WFOS:
        files[wfo] = open("/tmp/%sRR3.txt" % (wfo,), "w")

    for row in acursor:
        files[row[1]].write(row[0].replace("\001", ""))
        files[row[1]].write("\n")

    for wfo in WFOS:
        files[wfo].close()

    msg = MIMEMultipart()
    msg["Subject"] = "NWS RR3 Data for %s - %s" % (
        sts.strftime("%d %b %Y"),
        now.strftime("%d %b %Y"),
    )
    msg["From"] = "akrherz@iastate.edu"
    msg["To"] = "justin.glisan@iowaagriculture.gov"
    msg.preamble = "RR3 Report"

    fn = "RR3-%s-%s.txt" % (sts.strftime("%Y%m%d"), now.strftime("%Y%m%d"))

    for wfo in WFOS:
        b = MIMEBase("Text", "Plain")
        with open("/tmp/%sRR3.txt" % (wfo,), "rb") as fp:
            b.set_payload(fp.read())
        encoders.encode_base64(b)
        b.add_header(
            "Content-Disposition", 'attachment; filename="%s-%s"' % (wfo, fn)
        )
        msg.attach(b)
        os.unlink("/tmp/%sRR3.txt" % (wfo,))

    # Send the email via our own SMTP server.
    s = smtplib.SMTP("mailhub.iastate.edu")
    s.sendmail(msg["From"], msg["To"], msg.as_string())
    s.quit()


if __name__ == "__main__":
    main()
