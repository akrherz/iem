""".. title:: NWS Warnings with Emergency Significance

Return to `JSON Services </json/>`_

Changelog
---------

- 2024-08-09: Initial documentation update

"""

import json

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name.")


def run():
    """Generate data."""
    data = {"generated_at": utc().strftime(ISO8601), "events": []}
    with get_sqlalchemy_conn("postgis") as pgconn:
        res = pgconn.exec_driver_sql(
            """
            SELECT extract(year from issue)::int as year, wfo, eventid,
            phenomena, significance,
            min(product_issue at time zone 'UTC') as utc_product_issue,
            min(init_expire at time zone 'UTC') as utc_init_expire,
            min(issue at time zone 'UTC') as utc_issue,
            max(expire at time zone 'UTC') as utc_expire,
            array_to_string(array_agg(distinct substr(ugc, 1, 2)), ',')
            as states
            from warnings
            WHERE phenomena in ('TO', 'FF') and significance = 'W'
            and is_emergency
            GROUP by year, wfo, eventid, phenomena, significance
            ORDER by utc_issue ASC
        """
        )
        for row in res.mappings():
            uri = (
                f"/vtec/#{row['year']}-O-NEW-K{row['wfo']}-"
                f"{row['phenomena']}-{row['significance']}-"
                f"{row['eventid']:04.0f}"
            )
            data["events"].append(
                dict(
                    year=row["year"],
                    phenomena=row["phenomena"],
                    significance=row["significance"],
                    eventid=row["eventid"],
                    issue=row["utc_issue"].strftime(ISO8601),
                    product_issue=row["utc_product_issue"].strftime(ISO8601),
                    expire=row["utc_expire"].strftime(ISO8601),
                    init_expire=row["utc_init_expire"].strftime(ISO8601),
                    uri=uri,
                    wfo=row["wfo"],
                    states=row["states"],
                )
            )
    return json.dumps(data)


@iemapp(
    help=__doc__,
    schema=Schema,
    memcachekey="/json/vtec_emergencies",
    memcacheexpire=3600,
)
def application(_environ, start_response):
    """Answer request."""
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return run()
