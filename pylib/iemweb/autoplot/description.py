"""Typed description of an autoplot, returned by ``get_description()``.

The web frontend and ``get_autoplot_context`` still consume plain dicts, so
``PlotDescription.to_dict`` is the boundary.  Use :func:`describe` to get a
dict from any autoplot module, whether it returns a legacy dict or a
``PlotDescription``.
"""

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field, fields, replace
from typing import Any, ClassVar

from pydantic import BaseModel
from pydantic_core import PydanticUndefined

Scalar = str | int | float
# Evaluated each time the description is built, for dates relative to now
Lazy = Scalar | Callable[[], Scalar]


@dataclass(frozen=True, kw_only=True)
class Arg:
    """Base widget definition.  Subclasses set the ``type`` string."""

    type: ClassVar[str]
    virtual: ClassVar[bool] = False
    # Left empty when used as ``Annotated`` metadata on a params model field,
    # the field name is filled in by ``PlotDescription.from_model``.
    name: str = ""
    label: str
    # A callable is evaluated by ``PlotDescription.from_model``, so a dynamic
    # default (today's date) is computed per request, not at import time.
    default: Lazy | None = None
    optional: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Return the legacy dict, omitting fields left at their default."""
        res: dict[str, Any] = {"type": self.type}
        for fld in fields(self):
            val = getattr(self, fld.name)
            if callable(val):
                val = val()
            if fld.name in ("name", "label", "default") or val != fld.default:
                res[fld.name] = val
        return res


@dataclass(frozen=True, kw_only=True)
class SelectArg(Arg):
    """Dropdown of ``options`` (value -> label)."""

    type: ClassVar[str] = "select"
    options: Mapping[str, str]
    alias: Mapping[str, str] | None = None
    oldname: str | None = None
    multiple: bool = False
    all: bool = False
    showvalue: bool = False


@dataclass(frozen=True, kw_only=True)
class FilterVarArg(Arg):
    """Variable/comparator/threshold filter widget."""

    type: ClassVar[str] = "filtervar"
    options: Mapping[str, str]
    comp_default: str | None = None
    t_default: float | None = None


@dataclass(frozen=True, kw_only=True)
class NumberArg(Arg):
    """Numeric widget with optional bounds."""

    min: Lazy | None = None
    max: Lazy | None = None
    gt: Scalar | None = None
    ge: Scalar | None = None
    lt: Scalar | None = None
    le: Scalar | None = None


@dataclass(frozen=True, kw_only=True)
class IntArg(NumberArg):
    """Integer."""

    type: ClassVar[str] = "int"


@dataclass(frozen=True, kw_only=True)
class FloatArg(NumberArg):
    """Float."""

    type: ClassVar[str] = "float"


@dataclass(frozen=True, kw_only=True)
class YearArg(Arg):
    """Year."""

    type: ClassVar[str] = "year"
    min: Lazy | None = None
    max: Lazy | None = None
    minval: int | None = None


@dataclass(frozen=True, kw_only=True)
class DateArg(Arg):
    """Date."""

    type: ClassVar[str] = "date"
    min: Lazy | None = None
    max: Lazy | None = None


@dataclass(frozen=True, kw_only=True)
class DateTimeArg(DateArg):
    """Date and time."""

    type: ClassVar[str] = "datetime"


@dataclass(frozen=True, kw_only=True)
class NetworkArg(Arg):
    """Widgets keyed to a network (or networks)."""

    network: str | list[str]
    all: bool = False


@dataclass(frozen=True, kw_only=True)
class StationArg(NetworkArg):
    """Station."""

    type: ClassVar[str] = "station"


@dataclass(frozen=True, kw_only=True)
class ZStationArg(NetworkArg):
    """Station (ASOS style identifiers)."""

    type: ClassVar[str] = "zstation"


@dataclass(frozen=True, kw_only=True)
class NetworkSelectArg(NetworkArg):
    """Network selector."""

    type: ClassVar[str] = "networkselect"


@dataclass(frozen=True, kw_only=True)
class SidArg(NetworkArg):
    """Station id."""

    type: ClassVar[str] = "sid"
    include_climodat: bool = False


@dataclass(frozen=True, kw_only=True)
class StateArg(Arg):
    """US state."""

    type: ClassVar[str] = "state"
    contiguous: bool = False


@dataclass(frozen=True, kw_only=True)
class TextArg(Arg):
    """Free text."""

    type: ClassVar[str] = "text"
    pattern: str | None = None


@dataclass(frozen=True, kw_only=True)
class CmapArg(Arg):
    """Colormap."""

    type: ClassVar[str] = "cmap"


@dataclass(frozen=True, kw_only=True)
class CSectorArg(Arg):
    """Map sector."""

    type: ClassVar[str] = "csector"


@dataclass(frozen=True, kw_only=True)
class DatArg(Arg):
    """Legacy date widget."""

    type: ClassVar[str] = "dat"


@dataclass(frozen=True, kw_only=True)
class DayArg(Arg):
    """Day of month."""

    type: ClassVar[str] = "day"


@dataclass(frozen=True, kw_only=True)
class FemaArg(Arg):
    """FEMA region."""

    type: ClassVar[str] = "fema"


@dataclass(frozen=True, kw_only=True)
class HourArg(Arg):
    """Hour."""

    type: ClassVar[str] = "hour"


@dataclass(frozen=True, kw_only=True)
class ZHourArg(Arg):
    """UTC hour."""

    type: ClassVar[str] = "zhour"


@dataclass(frozen=True, kw_only=True)
class MonthArg(Arg):
    """Month."""

    type: ClassVar[str] = "month"


@dataclass(frozen=True, kw_only=True)
class SDayArg(Arg):
    """Month and day."""

    type: ClassVar[str] = "sday"


@dataclass(frozen=True, kw_only=True)
class PhenomenaArg(Arg):
    """VTEC phenomena."""

    type: ClassVar[str] = "phenomena"


@dataclass(frozen=True, kw_only=True)
class SignificanceArg(Arg):
    """VTEC significance."""

    type: ClassVar[str] = "significance"


@dataclass(frozen=True, kw_only=True)
class UgcArg(Arg):
    """UGC code."""

    type: ClassVar[str] = "ugc"


@dataclass(frozen=True, kw_only=True)
class VtecPsArg(Arg):
    """VTEC phenomena and significance."""

    type: ClassVar[str] = "vtec_ps"
    virtual: ClassVar[bool] = True


@dataclass(frozen=True, kw_only=True)
class PlotDescription:
    """Everything the frontend and context builder need about an autoplot."""

    description: str
    arguments: list[Arg | dict[str, Any]] = field(default_factory=list)
    data: bool | None = None
    cache: int | None = None
    report: bool = False
    nopng: bool = False
    nass: bool = False
    highcharts: bool = False
    frontend: str | None = None
    text: bool = False
    plotmetadata: bool | None = None
    defaults: dict[str, Any] | None = None
    gallery: dict[str, Any] | None = None

    @classmethod
    def from_model(
        cls, model: type[BaseModel], **kwargs: Any
    ) -> "PlotDescription":
        """Build a description with ``arguments`` derived from a params model.

        Each field annotated with an :class:`Arg` instance becomes a widget.
        The field name becomes the widget name and the field default (or
        ``default_factory`` result) the widget default.  A field defaulting
        to ``None`` is an optional widget, which keeps the widget default
        given on the :class:`Arg` (what the form shows when enabled).
        """
        args: list[Arg | dict[str, Any]] = []
        for name, fld in model.model_fields.items():
            tmpl = next((m for m in fld.metadata if isinstance(m, Arg)), None)
            if tmpl is None:
                continue
            default = fld.get_default(call_default_factory=True)
            optional = tmpl.optional or default is None
            if tmpl.virtual:
                # Widget writes other ctx keys, the field default is unused
                optional, default = tmpl.optional, None
            if default is PydanticUndefined or default is None:
                default = tmpl.default
            if callable(default):
                default = default()
            args.append(
                replace(tmpl, name=name, default=default, optional=optional)
            )
        return cls(arguments=args, **kwargs)

    def to_dict(self) -> dict[str, Any]:
        """Return the legacy dict, omitting fields left at their default."""
        res: dict[str, Any] = {}
        for fld in fields(self):
            val = getattr(self, fld.name)
            if fld.name == "arguments":
                val = [a.to_dict() if isinstance(a, Arg) else a for a in val]
            if fld.name in ("description", "arguments") or (
                val != fld.default
            ):
                res[fld.name] = val
        return res


def normalize(desc: "PlotDescription | dict[str, Any]") -> dict[str, Any]:
    """Return a fresh legacy dict from either description flavor."""
    if isinstance(desc, PlotDescription):
        return desc.to_dict()
    res = dict(desc)
    res["arguments"] = [
        a.to_dict() if isinstance(a, Arg) else a
        for a in res.get("arguments", [])
    ]
    return res


def describe(mod: Any) -> dict[str, Any]:
    """Return the dict description of an autoplot module."""
    return normalize(mod.get_description())
