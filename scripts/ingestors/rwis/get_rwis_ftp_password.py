'''Get RWIS FTP password from the database settings'''
import psycopg2
DBCONN = psycopg2.connect(database='mesosite', host='iemdb', user='nobody')
cursor = DBCONN.cursor()

cursor.execute("""SELECT propvalue from properties 
    where propname = 'rwis_ftp_password'""")
row = cursor.fetchone()
print row[0]
