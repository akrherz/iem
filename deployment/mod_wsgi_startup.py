"""Invoked at mod-wsgi startup to get certain libraries loaded!"""

import os

os.environ["PROJ_LIB"] = "/opt/miniconda3/envs/prod/share/proj"
os.environ["MPLCONFIGDIR"] = "/var/cache/matplotlib"

from pyiem.plot.use_agg import plt
import pandas

import cartopy

if cartopy.config.get("pre_existing_data_dir", "") == "":
    cartopy.config[
        "pre_existing_data_dir"
    ] = "/opt/miniconda3/envs/prod/share/cartopy"
