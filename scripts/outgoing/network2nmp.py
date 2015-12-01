"""Export of data in National Mesonet Program CSV format

# DOS Linefeeds
# Add .EOO to last line of file
# station_id,LAT [deg N],LON [deg E],date_time,ELEV [m]
# null can be empty string or explicit NULL or null

"""
import psycopg2
import sys


def main(argv):
    """Do Something with arguments"""
    network = argv[1]


if __name__ == '__main__':
    main(sys.argv)