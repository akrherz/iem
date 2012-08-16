# http://skipperkongen.dk/2011/12/06/hello-world-plugin-for-nagios-in-python/

# optparse is Python 2.3 - 2.6, deprecated in 2.7
# For 2.7+ use http://docs.python.org/library/argparse.html#module-argparse
from optparse import OptionParser
 
# CONSTANTS FOR RETURN CODES UNDERSTOOD BY NAGIOS
# Exit statuses recognized by Nagios
UNKNOWN = -1
OK = 0
WARNING = 1
CRITICAL = 2
 
# TEMPLATE FOR READING PARAMETERS FROM COMMANDLINE
parser = OptionParser()
parser.add_option("-m", "--message", dest="message", 
   default='Hello world', help="A message to print after OK - ")
(options, args) = parser.parse_args()
 
# RETURN OUTPUT TO NAGIOS
# USING THE EXAMPLE -m PARAMETER PARSED FROM COMMANDLINE
print 'OK - %s' % (options.message)
raise SystemExit, OK