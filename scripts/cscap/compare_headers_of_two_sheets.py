import util
import ConfigParser
import gdata.spreadsheets.client
import gdata.docs.client
config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

spr_client = util.get_spreadsheet_client(config)
docs_client = util.get_docs_client(config)

cell_feed1 = spr_client.get_cells('0AqZGw0coobCxdG1HUFk5YXI3TzRlT1FfV0kzWXFEVVE', 
                                          'od7', query=gdata.spreadsheets.client.CellQuery(
                                                    min_row=1, max_row=1))                 
cell_feed2 = spr_client.get_cells('0AqZGw0coobCxdG1HUFk5YXI3TzRlT1FfV0kzWXFEVVE', 
                                          'od4', query=gdata.spreadsheets.client.CellQuery(
                                                    min_row=1, max_row=1)) 

cols1 = []
cols2 = []
for entry1 in cell_feed1.entry:
    cols1.append( entry1.cell.input_value)          
    
for entry2 in cell_feed2.entry:
    equiv = entry2.cell.input_value.replace("f2_", "f1_").replace("field2_", 'field1_')
    cols2.append( entry2.cell.input_value)
    cols1.remove(equiv)
print cols1
for one, two in zip(cols1, cols2):
    print one, two          