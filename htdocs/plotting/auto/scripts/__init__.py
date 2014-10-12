"""
Examples of widget types

dict(type='date', name='date2', default='2012/03/15', label='Bogus2:',
     min="1893/01/01"), # Comes back to python as yyyy-mm-dd

"""
# Association of plots
data = {'plots': [
    {'label': 'Daily', 'options': [
        {'id': "11", 'label': "ASOS/AWOS Daily Maximum Dew Point for a Year"},
        {'id': "21", 'label': "Change in NCDC 81 Daily Climatology over X Days"},
        {'id': "7", 'label': "Growing Degree Day Periods for One Year by Planting Date"},
        {'id': "19", 'label': "Histogram of Daily High/Low Temperatures"},
        {'id': "26", 'label': "Minimum Daily Low Temperature after 1 July"},
        {'id': "5", 'label': "Minimum Daily Temperature Range"},
        {'id': "22", 'label': "Percentage of Years within Temperature Range from Averages"},
        {'id': "25", 'label': "Spread of Daily High and Low Temperatures"},
        {'id': "4", 'label': "State Areal Coverage of Precip Intensity over X Days"},
    ]},
    {'label': 'Monthly', 'options': [
        {'id': "1", 'label': "July-August Days Above Temp v. May-June Precip"},
        {'id': "2", 'label': "Month Precipitation v Month Growing Degree Day Departures"},
        {'id': "3", 'label': "Monthly Temperature / Precipitation Statistics by Year"},
        {'id': "6", 'label': "Monthly Temperature/Precipitation Distributions"},
        {'id': "24", 'label': "Monthly Precipitation Climate District Ranks"},
        {'id': "8", 'label': "Monthly Precipitation Reliability"},
        {'id': "23", 'label': "Monthly Station Departures + El Nino 3.4 Index"},
        {'id': "9", 'label': "Growing Degree Day Climatology and Daily Values for one Year"},
        {'id': "15", 'label': "Daily Temperature Change Frequencies by Month"},
        {'id': "20", 'label': "Hours of Precipitation by Month"},
        #{'id': "17", 'label': "Daily Temperatures + Climatology for Year + Month"},
    ]},
    {'label': 'Yearly', 'options': [
        {'id': "12", 'label': "Days per year and latest date above given threshold"},
        {'id': "13", 'label': "End Date of Summer (warmest 91 day period) per Year"},
        {'id': "27", 'label': "First Fall Freeze then Killing Frost"},
        {'id': "10", 'label': "Last Spring and First Fall Date above/below given threshold"},
        {'id': "14", 'label': "Yearly Precipitation Contributions by Daily Totals"},
    ]},
    {'label': 'METAR ASOS Special Plots', 'options': [
        {'id': "16", 'label': "Wind Rose when specified criterion is meet"},
        {'id': "18", 'label': "Long term temperature time series"},
    ]},
]}
