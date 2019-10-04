#!/usr/bin/env python
""" Feature Voting"""
import cgi
import os
from http.cookies import SimpleCookie
import json
import datetime

from pyiem.util import get_dbconn, ssw


def do(vote):
    """ Do Something, yes do something """
    cookie = SimpleCookie(os.environ.get("HTTP_COOKIE", ''))
    myoid = 0
    if 'foid' in cookie:
        myoid = int(cookie['foid'].value)
    pgconn = get_dbconn('mesosite')
    cursor = pgconn.cursor()
    cursor.execute("""
        SELECT to_char(valid, 'YYmmdd')::int as oid, good, bad,
        abstain from feature ORDER by valid DESC LIMIT 1
    """)
    row = cursor.fetchone()
    foid = row[0]
    d = {'good': row[1], 'bad': row[2], 'abstain': row[3],
         'can_vote': True}
    if myoid == foid:
        d['can_vote'] = False

    if myoid < foid and vote in ['good', 'bad', 'abstain']:
        # Allow this vote
        d[vote] += 1
        cursor.execute("""UPDATE feature
        SET """+vote+""" = """+vote+""" + 1
        WHERE to_char(valid, 'YYmmdd')::int = %s
        """, (foid,))
        # Now we set a cookie
        expiration = datetime.datetime.now() + datetime.timedelta(days=4)
        cookie = SimpleCookie()
        cookie["foid"] = foid
        cookie["foid"]["path"] = "/onsite/features/"
        cookie["foid"]["expires"] = expiration.strftime(
                                                "%a, %d-%b-%Y %H:%M:%S CST")
        ssw(cookie.output() + "\n")
        cursor.close()
        pgconn.commit()
        d['can_vote'] = False

    return d


def main():
    """Do Something"""
    form = cgi.FieldStorage()
    vote = form.getfirst('vote', 'missing')
    ssw("Content-type: application/json\n")
    j = do(vote)
    ssw("\n")  # Finalize headers
    ssw(json.dumps(j))


if __name__ == '__main__':
    main()
