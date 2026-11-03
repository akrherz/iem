"""The frontend to autoplot content generation.

Typically called as a Rewrite from Apache.

"""

import json
import os
import pathlib
import sys
import tempfile
import traceback
from collections.abc import Callable
from datetime import UTC
from io import BytesIO
from typing import Annotated
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import rasterio
from matplotlib.figure import Figure
from pandas.api.types import is_datetime64_any_dtype as isdt
from PIL import Image
from pydantic import Field, ValidationError, field_validator
from pyiem.autoplot import get_autoplot_context
from pyiem.exceptions import (
    BadWebRequest,
    IncompleteWebRequest,
    NoDataFound,
    UnknownStationException,
)
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import (
    TELEMETRY,
    CGIModel,
    emit_to_sidedoor,
    error_log,
    iemapp,
    write_telemetry,
)
from pymemcache.client import Client
from pymemcache.exceptions import MemcacheIllegalInputError

from iemweb.autoplot.description import describe
from iemweb.autoplot.meta import import_script

# Attempt to stop hangs within mod_wsgi and numpy
np.seterr(all="ignore")

AUTOPLOT_TIMING = "AutoplotTiming "
AUTOPLOT_TIMING_URI_MAXLEN = 1024
HTTP200 = "200 OK"
HTTP400 = "400 Bad Request"
HTTP422 = "422 Unprocessable Entity"
HTTP500 = "500 Internal Server Error"


class Schema(CGIModel):
    """See how we are called."""

    fmt: Annotated[str, Field(description="The desired return format.")] = (
        "png"
    )
    p: Annotated[
        int,
        Field(description="Autoplot number", ge=1, le=999),
    ]
    q: Annotated[str, Field(description="Encoded URI parameters.")] = ""

    @field_validator("q", mode="before")
    @classmethod
    def forgive_things_with_q(cls, value: str):
        """Forgive some things found in the wild."""
        if "network:WFO::wfo:PHEB" in value:
            value = value.replace("network:WFO", "network:NWS")
        if "network:WFO::wfo:NHC" in value:
            value = value.replace("network:WFO", "network:NCEP")
        if "network:WFO::wfo:PAAQ" in value:
            value = value.replace("network:WFO", "network:NWS")
        if "network:AWOS" in value:
            value = value.replace("network:AWOS", "network:IA_ASOS")
        return value


def format_geojson_response(gdf: pd.DataFrame, defaultcol: str) -> str:
    """Convert geodataframe into GeoJson."""
    # Avert your eyes children
    jdict = json.loads(gdf.to_json(), parse_float=lambda x: round(float(x), 2))
    jdict["meta"] = {}
    jdict["meta"]["propdefault"] = defaultcol
    jdict["meta"]["proporder"] = [x for x in gdf.columns if x != "geom"]
    return json.dumps(jdict)


def parser(cgistr: str) -> dict[str, str | list[str]]:
    """Convert a CGI string into a dict that gets passed to the plotting
    routine"""
    data: dict[str, str | list[str]] = {}
    # GIGO
    if cgistr.find("::::") > -1:
        raise IncompleteWebRequest("Too many semicolons")
    # Forive a three colon sequence and tokenize by double colons
    for token in cgistr.replace(":::", ": ::").split("::"):
        token2 = [x.strip() for x in token.split(":")]
        if len(token2) != 2:
            continue
        varname, value = token2
        if varname in data:
            curval = data[varname]
            if isinstance(curval, str):
                data[varname] = [curval, value]
            else:
                curval.append(value)
        else:
            data[varname] = value
    return data


def get_response_headers(status, fmt):
    """Figure out some headers"""
    extra = None
    if fmt == "png":
        ctype = "image/png"
    elif fmt == "js":
        ctype = "application/javascript"
    elif fmt == "geojson":
        ctype = "application/vnd.geo+json"
    elif fmt == "svg":
        ctype = "image/svg+xml"
    elif fmt == "pdf":
        ctype = "application/pdf"
    elif fmt in ["csv", "txt"]:
        ctype = "text/plain"
    elif fmt == "geotiff":
        # Can't handle writting error into this type
        if status != HTTP200:
            ctype = "text/plain"
        else:
            ctype = "image/tiff"
            extra = [
                ("Content-Disposition", "attachment;Filename=autoplot.geotiff")
            ]
    else:
        if status != HTTP200:
            ctype = "text/plain"
        else:
            ctype = "application/vnd.ms-excel"
            extra = [("Content-Disposition", "attachment;Filename=iem.xlsx")]
    res = [("Content-type", ctype)]
    if extra:
        res.extend(extra)
    return res


