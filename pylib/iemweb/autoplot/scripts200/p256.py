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
$ wget -O RTPIA.txt 'https://mesonet.agron.iastate.edu/plotting/auto/plot/256/fmt:text::date:2024-06-10&wfo=DMX&state=IA&by=state&report=12z'
$ cat RTPIA.txt | dcshef
</pre>

<p>Generate a RTPBOU report for the morning of 21 May 2024:</p>
<pre>
$ wget -O RTPBOU.txt 'https://mesonet.agron.iastate.edu/plotting/auto/plot/256/fmt:text::date:2024-05-21&wfo=BOU&by=wfo&report=12z'
$ cat RTPBOU.txt | dcshef
</pre>

<p><strong>Report Types:</strong>
<ul>
    <li><strong>12z:</strong> Morning ~12 UTC reports made between 5 AM and
    11 AM local time.</li>
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
    report += ".END\n\n$$\n"

    return None, obsdf, report
