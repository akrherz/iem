"""Invoked at mod-wsgi startup to get certain libraries loaded!"""

import os

os.environ["PROJ_LIB"] = "/opt/miniconda3/envs/prod/share/proj"
os.environ["MPLCONFIGDIR"] = "/var/cache/matplotlib"

from pyiem.plot.use_agg import plt
import pandas

# Temp debugging
import cartopy

print("cartopy.config is...")
print(cartopy.config)

if cartopy.config.get("pre_existing_data_dir", "") == "":
    cartopy.config[
        "pre_existing_data_dir"
    ] = "/opt/miniconda3/envs/prod/share/cartopy"
