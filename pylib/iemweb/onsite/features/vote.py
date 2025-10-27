"""Feature Voting"""

import json
from datetime import datetime, timedelta
from http.cookies import SimpleCookie

from pydantic import Field
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy.engine import Connection


class Schema(CGIModel):
    """See how we are called."""

    vote: str = Field(
        default=None,
        description="The vote to cast",
        pattern="^(good|bad|abstain)$",
    )


@with_sqlalchemy_conn("mesosite")
def do(environ: dict, headers, vote, conn: Connection | None = None):
    """Do Something, yes do something"""
    cookie = SimpleCookie(environ.get("HTTP_COOKIE", ""))
    myoid = 0
    if "foid" in cookie:
        myoid = int(cookie["foid"].value)
    res = conn.execute(
        sql_helper(
            "SELECT to_char(valid, 'YYmmdd')::int as oid, good, bad, abstain "
            "from feature WHERE valid < now() ORDER by valid DESC LIMIT 1"
        )
    )
    if res.rowcount == 0:
        return {"good": 0, "bad": 0, "abstain": 0, "can_vote": False}
    row = res.mappings().fetchone()
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
        for _ in range(10):
            conn.execute(
                sql_helper(
                    """
    insert into weblog(uri, referer, http_status, x_forwarded_for)
    values (:uri, :referer, :status, :xff)
    """
                ),
                {
                    "uri": environ.get("REQUEST_URI", ""),
                    "referer": environ.get("HTTP_REFERER", ""),
                    "status": 404,
                    "xff": environ.get("HTTP_X_FORWARDED_FOR", ""),
                },
            )
        conn.execute(
            sql_helper(
                "UPDATE feature SET {vote} = {vote} + 1 WHERE "
                "to_char(valid, 'YYmmdd')::int = :oid",
                vote=vote,
            ),
            {"oid": foid},
        )
        # Now we set a cookie
        expiration = datetime.now() + timedelta(days=4)
        cookie = SimpleCookie()
        cookie["foid"] = foid
        cookie["foid"]["path"] = "/onsite/features/"
        cookie["foid"]["expires"] = expiration.strftime(
            "%a, %d-%b-%Y %H:%M:%S CST"
        )
        headers.append(("Set-Cookie", cookie.output(header="")))
        conn.commit()
        d["can_vote"] = False
    return d


@iemapp(schema=Schema)
def application(environ, start_response):
    """Process this request.

    This should look something like "/onsite/features/vote.json"
    or like "/onsite/features/vote/abstain.json".
    """
    headers = [("Content-type", "application/json")]
    vote = environ["vote"]
    j = do(environ, headers, vote)
    start_response("200 OK", headers)
    return json.dumps(j)
