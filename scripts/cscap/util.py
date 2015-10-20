"""
Utility Functions that are common to our scripts, I hope
"""
import gdata.gauth
import gdata.spreadsheets.client
import gdata.spreadsheets.data as spdata
import gdata.docs.client

import json
import os

# Load up the CONFIG
CONFIG = json.load(open('%s/mytokens.json' % (os.path.dirname(__file__),)))


def save_config():
    """ Save the configuration to disk """
    json.dump(CONFIG, open('mytokens.json', 'w'))


class Worksheet(object):

    def __init__(self, spr_client, entry):
        self.spr_client = spr_client
        self.entry = entry
        self.set_metadata()
        self.id = entry.id.text.split("/")[-1]
        self.spread_id = entry.id.text.split("/")[-2]

    def set_metadata(self):
        self.title = self.entry.title.text
        self.rows = int(self.entry.row_count.text)
        self.cols = int(self.entry.col_count.text)
        self.cell_feed = None
        self.list_feed = None
        self.data = {}
        self.numdata = {}

    def refetch_feed(self):
        self.entry = self.spr_client.get_worksheet(self.spread_id, self.id)
        self.set_metadata()

    def get_list_feed(self):
        if self.list_feed is not None:
            return self.list_feed
        self.list_feed = self.spr_client.get_list_feed(self.spread_id, self.id)
        return self.list_feed

    def get_cell_feed(self):
        if self.cell_feed is not None:
            return
        self.cell_feed = self.spr_client.get_cells(self.spread_id, self.id)
        for entry in self.cell_feed.entry:
            row = entry.cell.row
            _rowstore = self.data.setdefault(row, dict())
            # https://developers.google.com/google-apps/spreadsheets/?hl=en#working_with_cell-based_feeds
            # The input_value could be a function, pick the numeric_value
            # first, which can be None for non-numeric types
            if entry.cell.numeric_value is not None:
                _numstore = self.numdata.setdefault(row, dict())
                _numstore[entry.cell.col] = entry.cell.numeric_value
            _rowstore[entry.cell.col] = entry.cell.input_value

    def get_cell_value(self, row, col, numeric=False):
        """Return the cell value

        Args:
          row (int): the raw desired
          col (int): the column desired
          numeric (bool): Attempt to use the numeric value before the text val

        Returns:
          object
        """
        if not numeric:
            return self.data.get(str(row), {}).get(str(col))
        txtval = self.data.get(str(row), {}).get(str(col))
        numval = self.numdata.get(str(row), {}).get(str(col))
        return (numval if numval is not None else txtval)

    def get_cell_entry(self, row, col):
        for entry in self.cell_feed.entry:
            if entry.cell.row == str(row) and entry.cell.col == str(col):
                return entry
        return None

    def del_column(self, label):
        """ Delete a column from the worksheet that has a given label
        this also zeros out any data in the column too
        """
        self.get_cell_feed()
        for col in range(1, int(self.cols)+1):
            if self.get_cell_value(1, col) != label:
                continue
            print 'Found %s in column %s, deleting column' % (label, col)
            entry = self.get_cell_entry(1, col)
            entry.cell.input_value = ""
            self.spr_client.update(entry)

            updateFeed = spdata.build_batch_cells_update(self.spread_id,
                                                         self.id)
            for row in range(1, int(self.rows)+1):
                updateFeed.add_set_cell(str(row), str(col), "")
            self.cell_feed = self.spr_client.batch(updateFeed, force=True)

        self.refetch_feed()
        while self.trim_columns():
            print 'Trimming Columns!'

    def add_column(self, label, row2=None, row3=None):
        """ Add a column, if it does not exist """
        self.get_cell_feed()
        for col in range(1, int(self.cols)+1):
            if self.get_cell_value("1", col) == label:
                print 'Column %s with label already found: %s' % (col, label)
                return
        self.cols = self.cols + 1
        self.entry.col_count.text = "%s" % (self.cols,)
        self.entry = self.spr_client.update(self.entry)

        for i, lbl in enumerate([label, row2, row3]):
            if lbl is None:
                continue
            entry = self.spr_client.get_cell(self.spread_id, self.id,
                                             str(i+1),
                                             str(self.cols))
            entry.cell.input_value = lbl
            self.spr_client.update(entry)

        self.refetch_feed()
        self.cell_feed = None

    def drop_last_column(self):
        self.cols = self.cols - 1
        self.entry.col_count.text = "%s" % (self.cols,)
        self.entry = self.spr_client.update(self.entry)
        self.cell_feed = None

    def trim_columns(self):
        """ Attempt to trim off any extraneous columns """
        self.get_cell_feed()
        for col in range(1, int(self.cols)+1):
            if self.data["1"].get(str(col)) is not None:
                continue
            print 'Column Delete Candidate %s' % (col,)
            found_data = False
            for row in range(1, int(self.rows)+1):
                if self.data.get(str(row), {}).get(str(col)) is not None:
                    found_data = True
                    print(('ERROR row: %s has data: %s'
                           ) % (row, self.data[str(row)][str(col)]))
            if not found_data:
                print 'Deleting column %s' % (col,)
                if col == int(self.cols):
                    self.drop_last_column()
                    return True
                # Move columns left
                updateFeed = spdata.build_batch_cells_update(self.spread_id,
                                                             self.id)
                for col2 in range(int(col), int(self.cols)):
                    for row in range(1, int(self.rows)+1):
                        updateFeed.add_set_cell(str(row), str(col2),
                                                self.get_cell_value(row,
                                                                    col2 + 1))
                self.cell_feed = self.spr_client.batch(updateFeed, force=True)
                # Drop last column
                self.refetch_feed()
                self.drop_last_column()
                return True
        return False


