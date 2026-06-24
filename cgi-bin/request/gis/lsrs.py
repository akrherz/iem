"""A shim for a frequently typoed URL to the LSR backend.

Implementation at https://github.com/akrherz/iem/blob/main/pylib/iemweb/request/gis/lsr.py
User documentation available at https://mesonet.agron.iastate.edu/cgi-bin/request/gis/lsr.py?help"""

from iemweb.request.gis.lsr import application

__all__ = ["application"]
