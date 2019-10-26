"""Wrote my own tcptraffic nagios script, sigh"""
from __future__ import print_function
import sys
import datetime
import json
import os
import getpass


def compute_rate(old, new, seconds):
    """Compute a rate that makes sense"""
    delta = new - old
    if delta < 0:
        delta = new
    return delta / seconds


def read_stats(device):
    """read the stats"""
    fn = "/tmp/check_tcptraffic_py_%s_%s" % (device, getpass.getuser())
    if not os.path.isfile(fn):
        return
    fp = open(fn)
    try:
        payload = json.load(fp)
    except Exception:
        # remove the file
        os.unlink(fn)
        return
    fp.close()
    payload["valid"] = datetime.datetime.strptime(
        payload["valid"], "%Y-%m-%dT%H:%M:%SZ"
    )
    return payload


def write_stats(device, payload):
    """write to tmp file"""
    fp = open("/tmp/check_tcptraffic_py_%s_%s" % (device, getpass.getuser()), "w")
    json.dump(payload, fp)
    fp.close()


def get_stats(device):
    """Get the stats"""
    for line in open("/proc/net/dev", "r").readlines():
        if not line.strip().startswith(device + ":"):
            continue
        tokens = line.strip().split()
        if len(tokens) == 17:
            rxbytes = int(tokens[1])
            txbytes = int(tokens[9])
            payload = dict(
                valid=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                rxbytes=rxbytes,
                txbytes=txbytes,
                device=device,
            )
            return payload


def main(argv):
    """Go Main Go"""
    device = argv[1]
    old = read_stats(device)
    current = get_stats(device)
    if current is None:
        print("CRITICAL - nodata")
        sys.exit(2)
    write_stats(device, current)
    if old is None:
        print("CRITICAL - initializing counter")
        sys.exit(2)
    # need to support rhel6 hosts, so no total_seconds()
    seconds = (datetime.datetime.utcnow() - old["valid"]).days * 86400 + (
        datetime.datetime.utcnow() - old["valid"]
    ).seconds
    if seconds < 1 or seconds > 700:
        print("CRITICAL - seconds timer is too large %s" % (seconds,))
        sys.exit(2)
    rxrate = compute_rate(old["rxbytes"], current["rxbytes"], seconds)
    txrate = compute_rate(old["txbytes"], current["txbytes"], seconds)

    print(
        (
            "TCPTRAFFIC OK - %s %.0f bytes/s | TOTAL=%.0fB;400000000;500000000 "
            "IN=%.0fB;; OUT=%.0fB;; TIME=%.0f;;"
        )
        % (device, rxrate + txrate, rxrate + txrate, rxrate, txrate, seconds)
    )
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv)
