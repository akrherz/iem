"""Ensure iembot is up."""
import sys

import requests


def main():
    """Go Main Go."""
    req = requests.get("http://iembot:9004/room/kdmx.xml")
    if req.status_code == 200:
        print("OK - len(kdmx.xml) is %s" % (len(req.content),))
        return 0
    print("CRITICAL - /room/kdmx.xml returned code %s" % (req.status_code,))
    return 2


if __name__ == "__main__":
    sys.exit(main())
