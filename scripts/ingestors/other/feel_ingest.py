"""
Ingest the ISU FEEL Farm data
"""
import pandas as pd
import datetime
import psycopg2


BASE = "/mnt/home/mesonet/ot/ot0005/incoming/Pierson"

def get_starttimes():
    """ Figure out when we have data """
    CURSOR.execute("""SELECT max(valid) from feel_data_hourly""")
    row = CURSOR.fetchone()
    hstart = row[0]

    CURSOR.execute("""SELECT max(valid) from feel_data_daily""")
    row = CURSOR.fetchone()
    dstart = row[0]

    return dstart, hstart

def ingest():
    """ Lets do something """
    
    dstart, hstart = get_starttimes()
    if dstart is None:
        dstart = datetime.date(1980,1,1)
    if hstart is None:
        hstart = datetime.datetime(1980,1,1)
    
    df = pd.read_csv('%s/ISU_Feel_Daily.dat' % (BASE,), header=0,
                     skiprows=[0,2,3], quotechar='"', warn_bad_lines=True)
    
    for _, row in df.iterrows():
        ts = datetime.datetime.strptime(row['TIMESTAMP'][:10], '%Y-%m-%d')
        if ts.date() <= dstart:
            continue
        CURSOR.execute("""INSERT into feel_data_daily(
            valid, AirTemp_Max, AirTemp_Min, Rain_Tot,
            Windspeed_Max, SolarRad_MJ_Tot) VALUES (%s, %s, %s, %s,
            %s, %s)""", (ts, row['AirTemp_Max'], row['AirTemp_Min'],
                         row['Rain_Tot'], row['Windspeed_Max'], 
                         row['SolarRad_MJ_Tot']))

    df = pd.read_csv('%s/ISU_Feel_Hourly.dat' % (BASE,), header=0,
                     skiprows=[0,2,3], quotechar='"', warn_bad_lines=True)
    
    for _, row in df.iterrows():
        ts = datetime.datetime.strptime(row['TIMESTAMP'][:13], '%Y-%m-%d %H')
        if ts <= hstart:
            continue
        CURSOR.execute("""INSERT into feel_data_hourly(
            valid, BattVolt_Avg, PanTemp_Avg, AirTemp_Avg,
            RH_Avg, sat_vp_Avg, act_vp_Avg, WindDir_Avg, Windspeed_Avg,
            SolarRad_mV_Avg, SolarRad_W_Avg, Soil_Temp_5_Avg, Rain_Tot,
            LWS1_Avg, LWS2_Avg, LWS3_Avg, LWS1_Ohms, LWS2_Ohms,
            LWS3_Ohms, LWS1_Ohms_Hst, LWS2_Ohms_Hst, LWS3_Ohms_Hst) VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s)""", (ts, row['BattVolt_Avg'], 
            row['PanTemp_Avg'], row['AirTemp_Avg'],
            row['RH_Avg'], row['sat_vp_Avg'], row['act_vp_Avg'], 
            row['WindDir_Avg'], row['Windspeed_Avg'],
            row['SolarRad_mV_Avg'], row['SolarRad_W_Avg'], 
            row['Soil_Temp_5_Avg'], row['Rain_Tot'],
            row['LWS1_Avg'], row['LWS2_Avg'], row['LWS3_Avg'],
            row['LWS1_Ohms'], row['LWS2_Ohms'],
            row['LWS3_Ohms'], row['LWS1_Ohms_Hst'], row['LWS2_Ohms_Hst'], 
            row['LWS3_Ohms_Hst']))


def main():
    """ Go Main """
    ingest()

if __name__ == '__main__':
    PGCONN = psycopg2.connect(database='other', host='iemdb')
    CURSOR = PGCONN.cursor()
    main()
    CURSOR.close()
    PGCONN.commit()
