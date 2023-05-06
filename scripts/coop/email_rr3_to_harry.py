"""
Send Harry Hillaker a weekly email summarizing the past seven days worth of
RR3 products.
"""
import datetime
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

from pyiem.util import get_dbconn

WFOS = ["KDMX", "KARX", "KDVN", "KFSD", "KOAX"]


def main():
    """Go Main Go"""
    pgconn = get_dbconn("afos")
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

    for row in acursor:
        with open(f"/tmp/{row[1]}RR3.txt", "a", encoding="ascii") as fh:
            fh.write(row[0].replace("\001", ""))
            fh.write("\n")

    msg = MIMEMultipart()
    msg["Subject"] = f"NWS RR3 Data for {sts:%d %b %Y} - {now:%d %b %Y}"
    msg["From"] = "akrherz@iastate.edu"
    msg["To"] = "justin.glisan@iowaagriculture.gov"
    msg.preamble = "RR3 Report"

    fn = f"RR3-{sts:%Y%m%d}-{now:%Y%m%d}.txt"

    for wfo in WFOS:
        b = MIMEBase("Text", "Plain")
        with open(f"/tmp/{wfo}RR3.txt", "rb") as fp:
            b.set_payload(fp.read())
        encoders.encode_base64(b)
        b.add_header(
            "Content-Disposition", f'attachment; filename="{wfo}-{fn}"'
        )
        msg.attach(b)
        os.unlink(f"/tmp/{wfo}RR3.txt")

    # Send the email via our own SMTP server.
    s = smtplib.SMTP("mailhub.iastate.edu")
    s.sendmail(msg["From"], msg["To"], msg.as_string())
    s.quit()


if __name__ == "__main__":
    main()