class Spreadsheet(object):

    def __init__(self, spr_client, resource_id):
        self.spr_client = spr_client
        self.id = resource_id
        self.worksheets = {}
        self.get_worksheets()

    def get_worksheets(self):
        """ Get the worksheets associated with this spreadsheet """
        feed = self.spr_client.GetWorksheets(self.id)
        for entry in feed.entry:
            self.worksheets[entry.title.text] = Worksheet(self.spr_client,
                                                          entry)


def get_xref_siteids_plotids(spr_client, config):
    ''' Get a dict of site IDs with a list of plot IDs for each '''
    spreadkeys = get_xref_plotids(spr_client, config)
    data = {}
    for uniqueid in spreadkeys.keys():
        data[uniqueid.lower()] = []
        feed = spr_client.get_list_feed(spreadkeys[uniqueid], 'od6')
        for entry in feed.entry:
            d = entry.to_dict()
            if d['plotid'] is None:
                continue
            data[uniqueid.lower()].append(d['plotid'].lower())
    return data


def get_xref_plotids(spr_client, config):
    ''' Build the xreference of siteID to plotid spreadsheet keys '''
    feed = spr_client.get_list_feed(config.get('cscap', 'metamaster'), 'od6')
    data = {}
    for entry in feed.entry:
        d = entry.to_dict()
        data[d['uniqueid']] = d['keyspread']
    return data


def get_docs_client(config):
    """ Return an authorized docs client """
    token = gdata.gauth.OAuth2Token(
        client_id=config.get('appauth', 'client_id'),
        client_secret=config.get('appauth', 'app_secret'),
        user_agent='daryl.testing',
        scope=config.get('googleauth', 'scopes'),
        refresh_token=config.get('googleauth', 'refresh_token'))

    docs_client = gdata.docs.client.DocsClient()
    token.authorize(docs_client)
    return docs_client


def get_spreadsheet_client(config):
    """ Return an authorized spreadsheet client """
    token = gdata.gauth.OAuth2Token(
        client_id=config.get('appauth', 'client_id'),
        client_secret=config.get('appauth', 'app_secret'),
        user_agent='daryl.testing',
        scope=config.get('googleauth', 'scopes'),
        refresh_token=config.get('googleauth', 'refresh_token'))

    spr_client = gdata.spreadsheets.client.SpreadsheetsClient()
    token.authorize(spr_client)
    return spr_client


def get_sites_client(config, site='sustainablecorn'):
    """ Return an authorized sites client """
    import gdata.sites.client as sclient
    token = gdata.gauth.OAuth2Token(
        client_id=config.get('appauth', 'client_id'),
        client_secret=config.get('appauth', 'app_secret'),
        user_agent='daryl.testing',
        scope=config.get('googleauth', 'scopes'),
        refresh_token=config.get('googleauth', 'refresh_token'))

    spr_client = sclient.SitesClient(site=site)
    token.authorize(spr_client)
    return spr_client


