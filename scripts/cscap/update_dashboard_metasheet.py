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
                                            min_row=5, max_row=5))

list_feed = spr_client.get_list_feed( config.get('cscap', 'metamaster'), 'od6')

for entry in list_feed.entry:
    data = entry.to_dict()
    bad = False
    for key in data.keys():
        if data[key] is not None and data[key].find("TBD") > -1:
            bad = True
    print data['uniqueid'], bad
    
    for entry in cell_feed.entry:
        if int(entry.cell.col) < 2:
            continue
        heading = column_ids[ int(entry.cell.col) ]
        if heading == data['uniqueid']:
            if bad:
                uri = "https://docs.google.com/spreadsheet/ccc?key=0AugT6NSY_M5HdGd2cFV2WXBCQlJZNDRoSjZ0Qml4bnc#gid=0"
                entry.cell.input_value = '=hyperlink("%s", "Entry")' % (uri,)    
            else:
                entry.cell.input_value = 'Complete!'
            #print 'here'
            spr_client.update(entry)    
            
