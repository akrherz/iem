#!/usr/bin/env python

# BSD Licensed, Copyright (c) 2006-2010 TileCache Contributors
from __future__ import print_function

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

import requests

# setting this to True will exchange more useful error messages
# for privacy, hiding URLs and error messages.
HIDE_ALL = False


class WMS(object):
    fields = ("bbox", "srs", "width", "height", "format", "layers", "styles")
    defaultParams = {"version": "1.1.1", "request": "GetMap", "service": "WMS"}
    __slots__ = ("base", "params", "client", "data", "response")

    def __init__(self, base, params, user=None, password=None):
        """Constructor"""
        self.base = base
        if self.base[-1] not in "?&":
            if "?" in self.base:
                self.base += "&"
            else:
                self.base += "?"

        self.params = {}

        for key, val in self.defaultParams.items():
            if self.base.lower().rfind("%s=" % key.lower()) == -1:
                self.params[key] = val
        for key in self.fields:
            if key in params:
                self.params[key] = params[key]
            elif self.base.lower().rfind("%s=" % key.lower()) == -1:
                self.params[key] = ""

    def url(self):
        """Generate URL"""
        return self.base + urlencode(self.params)

    def fetch(self):
        """Fetch image from backend"""
        req = requests.get(self.url())
        data = req.content
        if req.headers.get("content-type") != "image/png":
            raise Exception(
                (
                    "Did not get image data back. \n"
                    "URL: %s\nStatus: %s\n"
                    "Response: \n%s"
                )
                % (self.url(), req.status_code, data)
            )
        return data, req

    def setBBox(self, box):
        """set bounding box"""
        self.params["bbox"] = ",".join(map(str, box))