def build_treatments(feed):
    """
    Process the Treatments spreadsheet and generate a dictionary of
    field metadata
    @param feed the processed spreadsheet feed
    """
    data = None
    treatment_names = {}
    for entry in feed.entry:
        row = entry.to_dict()
        if data is None:
            data = {}
            for key in row.keys():
                if key in ['uniqueid', 'name', 'key'] or key[0] == '_':
                    continue
                print 'Found Key: %s' % (key,)
                data[key] = {'TIL': [None, ], 'ROT': [None, ], 'DWM': [None, ],
                             'NIT': [None, ],
                             'LND': [None, ], 'REPS': 1}
        if 'key' not in row or row['key'] is None or row['key'] == '':
            continue
        treatment_key = row['key']
        treatment_names[treatment_key] = row['name'].strip()
        for colkey in row.keys():
            cell = row[colkey]
            if colkey in data.keys():  # Is sitekey
                sitekey = colkey
                if cell is not None and cell != '':
                    if treatment_key[:3] in data[sitekey].keys():
                        data[sitekey][treatment_key[:3]].append(treatment_key)
                if treatment_key == 'REPS' and cell not in ('?', 'TBD', None):
                    print 'Found REPS for site: %s as: %s' % (sitekey,
                                                              int(cell))
                    data[sitekey]['REPS'] = int(cell)

    return data, treatment_names


def build_sdc(feed):
    """
    Process the Site Data Collected spreadsheet
    @param feed the processed spreadsheet feed
    @return data is a two tier dictionary of years x siteids
    """
    data = None
    sdc_names = {}
    site_ids = []
    for entry in feed.entry:
        # Turn the entry into a dictionary with the first row being the keys
        row = entry.to_dict()
        if data is None:
            data = {'2011': {}, '2012': {}, '2013': {}, '2014': {}, '2015': {}}
            for key in row.keys():
                if key in ['uniqueid', 'name', 'key'] or key[0] == '_':
                    continue
                site_ids.append(key)
                for yr in ['2011', '2012', '2013', '2014', '2015']:
                    data[yr][key] = []
        # If the 'KEY' column is blank or has nothing in it, skip it...
        if row['key'] is None or row['key'] == '':
            continue
        # This is our Site Data Collected Key Identifier
        sdc_key = row['key']
        sdc_names[sdc_key] = {'name': row['name'], 'units': row['units']}

        # Iterate over our site_ids
        for sitekey in site_ids:
            if row[sitekey] is None:
                continue
            for yr in ['2011', '2012', '2013', '2014', '2015']:
                if (row[sitekey].strip().lower() == 'x' or
                        row[sitekey].find('%s' % (yr[2:],)) > -1):
                    data[yr][sitekey].append(sdc_key)

    return data, sdc_names


def get_site_metadata(config, spr_client=None):
    '''
    Return a dict of research site metadata
    '''
    meta = {}
    if spr_client is None:
        spr_client = get_spreadsheet_client(config)

    lf = spr_client.get_list_feed(config.get('cscap', 'metamaster'), 'od6')
    for entry in lf.entry:
        d = entry.to_dict()
        meta[d['uniqueid']] = {'climate_site': d['iemclimatesite'].split()[0],
                               }
    return meta


def get_driveclient():
    """ Return an authorized apiclient """
    from oauth2client.client import SignedJwtAssertionCredentials
    from httplib2 import Http
    from apiclient.discovery import build

    client_email = CONFIG['service_account']
    with open("CSCAP-6886c10d6ffb.p12") as f:
        private_key = f.read()

    credentials = SignedJwtAssertionCredentials(
        client_email, private_key,
        'https://www.googleapis.com/auth/drive.readonly')

    http_auth = credentials.authorize(Http())

    return build('drive', 'v2', http=http_auth)


def get_folders(drive):
    """Return a dict of Google Drive Folders"""
    f = {}

    folders = drive.files().list(
        q="mimeType = 'application/vnd.google-apps.folder'",
        maxResults=999).execute()
    for _, item in enumerate(folders['items']):
        f[item['id']] = dict(title=item['title'], parents=[],
                             basefolder=None)
        for parent in item['parents']:
            f[item['id']]['parents'].append(parent['id'])

    for thisfolder in f:
        # title = f[thisfolder]['title']
        if len(f[thisfolder]['parents']) == 0:
            continue
        parentfolder = f[thisfolder]['parents'][0]
        while len(f[parentfolder]['parents']) > 0:
            parentfolder = f[parentfolder]['parents'][0]
        # print title, '->', f[parentfolder]['title']
        f[thisfolder]['basefolder'] = parentfolder
    return f
