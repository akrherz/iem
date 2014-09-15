"""
Examples of widget types

dict(type='date', name='date2', default='2012/03/15', label='Bogus2:',
     min="1893/01/01"), # Comes back to python as yyyy-mm-dd

"""
# Association of plots
data = {'plots': [
    {'label': 'Daily', 'options': [
        {'id': "4", 'label': "State Areal Coverage of Precip Intensity over X Days"},
        {'id': "5", 'label': "Minimum Daily Temperature Range"},
        {'id': "7", 'label': "Growing Degree Day Periods for One Year by Planting Date"},
        {'id': "11", 'label': "ASOS/AWOS Daily Maximum Dew Point for a Year"},
    ]},
    {'label': 'Monthly', 'options': [
        {'id': "1", 'label': "July-August Days Above Temp v. May-June Precip"},
        {'id': "2", 'label': "Month Precipitation v Month Growing Degree Day Departures"},
        {'id': "3", 'label': "Monthly Temperature / Precipitation Statistics by Year"},
        {'id': "6", 'label': "Monthly Temperature/Precipitation Distributions"},
        {'id': "8", 'label': "Monthly Precipitation Reliability"},
        {'id': "9", 'label': "Growing Degree Day Climatology and Daily Values for one Year"},
        {'id': "15", 'label': "Daily Temperature Change Frequencies by Month"},
        #{'id': "17", 'label': "Daily Temperatures + Climatology for Year + Month"},
    ]},
    {'label': 'Yearly', 'options': [
        {'id': "10", 'label': "Last Spring and First Fall Date below given threshold"},
        {'id': "12", 'label': "Days per year and latest date above given threshold"},
        {'id': "13", 'label': "End Date of Summer (warmest 91 day period) per Year"},
        {'id': "14", 'label': "Yearly Precipitation Contributions by Daily Totals"},
    ]},
    {'label': 'METAR ASOS Special Plots', 'options': [
        {'id': "16", 'label': "Wind Rose when TS (thunder) is reported"},
    ]},
]}
