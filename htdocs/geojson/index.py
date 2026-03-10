"""
Dispatch for anything asking for /geojson/ content on the website.

implemented in /pylib/iemweb/geojson/index.py
"""

from iemweb.geojson.index import application

__all__ = ["application"]
