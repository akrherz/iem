"""answer any requests for talltowers data

Run from RUN_1MIN.sh
"""
# pylint: disable=abstract-class-instantiated
from __future__ import print_function
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn

TOWERS = {'ETTI4': 0, 'MCAI4': 1}
RTOWERS = ['ETTI4', 'MCAI4']


def gen_df(row):
    """Make me a dataframe of this data!"""
    pgconn = get_dbconn('talltowers',
                        host='iemdb-talltowers.local', user='tt_web')
    stations = row['stations'].split(",")
    towers = [TOWERS[station] for station in stations]
    df = read_sql("""
    SELECT * from data_analog WHERE tower in %s
    and valid >= %s and valid < %s ORDER by tower, valid
    """, pgconn, params=(tuple(towers), row['sts'], row['ets']),
                  index_col=None)
    df['tower'] = df['tower'].apply(lambda x: RTOWERS[x])
    return df


def do(row):
    """Process an actual request for data, please """
    df = gen_df(row)
    filename = ("/mesonet/share/pickup/talltowers/%s."
                ) % (row['valid'].strftime("%Y%m%d%H%M%S"), )
    if row['fmt'] == 'excel' and len(df.index) < 64000:

        def fmt(val):
            return val.strftime("%Y-%m-%d %H:%M")
        df['valid'] = df['valid'].apply(fmt)
        filename += "xlsx"
        with pd.ExcelWriter(filename) as writer:
            df.to_excel(writer, 'Analog Data', index=False)
    elif row['fmt'] == 'comma':
        filename += "csv"
        df.to_csv(filename, index=False)
    else:
        filename += "txt"
        df.to_csv(filename, sep='\t', index=False)

    msg = MIMEMultipart('alternative')
    msg['From'] = 'akrherz@iastate.edu'
    msg['To'] = row['email']
    text = """
Greetings,

Thank you for requesting ISU Tall Towers data.  You can find your data here:

%s

    """ % (filename.replace("/mesonet/share",
                            "https://mesonet.agron.iastate.edu"), )

    try:
        s = smtplib.SMTP('mailhub.iastate.edu')
    except Exception as _:
        time.sleep(57)
        s = smtplib.SMTP('mailhub.iastate.edu')
    part1 = MIMEText(text, 'plain')
    msg.attach(part1)
    s.sendmail(msg['From'], [msg['To']], msg.as_string())
    s.quit()
    return filename


def main():
    """Go Main Go"""
    pgconn = get_dbconn('mesosite')
    cursor = pgconn.cursor()
    df = read_sql("""
    SELECT * from talltowers_analog_queue
    WHERE filled = 'f'
    """, pgconn, index_col=None)
    for _, row in df.iterrows():
        print(("Processing talltowers request for: %s[%s]"
               ) % (row['email'], row['aff']))
        filename = do(row)
        print(" --> %s" % (filename,))
        cursor.execute("""
        UPDATE talltowers_analog_queue SET filled = 't'
        WHERE valid = %s and email = %s
        """, (row['valid'], row['email']))
    cursor.close()
    pgconn.commit()


if __name__ == '__main__':
    main()
