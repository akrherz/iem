"""
"""
import gdata.spreadsheets.client
import gdata.spreadsheets.data
import gdata.docs.data
import gdata.docs.client
import gdata.gauth
import re
import ConfigParser
import sys
import util

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

spr_client = util.get_spreadsheet_client(config)
docs_client = util.get_docs_client(config)

query = gdata.docs.client.DocsQuery(show_collections='false',
                                    title='NWREC Nafziger & Villamil Plot Identifiers')
feed = docs_client.GetAllResources(query=query)
spread = util.Spreadsheet(docs_client, spr_client, feed[0])
spread.get_worksheets()
spread.worksheets['Sheet 1'].get_list_feed()
plotIDS = []
for entry in spread.worksheets['Sheet 1'].list_feed.entry:
    data = entry.to_dict()
    plotIDS.append( data['plotid'] )


query = gdata.docs.client.DocsQuery(show_collections='false',
                                    title='NWREC Nafziger & Villamil Agronomic Data')
feed = docs_client.GetAllResources(query=query)
spread = util.Spreadsheet(docs_client, spr_client, feed[0])
spread.get_worksheets()
spread.worksheets['2011'].get_list_feed()
for entry in spread.worksheets['2011'].list_feed.entry:
    data = entry.to_dict()
    if data['plotid'] in plotIDS:
        plotIDS.remove( data['plotid'] )
        
for idd in plotIDS:
    print idd