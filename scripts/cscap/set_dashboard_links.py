"""
  This script updates the data dashboard
"""
import util
import sys
import ConfigParser
import gdata.spreadsheets.client
import gdata.docs.client
config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

YEAR = sys.argv[1]

# Get me a client, stat
spr_client = util.get_spreadsheet_client(config)
docs_client = util.get_docs_client(config)

ss = util.Spreadsheet(docs_client, spr_client, config.get('cscap', 'dashboard'))
SHEET = ss.worksheets[YEAR]
SHEET.get_cell_feed()

column_ids = [""] * 100
for col in range(1, SHEET.cols+1):
    entry = SHEET.get_cell_entry(1, col)
    pos = entry.title.text
    text = entry.cell.input_value
    column_ids[ int(entry.cell.col) ] = text

lookuprefs = {
              'agr1': 'Agronomic Data',
              'agr2': 'Agronomic Data',
              'agr3': 'Agronomic Data',
              'agr4': 'Agronomic Data',
              'agr5': 'Agronomic Data',
              'agr6': 'Agronomic Data',
              'agr7': 'Agronomic Data',
              'agr8': 'Agronomic Data',
              'agr9': 'Agronomic Data',
              'agr10': 'Agronomic Data',
              'agr11': 'Agronomic Data',
              'agr12': 'Agronomic Data',
              'agr13': 'Agronomic Data',
              'agr14': 'Agronomic Data',
              'agr15': 'Agronomic Data',
              'agr16': 'Agronomic Data',
              'agr17': 'Agronomic Data',
              'agr18': 'Agronomic Data',
              'agr19': 'Agronomic Data',
              'agr20': 'Agronomic Data',
              'agr21': 'Agronomic Data',
              'agr22': 'Agronomic Data',
              'agr23': 'Agronomic Data',
              'agr24': 'Agronomic Data',
              'agr25': 'Agronomic Data',
              'agr26': 'Agronomic Data',
              'agr27': 'Agronomic Data',
              'agr28': 'Agronomic Data',
              'agr29': 'Agronomic Data',
              'agr30': 'Agronomic Data',
              'agr31': 'Agronomic Data',
              'agr32': 'Agronomic Data',
              'agr33': 'Agronomic Data',
              'agr34': 'Agronomic Data',
              'agr37': 'Agronomic Data',
              'agr38': 'Agronomic Data',
              'agr39': 'Agronomic Data',
              'agr40': 'Agronomic Data',
              'soil1': 'Soil Bulk Density and Water Retention Data',
              'soil2': 'Soil Bulk Density and Water Retention Data',
              'soil6': 'Soil Texture Data',
              'soil11': 'Soil Texture Data',
              'soil12': 'Soil Texture Data',
              'soil13': 'Soil Texture Data',
              'soil14': 'Soil Texture Data',              
              'soil15': 'Soil Nitrate Data',
              'soil16': 'Soil Nitrate Data',
              'soil22': 'Soil Nitrate Data',
              }
varconv = {
           'soil1': 'bulkdensity',
           'soil2': 'waterretentionat15bar',
           'soil15': 'soilnitratespringsampling',
           'soil16': 'soilnitratefallsampling',
           'soil22': 'soil22fallsoilammoniumoptional',
           }

CACHE = {}
QUERY_CACHE = {}

def docs_query(title):
    if QUERY_CACHE.has_key(title):
        #print 'QUERY_CACHE HIT'
        return QUERY_CACHE[ title ]
    
    query = gdata.docs.client.DocsQuery(show_collections='true', 
                                title=title)
    # We need to go search for the spreadsheet
    resources = docs_client.GetAllResources(query=query)
    QUERY_CACHE[title] = resources
    if len(resources) == 0:
        print 'Could not find spreadsheet |%s|' % (title,)
    return resources

def do_row(row):
    """ Actually process a row in the SHEET """
    firstcolumn = SHEET.get_cell_entry(row, 1)
    varname = firstcolumn.cell.input_value.split()[0].lower()
    spreadtitle = lookuprefs.get(varname)
    if spreadtitle is None:
        print 'ERROR: Do not know how to reference %s in lookuprefs' % (
                                                                varname,)
        return
    
    for col in range(2,SHEET.cols+1):
        entry = SHEET.get_cell_entry(row, col)
        siteid = column_ids[ int(entry.cell.col) ]
        if siteid in ['', 'Required (R)']:
            continue

        querytitle = '%s %s' % (siteid, spreadtitle)
        resources = docs_query(querytitle)   
        if len(resources) == 0:
            continue
        if len(resources) == 2:
            print 'Duplicate spread title: |%s %s|' % (siteid, spreadtitle,)
            for res in resources:
                print siteid, res.title.text, res.get_html_link().href
            continue
    
        skey = resources[0].get_id().split("/")[-1][14:]
        if CACHE.has_key(skey):
            list_feed = CACHE[skey]
        else:
            # Get the list feed for this spreadsheet
            ss = util.Spreadsheet(docs_client, spr_client, resources[0])
            list_feed = ss.worksheets[YEAR].get_list_feed()
            CACHE[skey] = list_feed
        misses = 0
        na = False
        dnc = False
        lookupcol = varconv.get(varname, varname)
        for entry2 in list_feed.entry:
            data = entry2.to_dict()
            if not data.has_key(lookupcol):
                na = True
                break
            if data[lookupcol] is None:
                misses += 1
            elif data[lookupcol].lower() == 'did not collect':
                dnc = True
    
        #if na:
        #    print 'Could not find header: %s in spreadtitle: %s %s' % (lookupcol,
        #                                                    siteid, spreadtitle)
    
        uri = resources[0].get_html_link().href
        if na:
            newvalue = 'N/A'
        elif dnc:
            newvalue = 'Did not collect'
        elif misses == 0:
            newvalue = 'Complete!'
        else:
            newvalue = '=hyperlink("%s", "Entry")' % (uri,)
        if newvalue != entry.cell.input_value:
            print '--> New Value: %s [%s] OLD: %s NEW: %s' % (siteid, varname,
                                            entry.cell.input_value, newvalue)
            entry.cell.input_value = newvalue
            spr_client.update(entry)
        
for i in range(6,65):
    do_row(i)
