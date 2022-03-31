"""Generation of faked METAR collective.

/AWOS/iowa_metar_collective.txt
"""
from io import StringIO

import pandas as pd
from pyiem.util import get_sqlalchemy_conn, utc


def add_output(sio):
    """Do as I say"""
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            "select raw from current c JOIn stations t on (t.iemid = c.iemid) "
            "WHERE t.network = 'IA_ASOS' and "
            "valid > now() - '2 hours'::interval "
            "and id not in ('CWI', 'FOD', 'SUX', 'MCW', 'MIW', 'IOW', 'AMW', "
            "'DSM', 'LWD', 'DBQ', 'CID', 'DVN', 'EST', 'OTM', 'ALO', 'SPW', "
            "'BRL') ORDER by id ASC",
            conn,
        )
    sio.write("000 \r\r\n")
    sio.write(f"SAUS80 KIEM {utc():%d%H%M}\r\r\n")
    sio.write("METAR \r\r\n")
    for _, row in df.iterrows():
        sio.write(f"{row['raw']}=\r\r\n")


def application(_environ, start_response):
    """Do Something"""
    headers = [("Content-type", "text/plain")]
    start_response("200 OK", headers)
    sio = StringIO()
    add_output(sio)
    return [sio.getvalue().encode("ascii")]
