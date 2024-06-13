"""Test iemweb.autoplot.barchar module."""

import pandas as pd
import pytest
from iemweb.autoplot.barchart import barchar_with_top10
from pyiem.plot import figure


@pytest.mark.mpl_image_compare(tolerance=0.02)
def test_barchart_simple():
    """Test the barchart module."""
    fig = figure()
    df = pd.DataFrame(
        {
            "a": range(20),
        },
        index=pd.Index(list(range(2000, 2020)), name="Year"),
    )
    barchar_with_top10(fig, df, "a")
    return fig
