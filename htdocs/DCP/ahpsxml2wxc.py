"""Convert the AHPS XML into WXC format"""
import datetime

from paste.request import parse_formvars
from twisted.words.xish import domish, xpath
import requests


def do(nwsli):
    """work"""
    res = ""
    xml = requests.get(
        (
            "https://water.weather.gov/ahps2/"
            "hydrograph_to_xml.php?gage=%s&output=xml"
        )
        % (nwsli,)
    ).content
    elementStream = domish.elementStream()
    roots = []
    results = []
    elementStream.DocumentStartEvent = roots.append
    elementStream.ElementEvent = lambda elem: roots[0].addChild(elem)
    elementStream.DocumentEndEvent = lambda: results.append(roots[0])

    res += """IEM %s AHPS2WXC host=0 TimeStamp=%s
        5
        15 Station
         6 UTCDate
         4 UTCTime
         7 Stage
         7 CFS\n""" % (
        nwsli,
        datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
    )

    elementStream.parse(xml)
    elem = results[0]
    nodes = xpath.queryForNodes("/site/forecast/datum", elem)
    if nodes is None:
        return res
    i = 0
    maxval = {"val": 0, "time": None}
    for node in nodes:
        utc = datetime.datetime.strptime(
            str(node.valid)[:15], "%Y-%m-%dT%H:%M"
        )
        res += ("%12s%03i %6s %4s %7s %7s\n") % (
            nwsli,
            i,
            utc.strftime("%b %-d"),
            utc.strftime("%H%M"),
            node.primary,
            node.secondary,
        )
        if float(str(node.primary)) > maxval["val"]:
            maxval["val"] = float(str(node.primary))
            maxval["time"] = utc
            maxval["cfs"] = float(str(node.secondary))
        i += 1
    if maxval["time"] is not None:
        utc = maxval["time"]
        res += ("%12sMAX %6s %4s %7s %7s\n") % (
            nwsli,
            utc.strftime("%b %-d"),
            utc.strftime("%H%M"),
            maxval["val"],
            maxval["cfs"],
        )
    return res


def application(environ, start_response):
    """Do Fun Things"""
    fields = parse_formvars(environ)
    nwsli = fields.get("nwsli", "MROI4")[:5]
    start_response("200 OK", [("Content-type", "text/plain")])
    return [do(nwsli).encode("ascii")]
