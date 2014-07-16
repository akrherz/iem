'''
 farmname    | character varying(128) | 
 expansion   | character varying(24)  | 
 unitnumber  | character varying(16)  | 
 farmnumber  | character varying(16)  | 
 turbinename | character varying(16)  | 
 geom        | geometry(Point,4326)   | 

'''
import psycopg2
dbconn = psycopg2.connect(database='mec', host='192.168.0.23')
cursor = dbconn.cursor()

for line in open('mec-cypher.txt'):
    tokens = line.strip().split("\t")
    print tokens
    sql = """INSERT into turbines(farmname, expansion, unitnumber,
    farmnumber, turbinename, geom) values ('%s', '%s', '%s',
    '%s', '%s', 'SRID=4326;POINT(%s %s)')""" % (tokens[0], tokens[1],
    tokens[2], tokens[5], tokens[7], tokens[4], tokens[3])
    cursor.execute(sql)


cursor.close()
dbconn.commit()
dbconn.close()
