"""Get RWIS FTP password from the database settings"""
from __future__ import print_function
from pyiem.util import get_properties


def main():
    """Go Main Go"""
    props = get_properties()
    print(props["rwis_ftp_password"])


if __name__ == "__main__":
    main()
