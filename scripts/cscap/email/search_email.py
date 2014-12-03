import imaplib
import re
import email
import datetime
import getpass

out = open('completed.txt', 'w')

obj = imaplib.IMAP4_SSL('imap.gmail.com', 993)    
obj.login('akrherz@iastate.edu', getpass.getpass())
obj.select("[Gmail]/All Mail")
typ, data = obj.search(None, '(SUBJECT "RUN_12Z.sh" since "01-JUL-2013")')
for num in data[0].split():
    typ, data = obj.fetch(num, '(RFC822)')
    date = None
    for line in data[0][1].split("\r\n"):
        if line.startswith("Date:"):
            a = " ".join(line.split()[2:5])
            date = datetime.datetime.strptime(a, "%d %b %Y")
        if line.find("Complete!") > 0:
            # --> New Value: NAEW.WS111 [agr20]
            tokens = line.split()
            print date.strftime("%Y-%m-%d"), tokens[3], tokens[4]
    #msg = email.message_from_string(data[0][1])
    #print data
    #sys.exit()
    #for part in msg.walk():
    #    if part.get_content_type() == 'text/plain':
    #        text = part.get_payload().replace("=\r\n", "\n")
    #        print text

out.close()