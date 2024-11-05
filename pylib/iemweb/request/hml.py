""".. title:: Hydrological Markup Language (HML) Data

Return to `API Services </api/#cgi>`_ or `HML Request </request/hml.php>`_.

Documentation for /cgi-bin/request/hml.py
-----------------------------------------

This service provides the processed data from HML products.  This service
does not emit the HML product itself, but rather the processed data. Due to
lame reasons, you can only request forecast data within a single UTC year.

Changelog
---------

- 2024-11-05: Initial implementation

Example Usage
~~~~~~~~~~~~~

Provide all Guttenberg, IA GTTI4 observation data for 2024 in CSV format:

https://mesonet.agron.iastate.edu/cgi-bin/request/hml.py\
?station=GTTI4&sts=2024-01-01T00:00Z&ets=2025-01-01T00:00Z&fmt=csv\
&kind=obs

And then Excel

https://mesonet.agron.iastate.edu/cgi-bin/request/hml.py\
?station=GTTI4&sts=2024-01-01T00:00Z&ets=2025-01-01T00:00Z&fmt=excel\
&kind=obs

Provide all Guttenberg, IA GTTI4 forecast data for 2024 in CSV

https://mesonet.agron.iastate.edu/cgi-bin/request/hml.py\
?station=GTTI4&sts=2024-01-01T00:00Z&ets=2025-01-01T00:00Z&fmt=csv\
&kind=forecast

And then Excel

https://mesonet.agron.iastate.edu/cgi-bin/request/hml.py\
?station=GTTI4&sts=2024-01-01T00:00Z&ets=2025-01-01T00:00Z&fmt=excel\
&kind=forecast

"""

from io import BytesIO
from zoneinfo import ZoneInfo

import pandas as pd
from pydantic import AwareDatetime, Field, field_validator
from pyiem.database import get_sqlalchemy_conn
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp
from sqlalchemy import text

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class MyModel(CGIModel):
    """Our model"""

    kind: str = Field(
        "obs",
        description="The type of data to request, either 'obs' or 'forecasts'",
        pattern="^(obs|forecasts)$",
    )
    fmt: str = Field(
        "csv",
        description="The format of the output file, either 'csv' or 'excel'",
        pattern="^(csv|excel)$",
    )
    tz: str = Field("UTC", description="The timezone to use for timestamps")
    sts: AwareDatetime = Field(
        None, description="The start timestamp for the data"
    )
    ets: AwareDatetime = Field(
        None, description="The end timestamp for the data"
    )
    station: ListOrCSVType = Field(
        ...,
        description=(
            "The station(s) to request data for, "
            "either multi params or comma separated"
        ),
    )
    year1: int = Field(None, description="The start year, if not using sts")
    month1: int = Field(None, description="The start month, if not using sts")
    day1: int = Field(None, description="The start day, if not using sts")
    hour1: int = Field(0, description="The start hour, if not using sts")
    minute1: int = Field(0, description="The start minute, if not using sts")
    year2: int = Field(None, description="The end year, if not using ets")
    month2: int = Field(None, description="The end month, if not using ets")
    day2: int = Field(None, description="The end day, if not using ets")
    hour2: int = Field(0, description="The end hour, if not using ets")
    minute2: int = Field(0, description="The end minute, if not using ets")

    @field_validator("tz", mode="before")
    def check_tz(cls, value):
        """Ensure the timezone is valid."""
        try:
            ZoneInfo(value)
        except Exception as exp:
            raise ValueError("Invalid timezone provided") from exp
        return value


def get_obs(dbconn, environ: dict) -> pd.DataFrame:
    """Get data!"""
    df = pd.read_sql(
        text(
            """
        select distinct d.station, d.valid, k.label, d.value
        from hml_observed_data d JOIN
        hml_observed_keys k on (d.key = k.id) WHERE
        station = ANY(:stations) and valid >= :sts and valid < :ets
        ORDER by valid ASC
        """
        ),
        dbconn,
        params={
            "stations": environ["station"],
            "sts": environ["sts"],
            "ets": environ["ets"],
        },
    )
    # muck the timezones
    if not df.empty:
        tzinfo = ZoneInfo(environ["tz"])
        df["valid"] = (
            df["valid"].dt.tz_convert(tzinfo).dt.strftime("%Y-%m-%d %H:%M")
        )
        df = df.pivot_table(
            index=["station", "valid"],
            columns="label",
            values="value",
            aggfunc="first",
        ).reset_index()
        df = df.rename(
            columns={
                "valid": f"valid[{environ['tz']}]",
            }
        )
    return df


def get_forecasts(dbconn, environ: dict) -> pd.DataFrame:
    """Get data!"""
    year = environ["sts"].year
    df = pd.read_sql(
        text(
            f"""
        select station, issued, primaryname, primaryunits,
        secondaryname, secondaryunits, valid as forecast_valid,
        primary_value, secondary_value from hml_forecast f,
        hml_forecast_data_{year} d WHERE
        f.station = ANY(:stations) and f.issued >= :sts and f.issued < :ets
        and f.id = d.hml_forecast_id ORDER by issued ASC, forecast_valid ASC
        """
        ),
        dbconn,
        params={
            "stations": environ["station"],
            "sts": environ["sts"],
            "ets": environ["ets"],
        },
    )
    # muck the timezones
    if not df.empty:
        tzinfo = ZoneInfo(environ["tz"])
        for col in ["forecast_valid", "issued"]:
            df[col] = (
                df[col].dt.tz_convert(tzinfo).dt.strftime("%Y-%m-%d %H:%M")
            )
        df = df.rename(
            columns={
                "forecast_valid": f"forecast_valid[{environ['tz']}]",
                "issued": f"issued[{environ['tz']}]",
            }
        )
    return df


def rect(station):
    """Cleanup."""
    station = station.upper()
    return station[:5]


@iemapp(help=__doc__, schema=MyModel)
def application(environ, start_response):
    """Get stuff"""
    environ["station"] = [rect(x) for x in environ["station"]]
    with get_sqlalchemy_conn("hml") as dbconn:
        if environ["kind"] == "obs":
            df = get_obs(dbconn, environ)
        else:
            df = get_forecasts(dbconn, environ)

    bio = BytesIO()
    if environ["fmt"] == "excel":
        with pd.ExcelWriter(bio, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="HML Data", index=False)
        headers = [
            ("Content-type", EXL),
            ("Content-disposition", "attachment;Filename=hml.xlsx"),
        ]
    else:
        df.to_csv(bio, index=False)
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-disposition", "attachment;Filename=hml.csv"),
        ]
    start_response("200 OK", headers)
    return [bio.getvalue()]
