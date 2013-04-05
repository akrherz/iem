"""
 Assign links in the dashboard to generated spreadsheets?
"""
import util
import ConfigParser
import gdata.spreadsheets.client
import gdata.docs.client
config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

# Get me a client, stat
spr_client = util.get_spreadsheet_client(config)
docs_client = util.get_docs_client(config)

# Go get row 1
cell_feed = spr_client.get_cells( config.get('cscap', 'dashboard'), 
                            'od6', query=gdata.spreadsheets.client.CellQuery(
                                                    min_row=1, max_row=1))
column_ids = [""] * 100
for entry in cell_feed.entry:
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
           'soil22': 'soil22soilammoniumoptional',
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
    return resources

def do_row(row):
    cell_feed = spr_client.get_cells( config.get('cscap', 'dashboard'), 
                        'od6', query=gdata.spreadsheets.client.CellQuery(
                                        min_row=row, max_row=row))
    firstcolumn = cell_feed.entry[0]
    varname = firstcolumn.cell.input_value.split()[0].lower()
    spreadtitle = lookuprefs.get(varname)
    if spreadtitle is None:
        print 'ERROR: Do not know how to reference %s in lookuprefs' % (
                                                                varname,)
        return
    
    for entry in cell_feed.entry[1:]:
        siteid = column_ids[ int(entry.cell.col) ]

        querytitle = '%s %s' % (siteid, spreadtitle)
        resources = docs_query(querytitle)   
        if len(resources) == 0:
            print 'Can not find spread title: |%s %s|' % (siteid, spreadtitle,)
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
            list_feed = spr_client.get_list_feed(skey , 'od7')
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
    
        if na:
            print 'Could not find header: %s in spreadtitle: %s %s' % (lookupcol,
                                                            siteid, spreadtitle)
    
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
            entry.cell.input_value = newvalue
            spr_client.update(entry)
        
for i in range(6,65):
    do_row(i)
