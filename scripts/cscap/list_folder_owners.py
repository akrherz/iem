"""
 List out the folders on the Google Drive and see who their owners are!
"""
import util
import ConfigParser
import gdata.docs.client

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

docs_client = util.get_docs_client(config)

query = gdata.docs.client.DocsQuery(categories=['folder'], 
                                    params={'showfolders': 'true'})
feed = docs_client.GetAllResources(query=query)

for entry in feed:
    if entry.author[0].email.text != 'cscap.automation@gmail.com':
        print entry.title.text, entry.author[0].email.text