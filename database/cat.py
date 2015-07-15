""" Dump all stuff into one file"""
import sys
import os

def main(argv):
    # Go
    dbname = argv[1]
    print open('init/%s.sql' % (dbname, )).read()
    i = 0
    while os.path.isfile('upgrade/%s/%s.sql' % (dbname, i)):
        print open('upgrade/%s/%s.sql' % (dbname, i)).read()
        i += 1

if __name__ == '__main__':
    main(sys.argv)
