"""Invoked at mod-wsgi startup to get certain libraries loaded!"""
# pylint: disable=unused-import

import os
import sys
import traceback
import warnings

envpath = "/opt/miniconda3/envs/prod"
os.environ["PROJ_LIB"] = f"{envpath}/share/proj"
os.environ["MPLCONFIGDIR"] = "/var/cache/matplotlib"
os.environ["CARTOPY_OFFLINE_SHARED"] = f"{envpath}/share/cartopy"


# https://stackoverflow.com/questions/22373927/get-traceback-of-warnings
def warn_with_traceback(
    message, category, filename, lineno, file=None, line=None
):

    log = file if hasattr(file, "write") else sys.stderr
    traceback.print_stack(file=log)
    log.write(
        warnings.formatwarning(message, category, filename, lineno, line)
    )


warnings.showwarning = warn_with_traceback
# Stop pandas UserWarning for now in prod
if os.path.exists("/etc/IEMDEV"):
    # Some debugging
    warnings.simplefilter("always", category=ResourceWarning)
else:
    warnings.filterwarnings("ignore", category=UserWarning)

from pyiem.plot.use_agg import plt
import pandas

# TODO remove someday when pyiem is updated
import cartopy

if cartopy.config.get("pre_existing_data_dir", "") == "":
    cartopy.config["pre_existing_data_dir"] = f"{envpath}/share/cartopy"
