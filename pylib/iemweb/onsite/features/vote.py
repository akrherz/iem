"""Feature Voting"""

import json
from collections.abc import Callable
from datetime import datetime, timedelta
from http.cookies import SimpleCookie
from typing import Annotated

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy.engine import Connection


class Schema(CGIModel):
    """See how we are called."""

    vote: Annotated[
        str | None,
        Field(
            description="The vote to cast",
            pattern="^(good|bad|abstain)$",
        ),
    ] = None


def do(environ: dict, headers, vote, conn: Connection):
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
    row = res.mappings().fetchone()
    if row is None:
        return {"good": 0, "bad": 0, "abstain": 0, "can_vote": False}
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
    insert into weblog(uri, referer, http_status, client_addr)
    values (:uri, :referer, :status, :host)
    """
                ),
                {
                    "uri": environ.get("REQUEST_URI", ""),
                    "referer": environ.get("HTTP_REFERER", ""),
                    "status": 404,
                    "host": environ.get("REMOTE_ADDR"),
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
def application(environ: dict, start_response: Callable):
    """Process this request.

    This should look something like "/onsite/features/vote.json"
    or like "/onsite/features/vote/abstain.json".
    """
    headers = [("Content-type", "application/json")]
    vote = environ["vote"]
    with get_sqlalchemy_conn("mesosite", rw=True) as conn:
        payload = json.dumps(do(environ, headers, vote, conn))
    start_response("200 OK", headers)
    return payload
