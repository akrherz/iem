"""Excerise the imports."""

import pytest
from iemweb.autoplot import data as autoplot_data
from iemweb.autoplot import import_script


def genmod():
    """Generate modules to test against."""
    for plot in autoplot_data["plots"]:
        for entry in plot["options"]:
            pid = entry["id"]
            yield import_script(pid)


@pytest.mark.parametrize("mod", genmod())
def test_import_all_scripts(mod):
    """Just import things."""
    assert isinstance(mod.get_description(), dict)