def error_image(message, fmt):
    """Create an error image"""
    fig = Figure(figsize=(8, 6))
    ax = fig.add_subplot(1, 1, 1)
    cleantext = str(message).replace("\t", "")
    msg = f"IEM Autoplot generation resulted in an error\n{cleantext}"
    ax.text(0.5, 0.5, msg, transform=ax.transAxes, ha="center", va="center")
    ax.axis("off")
    ram = BytesIO()
    fig.savefig(ram, format=fmt, dpi=100)
    ram.seek(0)
    fig.clear()
    return ram.read()


def handle_error(exp, fmt, environ: dict) -> bytes | str:
    """Handle errors"""
    _exc_type, _exc_value, exc_traceback = sys.exc_info()
    tb = traceback.extract_tb(exc_traceback)[-1]
    if not isinstance(exp, UnknownStationException):
        error_log(
            environ,
            f"URI:{environ['REQUEST_URI']} {exp.__class__.__name__} "
            f"method:{tb[2]} lineno:{tb[1]} {exp}",
        )
    if not isinstance(
        exp,
        IncompleteWebRequest | NoDataFound | UnknownStationException,
    ):
        traceback.print_exc()
    if fmt in ["png", "svg", "pdf"]:
        return error_image(str(exp), fmt)
    if fmt == "js":
        return f"alert('{exp}');"
    return str(exp)


def get_res_by_fmt(p: int, fmt: str, fdict: dict):
    """Do the work of actually calling things"""
    mod = import_script(p)
    # Ensure fmt and autoplot module jive
    fmt2method = {
        "geotiff": "get_raster",
        "geojson": "geojson",
        "js": "get_highcharts",
    }
    if fmt in fmt2method and not hasattr(mod, fmt2method[fmt]):
        raise BadWebRequest(
            f"Format {fmt} is not supported by this autoplot module"
        )

    meta = describe(mod)
    # When _gallery is set, inspect meta to see if it has something hardcoded
    gallery = fdict.pop("_gallery", None)
    if gallery is not None and meta.get("gallery") is not None:
        fdict.update(meta["gallery"])
    # Allow returning of javascript as a string
    ctx = get_autoplot_context(fdict, meta)
    # Pivot context into typed Params model
    try:
        ctx = mod.Params.model_validate(ctx)
    except ValidationError as exp:
        raise BadWebRequest(f"Invalid parameters: {exp}") from exp
    if fmt == "js":
        # Need to pass the container name
        ctx["_e"] = fdict.get("_e", "ap_container")
        res = mod.get_highcharts(ctx)
    elif fmt == "geotiff":
        (img, imgaff, crs) = mod.get_raster(ctx)
        ram = BytesIO()
        with rasterio.open(
            ram,
            "w",
            driver="GTiff",
            width=img.shape[1],
            height=img.shape[0],
            count=1,
            dtype=img.dtype,
            crs=crs,
            transform=imgaff,
        ) as dst:
            dst.write(img, 1)
        res = [ram.getvalue(), None, None]
    elif fmt == "geojson":
        res = format_geojson_response(*mod.geojson(ctx))
    else:
        res = mod.plotter(ctx)
    # res should be either a 2 or 3 length tuple, rectify this otherwise
    if not isinstance(res, list | tuple):
        res = [res, None, None]
    if len(res) == 2:
        res = [res[0], res[1], None]
    return res, meta


def plot_metadata(fig, start_time, p):
    """Place timestamp on the image"""
    now = utc().astimezone(ZoneInfo("America/Chicago"))
    fig.text(
        0.01,
        0.005,
        f"Generated at {now:%-d %b %Y %-I:%M %p %Z} in "
        f"{((utc() - start_time).total_seconds()):.2f}s",
        va="bottom",
        ha="left",
        fontsize=8,
    )
    fig.text(
        0.99,
        0.005,
        f"IEM Autoplot App #{p}",
        va="bottom",
        ha="right",
        fontsize=8,
    )


