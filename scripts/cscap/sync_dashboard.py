"""
 Programically update the dashboard when we find new data?
"""
import util
import ConfigParser
config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

# Get me a client, stat
spr_client = util.get_spreadsheet_client(config)

cell = spr_client.get_cell( config.get('cscap', 'dashboard'), 
                                          'od6', 5, 2)
print cell.title.text
print cell

#dash_cells = spr_client.get_cells( config.get('cscap', 'dashboard'), 
#                                          'od6')

#for entry in dash_cells.entry:
    #data = entry.to_dict()
    #if data.get('nwrec') == 'IASTATE':
    #    print entry
#    print entry.title.text, entry.cell.input_value, entry.cell.text