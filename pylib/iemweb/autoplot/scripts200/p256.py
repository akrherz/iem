"""
Due to various software and support issues at the National Weather Service,
they generally stopped the generation of Regional Temperature and Precipitation
(RTP) reports during 2024.  The IEM processes all of the raw SHEF encoded
reports from the COOP networks and attempts robust accounting of Airport ASOS
reports, so this autoplot attempts to generate a RTP report for others to
use.</p>

<p>Since this tool is within the autoplot framework, you can automate the
generation and download of the SHEF text reports. Here are some examples:</p>

<p>Generate a RTPIA report for the morning of 10 June 2024. Note that
when even requesting a state report, it is good to set the CWA so to get
a locally relevant timezone.</p>
<pre>
$ wget -O RTPIA.txt 'https://mesonet.agron.iastate.edu/plotting/auto/plot/\
256/fmt:text::date:2024-06-10&wfo=DMX&state=IA&by=state&report=12z'
$ cat RTPIA.txt | dcshef
</pre>

<p>Generate a RTPBOU report for the morning of 21 May 2024:</p>
<pre>
$ wget -O RTPBOU.txt 'https://mesonet.agron.iastate.edu/plotting/auto/plot/\
256/fmt:text::date:2024-05-21&wfo=BOU&by=wfo&report=12z'
$ cat RTPBOU.txt | dcshef
</pre>

<p><strong>Report Types:</strong>
<ul>
    <li><strong>12z:</strong> COOP Morning ~12 UTC reports made between 5 AM
    and 11 AM local time.  Computed ASOS summaries for previous day and for
    12 UTC to 12 UTC period.</li>
</ul></p>

<p><strong>Implementation Notes:</strong>
<ol>
    <li>The choice of a WFO governs the timezone used for the report.</li>
</ol>
</p>

<p><strong>Work in progress, please report bugs!</strong> akrherz@iastate.edu
</p>
"""

from datetime import date
from zoneinfo import ZoneInfo

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.reference import StationAttributes as SA
from pyiem.util import get_autoplot_context, utc
from sqlalchemy import text

