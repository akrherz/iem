"""
Utility Functions that are common to our scripts, I hope
$Id$:
"""

def build_treatments(feed):
    """
    Process the Treatments spreadsheet and generate a dictionary of
    field metadata
    @param feed the processed spreadsheet feed
    """
    data = None
    treatment_names = {}
    for entry in feed.entry:
        row = entry.to_dict()
        if data is None:
            data = {}
            for key in row.keys():
                if key in ['uniqueid','name','key'] or key[0] == '_':
                    continue
                print 'Found Key: %s' % (key,)
                data[key] = {'TIL': [None,], 'ROT': [None,], 'DWM': [None,], 'NIT': [None,], 
                             'LND': [None,], 'REPS': 1}
        if row['key'] is None or row['key'] == '':
            continue
        treatment_key = row['key']
        treatment_names[treatment_key] = row['name']
        for colkey in row.keys():
            cell = row[colkey]
            if colkey in data.keys(): # Is sitekey
                sitekey = colkey
                if cell is not None and cell != '':
                    if treatment_key[:3] in data[sitekey].keys():
                        data[sitekey][treatment_key[:3]].append( treatment_key )
                if treatment_key == 'REPS' and cell not in ('?','TBD'):
                    print 'Found REPS for site: %s as: %s' % (sitekey, int(cell))
                    data[sitekey]['REPS'] = int(cell)
    
    return data, treatment_names

def build_sdc(feed):
    """
    Process the Site Data Collected spreadsheet
    @param feed the processed spreadsheet feed
    """
    data = None
    sdc_names = {}
    for entry in feed.entry:
        row = entry.to_dict()
        if data is None:
            data = {}
            for key in row.keys():
                if key in ['uniqueid','name','key'] or key[0] == '_':
                    continue
                print 'Found Key: %s' % (key,)
                data[key] = []
        if row['key'] is None or row['key'] == '':
            continue
        sdc_key = row['key']
        sdc_names[sdc_key] = {'name': row['name'], 'units': row['units']}
        for sitekey in row.keys():
            if sitekey in data.keys():
                if row[sitekey] is not None and row[sitekey] != '':
                    data[sitekey].append( sdc_key )
    return data, sdc_names