import gdata.docs.client
import ConfigParser
import util

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

# Get me a client, stat
spr_client = util.get_spreadsheet_client(config)
docs_client = util.get_docs_client(config)

query = gdata.docs.client.DocsQuery(show_collections='true', title='NAEW Agronomic Data')
feed = docs_client.GetAllResources(query=query)

newcols = [
    ['AGR44', '[44] Red clover or mixed cover crop biomass in spring of spreadsheet year', 'kg ha-1'],
    ['AGR45', '[45] Red clover or mixed cover crop total nitrogen in spring of spreadsheet year', 'kg ha-1'],
    ['AGR46', '[46] Red clover or mixed cover crop total carbon in spring of spreadsheet year', 'kg ha-1'],
           ]

for entry in feed:
    spreadkey = entry.id.text.split("/")[-1][14:]
    feed2 = spr_client.GetWorksheets( spreadkey )
    for entry2 in feed2.entry:
        worksheet = entry2.id.text.split("/")[-1]
        print 'Processing %s WRK: %s Title: %s' % (entry.title.text, 
                                                   worksheet, entry2.title.text),
        feed3 = spr_client.get_list_feed(spreadkey, worksheet)
        row = feed3.entry[0]
        data = row.to_dict()
        if data.get('agr41') is None and data.get('agr42') is None:
            print ' ... not found!'
            continue

        plusone = int(entry2.col_count.text) + 3
        entry2.col_count.text = str(plusone)
        spr_client.update(entry2)
        
        # Add a column?
        for i in range(len(newcols)):
            cell = spr_client.get_cell(spreadkey, worksheet,1, plusone-i)
            cell.cell.input_value = newcols[i][0]
            spr_client.update(cell)
    
            cell = spr_client.get_cell(spreadkey, worksheet,2, plusone-i)
            cell.cell.input_value = newcols[i][1]
            spr_client.update(cell)
    
            cell = spr_client.get_cell(spreadkey, worksheet,3, plusone-i)
            cell.cell.input_value = newcols[i][2]
            spr_client.update(cell)

        print ' ... updated'
        #sys.exit()
        
