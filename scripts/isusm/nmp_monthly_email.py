"""Generates an email with the National Mesonet Program contact status

Requires: iem property `nmp_monthly_email_list`

Period of performance is previous month 7th thru this month 6th

Run on the 7th from `RUN_2AM.sh`

"""

import smtplib
from datetime import date, datetime, timedelta
from email.mime.text import MIMEText

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.util import get_properties


def generate_report(start_date, end_date):
    """Generate the text report"""
    days = (end_date - start_date).days + 1
    totalobs = days * 24 * 25
    with get_sqlalchemy_conn("isuag") as pgconn:
        df = pd.read_sql(
            "SELECT station, count(*) from sm_hourly WHERE valid >= %s "
            "and valid < %s GROUP by station ORDER by station",
            pgconn,
            params=(start_date, end_date + timedelta(days=1)),
            index_col="station",
        )
    performance = min([100, df["count"].sum() / float(totalobs) * 100.0])
    return """
Iowa Environmental Mesonet Data Delivery Report
===============================================

  Dataset: ISU Soil Moisture Network
  Performance Period: %s thru %s
  Reported Performance: %.1f%%
  Reporting Platforms: %.0f

Additional Details
==================
  Total Required Obs: %.0f (24 hourly obs x 25 platforms x %.0f days)
  Observations Delivered: %.0f
  Report Generated: %s

.END
""" % (
        start_date.strftime("%d %b %Y"),
        end_date.strftime("%d %b %Y"),
        performance,
        len(df.index),
        totalobs,
        days,
        df["count"].sum(),
        datetime.now().strftime("%d %B %Y %H:%M %p"),
    )


def main():
    """Go Main Go"""
    emails = get_properties()["nmp_monthly_email_list"].split(",")

    end_date = date.today().replace(day=6)
    start_date = (end_date - timedelta(days=40)).replace(day=7)
    report = generate_report(start_date, end_date)

    msg = MIMEText(report)
    msg["Subject"] = "[IEM] Synoptic Contract Deliverables Report"
    msg["From"] = "IEM Automation <akrherz@iastate.edu>"
    msg["To"] = ", ".join(emails)
    msg.add_header("reply-to", "akrherz@iastate.edu")

    # Send the email via our own SMTP server.
    smtp = smtplib.SMTP("mailhub.iastate.edu")
    smtp.sendmail(msg["From"], msg["To"], msg.as_string())
    smtp.quit()


if __name__ == "__main__":
    main()
