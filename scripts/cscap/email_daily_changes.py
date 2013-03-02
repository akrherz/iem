"""
 Print out changes feed
"""
import ConfigParser
import sys
import util
import datetime
import pytz
import smtplib

rtype_xref = {
'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'MS Excel',
'application/vnd.ms-excel': 'MS Excel',
'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'MS PowerPoint',
              }

EMAILS = ['labend@iastate.edu','akrherz@iastate.edu']
if len(sys.argv) == 2:
    EMAILS = ['akrherz@iastate.edu',]

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

today = datetime.datetime.utcnow() 
today = today.replace(tzinfo=pytz.timezone("UTC"), hour=12,minute=0,second=0,
                  microsecond=0)
yesterday = today - datetime.timedelta(days=1)

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

# Get me a client, stat
spr_client = util.get_spreadsheet_client(config)
docs_client = util.get_docs_client(config)

changestamp = int(config.get('memory', 'changestamp'))

html = """
<h3>CSCAP Documents/Spreadsheet Changes</h3>
<br />
<p>Period: 7 AM %s - 7 AM %s

<p><table border="1" cellpadding="3" cellspacing="0">
<thead>
<tr><th>Time</th><th>Author</th><th>Type</th><th>Resource</th></tr>
</thead>
<tbody>
""" % (yesterday.strftime("%-d %B %Y"), today.strftime("%-d %B %Y"))

loopcount = 0
while 1:
    loopcount += 1
    #print '%s Get Feed changestamp: %s' % (loopcount, changestamp)
    feed = docs_client.get_changes(expand_acl=True, changestamp=changestamp)
    count = 0
    for entry in feed.entry:
        #edited = entry.get_elements('edited')
        count += 1
        link = entry.get_html_link()
        rtype = entry.get_resource_type()
        rtype = rtype_xref.get(rtype, rtype)
        if rtype in ['folder',]:
            continue
        title = entry.title.text
        if link:
            uri = link.href
        else:
            uri = '#'
        updated = datetime.datetime.strptime(entry.updated.text[:19], 
                                             '%Y-%m-%dT%H:%M:%S')
        updated = updated.replace(tzinfo=pytz.timezone("UTC"))
        changestamp = max(int(entry.changestamp.value) +1, changestamp)
        if updated < yesterday:
            print '%s %s updated: %s' % (title, rtype, entry.updated.text)
            continue
        updated = updated.astimezone(pytz.timezone("America/Chicago"))
        author = "N/A"
        if entry.last_modified_by:
            author = entry.last_modified_by.email.text
        html += "<tr><td>%s</td><td>%s</td><td>%s</td><td><a href=\"%s\">%s</a></td></tr>\n" % (
            updated.strftime("%-d %b %-I:%M %P"), author, rtype, uri, title)
        #if entry.filename:
        #    print entry.filename.text
        #print entry.changestamp.value
    if count == 0 or loopcount == 10:
        break

config.set('memory', 'changestamp', changestamp +1)
config.write( open('mytokens.cfg', 'w'))

html += """</tbody></table><p>That is all...""" 
msg = MIMEMultipart('alternative')
msg['Subject'] = "CSCAP Data ChangeLog"
msg['From'] = 'mesonet@mesonet.agron.iastate.edu'
msg['To'] = ','.join(EMAILS)


# Create the body of the message (a plain-text and an HTML version).
text = "See html variant"
# Record the MIME types of both parts - text/plain and text/html.
part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')

msg.attach(part1)
msg.attach(part2)

s = smtplib.SMTP('mailhub.iastate.edu')
s.sendmail(msg['From'], EMAILS, msg.as_string())
s.quit()

