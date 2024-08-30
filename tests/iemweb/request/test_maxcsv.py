"""Test things in request/maxcsv.py"""

import numpy as np
from iemweb.request.maxcsv import figure_phase


def test_moon_phase_calc():
    """Test the moon phase calculation"""
    # lame
    for p1 in np.arange(0, 1.1, 0.1):
        for p2 in np.arange(0, 1.1, 0.1):
            assert figure_phase(p1, p2) is not None
