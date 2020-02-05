"""Invoked at mod-wsgi startup to get certain libraries loaded!"""

import os

os.environ["PROJ_LIB"] = "/opt/miniconda3/envs/prod/share/proj"

from pyiem.plot.use_agg import plt
import pandas
