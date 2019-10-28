"""Ensure that Openfire is somewhat running"""
import sys

import requests


def main():
    """Go Main Go"""
    req = requests.get("http://iem-openfire:7070")
    if req.status_code == 200:
        print("OK")
        return 0
    print("FATAL")
    return 2


if __name__ == "__main__":
    sys.exit(main())
