import util
import ConfigParser
import gdata.spreadsheets.client
import gdata.docs.client
config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

# Get me a client, stat
spr_client = util.get_spreadsheet_client(config)
docs_client = util.get_docs_client(config)

list_feed = spr_client.get_list_feed( config.get('cscap', 'sdckey'), 'od6')

data = ['','','','']

for entry in list_feed.entry:
    d = entry.to_dict()
    if d['key'] is None:
        continue
    data.append("%s %s" % (d['key'], d['name'].strip()))

dash_feed = spr_client.get_list_feed( config.get('cscap', 'dashboard'), 'od6')

i = 0
for entry in dash_feed.entry:
    d = entry.to_dict()
    tokens = d['uniqueid'].split()
    print data[i], tokens[0]
    i += 1
    #if data.has_key(tokens[0]):
        #shouldbe = "%s %s" % (tokens[0], data[tokens[0]])
        #if shouldbe != d['uniqueid']:
            #print shouldbe, d['uniqueid']
            #entry.set_value('uniqueid', shouldbe)
            #spr_client.update(entry)
        #del(data[tokens[0]])

#keys = data.keys()
#for row in range(81, 81+len(data.keys())):
#    entry = spr_client.get_cell(config.get('cscap', 'dashboard'), 'od6', row, 1)
#    entry.cell.input_value = "%s %s"  % (keys[81-row], data[keys[81-row]])
#    spr_client.update(entry)

#print data