'''
 Some of our solar radiation data is not good!
'''
import psycopg2
ISUAG = psycopg2.connect(database='isuag', host='iemdb', user='nobody')
cursor = ISUAG.cursor()

def main():
    ''' Go main go '''
    cursor.execute("""
     SELECT station, yr, mo from 
      (select station, extract(year from valid) as yr, 
      extract(month from valid) as mo, sum(c80) from daily 
      GROUP by station, yr, mo) as foo
     WHERE sum < 100
    """)
    for row in cursor:
        print 'Reprocess %s %i-%02i' % (row[0], row[1], row[2])
        

if __name__ == '__main__':
    main()