""".. title:: Model Output Statistics (MOS) Data

Return to `API Services </api/#cgi>`_

Documentation for /cgi-bin/request/mos.py
-----------------------------------------

This application provides access to the Model Output Statistics (MOS) data
that the IEM processes and archives.

Example Usage
~~~~~~~~~~~~~

Return all the NBS MOS data for KDSM for MOS runs made on 14 Dec 2023

https://mesonet.agron.iastate.edu/cgi-bin/request/mos.py?\
station=KDSM&model=NBS&sts=2023-12-14T00:00Z&ets=2023-12-15T00:00Z&format=csv

and in Excel format this time

https://mesonet.agron.iastate.edu/cgi-bin/request/mos.py?\
station=KDSM&model=NBS&sts=2023-12-14T00:00Z&ets=2023-12-15T00:00Z&format=excel

and in JSON format this time

https://mesonet.agron.iastate.edu/cgi-bin/request/mos.py?\
station=KDSM&model=NBS&sts=2023-12-14T00:00Z&ets=2023-12-15T00:00Z&format=json

"""

from io import BytesIO, StringIO
from typing import Annotated

import pandas as pd
from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import IncompleteWebRequest
from pyiem.webutil import CGIModel, iemapp

from iemweb.fields import (
    DAY_OF_MONTH_FIELD_OPTIONAL,
    HOUR_FIELD,
    MONTH_FIELD_OPTIONAL,
    YEAR_FIELD_OPTIONAL,
)

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class MyModel(CGIModel):
    """Our model"""

    format: Annotated[
        str,
        Field(
            description="The format of the data response. csv, json, or excel",
            pattern=r"^(csv|json|excel)$",
        ),
    ] = "csv"
    model: Annotated[
        str,
        Field(
            description="The model to query",
            pattern=r"^(AVN|ETA|GFS|LAV|MEX|NAM|NBE|NBS)$",
        ),
    ]
    ets: Annotated[
        AwareDatetime | None,
        Field(
            description="The end time for the data request",
        ),
    ] = None
    station: Annotated[
        str, Field(description="The 4 character station identifier")
    ]
    sts: Annotated[
        AwareDatetime | None,
        Field(
            description="The start time for the data request",
        ),
    ] = None
    year1: YEAR_FIELD_OPTIONAL = None
    month1: MONTH_FIELD_OPTIONAL = None
    day1: DAY_OF_MONTH_FIELD_OPTIONAL = None
    hour1: HOUR_FIELD = 0
    year2: YEAR_FIELD_OPTIONAL = None
    month2: MONTH_FIELD_OPTIONAL = None
    day2: DAY_OF_MONTH_FIELD_OPTIONAL = None
    hour2: HOUR_FIELD = 23


def get_data(sts, ets, station, model, fmt):
    """Go fetch data please"""
    xref = {"NAM": "ETA", "GFS": "AVN"}
    model2 = xref.get(model, model)
    with get_sqlalchemy_conn("mos") as conn:
        df = pd.read_sql(
            sql_helper(
                """
            select
            runtime at time zone 'UTC' as utc_runtime,
            ftime at time zone 'UTC' as utc_ftime,
            *, t06_1 ||'/'||t06_2 as t06,
            t12_1 ||'/'|| t12_2 as t12  from alldata WHERE station = :station
            and runtime >= :sts and runtime <= :ets and model = ANY(:models)
            ORDER by runtime,ftime ASC"""
            ),
            conn,
            params={
                "sts": sts,
                "ets": ets,
                "models": [model, model2],
                "station": station,
            },
        )
    df = df.drop(columns=["runtime", "ftime"]).rename(
        columns={"utc_runtime": "runtime", "utc_ftime": "ftime"}
    )
    if not df.empty:
        df = df.dropna(axis=1, how="all")
    if fmt == "json":
        return df.to_json(orient="records", date_format="iso")
    if fmt == "excel":
        bio = BytesIO()
        with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Data", index=False)
        return bio.getvalue()

    sio = StringIO()
    df.to_csv(sio, index=False)
    return sio.getvalue()


@iemapp(help=__doc__, schema=MyModel, default_tz="UTC")
def application(environ, start_response):
    """See how we are called"""
    if environ["sts"] is None or environ["ets"] is None:
        raise IncompleteWebRequest("Missing sts and/or ets")
    fmt = environ["format"]
    station = environ["station"].upper()
    model = environ["model"]
    if fmt != "excel":
        payload = get_data(
            environ["sts"], environ["ets"], station, model, fmt
        ).encode("ascii")
        start_response("200 OK", [("Content-type", "text/plain")])
        return [payload]
    headers = [
        ("Content-type", EXL),
        ("Content-disposition", "attachment; Filename=mos.xlsx"),
    ]
    payload = get_data(environ["sts"], environ["ets"], station, model, fmt)
    start_response("200 OK", headers)
    return [payload]
