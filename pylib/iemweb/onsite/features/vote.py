"""Feature Voting"""

import datetime
import json
from http.cookies import SimpleCookie

from pyiem.util import get_dbconnc
from pyiem.webutil import iemapp


def do(environ, headers, vote):
    """Do Something, yes do something"""
    cookie = SimpleCookie(environ.get("HTTP_COOKIE", ""))
    myoid = 0
    if "foid" in cookie:
        myoid = int(cookie["foid"].value)
    pgconn, cursor = get_dbconnc("mesosite")
    cursor.execute(
        "SELECT to_char(valid, 'YYmmdd')::int as oid, good, bad, abstain "
        "from feature WHERE valid < now() ORDER by valid DESC LIMIT 1"
    )
    if cursor.rowcount == 0:
        pgconn.close()
        return {"good": 0, "bad": 0, "abstain": 0, "can_vote": False}
    row = cursor.fetchone()
    foid = row["oid"]
    d = {
        "good": row["good"],
        "bad": row["bad"],
        "abstain": row["abstain"],
        "can_vote": True,
    }
    if myoid == foid:
        d["can_vote"] = False

    if myoid < foid and vote in ["good", "bad", "abstain"]:
        # Allow this vote
        d[vote] += 1
        cursor.execute(
            f"UPDATE feature SET {vote} = {vote} + 1 WHERE "
            "to_char(valid, 'YYmmdd')::int = %s",
            (foid,),
        )
        # Now we set a cookie
        expiration = datetime.datetime.now() + datetime.timedelta(days=4)
        cookie = SimpleCookie()
        cookie["foid"] = foid
        cookie["foid"]["path"] = "/onsite/features/"
        cookie["foid"]["expires"] = expiration.strftime(
            "%a, %d-%b-%Y %H:%M:%S CST"
        )
        headers.append(("Set-Cookie", cookie.output(header="")))
        cursor.close()
        pgconn.commit()
        d["can_vote"] = False
    pgconn.close()
    return d


@iemapp()
def application(environ, start_response):
    """Process this request.

    This should look something like "/onsite/features/vote.json"
    or like "/onsite/features/vote/abstain.json".
    """
    headers = [("Content-type", "application/json")]
    vote = environ.get("vote", "missing")
    j = do(environ, headers, vote)
    start_response("200 OK", headers)
    return [json.dumps(j).encode("ascii")]
