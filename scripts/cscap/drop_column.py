import util
import gdata.docs.client
import ConfigParser
config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

# Get me a client, stat
spr_client = util.get_spreadsheet_client(config)
docs_client = util.get_docs_client(config)

query = gdata.docs.client.DocsQuery(show_collections='false', 
                                    title='Agronomic Data')
entries = docs_client.GetAllResources(query=query)


for entry in entries:
    spreadsheet = util.Spreadsheet(docs_client, spr_client, entry)
    for yr in ["2011", "2012", "2013", "2014", "2015"]:
        spreadsheet.worksheets[yr].del_column("AGR35")