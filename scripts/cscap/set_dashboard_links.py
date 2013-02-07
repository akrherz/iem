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
              'soil2': 'Soil Bulk Density and Water Retention Data',
              }
varconv = {
           'soil2': 'waterretentionat0bar',
           }


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
    
        query = gdata.docs.client.DocsQuery(show_collections='true', 
                                title='%s %s' % (siteid, spreadtitle))
    
    
        # We need to go search for the spreadsheet
        resources = docs_client.GetAllResources(query=query)
        if len(resources) == 0:
            print 'Can not find spread title: |%s %s|' % (siteid, spreadtitle,)
            continue
        if len(resources) == 2:
            print 'Duplicate spread title: |%s %s|' % (siteid, spreadtitle,)
            for res in resources:
                print siteid, res.title.text, res.get_html_link().href
            continue
    
        
        # Get the list feed for this spreadsheet
        list_feed = spr_client.get_list_feed( 
                        resources[0].get_id().split("/")[-1][14:], 'od7')
        misses = 0
        na = False
        lookupcol = varconv.get(varname, varname)
        for entry2 in list_feed.entry:
            data = entry2.to_dict()
            if not data.has_key(lookupcol):
                na = True
                break
            if data[lookupcol] is None:
                misses += 1
    
        if na:
            print 'Could not find header: %s in spreadtitle: %s %s' % (lookupcol,
                                                            siteid, spreadtitle)
    
        uri = resources[0].get_html_link().href
        if na:
            entry.cell.input_value = 'N/A'
        elif misses == 0:
            entry.cell.input_value = 'Complete!'
        else:
            entry.cell.input_value = '=hyperlink("%s", "Entry")' % (uri,)    
        spr_client.update(entry)
        
for i in range(40,41):
    do_row(i)
