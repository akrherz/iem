"""Typed autoplot parameters.

An autoplot module may define a ``Params`` model::

    class Params(AutoplotParams):
        station: Annotated[str, ARG_STATION] = "IATAME"
        threshold: Annotated[int, IntArg(label="Threshold")] = 93

    def get_description() -> PlotDescription:
        return PlotDescription.from_model(Params, description=__doc__)

    def plotter(ctx: Params): ...

The one model both describes the widgets and types the context handed to the
plotter.  Parsing of the request stays with ``get_autoplot_context``, which
is lenient (bad values fall back to defaults), the model then validates and
types its output.
"""

import re
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from iemweb.autoplot.description import Arg, SDayArg

_SLASH_DATE = re.compile(r"^\d{4}/\d{2}/\d{2}")
_HHMM = re.compile(r" (\d{2})(\d{2})$")


class AutoplotParams(BaseModel):
    """Base class for an autoplot ``Params`` model.

    Keys added by the context builder that are not widgets (``_nt``,
    ``network``, ``_r``, ...) are kept as extras.  Dict style access remains
    so that helpers expecting the legacy ``ctx`` dict keep working.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    dpi: int | None = None
    sname: str | None = Field(default=None, alias="_sname")

    @model_validator(mode="before")
    @classmethod
    def _prepare_input(cls, data: Any) -> Any:
        """Apply widget defaults, then convert sday values to dates.

        A required field (no model default) falls back to its widget default
        when absent, so the script can be called with no arguments.  An
        ``mmdd`` (or legacy ``yyyy-mm-dd``) sday becomes a date in 2000.
        """
        if not isinstance(data, dict):
            return data
        data = dict(data)
        for name, fld in cls.model_fields.items():
            key_in = next((k for k in (name, fld.alias) if k in data), None)
            if key_in is None and fld.is_required():
                arg = next(
                    (m for m in fld.metadata if isinstance(m, Arg)), None
                )
                if arg is not None and arg.default is not None:
                    dflt = arg.default
                    dflt = dflt() if callable(dflt) else dflt
                    if isinstance(dflt, str) and _SLASH_DATE.match(dflt):
                        # Widget defaults use yyyy/mm/dd, pydantic wants -
                        dflt = dflt.replace("/", "-", 2)
                        # and hh:mm, not hhmm
                        dflt = _HHMM.sub(r" \1:\2", dflt)
                    data[name] = dflt
        for name, fld in cls.model_fields.items():
            if not any(isinstance(m, SDayArg) for m in fld.metadata):
                continue
            for key in (name, fld.alias):
                val = data.get(key)
                if not isinstance(val, str):
                    continue
                try:
                    if "-" in val:
                        data[key] = datetime.strptime(val[:10], "%Y-%m-%d")
                    else:
                        data[key] = datetime.strptime(f"2000{val}", "%Y%m%d")
                    data[key] = data[key].date()
                except ValueError:
                    pass  # let pydantic report the bad value
        return data

    @classmethod
    def _field_name(cls, key: str) -> str | None:
        """Map a dict key (field name or alias) to a field name."""
        for name, fld in cls.model_fields.items():
            if key in (name, fld.alias):
                return name
        return None

    def __getitem__(self, key: str) -> Any:
        """Dict style read."""
        if (name := self._field_name(key)) is not None:
            return getattr(self, name)
        return (self.model_extra or {})[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Dict style write."""
        if (name := self._field_name(key)) is not None:
            setattr(self, name, value)
        elif self.model_extra is not None:
            self.model_extra[key] = value

    def __contains__(self, key: object) -> bool:
        """Was this key provided?  Mirrors the legacy ctx dict."""
        if not isinstance(key, str):
            return False
        if (name := self._field_name(key)) is not None:
            return name in self.model_fields_set
        return key in (self.model_extra or {})

    def get(self, key: str, default: Any = None) -> Any:
        """Dict style read with a default."""
        return self[key] if key in self else default

    def pop(self, key: str, *default: Any) -> Any:
        """Dict style pop, the key is no longer seen by ``get``."""
        if key not in self:
            if default:
                return default[0]
            raise KeyError(key)
        value = self[key]
        if (name := self._field_name(key)) is not None:
            self.model_fields_set.discard(name)
        else:
            (self.model_extra or {}).pop(key, None)
        return value
