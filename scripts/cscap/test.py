import util
import gdata.docs.client
import ConfigParser
config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

# Get me a client, stat
spr_client = util.get_spreadsheet_client(config)
docs_client = util.get_docs_client(config)

query = gdata.docs.client.DocsQuery(show_collections='false', 
                                    title='API Exercise')
feed = docs_client.GetAllResources(query=query)

"""
<ns0:id>https://docs.google.com/feeds/id/spreadsheet%3A0AqZGw0coobCxdDA2RUFKa0FCZzBrbWtRYVA5TVRrYUE</ns0:id>
<ns1:resourceId>spreadsheet:0AqZGw0coobCxdDA2RUFKa0FCZzBrbWtRYVA5TVRrYUE</ns1:resourceId>
<ns0:title>DPAC Kladivko Agronomic Data</ns0:title>

['AddCategory', 'AddLabel', 'FindAclLink', 'FindAlternateLink', 'FindChildren', 
 'FindEditLink', 'FindEditMediaLink', 'FindExtensions', 'FindFeedLink', 
 'FindHtmlLink', 'FindLicenseLink', 'FindMediaLink', 'FindNextLink', 
 'FindPostLink', 'FindPreviousLink', 'FindSelfLink', 'FindUrl', 
 'GetAclFeedLink', 'GetAclLink', 'GetAlternateLink', 'GetAttributes', 
 'GetCategories', 'GetEditLink', 'GetEditMediaLink', 'GetElements', 
 'GetFeedLink', 'GetFirstCategory', 'GetHtmlLink', 'GetId', 'GetLabels', 
 'GetLicenseLink', 'GetLink', 'GetNextLink', 'GetPostLink', 'GetPreviousLink', 
 'GetResourceType', 'GetResumableCreateMediaLink', 'GetResumableEditMediaLink', 
 'GetRevisionsFeedLink', 'GetSelfLink', 'HasLabel', 'InCollections', 
 'IsHidden', 'IsMedia', 'IsMine', 'IsPrivate', 'IsRestrictedDownload', 
 'IsSharedWithDomain', 'IsStarred', 'IsTrashed', 'IsViewed', 'RemoveCategories', 
 'RemoveLabel', 'SetResourceType', 'ToString', 
 '_XmlElement__get_extension_attributes', '_XmlElement__get_extension_elements', 
 '_XmlElement__set_extension_attributes', '_XmlElement__set_extension_elements', 
 '__class__', '__delattr__', '__dict__', '__doc__', '__format__', 
 '__getattribute__', '__hash__', '__init__', '__module__', '__new__', 
 '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', 
 '__str__', '__subclasshook__', '__weakref__', '_attach_members', 
 '_become_child', '_get_namespace', '_get_rules', '_get_tag', '_harvest_tree', 
 '_list_xml_members', '_members', '_other_attributes', '_other_elements', 
 '_qname', '_rule_set', '_set_namespace', '_set_tag', '_to_tree', 'acl_feed', 
 'add_category', 'add_label', 'attributes', 'author', 'batch_id', 
 'batch_operation', 'batch_status', 'category', 'children', 'content', 
 'contributor', 'control', 'deleted', 'description', 'etag', 
 'extension_attributes', 'extension_elements', 'feed_link', 'filename', 
 'find_acl_link', 'find_alternate_link', 'find_edit_link', 
 'find_edit_media_link', 'find_feed_link', 'find_html_link', 
 'find_license_link', 'find_media_link', 'find_next_link', 'find_post_link', 
 'find_previous_link', 'find_self_link', 'find_url', 'get_acl_feed_link', 
 'get_acl_link', 'get_alternate_link', 'get_attributes', 'get_categories', 
 'get_edit_link', 'get_edit_media_link', 'get_elements', 'get_feed_link', 
 'get_first_category', 'get_html_link', 'get_id', 'get_labels', 
 'get_license_link', 'get_link', 'get_next_link', 'get_post_link', 
 'get_previous_link', 'get_resource_type', 'get_resumable_create_media_link', 
 'get_resumable_edit_media_link', 'get_revisions_feed_link', 'get_self_link', 
 'has_label', 'id', 'in_collections', 'is_hidden', 'is_media', 'is_mine', 
 'is_private', 'is_restricted_download', 'is_shared_with_domain', 'is_starred', 
 'is_trashed', 'is_viewed', 'last_modified_by', 'last_viewed', 'link', 
 'namespace', 'published', 'quota_bytes_used', 'remove_categories', 
 'remove_label', 'resource_id', 'rights', 'set_resource_type', 'source', 
 'suggested_filename', 'summary', 'tag', 'text', 'title', 'to_string', 
 'updated', 'writers_can_invite']
 
 <ns0:entry ns1:etag="&quot;VFYPUEdZFit7ImBoDFc.&quot;" 
 xmlns:ns0="http://www.w3.org/2005/Atom" 
 xmlns:ns1="http://schemas.google.com/g/2005">
 <ns0:category scheme="http://schemas.google.com/spreadsheets/2006" 
 term="http://schemas.google.com/spreadsheets/2006#worksheet" />
 <ns0:id>https://spreadsheets.google.com/feeds/worksheets/0AqZGw0coobCxdGpQczFxbkI3ZDFJWnBLWnFrT1JVanc/od7</ns0:id>
 <ns0:content src="https://spreadsheets.google.com/feeds/list/0AqZGw0coobCxdGpQczFxbkI3ZDFJWnBLWnFrT1JVanc/od7/private/full" 
 type="application/atom+xml;type=feed" />
 <ns2:rowCount xmlns:ns2="http://schemas.google.com/spreadsheets/2006">15</ns2:rowCount>
 <ns0:updated>2013-02-25T22:00:01.825Z</ns0:updated>
 <ns0:link href="https://spreadsheets.google.com/feeds/cells/0AqZGw0coobCxdGpQczFxbkI3ZDFJWnBLWnFrT1JVanc/od7/private/full" 
 rel="http://schemas.google.com/spreadsheets/2006#cellsfeed" 
 type="application/atom+xml" />
 <ns0:link href="https://spreadsheets.google.com/tq?key=0AqZGw0coobCxdGpQczFxbkI3ZDFJWnBLWnFrT1JVanc&amp;sheet=od7" 
 rel="http://schemas.google.com/visualization/2008#visualizationApi" 
 type="application/atom+xml" />
 <ns0:link href="https://spreadsheets.google.com/feeds/worksheets/0AqZGw0coobCxdGpQczFxbkI3ZDFJWnBLWnFrT1JVanc/private/full/od7" 
 rel="self" type="application/atom+xml" />
 <ns0:link href="https://spreadsheets.google.com/feeds/worksheets/0AqZGw0coobCxdGpQczFxbkI3ZDFJWnBLWnFrT1JVanc/private/full/od7" 
 rel="edit" type="application/atom+xml" />
 <ns0:title>2011</ns0:title>
 <ns2:colCount xmlns:ns2="http://schemas.google.com/spreadsheets/2006">25</ns2:colCount>
 <ns2:edited xmlns:ns2="http://www.w3.org/2007/app">2013-02-25T22:00:01.825Z</ns2:edited>
 </ns0:entry>

"""

for entry in feed:
    spreadsheet = util.Spreadsheet(docs_client, spr_client, entry)
    #print spreadsheet.worksheets["Sheet1"].cols
    spreadsheet.worksheets["Sheet1"].add_column("Yo")
    #print spreadsheet.worksheets["Sheet1"].cols
    #spreadsheet.worksheets["Sheet1"].trim_columns()
    #spreadsheet.get_worksheets()
    #for title in spreadsheet.worksheets.keys():
        #ws = spreadsheet.worksheets[title]
        #print "%s %s rows: %s cols: %s" % (spreadsheet.title, title, ws.rows,
        #                                   ws.cols) 
