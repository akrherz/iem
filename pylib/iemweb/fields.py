"""Stanardized fields used as parameters in Models."""

from datetime import date
from typing import Annotated

from pydantic import Field

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
_SF = Field(
    description="Two letter (uppercase) United States code",
    pattern="^[A-Z]{2}$",
)
STATE_FIELD = Annotated[str, _SF]
STATE_FIELD_OPTIONAL = Annotated[str | None, _SF]

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
