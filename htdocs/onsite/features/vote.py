""" Feature Voting"""
from http.cookies import SimpleCookie
import json
import datetime

from paste.request import parse_formvars
from pyiem.util import get_dbconn


def do(environ, headers, vote):
    """Do Something, yes do something"""
    cookie = SimpleCookie(environ.get("HTTP_COOKIE", ""))
    myoid = 0
    if "foid" in cookie:
        myoid = int(cookie["foid"].value)
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT to_char(valid, 'YYmmdd')::int as oid, good, bad, abstain "
        "from feature WHERE valid < now() ORDER by valid DESC LIMIT 1"
    )
    row = cursor.fetchone()
    foid = row[0]
    d = {"good": row[1], "bad": row[2], "abstain": row[3], "can_vote": True}
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

    return d


def application(environ, start_response):
    """Process this request.

    This should look something like "/onsite/features/vote.json"
    or like "/onsite/features/vote/abstain.json".
    """
    headers = [("Content-type", "application/json")]
    fields = parse_formvars(environ)
    vote = fields.get("vote", "missing")
    j = do(environ, headers, vote)
    start_response("200 OK", headers)
    return [json.dumps(j).encode("ascii")]
