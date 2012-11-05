"""
Ingest the Colo tower data arriving via email!
"""
import sys
import mx.DateTime
import email.parser
msg = email.parser.Parser().parse(sys.stdin)
for part in msg.walk():
    if part.get_filename() != None:
        fp = mx.DateTime.now().strftime("/home/colo/colo%Y%m%d%H%M%S.txt")
        o = open(fp, 'a')
        o.write( part.get_payload() )
        o.close()