def get_mckey(scriptnum: int, fdict: dict, fmt: str) -> str:
    """Figure out what our memcache key should be."""
    vals = []
    for key in fdict:
        # Internal app controls should not be used on the memcache key
        # except when they should be, sigh
        if not key.startswith("_") or key in ["_r", "_"]:
            vals.append(f"{key}:{fdict[key]}")  # noqa
    mckey = (
        f"/plotting/auto/plot/{scriptnum}/{'::'.join(vals)}.{fmt}"
    ).replace(" ", "")
    # If the key does not decode to ascii, this is likely a naughty request
    try:
        mckey.encode("ascii")
    except UnicodeEncodeError as exp:
        raise BadWebRequest("Memcache key is non-ASCII") from exp

    return mckey


def rectify_dpi(fdict: dict):
    """Ensure that the dpi is in good shape."""
    try:
        dpi = int(float(str(fdict.get("dpi", "100"))))
        fdict["dpi"] = str(max(min(dpi, 500), 50))
    except (TypeError, ValueError, OverflowError) as exp:
        raise BadWebRequest("dpi must be a number between 50 and 500") from exp


def check_memcache(mc, mckey: str, forced: bool) -> str | None:
    """Check memcache for the given key."""
    if len(mckey) >= 250 or not forced:
        return None
    try:
        res = mc.get(mckey)
    except MemcacheIllegalInputError as exp:
        raise BadWebRequest("Memcache key is invalid") from exp
    except Exception:
        res = None
    return res


