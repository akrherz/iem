"""
http://agebb.missouri.edu/weather/history/index.asp?station_prefix=bfd
"""
import pandas as pd

df = pd.read_table("/tmp/boone_daily.html", sep='\t', header=[0, 1, 2, 3, 4, 5])
print df.columns