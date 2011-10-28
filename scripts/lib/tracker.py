import pg, sys, mx.DateTime
import smtplib
from email.MIMEText import MIMEText

import iemdb
IEM = iemdb.connect('iem', bypass=True)

class Engine(object):

    def __init__(self):
        """
        IEM Tracker instance, we can bunch emails this way
        """
        self.emails = {}
        pass


    def doAlert(self, sid, myOb, network, portNetID, dontmail):
        """
        We have an offline station!
        """
        # Check to see if we already know this site is offline!
        sql = """SELECT * from offline WHERE station = '%s' 
              and network = '%s' """ % (sid, network)
        icursor = IEM.cursor()
        icursor.execute( sql )
        rowcount = icursor.rowcount
        icursor.close()
        if rowcount > 0:
            return

        openTickets = ""
        closedTickets = ""
        try:
            mydb = pg.connect("portfolio", "meteor.geol.iastate.edu", 
                   5432, None, None, "mesonet")

            sql = """INSERT into tt_base (portfolio, s_mid, subject, 
                     status, author) VALUES ('%s', '%s', 'Site Offline', 
                     'OPEN', 'mesonet')""" % (portNetID, sid)
            mydb.query(sql)
            # Get the number of the ticket just generated
            rs = mydb.query("""
                 SELECT last_value as lv from tt_base_id_seq""").dictresult()
            ticketID = rs[0]["lv"]
            # Insert Log entry
            sql = """INSERT into tt_log(portfolio, s_mid, author, status_c, 
                  comments, tt_id) VALUES ('%s', '%s', 'mesonet', 
                  'OKAY', 'Site Offline since %s', %s )""" % ( 
                  portNetID, sid, myOb.get('ts'), ticketID )
            mydb.query(sql)

            # Lets get a list of Tickets currently open for this site
            sql = """SELECT *, to_char(entered, 'YYYY-MM-DD HH PM') as d 
                   from tt_base WHERE s_mid = '%s' and id != %s 
                   and portfolio = '%s' and status != 'CLOSED' 
                   ORDER by id DESC""" % (sid, ticketID, portNetID)
            rs = mydb.query(sql).dictresult()
            for i in range(len(rs)):
                t = " %-6s %16s     %s\n" % (rs[i]['id'], rs[i]['d'], 
                   rs[i]['subject'])
                openTickets = openTickets + t

            # Lets get the most recently closed tickets
            sql = """SELECT *, to_char(last, 'YYYY-MM-DD HH PM') as d 
                 from tt_base WHERE s_mid = '%s' and id != %s 
                 and portfolio = '%s' and status = 'CLOSED' 
                 ORDER by last DESC LIMIT 5""" % (sid, ticketID, portNetID)
            rs = mydb.query(sql).dictresult()
            for i in range(len(rs)):
                t = " %-6s %16s     %s\n" % (rs[i]['id'], rs[i]['d'], 
                     rs[i]['subject'])
                closedTickets = closedTickets + t
        except:
            print "%s -- %s \n" % (sys.exc_type, sys.exc_value) 
            sys.exc_traceback = None
            print "Error generating Trouble Ticket for "+ sid
            ticketID = "ERROR"

        if openTickets == "": openTickets = " --None--"
        if closedTickets == "": closedTickets = " --None--"

        # Compose Message for the alert
        mformat = """
----------------------
| IEM TRACKER REPORT |  New Ticket Generated: # %s
================================================================
 Station Name      :  [%s] - %s 
 Status Change     :  [OFFLINE] Site is NOT reporting to the IEM
 Last Observation  :  %s

 Other Currently 'Open' Tickets for this Site:
 #      OPENED_ON           TICKET TITLE
%s 

 Most Recently 'Closed' Trouble Tickets for this Site:
 #      CLOSED_ON           TICKET TITLE
%s

================================================================
"""

        mailStr = mformat % (ticketID, sid, myOb.get("sname"), \
                          str(myOb.get('ts')), openTickets, closedTickets )

        # Update IEMAccess
        sql = """INSERT into offline(station, network, valid, trackerid) 
                values ('%s','%s','%s', %s)""" % (sid, network, 
                myOb.get('ts'), ticketID)
        icursor = IEM.cursor()
        icursor.execute(sql)
        icursor.close()
        IEM.commit()

        if (dontmail != 0):
            return

        subject = "[IEM] %s Offline" % ( myOb.get("sname"), )
        # Okay, we need to figure out who should be alerted about this outage
        rs = mydb.query("""SELECT * from iem_site_contacts WHERE 
          s_mid = '%s' and email IS NOT NULL""" % (sid,)).dictresult()
        for i in range(len(rs)):
            email = rs[i]["email"]
            if not self.emails.has_key(email):
                self.emails[email] = {'subject': subject, 'body': mailStr}
            else:
                self.emails[email]['subject'] = "[IEM] Multiple Sites"
                self.emails[email]['body'] += "=======================\n"
                self.emails[email]['body'] += mailStr


    def send(self):
        """
        And finally send emails when we are finished
        """
        s = smtplib.SMTP()
        s.connect()
        for email in self.emails:
            msg = MIMEText( self.emails[email]['body'] )
            msg['From'] = "akrherz@iastate.edu"
            msg['Subject'] = self.emails[email]['subject']
            s.sendmail("akrherz@iastate.edu", email, msg.as_string())
        s.close()

    def checkStation(self, sid, myOb, network, portNetID, dontmail):
        """
        Perhaps this station is back online!
        """
        # Did we consider this station offline
        sql = """SELECT trackerid, valid from offline WHERE station = '%s' and 
              network = '%s' """ % (sid, network)
        icursor = IEM.cursor()
        icursor.execute( sql )
        row = icursor.fetchone()
        rowcount = icursor.rowcount
        icursor.close()
        if rowcount == 0:
            return

        ticketID = row[0]
        offlineAt = str(row[1])
        offlineTS = mx.DateTime.strptime(offlineAt[:19], "%Y-%m-%d %H:%M:%S")
        offlineDur = (myOb.get('ts') - offlineTS).strftime('%d days %H hours %M minutes')
        try:
            import pg
            mydb = pg.connect("portfolio", "meteor.geol.iastate.edu", 
                   5432, None, None, "mesonet")

            mydb.query("""INSERT into tt_log(portfolio, s_mid, author, 
                 status_c, comments, tt_id) VALUES ('%s', '%s', 'mesonet', 
                 'CLOSED', 'Site Back Online at: %s', %s)""" % (
                 portNetID, sid, myOb.get('ts'), ticketID))
            mydb.query("""UPDATE tt_base SET last = CURRENT_TIMESTAMP, 
                       status = 'CLOSED' WHERE id = %s """ % (ticketID,))

        except:
            print "Problem Clearing Ticket!"
 
        # Compose Message for the alert
        mformat = """
               ---------------------------------
               |  *** IEM TRACKER REPORT ***   |
  ------------------------------------------------------------

  ID                :  %s
  Station Name      :  %s
  Status Change     :  [ONLINE] Site is reporting to the IEM
  Trouble Ticket#   :  %s

  Last Observation  :  %s
  Outage Duration   :  %s
    
  IEM Tracker Action:  This trouble ticket has been marked
                       CLOSED pending any further information.
  ------------------------------------------------------------

  * If you have any information pertaining to this outage, 
    please directly respond to this email.
  * Questions about this alert?  Email:  akrherz@iastate.edu
  * Thanks!!!
"""
        mailStr = mformat % (sid, myOb.get("sname"), ticketID, \
                          str(myOb.get('ts')), offlineDur )

        sql = """DELETE from offline WHERE station = '%s' 
              and network = '%s' """ % (sid, network)
        icursor = IEM.cursor()
        icursor.execute( sql )
        icursor.close()
        IEM.commit()

        if dontmail != 0:
            return

        subject = "[IEM] %s Online" % ( myOb.get("sname"), )
        rs = mydb.query("""SELECT * from iem_site_contacts WHERE 
             s_mid = '%s' and email IS NOT NULL""" % (sid,)).dictresult()
        for i in range(len(rs)):
            email = rs[i]["email"]
            if not self.emails.has_key(email):
                self.emails[email] = {'subject': subject, 'body': mailStr}
            else:
                self.emails[email]['subject'] = "[IEM] Multiple Sites"
                self.emails[email]['body'] += "=======================\n"
                self.emails[email]['body'] += mailStr