PDICT = {
    "state": "By State",
    "wfo": "By NWS Forecast Office",
}
PDICT2 = {
    "12z": "Morning 12 UTC Report",
}
# Unique timezones for WFOs
MAPTZ2SHEFTZ = {
    "Pacific/Guam": "Z",  # TODO
    "America/Phoenix": "P",
    "America/New_York": "E",
    "America/Boise": "M",
    "America/Chicago": "C",
    "America/Indiana/Indianapolis": "ES",
    "America/Detroit": "E",
    "Pacific/Honolulu": "Z",  # TODO
    "America/Puerto_Rico": "E",
    "America/Anchorage": "P",  # TODO
    "America/Los_Angeles": "P",
    "America/Juneau": "P",  # TODO
    "America/Denver": "M",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    return {
        "description": __doc__,
        "data": True,
        "report": True,
        "nopng": True,
        "cache": 120,
        "arguments": [
            {
                "type": "select",
                "name": "by",
                "default": "wfo",
                "label": "Generate RTP for state or WFO:",
                "options": PDICT,
            },
            {
                "type": "state",
                "name": "state",
                "default": "IA",
                "label": "Select State:",
            },
            {
                "type": "networkselect",
                "name": "wfo",
                "default": "DMX",
                "network": "WFO",
                "label": "Select WFO (used to pick timezone for report):",
            },
            {
                "type": "select",
                "name": "report",
                "default": "12z",
                "label": "Select RTP Report Type:",
                "options": PDICT2,
            },
            {
                "type": "date",
                "name": "date",
                "default": date.today().strftime("%Y/%m/%d"),
                "label": "Date of Interest:",
            },
        ],
    }


def get_asos(ctx: dict) -> pd.DataFrame:
    """Figure out the data."""
    params = {
        "date": ctx["date"],
        "wfo": ctx["wfo"],
        "state": ctx["state"],
        "attr": SA.SHEF_6HR_SRC,
    }
    limiter = " wfo = :wfo "
    if ctx["by"] == "state":
        limiter = " state = :state "
    with get_sqlalchemy_conn("mesosite") as conn:
        # Figure out which stations we care about
        stations = pd.read_sql(
            text(f"""
                select id, name, value as snow_src, null as snow,
                null as snowd from stations s LEFT
                JOIN station_attributes a on (s.iemid = a.iemid and
                a.attr = :attr)
                where network ~* 'ASOS' and {limiter} ORDER by id ASC
            """),
            conn,
            index_col="id",
            params=params,
        )
    # If we have any snow_src values, we should go fishing for that data
    if stations["snow_src"].notnull().any():
        # 12z to 12z snow
        ets = utc(ctx["date"].year, ctx["date"].month, ctx["date"].day, 12)
        sts = ets - pd.Timedelta("24 hours")
        with get_sqlalchemy_conn("hads") as conn:
            snowdf = pd.read_sql(
                text(f"""
                select station, valid, substr(key, 1, 3) as shefvar, value
                from raw{ets:%Y} WHERE
                station = ANY(:stations) and
                substr(key, 1, 3) in ('SFQ', 'SFD') and
                valid > :sts and valid <= :ets and value is not null
                ORDER by station asc, valid asc
                """),
                conn,
                params={
                    "stations": stations["snow_src"].dropna().to_list(),
                    "sts": sts,
                    "ets": ets,
                },
            )
            for snowsrc, gdf in snowdf.groupby("station"):
                asosid = stations[stations["snow_src"] == snowsrc].index[0]
                stations.at[asosid, "cnt_6hr"] = len(gdf["valid"].unique())
                snowfall = gdf[gdf["shefvar"] == "SFD"]["value"].sum()
                qobs = gdf[gdf["shefvar"] == "SFQ"]
                if not qobs.empty and qobs["valid"].values[-1] == ets:
                    stations.at[asosid, "snowd"] = qobs["value"].values[-1]
                stations.at[asosid, "snow"] = snowfall

    with get_sqlalchemy_conn("asos") as conn:
        # 6z to 6z high
        ets = utc(ctx["date"].year, ctx["date"].month, ctx["date"].day, 6)
        sts = ets - pd.Timedelta("24 hours")
        highsdf = pd.read_sql(
            text(
                """
    select station,
    max(coalesce(max_tmpf_6hr, tmpf)) as calc_max_tmpf from alldata
    where valid >= :sts and valid < :ets and station = ANY(:stations)
    GROUP by station ORDER by station ASC
"""
            ),
            conn,
            params={
                "stations": stations.index.to_list(),
                "sts": sts,
                "ets": ets,
            },
            index_col="station",
        )
        stations["high"] = highsdf["calc_max_tmpf"]
        # 0z to 12z low
        ets = utc(ctx["date"].year, ctx["date"].month, ctx["date"].day, 12)
        sts = utc(ctx["date"].year, ctx["date"].month, ctx["date"].day, 0)
        lowsdf = pd.read_sql(
            text(
                """
    select station,
    min(coalesce(min_tmpf_6hr, tmpf)) as calc_min_tmpf from alldata
    where valid >= :sts and valid < :ets and station = ANY(:stations)
    GROUP by station ORDER by station ASC
"""
            ),
            conn,
            index_col="station",
            params={
                "stations": stations.index.to_list(),
                "sts": sts,
                "ets": ets,
            },
        )
        stations["low"] = lowsdf["calc_min_tmpf"]
        # 12z to 12z precip
        ets = utc(ctx["date"].year, ctx["date"].month, ctx["date"].day, 12)
        sts = ets - pd.Timedelta("24 hours")
        precipdf = pd.read_sql(
            text(
                """
    with obs as (
    select station, date_trunc('hour', valid) as ts,
    max(p01i) as precip from alldata
    where valid >= :sts and valid < :ets and station = ANY(:stations)
    GROUP by station, ts)
    select station, sum(precip) as precip from obs
    GROUP by station ORDER by station ASC
"""
            ),
            conn,
            params={
                "stations": stations.index.to_list(),
                "sts": sts,
                "ets": ets,
            },
            index_col="station",
        )
        stations["precip"] = precipdf["precip"]
    # drop any rows with all missing data, except `name`
    stations = stations.dropna(how="all", subset=["high", "low", "precip"])
    return stations


def get_obsdf(ctx: dict) -> pd.DataFrame:
    """Figure out the data."""
    params = {
        "date": ctx["date"],
        "wfo": ctx["wfo"],
        "state": ctx["state"],
    }
    limiter = " and t.wfo = :wfo "
    if ctx["by"] == "state":
        limiter = " and t.state = :state "
    sql = f"""
        select t.id, t.name, s.snow, s.snowd, s.pday, s.max_tmpf, s.min_tmpf,
        s.coop_valid
        from summary s JOIN stations t on (s.iemid = t.iemid)
        WHERE s.day = :date {limiter} and t.network ~* 'COOP' and
        coop_valid is not null
        ORDER by t.id ASC
    """
    with get_sqlalchemy_conn("iem") as conn:
        obs = pd.read_sql(text(sql), conn, params=params)
    if not obs.empty:
        obs["coop_local_valid"] = obs["coop_valid"].dt.tz_convert(
            ctx["_nt"].sts[ctx["wfo"]]["tzname"],
        )
        if ctx["report"] == "12z":
            # Require obs to be between 5 and 10 AM local time
            obs = obs[
                (obs["coop_local_valid"].dt.hour >= 5)
                & (obs["coop_local_valid"].dt.hour <= 10)
            ]
    return obs


def pp(val, width, dec):
    """Format a value."""
    if pd.isna(val):
        return " " * (width - 1) + "M"
    return f"{val:.{dec}f}".rjust(width)


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())

    obsdf = get_obsdf(ctx)
    asosdf = get_asos(ctx)
    wfo = ctx["wfo"]
    dt = ctx["date"]
    tzname = ctx["_nt"].sts[wfo]["tzname"]
    zc = MAPTZ2SHEFTZ[tzname]
    lnow = utc().astimezone(ZoneInfo(tzname))
    pil = wfo if ctx["by"] == "wfo" else f"{ctx['state']} "
    report = (
        "000 \n"
        f"ASUS63 XIEM {utc():%d%H%M}\n"
        f"RTP{pil}\n\n"
        "IEM Generated Regional Temperature and Precipitation Report\n"
        "Iowa State University Ames IA\n"
        f"{lnow:%I%M %p %a %b %d %Y %Z}\n\n"
        "COOP Reports\n\n"
        f".BR {wfo} {dt:%Y%m%d} {zc} DH07/TAIRZX/TAIRZN/PPDRZZ/SFDRZZ/SDIRZZ\n"
    )
    for _, row in obsdf.iterrows():
        report += (
            f"{row['id']:6s}:{row['name']:25.25s}: "
            f"DH{row['coop_local_valid'].strftime('%H%M')}/ "
            f"{pp(row['max_tmpf'], 4, 0)} /{pp(row['min_tmpf'], 4, 0)} /"
            f"{pp(row['pday'], 5, 2)} /{pp(row['snow'], 5, 1)} /"
            f"{pp(row['snowd'], 5, 1)}\n"
        )
    report += ".END\n\n"

    if asosdf["snow_src"].notnull().any():
        report += (
            "ASOS Reports with 6 Hour Snowfall Supplemented\n\n"
            f".BR {wfo} {dt:%Y%m%d} Z DH06/TAIRVX/DH12/TAIRVP/PPDRVZ/"
            "SFDRZZ/SDIRZZ\n"
            ": Station Name and Number of 6 Hour Reports\n"
            ": 06Z (yesterday) to 06Z HIGH TEMPERATURE\n"
            ": 00Z TO 12Z TODAY LOW TEMPERATURE\n"
            ": 12Z YESTERDAY TO 12Z TODAY RAINFALL\n"
            ": 12Z YESTERDAY TO 12Z TODAY SNOWFALL\n"
            ": 12Z TODAY SNOW DEPTH\n"
        )
        for sid, row in asosdf[asosdf["snow_src"].notna()].iterrows():
            cnt = 0 if pd.isna(row["cnt_6hr"]) else int(row["cnt_6hr"])
            quorum = f"({cnt}/4)"
            report += (
                f"{sid:6s}:{row['name']:19.19s}{quorum}: "
                f"{pp(row['high'], 4, 0)} /{pp(row['low'], 4, 0)} /"
                f"{pp(row['precip'], 5, 2)} /"
                f"{pp(row['snow'], 5, 1)} /"
                f"{pp(row['snowd'], 5, 0)}\n"
            )
        report += ".END\n\n"

    report += (
        "ASOS Reports\n\n"
        f".BR {wfo} {dt:%Y%m%d} Z DH06/TAIRVX/DH12/TAIRVP/PPDRVZ\n"
        ": 06Z (yesterday) to 06Z HIGH TEMPERATURE\n"
        ": 00Z TO 12Z TODAY LOW TEMPERATURE\n"
        ": 12Z YESTERDAY TO 12Z TODAY RAINFALL\n"
    )
    for sid, row in asosdf[asosdf["snow_src"].isna()].iterrows():
        report += (
            f"{sid:6s}:{row['name']:25.25s}: "
            f"{pp(row['high'], 4, 0)} /{pp(row['low'], 4, 0)} /"
            f"{pp(row['precip'], 5, 2)}\n"
        )
    report += ".END\n\n"

    return None, obsdf, report + "$$\n"
