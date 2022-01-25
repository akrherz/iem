"""Invoked at mod-wsgi startup to get certain libraries loaded!"""
# pylint: disable=unused-import

import os
import warnings

envpath = "/opt/miniconda3/envs/prod"
os.environ["PROJ_LIB"] = f"{envpath}/share/proj"
os.environ["MPLCONFIGDIR"] = "/var/cache/matplotlib"
os.environ["CARTOPY_OFFLINE_SHARED"] = f"{envpath}/share/cartopy"

# Stop pandas UserWarning for now
warnings.filterwarnings("ignore", category=UserWarning)

from pyiem.plot.use_agg import plt
import pandas

# TODO remove someday when pyiem is updated
import cartopy

if cartopy.config.get("pre_existing_data_dir", "") == "":
    cartopy.config["pre_existing_data_dir"] = f"{envpath}/share/cartopy"
