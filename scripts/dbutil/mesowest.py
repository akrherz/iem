"""Review mesowest station file for differences"""
import pandas as pd
import psycopg2
import requests
import os


def cache_file():
    localfn = "/mesonet/tmp/mesowest_csv.tbl"
    if os.path.isfile(localfn):
        return
    r = requests.get('http://mesowest.utah.edu/data/mesowest_csv.tbl')
    o = open(localfn, 'w')
    o.write(r.content)
    o.close()


def main():
    cache_file()
    OUTPUT = open('insert.sql', 'w')
    df = pd.read_csv('/mesonet/tmp/mesowest_csv.tbl')
    # copy paste from /DCP/tomb.phtml
    for line in open('tomb.txt'):
        nwsli = line.split()[0]
        if nwsli not in df['primary id'].values:
            continue
        df2 = df[df['primary id'] == nwsli]
        row = df2.iloc[0]
        sql = """INSERT into stations(id, name, network, country, state,
    plot_name, elevation, online, metasite, geom) VALUES ('%s', '%s', '%s',
    '%s', '%s', '%s', %s, 't', 'f', 'SRID=4326;POINT(%s %s)');
    """ % (nwsli, row['station name'], row['state'] + '_DCP', row['country'],
           row['state'], row['station name'], row['elevation'],
           row['longitude'], row['latitude'])
        OUTPUT.write(sql)
        print nwsli

    OUTPUT.close()

if __name__ == '__main__':
    main()
