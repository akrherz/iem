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

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AutoplotParams(BaseModel):
    """Base class for an autoplot ``Params`` model.

    Keys added by the context builder that are not widgets (``_nt``,
    ``network``, ``_r``, ...) are kept as extras.  Dict style access remains
    so that helpers expecting the legacy ``ctx`` dict keep working.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    dpi: int | None = None
    sname: str | None = Field(default=None, alias="_sname")

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
