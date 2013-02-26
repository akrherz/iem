"""
Utility Functions that are common to our scripts, I hope
"""
import gdata.gauth
import gdata.spreadsheets.client
import gdata.spreadsheets.data as spdata
import gdata.docs.client

class Worksheet(object):
    
    def __init__(self, doc_client, spr_client, entry):
        self.doc_client = doc_client
        self.spr_client = spr_client
        self.entry = entry
        self.set_metadata()
        self.id = entry.id.text.split("/")[-1]
        self.spread_id = entry.id.text.split("/")[-2]
        
    def set_metadata(self):
        self.title = self.entry.title.text
        self.rows = int( self.entry.row_count.text )
        self.cols = int( self.entry.col_count.text )
        self.cell_feed = None
        self.data = {}

    def refetch_feed(self):
        self.entry = self.spr_client.get_worksheet(self.spread_id, self.id)
        self.set_metadata()

    def get_cell_feed(self):
        if self.cell_feed is not None:
            return
        self.cell_feed = self.spr_client.get_cells(self.spread_id, self.id)
        for entry in self.cell_feed.entry:
            row = entry.cell.row
            if not self.data.has_key(row):
                self.data[row] = {}
            self.data[ row ][ entry.cell.col ] = entry.cell.input_value

    def get_cell_value(self, row, col):
        return self.data.get(str(row), {}).get(str(col))

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
            if self.get_cell_value(1, col) == label:
                print 'Found %s in column %s, deleting column' % (label, col)
                entry = self.get_cell_entry(1, col)
                entry.cell.input_value = ""
                self.spr_client.update(entry)

                updateFeed = spdata.build_batch_cells_update(self.spread_id, self.id)
                for row in range(1, int(self.rows)+1): 
                    updateFeed.add_set_cell(str(row), str(col), "")
                self.cell_feed = self.spr_client.batch(updateFeed, force=True)

        self.refetch_feed()
        while self.trim_columns():
            print 'Trimming Columns!'

    def add_column(self, label):
        """ Add a column, if it does not exist """
        self.get_cell_feed()
        for col in range(1, int(self.cols)+1):
            if self.get_cell_value("1", col) == label:
                print 'Column %s with label already found: %s' % (col, label)
                return
        self.cols = self.cols + 1
        self.entry.col_count.text = "%s" % (self.cols,)
        self.entry = self.spr_client.update(self.entry)
        # Get cell
        entry = self.spr_client.get_cell(self.spread_id, self.id, "1", str(self.cols))
        entry.cell.input_value = label
        self.spr_client.update(entry)
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
                    print 'ERROR row: %s has data: %s' % (row,
                                    self.data[str(row)][str(col)])
            if not found_data:
                print 'Deleting column %s' % (col,)
                if col == int(self.cols):
                    self.drop_last_column()
                    return True
                # Move columns left
                updateFeed = spdata.build_batch_cells_update(self.spread_id, self.id)
                for col2 in range(int(col), int(self.cols)):
                    for row in range(1, int(self.rows)+1): 
                        updateFeed.add_set_cell(str(row), str(col2), 
                                                self.get_cell_value(row, col2 + 1))
                self.cell_feed = self.spr_client.batch(updateFeed, force=True)
                # Drop last column
                self.refetch_feed()
                self.drop_last_column()
                return True
        return False
 
class Spreadsheet(object):
    
    def __init__(self, docs_client, spr_client, entry):
        self.docs_client = docs_client
        self.spr_client = spr_client
        self.entry = entry
        self.id = entry.resource_id.text.split(":")[1]
        self.title = entry.title.text
        self.worksheets = {}
        self.get_worksheets()
    
    def get_worksheets(self):
        """ Get the worksheets associated with this spreadsheet """
        feed = self.spr_client.GetWorksheets( self.id )
        for entry in feed.entry:
            self.worksheets[ entry.title.text ] = Worksheet(self.docs_client,
                                                            self.spr_client,
                                                             entry )

def get_docs_client(config):
    """ Return an authorized docs client """
    token = gdata.gauth.OAuth2Token(client_id=config.get('appauth','client_id'),
                    client_secret=config.get('appauth', 'app_secret'),
                    user_agent='daryl.testing',
                    scope=config.get('googleauth', 'scopes'),
                    refresh_token=config.get('googleauth', 'refresh_token'))

    docs_client = gdata.docs.client.DocsClient()
    token.authorize(docs_client)
    return docs_client

def get_spreadsheet_client(config):
    """ Return an authorized spreadsheet client """
    token = gdata.gauth.OAuth2Token(client_id=config.get('appauth','client_id'),
                    client_secret=config.get('appauth', 'app_secret'),
                    user_agent='daryl.testing',
                    scope=config.get('googleauth', 'scopes'),
                    refresh_token=config.get('googleauth', 'refresh_token'))

    spr_client = gdata.spreadsheets.client.SpreadsheetsClient()
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
                if key in ['uniqueid','name','key'] or key[0] == '_':
                    continue
                print 'Found Key: %s' % (key,)
                data[key] = {'TIL': [None,], 'ROT': [None,], 'DWM': [None,], 
                             'NIT': [None,], 
                             'LND': [None,], 'REPS': 1}
        if row['key'] is None or row['key'] == '':
            continue
        treatment_key = row['key']
        treatment_names[treatment_key] = row['name']
        for colkey in row.keys():
            cell = row[colkey]
            if colkey in data.keys(): # Is sitekey
                sitekey = colkey
                if cell is not None and cell != '':
                    if treatment_key[:3] in data[sitekey].keys():
                        data[sitekey][treatment_key[:3]].append( treatment_key )
                if treatment_key == 'REPS' and cell not in ('?','TBD', None):
                    print 'Found REPS for site: %s as: %s' % (sitekey, int(cell))
                    data[sitekey]['REPS'] = int(cell)
    
    return data, treatment_names

def build_sdc(feed):
    """
    Process the Site Data Collected spreadsheet
    @param feed the processed spreadsheet feed
    """
    data = None
    sdc_names = {}
    for entry in feed.entry:
        row = entry.to_dict()
        if data is None:
            data = {}
            for key in row.keys():
                if key in ['uniqueid','name','key'] or key[0] == '_':
                    continue
                print 'Found Key: %s' % (key,)
                data[key] = []
        if row['key'] is None or row['key'] == '':
            continue
        sdc_key = row['key']
        sdc_names[sdc_key] = {'name': row['name'], 'units': row['units']}
        for sitekey in row.keys():
            if sitekey in data.keys():
                if row[sitekey] is not None and row[sitekey] != '':
                    data[sitekey].append( sdc_key )
    return data, sdc_names