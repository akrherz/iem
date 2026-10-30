"""Test typed autoplot descriptions."""

import glob
import re
from datetime import date
from typing import Annotated

import pytest
from iemweb.autoplot import ARG_STATION, import_script
from iemweb.autoplot.description import (
    IntArg,
    PlotDescription,
    SelectArg,
    YearArg,
    describe,
    normalize,
)
from iemweb.autoplot.params import AutoplotParams
from pydantic import Field
from pyiem.autoplot import get_autoplot_context


def test_arg_to_dict_omits_defaults():
    """Unset optional fields do not leak into the legacy dict."""
    arg = IntArg(name="x", label="X", default=1, ge=0)
    assert arg.to_dict() == {
        "type": "int",
        "name": "x",
        "label": "X",
        "default": 1,
        "ge": 0,
    }


def test_description_to_dict():
    """Mixed typed and legacy dict arguments both come out as dicts."""
    desc = PlotDescription(
        description="hi",
        cache=60,
        plotmetadata=False,
        arguments=[
            SelectArg(name="a", label="A", default="x", options={"x": "X"}),
            {"type": "int", "name": "b", "label": "B", "default": 1},
        ],
    )
    res = desc.to_dict()
    assert res["cache"] == 60
    assert res["plotmetadata"] is False
    assert "data" not in res
    assert [a["name"] for a in res["arguments"]] == ["a", "b"]
    assert all(isinstance(a, dict) for a in res["arguments"])


def test_normalize_legacy_dict():
    """Legacy dicts are copied and their typed arguments converted."""
    legacy = {"description": "x", "arguments": [ARG_STATION]}
    res = normalize(legacy)
    assert res["arguments"][0]["type"] == "station"
    assert isinstance(legacy["arguments"][0], type(ARG_STATION))


def test_p1():
    """Test the converted pilot script."""
    res = describe(import_script(1))
    assert res["data"] is True
    assert res["arguments"][0]["name"] == "station"


def test_from_model():
    """Widgets derive from a params model, in field order."""

    class Params(AutoplotParams):
        a: Annotated[int, IntArg(label="A", ge=0)] = 3
        b: Annotated[int, YearArg(label="B")] = Field(
            default_factory=lambda: 7
        )
        c: Annotated[str | None, SelectArg(label="C", options={"x": "X"})] = (
            None
        )
        plain: int = 1

    res = PlotDescription.from_model(Params, description="d").to_dict()
    args = res["arguments"]
    assert [a["name"] for a in args] == ["a", "b", "c"]
    assert args[0] == {
        "type": "int",
        "name": "a",
        "label": "A",
        "default": 3,
        "ge": 0,
    }
    assert args[1]["default"] == 7
    assert args[2]["optional"] is True


def test_p1_params_roundtrip():
    """The typed context matches the legacy dict context."""
    mod = import_script(1)
    ctx = get_autoplot_context(
        {"station": "IA0200", "num1": "3", "dpi": "90"}, describe(mod)
    )
    params = mod.Params.model_validate(ctx)
    assert params.num1 == 3
    assert params.dpi == 90
    assert params.sname == ctx["_sname"] == params["_sname"]
    assert "year" in params
    assert "nope" not in params
    assert params.get("nope", 1) == 1
    params["_e"] = "x"
    assert params["_e"] == "x"
    # Extras from the context builder survive
    assert params["_nt"] is ctx["_nt"]


@pytest.mark.parametrize(
    "fn", glob.glob("pylib/iemweb/autoplot/scripts*/p*.py")
)
def test_all_scripts_describe(fn):
    """Every autoplot normalizes to a dict with plain-dict arguments."""
    pidx = int(re.search(r"p(\d+)\.py", fn).group(1))
    res = describe(import_script(pidx))
    assert isinstance(res["description"], str)
    assert all(isinstance(a, dict) for a in res["arguments"])


def test_optional_widget_keeps_widget_default():
    """An optional field is absent by default, but the widget has a default."""
    mod = import_script(92)
    arg = next(a for a in describe(mod)["arguments"] if a["name"] == "edate")
    assert arg["optional"] is True
    assert arg["default"] == date.today().strftime("%Y/%m/%d")


def test_p92_optional_roundtrip():
    """The optional date is absent unless provided, then a real date."""
    mod = import_script(92)
    cfg = describe(mod)
    params = mod.Params.model_validate(get_autoplot_context({}, cfg))
    assert params.edate is None
    assert "edate" not in params
    ctx = get_autoplot_context({"edate": "2025-02-03", "e": "yes"}, cfg)
    params = mod.Params.model_validate(ctx)
    assert params.edate == date(2025, 2, 3)
    assert params.e == "yes"


def test_p102_multiple_optional_networkselect():
    """Optional multi-select is a list when given, absent otherwise."""
    mod = import_script(102)
    cfg = describe(mod)
    args = {a["name"]: a for a in cfg["arguments"]}
    assert args["station"]["type"] == "networkselect"
    assert args["station"]["all"] is True
    assert args["ltype"]["multiple"] is True
    assert args["ltype"]["optional"] is True
    params = mod.Params.model_validate(get_autoplot_context({}, cfg))
    assert params.ltype is None
    ctx = get_autoplot_context({"ltype": ["TORNADO", "BOGUS"]}, cfg)
    params = mod.Params.model_validate(ctx)
    assert params.ltype == ["TORNADO"]
    assert params.station == "DMX"
    assert params["_nt"] is ctx["_nt"]


def test_p210_lazy_datetime_bounds_and_runtime_options():
    """Datetime defaults/bounds are lazy and select options are runtime."""
    mod = import_script(210)
    cfg = describe(mod)
    args = {a["name"]: a for a in cfg["arguments"]}
    assert args["ets"]["max"].endswith(" 2359")
    assert args["sts"]["default"].endswith("/01/01 0000")
    assert len(args["pil"]["options"]) > 10
    params = mod.Params.model_validate(get_autoplot_context({}, cfg))
    assert params.sts.month == 1
    assert params.cmap == "jet"
