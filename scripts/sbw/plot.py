from pyiem.plot import MapPlot
import pandas as pd

df = pd.read_csv('vertex.csv', index_col='WFO', na_values=['None'])
df['r'] = (df['CNTY_HITS'] - df['CWA_HITS']) / df['ALL'] * 100.
avgv = (df['CNTY_HITS'] - df['CWA_HITS']).sum() / float(df['ALL'].sum()) * 100.

m = MapPlot(sector='nws', axisbg='white',
            title='Percent of SVR+TOR Warning Vertices within 2km of County Border',
            subtitle='1 Oct 2007 through 23 May 2016, Overall Avg: %.1f%%, * CWA Borders Excluded' % (avgv,))
m.fill_cwas(df['r'], ilabel=True, lblformat='%.0f')
m.postprocess(filename='test.png')
