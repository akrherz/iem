""".. title:: Model Output Statistics (MOS) Data

Documentation for /cgi-bin/request/mos.py
-----------------------------------------

This application provides access to the Model Output Statistics (MOS) data
that the IEM processes and archives.

Example Usage
~~~~~~~~~~~~~

Return all the NBS MOS data for KDSM for MOS runs made on 14 Dec 2023

  https://mesonet.agron.iastate.edu/cgi-bin/request/mos.py?\
station=KDSM&model=NBS&sts=2023-12-14T00:00Z&ets=2023-12-15T00:00Z&format=csv

"""

from datetime import datetime
from io import BytesIO, StringIO
from zoneinfo import ZoneInfo

import pandas as pd
from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class MyModel(CGIModel):
    """Our model"""

    format: str = Field(
        "csv",
        description="The format of the data response. csv, json, or excel",
        pattern=r"^(csv|json|excel)$",
    )
    model: str = Field(
        ...,
        description="The model to query",
        pattern=r"^(AVN|ETA|GFS|LAV|MEX|NAM|NBE|NBS)$",
    )
    ets: AwareDatetime = Field(
        None,
        description="The end time for the data request",
    )
    station: str = Field(..., description="The 4 character station identifier")
    sts: AwareDatetime = Field(
        None,
        description="The start time for the data request",
    )
    year1: int = Field(
        None,
        description="The start year for the data request, when sts is not set",
    )
    month1: int = Field(
        None,
        description=(
            "The start month for the data request, when sts is not set"
        ),
    )
    day1: int = Field(
        None,
        description="The start day for the data request, when sts is not set",
    )
    hour1: int = Field(
        None,
        description="The start hour for the data request, when sts is not set",
    )
    year2: int = Field(
        None,
        description="The end year for the data request, when ets is not set",
    )
    month2: int = Field(
        None,
        description="The end month for the data request, when ets is not set",
    )
    day2: int = Field(
        None,
        description="The end day for the data request, when ets is not set",
    )
    hour2: int = Field(
        None,
        description="The end hour for the data request, when ets is not set",
    )


def get_data(sts, ets, station, model, fmt):
    """Go fetch data please"""
    model2 = model
    if model == "NAM":
        model2 = "ETA"
    if model == "GFS":
        model2 = "AVN"
    with get_sqlalchemy_conn("mos") as conn:
        df = pd.read_sql(
            text(
                """
            select
            runtime at time zone 'UTC' as utc_runtime,
            ftime at time zone 'UTC' as utc_ftime,
            *, t06_1 ||'/'||t06_2 as t06,
            t12_1 ||'/'|| t12_2 as t12  from alldata WHERE station = :station
            and runtime >= :sts and runtime <= :ets and
            (model = :model1 or model = :model2)
            ORDER by runtime,ftime ASC"""
            ),
            conn,
            params={
                "sts": sts,
                "ets": ets,
                "model1": model,
                "model2": model2,
                "station": station,
            },
        )
    df = df.drop(columns=["runtime", "ftime"]).rename(
        columns={"utc_runtime": "runtime", "utc_ftime": "ftime"}
    )
    if not df.empty:
        df = df.dropna(axis=1, how="all")
    if fmt == "json":
        return df.to_json(orient="records")
    if fmt == "excel":
        bio = BytesIO()
        # pylint: disable=abstract-class-instantiated
        with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Data", index=False)
        return bio.getvalue()

    sio = StringIO()
    df.to_csv(sio, index=False)
    return sio.getvalue()


@iemapp(help=__doc__, schema=MyModel, parse_times=False)
def application(environ, start_response):
    """See how we are called"""
    if environ["sts"] is None:
        environ["sts"] = datetime(
            environ["year1"],
            environ["month1"],
            environ["day1"],
            environ["hour1"],
            tzinfo=ZoneInfo("UTC"),
        )
    if environ["ets"] is None:
        environ["ets"] = datetime(
            environ["year2"],
            environ["month2"],
            environ["day2"],
            environ["hour2"],
            tzinfo=ZoneInfo("UTC"),
        )

    fmt = environ["format"]
    station = environ["station"].upper()
    model = environ["model"]
    if fmt != "excel":
        start_response("200 OK", [("Content-type", "text/plain")])
        return [
            get_data(
                environ["sts"], environ["ets"], station, model, fmt
            ).encode("ascii")
        ]
    headers = [
        ("Content-type", EXL),
        ("Content-disposition", "attachment; Filename=mos.xlsx"),
    ]
    start_response("200 OK", headers)
    return [get_data(environ["sts"], environ["ets"], station, model, fmt)]