def workflow(mc, environ: dict, query: Schema) -> tuple[str, bytes | str]:
    """we need to return a status and content"""
    # q is the full query string that was rewritten to use by apache
    fdict = parser(query.q)
    # Compute dpi
    rectify_dpi(fdict)
    # Compute memcache key for this request
    mckey = get_mckey(query.p, fdict, query.fmt)
    # Check memcache for this request
    res = check_memcache(mc, mckey, fdict.get("_cb") is None)
    if res:
        return HTTP200, res
    # memcache failed to save us work, so work we do!
    start_time = utc()
    # res should be a 3 length tuple
    try:
        res, meta = get_res_by_fmt(query.p, query.fmt, fdict)
    except (IncompleteWebRequest, NoDataFound, UnknownStationException) as exp:
        return HTTP400, handle_error(exp, query.fmt, environ)
    except BadWebRequest as exp:
        raise BadWebRequest("") from exp
    except Exception as exp:
        # Log this so that my review scripts see it.
        write_telemetry(
            TELEMETRY(
                timing=(utc() - start_time).total_seconds(),
                status_code=500,
                client_addr=environ.get("REMOTE_ADDR", "127.0.0.1"),
                app=environ.get("SCRIPT_NAME"),
                request_uri=environ.get("REQUEST_URI"),
                vhost=environ.get("HTTP_HOST"),
                valid=utc(),
            )
        )
        # Everything else should be considered fatal
        return HTTP500, handle_error(exp, query.fmt, environ)

    [mixedobj, df, report] = res
    # Our output content
    content = ""
    if query.fmt == "js" and isinstance(mixedobj, dict):
        content = f'Highcharts.chart("ap_container", {json.dumps(mixedobj)});'
    elif query.fmt in ["js", "geojson", "geotiff"]:
        content = mixedobj
    elif query.fmt in ["svg", "png", "pdf"]:
        if isinstance(mixedobj, Figure):
            # if our content is a figure, then add some fancy metadata to plot
            if meta.get("plotmetadata", True):
                plot_metadata(mixedobj, start_time, query.p)
            ram = BytesIO()
            mixedobj.savefig(ram, format=query.fmt, dpi=int(str(fdict["dpi"])))
            mixedobj.clear()
            ram.seek(0)
            content = ram.read()
        elif isinstance(mixedobj, Image.Image):
            ram = BytesIO()
            mixedobj.save(ram, query.fmt)
            ram.seek(0)
            content = ram.read()

        elif mixedobj is None:
            return (
                HTTP400,
                error_image(
                    ("plot requested but backend does not support plots"),
                    query.fmt,
                ),
            )
    elif query.fmt == "txt" and report is not None:
        content = report
    elif query.fmt in ["csv", "txt", "xlsx"] and df is not None:
        # If the index is a datetime object, we need to convert it to a string
        if isdt(df.index):
            dtz = df.index.tz
            # We could have timezone or zoneinfo :/
            if dtz is not None and dtz in [
                ZoneInfo("UTC"),  # until everything gets converted...
                UTC,
            ]:
                df.index = df.index.strftime(ISO8601)
            else:
                df.index = df.index.strftime("%Y-%m-%dT%H:%M:%S")
        # Dragons: do timestamp conversion as pandas has many bugs
        for column in df.columns:
            if isdt(df[column]):
                # Careful, only use ISO format when the timezone is UTC
                dtz = df[column].dt.tz
                # We could have timezone or zoneinfo :/
                if dtz is not None and dtz in [
                    UTC,
                    UTC,
                ]:
                    df[column] = df[column].dt.strftime(ISO8601)
                else:
                    df[column] = df[column].dt.strftime("%Y-%m-%dT%H:%M:%S")

        if query.fmt in ["csv", "txt"]:  # Meh on the txt here
            content = df.to_csv(index=(df.index.name is not None), header=True)
        elif query.fmt == "xlsx":
            # Can't write to ram buffer yet, unimplmented upstream
            (_, tmpfn) = tempfile.mkstemp()
            df.index.name = None
            # Need to set engine as xlsx/xls can't be inferred
            with pd.ExcelWriter(tmpfn, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="Sheet1")
            content = pathlib.Path(tmpfn).read_bytes()
            os.unlink(tmpfn)
    else:
        error_log(
            environ,
            f"Undefined edge case: fmt: {query.fmt} "
            f"uri: {environ.get('REQUEST_URI')}",
        )
        return HTTP422, "Undefined edge case encountered"

    dur = int(meta.get("cache", 43200))
    try:
        # we have a 10 MB limit within memcache, so don't write objects bigger
        if len(content) < 9.5 * 1024 * 1024:
            try:
                # Default encoding is ascii for text
                mc.set(
                    mckey.encode("ascii"),
                    (
                        content
                        if isinstance(content, bytes)
                        else content.encode("utf-8")
                    ),
                    dur,
                )
            except Exception:
                # Do not care
                pass
        else:
            error_log(
                environ,
                f"Memcache object too large: {len(content)} "
                f"uri: {environ.get('REQUEST_URI')}",
            )
    except UnicodeEncodeError as exp:
        raise BadWebRequest("Memcache key is non-ASCII") from exp
    except Exception as exp:
        error_log(environ, f"Exception while writting key: {mckey} {exp}")
    if isinstance(mixedobj, Figure):
        mixedobj.clear()
    # scripts/dbutil/mine_autoplot persists the log messages to the database.
    # Keep the URI bounded so the JSON payload stays below common syslog size
    # assumptions; the miner still skips malformed or truncated lines.
    # 141 is local1.notice
    payload = (
        "<141>"
        + AUTOPLOT_TIMING
        + json.dumps(
            {
                "appid": query.p,
                "timing": round((utc() - start_time).total_seconds(), 3),
                "uri": mckey[:AUTOPLOT_TIMING_URI_MAXLEN],
                "cache": dur,
            },
            separators=(",", ":"),
            sort_keys=True,
        )
    ).encode("utf-8")
    emit_to_sidedoor(payload)

    return HTTP200, content


@iemapp(schema=Schema, parse_times=False, allowed_as_list=["ltype"])
def application(environ: dict, start_response: Callable) -> str | bytes:
    """Our Application!"""
    query: Schema = environ["_cgimodel_schema"]
    mc = Client("iem-memcached:11211")
    try:
        # do the work!
        status, output = workflow(mc, environ, query)
    except BadWebRequest as exp:
        raise BadWebRequest("") from exp
    except Exception as exp:
        status = HTTP500
        output = handle_error(exp, query.fmt, environ)
    finally:
        mc.close()
    # Special case for when we are returning a javascript alert
    if query.fmt == "js" and status == HTTP400:
        start_response(HTTP200, get_response_headers(status, query.fmt))
    else:
        # Figure out what our response headers should be
        start_response(status, get_response_headers(status, query.fmt))
    # iemapp rectifies this
    return output
