"""Synthetic unit tests for the accumulated station plot."""

import pandas as pd
from iemweb.autoplot.scripts100.p172 import average_accumulations


def test_average_accumulations_keeps_observation_day_index():
    """The average series must stay indexed by day number, not timestamp."""
    frame = pd.DataFrame(
        {
            "row": [1, 2, 3, 1, 2, 3],
            "accum": [1.0, 3.0, 6.0, 2.0, 4.0, 9.0],
        },
        index=pd.date_range("2025-01-01", periods=6),
    )

    result = average_accumulations(frame)

    assert result.index.tolist() == [1, 2, 3]
    assert result["accum"].tolist() == [1.5, 3.5, 3.5]
