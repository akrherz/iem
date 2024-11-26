""".. title:: VTEC PDS Events

Return to `JSON Services </json/>`_

Changelog
---------

- 2024-08-05: Initial documtation update

"""

import json

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp

from iemweb.imagemaps import rectify_wfo


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP Callback")


def run():
    """Generate data."""
    data = {"generated_at": utc().strftime(ISO8601), "events": []}
    with get_sqlalchemy_conn("postgis") as conn:
        res = conn.exec_driver_sql(
            """
        SELECT vtec_year, wfo, eventid,
        phenomena, significance,
        min(product_issue at time zone 'UTC') as utc_product_issue,
        min(init_expire at time zone 'UTC') as utc_init_expire,
        min(issue at time zone 'UTC') as utc_issue,
        max(expire at time zone 'UTC') as utc_expire,
        array_to_string(array_agg(distinct substr(ugc, 1, 2)), ',') as states
        from warnings
        WHERE is_pds
        GROUP by vtec_year, wfo, eventid, phenomena, significance
        ORDER by utc_issue ASC
    """
        )
        for row in res.mappings():
            uri = (
                f"/vtec/event/{row['vtec_year']}-O-NEW-"
                f"{rectify_wfo(row['wfo'])}-{row['phenomena']}-"
                f"{row['significance']}-{row['eventid']:04.0f}"
            )
            data["events"].append(
                dict(
                    year=row["vtec_year"],
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
    memcacheexpire=3600,
    memcachekey="/json/vtec_pds",
)
def application(_environ, start_response):
    """Answer request."""
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return run()