"""
<ns0:entry ns1:etag="&quot;DUgKSBIJRCt7ImBk&quot;" xmlns:ns0="http://www.w3.org/2005/Atom" xmlns:ns1="http://schemas.google.com/g/2005"><ns0:category label="viewed" scheme="http://schemas.google.com/g/2005/labels" term="http://schemas.google.com/g/2005/labels#viewed" /><ns0:category label="spreadsheet" scheme="http://schemas.google.com/g/2005#kind" term="http://schemas.google.com/docs/2007#spreadsheet" /><ns0:category label="modified-by-me" scheme="http://schemas.google.com/g/2005/labels" term="http://schemas.google.com/g/2005/labels#modified-by-me" /><ns0:category label="shared" scheme="http://schemas.google.com/g/2005/labels" term="http://schemas.google.com/g/2005/labels#shared" /><ns0:id>https://docs.google.com/feeds/id/spreadsheet%3A0AqZGw0coobCxdFNtQkk4VHM2blNQbTFGcGJ6WXpLeHc</ns0:id><ns1:lastModifiedBy><ns0:name>gevan.behnke</ns0:name><ns0:email>gevan.behnke@gmail.com</ns0:email></ns1:lastModifiedBy><ns1:feedLink href="https://docs.google.com/feeds/default/private/full/spreadsheet%3A0AqZGw0coobCxdFNtQkk4VHM2blNQbTFGcGJ6WXpLeHc/acl" rel="http://schemas.google.com/acl/2007#accessControlList" /><ns1:feedLink href="https://docs.google.com/feeds/default/private/full/spreadsheet%3A0AqZGw0coobCxdFNtQkk4VHM2blNQbTFGcGJ6WXpLeHc/revisions" rel="http://schemas.google.com/docs/2007/revisions" /><ns1:quotaBytesUsed>0</ns1:quotaBytesUsed><ns2:writersCanInvite value="true" xmlns:ns2="http://schemas.google.com/docs/2007" /><ns0:updated>2013-01-04T16:35:53.178Z</ns0:updated><ns0:published>2012-07-19T13:49:27.668Z</ns0:published><ns0:content src="https://docs.google.com/feeds/download/spreadsheets/Export?key=0AqZGw0coobCxdFNtQkk4VHM2blNQbTFGcGJ6WXpLeHc" type="text/html" /><ns1:resourceId>spreadsheet:0AqZGw0coobCxdFNtQkk4VHM2blNQbTFGcGJ6WXpLeHc</ns1:resourceId><ns1:lastViewed>2012-07-19T17:17:14.300Z</ns1:lastViewed><ns0:title>NWREC Nafziger &amp; Villamil Soil Bulk Density and Water Retention Data</ns0:title><ns0:author><ns0:name>akrherz</ns0:name><ns0:email>akrherz@gmail.com</ns0:email></ns0:author><ns0:link href="https://docs.google.com/feeds/default/private/full/folder%3A0B6ZGw0coobCxNTFkNmJkNjUtMGEzMS00YzQ5LTgxN2UtYzBjYzdiZjUzYmI5" rel="http://schemas.google.com/docs/2007#parent" title="NWREC - Nafziger &amp; Villamil" type="application/atom+xml" /><ns0:link href="https://docs.google.com/spreadsheet/ccc?key=0AqZGw0coobCxdFNtQkk4VHM2blNQbTFGcGJ6WXpLeHc" rel="alternate" type="text/html" /><ns0:link href="https://docs.google.com/spreadsheet/ccc?key=0AqZGw0coobCxdFNtQkk4VHM2blNQbTFGcGJ6WXpLeHc&amp;output=html&amp;chrome=false&amp;widget=true" rel="http://schemas.google.com/docs/2007#embed" type="text/html" /><ns0:link href="https://ssl.gstatic.com/docs/doclist/images/icon_11_spreadsheet_list.png" rel="http://schemas.google.com/docs/2007#icon" type="image/png" /><ns0:link href="https://docs.google.com/feeds/upload/create-session/default/private/full/spreadsheet%3A0AqZGw0coobCxdFNtQkk4VHM2blNQbTFGcGJ6WXpLeHc" rel="http://schemas.google.com/g/2005#resumable-edit-media" type="application/atom+xml" /><ns0:link href="https://docs.google.com/feeds/upload/file/default/private/full/spreadsheet%3A0AqZGw0coobCxdFNtQkk4VHM2blNQbTFGcGJ6WXpLeHc" rel="http://schemas.google.com/docs/2007#alt-edit-media" type="application/atom+xml" /><ns0:link href="https://docs.google.com/feeds/vt?authuser=0&amp;gd=true&amp;id=0AqZGw0coobCxdFNtQkk4VHM2blNQbTFGcGJ6WXpLeHc&amp;v=8&amp;s=AMedNnoAAAAAUS073-ApB77v7lYtk9R8d77RhWilvcOv&amp;sz=s220" rel="http://schemas.google.com/docs/2007/thumbnail" type="image/jpeg" /><ns0:link href="https://spreadsheets.google.com/feeds/worksheets/0AqZGw0coobCxdFNtQkk4VHM2blNQbTFGcGJ6WXpLeHc/private/full" rel="http://schemas.google.com/spreadsheets/2006#worksheetsfeed" type="application/atom+xml" /><ns0:link href="https://spreadsheets.google.com/feeds/0AqZGw0coobCxdFNtQkk4VHM2blNQbTFGcGJ6WXpLeHc/tables" rel="http://schemas.google.com/spreadsheets/2006#tablesfeed" type="application/atom+xml" /><ns0:link href="https://docs.google.com/feeds/default/private/full/spreadsheet%3A0AqZGw0coobCxdFNtQkk4VHM2blNQbTFGcGJ6WXpLeHc" rel="edit" type="application/atom+xml" /><ns0:link href="https://docs.google.com/feeds/default/media/spreadsheet%3A0AqZGw0coobCxdFNtQkk4VHM2blNQbTFGcGJ6WXpLeHc" rel="edit-media" type="text/html" /><ns0:link href="https://docs.google.com/feeds/default/private/full/spreadsheet%3A0AqZGw0coobCxdFNtQkk4VHM2blNQbTFGcGJ6WXpLeHc" rel="http://schemas.google.com/docs/2007#alt-self" type="application/atom+xml" /><ns0:link href="https://docs.google.com/feeds/default/private/changes/199742" rel="self" type="application/atom+xml" /><ns2:changestamp value="199742" xmlns:ns2="http://schemas.google.com/docs/2007" /><ns2:edited xmlns:ns2="http://www.w3.org/2007/app">2013-02-26T20:32:19.503Z</ns2:edited><ns2:isShareable value="true" xmlns:ns2="http://schemas.google.com/docs/2007" /><ns2:isShareableByMe value="true" xmlns:ns2="http://schemas.google.com/docs/2007" /><ns2:modifiedByMeDate xmlns:ns2="http://schemas.google.com/docs/2007">2012-07-19T17:17:37.214Z</ns2:modifiedByMeDate><ns2:hasForm value="false" xmlns:ns2="http://schemas.google.com/docs/2007" /></ns0:entry>
['AddCategory', 'AddLabel', 'FindAclLink', 'FindAlternateLink', 'FindChildren', 
'FindEditLink', 'FindEditMediaLink', 'FindExtensions', 'FindFeedLink',
 'FindHtmlLink', 'FindLicenseLink', 'FindMediaLink', 'FindNextLink', 
 'FindPostLink', 'FindPreviousLink', 'FindSelfLink', 'FindUrl',
  'GetAclFeedLink', 'GetAclLink', 'GetAlternateLink', 'GetAttributes',
   'GetCategories', 'GetEditLink', 'GetEditMediaLink', 'GetElements', 
   'GetFeedLink', 'GetFirstCategory', 'GetHtmlLink', 'GetId', 'GetLabels', 
   'GetLicenseLink', 'GetLink', 'GetNextLink', 'GetPostLink', 'GetPreviousLink',
    'GetResourceType', 'GetResumableCreateMediaLink', 'GetResumableEditMediaLink',
'GetRevisionsFeedLink', 'GetSelfLink', 'HasLabel', 'InCollections', 'IsHidden', 
'IsMedia', 'IsMine', 'IsPrivate', 'IsRestrictedDownload', 'IsSharedWithDomain', 
'IsStarred', 'IsTrashed', 'IsViewed', 'RemoveCategories', 'RemoveLabel', 
'SetResourceType', 'ToString', '_XmlElement__get_extension_attributes', 
'_XmlElement__get_extension_elements', '_XmlElement__set_extension_attributes', 
'_XmlElement__set_extension_elements', '__class__', '__delattr__', '__dict__',
 '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', 
 '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__',
  '__str__', '__subclasshook__', '__weakref__', '_attach_members', '_become_child', 
  '_get_namespace', '_get_rules', '_get_tag', '_harvest_tree', '_list_xml_members', 
  '_members', '_other_attributes', '_other_elements', '_qname', '_rule_set', 
  '_set_namespace', '_set_tag', '_to_tree', 'acl_feed', 'add_category', 
  'add_label', 'attributes', 'author', 'batch_id', 'batch_operation',
   'batch_status', 'category', 'changestamp', 'children', 'content', 
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
    'get_resumable_edit_media_link', 'get_revisions_feed_link', 
    'get_self_link', 'has_label', 'id', 'in_collections', 'is_hidden', 
    'is_media', 'is_mine', 'is_private', 'is_restricted_download', 
    'is_shared_with_domain', 'is_starred', 'is_trashed', 'is_viewed', 
    'last_modified_by', 'last_viewed', 'link', 'namespace', 'published', 
    'quota_bytes_used', 'remove_categories', 'remove_label', 'removed', 
    'resource_id', 'rights', 'set_resource_type', 'source', 'suggested_filename',
     'summary', 'tag', 'text', 'title', 'to_string', 'updated', 'writers_can_invite']
"""
