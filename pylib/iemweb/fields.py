"""Stanardized fields used as parameters in Models."""

import re
from datetime import date
from typing import Annotated
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import (
    AfterValidator,
    BeforeValidator,
    Field,
    WithJsonSchema,
)

# --------------
# Never required, so no optional variant
CALLBACK_FIELD = Annotated[
    str | None,
    Field(
        description=(
            "Legacy JSON-P style callback.  It is likely best to not "
            "depend on this usage. The IEM website has a permissive CORS. "
        ),
        pattern=r"^[A-Za-z_$][0-9A-Za-z_$]*(?:\.[A-Za-z_$][0-9A-Za-z_$]*)*$",
        max_length=64,
    ),
]

# -------------
_DOM = Field(
    description="Day of the month",
    le=31,
    ge=1,
)
DAY_OF_MONTH_FIELD = Annotated[int, _DOM]
DAY_OF_MONTH_FIELD_OPTIONAL = Annotated[int | None, _DOM]

# --------------
_LATF = Field(
    description="Latitude (decimal degrees) of point of interest",
    ge=-90,
    le=90,
)
LATITUDE_FIELD = Annotated[float, _LATF]
LATITUDE_FIELD_OPTIONAL = Annotated[float | None, _LATF]

# --------------
_LONF = Field(
    description="Longitude (decimal degrees) of point of interest",
    ge=-180,
    le=180,
)
LONGITUDE_FIELD = Annotated[float, _LONF]
LONGITUDE_FIELD_OPTIONAL = Annotated[float | None, _LONF]


# --------------
_MF = Field(
    description="Month of the year",
    le=12,
    ge=1,
)
MONTH_FIELD = Annotated[int, _MF]
MONTH_FIELD_OPTIONAL = Annotated[int | None, _MF]

# --------------
_STF = Field(
    description=(
        "Either provide a single value, multiple parameters each with a "
        "single value, or a comma-separated list of values.  The context here "
        "is a list of station identifiers.  All lowercase letters are "
        "converted to uppercase."
    ),
)


def _clean_station_strings(val: list[str]) -> list[str]:
    """Clean up the station strings."""
    station_re = re.compile(r"^[A-Za-z0-9_]+$")
    for v in val:
        if not station_re.match(v.strip()):
            raise ValueError(f"Invalid station identifier: {v}")
    return [v.strip().upper() for v in val if v.strip()]


STATION_LIST_FIELD = Annotated[
    list,
    BeforeValidator(lambda v: v.split(",") if isinstance(v, str) else v),
    AfterValidator(_clean_station_strings),
    _STF,
    WithJsonSchema({"type": "string"}, mode="serialization"),
]

# --------------
_SF = Field(
    description="Two letter (uppercase) United States code",
    pattern="^[A-Z]{2}$",
)
STATE_FIELD = Annotated[str, _SF]
STATE_FIELD_OPTIONAL = Annotated[str | None, _SF]

# --------------
_TZF = Field(
    description=(
        "A time zone string specified by IANA.  Common examples include "
        "'America/Chicago', 'UTC', and 'Etc/UTC'.  The code implementation "
        "passes this provided string to the python ZoneInfo library."
    )
)


def _validate_tz(val: str):
    """Ensure we can use this."""
    # Opinionated, but we have historically accepted these two values as UTC
    if val in ["", "etc/utc"]:
        return "UTC"
    try:
        ZoneInfo(val)
    except ZoneInfoNotFoundError as exp:
        raise ValueError(f"Unknown timezone: {val}") from exp
    return val


TZ_FIELD = Annotated[
    str,
    BeforeValidator(_validate_tz),
    _TZF,
]
TZ_FIELD_OPTIONAL = Annotated[
    str | None,
    BeforeValidator(_validate_tz),
    _TZF,
]

# --------------
_VSF = Field(
    description=("One character (uppercase) VTEC significance code."),
    pattern="^[A-Z]$",
)
VTEC_SIG_FIELD = Annotated[str, _VSF]
VTEC_SIG_FIELD_OPTIONAL = Annotated[str | None, _VSF]

# --------------
_VPF = Field(
    description=("Two character (uppercase) VTEC phenomena code."),
    pattern="^[A-Z]{2}$",
)
VTEC_PH_FIELD = Annotated[str, _VPF]
VTEC_PH_FIELD_OPTIONAL = Annotated[str | None, _VPF]

# --------------
_VYF = Field(
    description=(
        "Year between 1986 and the current year for which the IEM "
        "database may have VTEC records."
    ),
    ge=1986,
    le=date.today().year + 1,  # Forgive a bit
)
VTEC_YEAR_FIELD = Annotated[int, _VYF]
VTEC_YEAR_FIELD_OPTIONAL = Annotated[int | None, _VYF]

# -----------------
_YF = Field(
    description=("Year field."),
    ge=1850,
    le=date.today().year + 1,  # Forgive a bit
)
YEAR_FIELD = Annotated[int, _YF]
YEAR_FIELD_OPTIONAL = Annotated[int | None, _YF]
