# Copyright (C) 2002, 2003 Intevation GmbH <intevation@intevation.de>
# Author: Bernhard Herzog <bh@intevation.de>
#
# This program is free software under the GPL (>=v2)
# Read the file GPL coming with the software for details.

"""Convert Well-Known Text format to python objects

Main entry point is the convert_well_known_text function which takes a
geometry in Well-Known Text format and returns a python object with the
geometry.
"""

__version__ = "$Revision: 1.1 $"
# $Source: /thubanrepository/thuban/Thuban/Model/wellknowntext.py,v $
# $Id: wellknowntext.py,v 1.1 2003/08/19 11:00:40 bh Exp $

import re


_open_parens = r"[ \t]*(\([ \t]*)*"
_close_parens = r"[ \t]*(\)[ \t]*)+"
rx_point_list = re.compile(_open_parens + r"(?P<coords>[^\)]+)"
                           + _close_parens + ",?")


def parse_coordinate_lists(wkt):
    """Return the coordinates in wkt as a list of lists of coordinate pairs.

    The wkt parameter is the coordinate part of a geometry in well-known
    text format.
    """
    geometry = []
    while wkt:
        match = rx_point_list.match(wkt)
        if match:
            poly = []
            wktcoords = match.group("coords")
            for pair in wktcoords.split(","):
                # a pair may be a triple actually. For now we just
                # ignore any third value
                x, y = map(float, pair.split())[:2]
                poly.append((x, y))
            geometry.append(poly)
            wkt = wkt[match.end(0):].strip()
        else:
            raise ValueError("Invalid well-known-text (WKT) syntax")
    return geometry


def parse_multipolygon(wkt):
    """
    Return the MULTIPOLYGON geometry wkt as a list of lists of float pairs
    """
    return parse_coordinate_lists(wkt)

def parse_polygon(wkt):
    """Return the POLYGON geometry in wkt as a list of float pairs"""
    return parse_coordinate_lists(wkt)

def parse_multilinestring(wkt):
    """
    Return the MULTILINESTRING geometry wkt as a list of lists of float pairs
    """
    return parse_coordinate_lists(wkt)

def parse_linestring(wkt):
    """Return the LINESTRING geometry in wkt as a list of float pairs"""
    return parse_coordinate_lists(wkt)[0]

def parse_point(wkt):
    """Return the POINT geometry in wkt format as pair of floats"""
    return parse_coordinate_lists(wkt)[0][0]


# map geometry types to parser functions
_function_map = [
    ("MULTIPOLYGON", parse_multipolygon),
    ("POLYGON", parse_polygon),
    ("MULTILINESTRING", parse_multilinestring),
    ("LINESTRING", parse_linestring),
    ("POINT", parse_point),
    ]

def convert_well_known_text(wkt):
    """Return the geometry given in well-known text format as python objects

    The function accepts only 2D data and supports the POINT, POLYGON,
    MULTIPOLYGON, LINESTRING and MULTILINESTRING geometries.

    The structure of the return value depends on the geometry type. For
    MULTIPOLYGON and MULTILINESTRING return a list of lists of
    coordinate pairs. For POLYGON and LINESTRING return a list of
    coordinate pairs. For POINT return a coordinate pair. All
    coordinates are floats.

    The string wkt may contain an SRID specification in addition to the
    actual geometry. This SRID is ignored.
    """
    parts = wkt.split(";")
    for part in parts:
        part = part.strip()
        if part.startswith("SRID"):
            # ignore SRIDs
            continue
        else:
            for geotype, function in _function_map:
                if part.startswith(geotype):
                    return function(part[len(geotype):])
            else:
                raise ValueError("Unsupported WKT-part %s" % repr(part[:20]))
    else:
        # there were no recognized geometries in the WKT string
        raise ValueError("No recognized geometry in WKT string")

def parse_wkt_thuban(wkt):
    """Like convert_well_known_text, but return lists of lists of pairs"""
    parts = wkt.split(";")
    for part in parts:
        part = part.strip()
        if part.startswith("SRID"):
            # ignore SRIDs
            continue
        else:
            # split on "(" to separate the geometry type from the
            # coordinate values
            components = part.split("(", 1)
            if len(components) > 1:
                return parse_coordinate_lists(components[1])
            else:
                raise ValueError("WKT part %r doesn't contain opening"
                                 " parenthesis" % part)
    else:
        # there were no recognized geometries in the WKT string
        raise ValueError("No recognized geometry in WKT string")
