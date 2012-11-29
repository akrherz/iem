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


cell_feed = spr_client.get_cells( config.get('cscap', 'dashboard'), 
                                          'od6', query=gdata.spreadsheets.client.CellQuery(
                                                    min_row=53, max_row=53))


for entry in cell_feed.entry:
    if int(entry.cell.col) < 2:
        continue
    heading = column_ids[ int(entry.cell.col) ]

    query = gdata.docs.client.DocsQuery(show_collections='true', 
                            title='%s Soil Nitrate Data' % (heading,))


    # We need to go search for the spreadsheet?
    resources = docs_client.GetAllResources(query=query)
    if len(resources) == 0:
        print 'No find!', heading
        continue
    if len(resources) == 2:
        print 'Duplicate', heading
        for res in resources:
            print heading, res.title.text, res.get_html_link().href
        continue

    uri = resources[0].get_html_link().href
    entry.cell.input_value = '=hyperlink("%s", "Entry")' % (uri,)
    spr_client.update(entry)