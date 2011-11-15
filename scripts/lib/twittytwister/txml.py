from twisted.internet import error
from twisted.web import sux, microdom

import logging
logger = logging.getLogger('twittytwister.txml')

class NoopParser(object):
    def __init__(self, n):
        self.name = n
        self.done = False
    def gotTagStart(self, name, attrs):
        pass
    def gotTagEnd(self, name, data):
        self.done = (name == self.name)
    def value(self):
        # don't store anything on the object after parsing this
        return None

class BaseXMLHandler(object):

    def __init__(self, n, handler_dict={}, enter_unknown=False):
        self.done = False
        self.current_ob = None
        self.tag_name = n
        self.before_delegates = {}
        self.after_delegates = {}
        self.handler_dict = handler_dict
        self.enter_unknown = enter_unknown

        for p in self.handler_dict:
            self.__dict__[self.cleanup(p)] = None

    def setBeforeDelegate(self, name, fn):
        self.before_delegates[name] = fn

    def setAfterDelegate(self, name, fn):
        self.after_delegates[name] = fn

    def setDelegate(self, name, before=None, after=None):
        if before:
            self.setBeforeDelegate(name, before)
        if after:
            self.setAfterDelegate(name, after)

    def setPredefDelegate(self, type, before=None, after=None):
        self.setDelegate(type.MY_TAG, before, after)

    def setSubDelegates(self, namelist, before=None, after=None):
        """Set a delegate for a sub-sub-item, according to a list of names"""
        if len(namelist) > 1:
            def set_sub(i):
                i.setSubDelegates(namelist[1:], before, after)
            self.setBeforeDelegate(namelist[0], set_sub)
        elif len(namelist) == 1:
            self.setDelegate(namelist[0], before, after)

    def objectStarted(self, name, o):
        if name in self.before_delegates:
            self.before_delegates[name](o)

    def objectFinished(self, name, o):
        if name in self.after_delegates:
            self.after_delegates[name](o)

    def gotTagStart(self, name, attrs):
        if self.current_ob:
            self.current_ob.gotTagStart(name, attrs)
        elif name in self.handler_dict:
            self.current_ob = self.handler_dict[name](name)
            self.objectStarted(name, self.current_ob)
        elif not self.enter_unknown:
            logger.warning("Got unknown tag %s in %s", name, self.__class__)
            self.current_ob = NoopParser(name)

    def gotTagEnd(self, name, data):
        if self.current_ob:
            self.current_ob.gotTagEnd(name, data)
            if self.current_ob.done:
                v = self.current_ob.value()
                if v is not None:
                    self.__dict__[self.cleanup(name)] = v
                    self.objectFinished(name, v)
                self.current_ob = None
        elif name == self.tag_name:
            self.done = True
            del self.current_ob
            self.gotFinalData(data)

    def gotFinalData(self, data):
        pass

    def value(self):
        # by default, the resulting value is the handler object itself,
        # but XMLStringHandler overwrites this
        return self

    def cleanup(self, n):
        return n.replace(':', '_')

    def __repr__(self):
        return "{%s %s}" % (self.tag_name, self.__dict__)

class XMLStringHandler(BaseXMLHandler):
    """XML data handler for simple string fields"""
    def gotFinalData(self, data):
        self.data = data

    def value(self):
        return self.data


class PredefinedXMLHandler(BaseXMLHandler):
    MY_TAG = ''
    SIMPLE_PROPS = []
    COMPLEX_PROPS = []

    # if set to True, contents inside unknown tags
    # will be parsed as if the unknown tags weren't
    # around it.
    ENTER_UNKNOWN = False

    def __init__(self, n):
        handler_dict = dict([(p.MY_TAG,p) for p in self.COMPLEX_PROPS])
        handler_dict.update([(p,XMLStringHandler) for p in self.SIMPLE_PROPS])
        super(PredefinedXMLHandler, self).__init__(n, handler_dict, self.ENTER_UNKNOWN)

class Author(PredefinedXMLHandler):
    MY_TAG = 'author'
    SIMPLE_PROPS = [ 'name', 'uri' ]

class Entry(PredefinedXMLHandler):
    MY_TAG = 'entry'
    SIMPLE_PROPS = ['id', 'published', 'title', 'content', 'link', 'updated',
                    'twitter:source', 'twitter:lang']
    COMPLEX_PROPS = [Author]

    def gotTagStart(self, name, attrs):
        super(Entry, self).gotTagStart(name, attrs)
        if name == 'link':
            self.__dict__[attrs['rel']] = attrs['href']

    def gotTagEnd(self, name, data):
        super(Entry, self).gotTagEnd(name, data)
        if name == 'link':
            del self.link

class Status(PredefinedXMLHandler):
    MY_TAG = 'status'
    SIMPLE_PROPS = ['created_at', 'id', 'text', 'source', 'truncated',
        'in_reply_to_status_id', 'in_reply_to_screen_name',
        'in_reply_to_user_id', 'favorited', 'user_id', 'geo']
    COMPLEX_PROPS = []

class RetweetedStatus(Status):
    MY_TAG = 'retweeted_status'

# circular reference:
Status.COMPLEX_PROPS.append(RetweetedStatus)


class User(PredefinedXMLHandler):
    MY_TAG = 'user'
    SIMPLE_PROPS = ['id', 'name', 'screen_name', 'location', 'description',
        'profile_image_url', 'url', 'protected', 'followers_count',
        'profile_background_color', 'profile_text_color', 'profile_link_color',
        'profile_sidebar_fill_color', 'profile_sidebar_border_color',
        'friends_count', 'created_at', 'favourites_count', 'utc_offset',
        'time_zone', 'following', 'notifications', 'statuses_count',
        'profile_background_image_url', 'profile_background_tile', 'verified',
        'geo_enabled']
    COMPLEX_PROPS = [Status]

# circular reference:
Status.COMPLEX_PROPS.append(User)


class SenderUser(User):
    MY_TAG = 'sender'

class RecipientUser(User):
    MY_TAG = 'recipient'

class DirectMessage(PredefinedXMLHandler):
    MY_TAG = 'direct_message'
    SIMPLE_PROPS = ['id', 'sender_id', 'text', 'recipient_id', 'created_at',
        'sender_screen_name', 'recipient_screen_name']
    COMPLEX_PROPS = [SenderUser, RecipientUser]


### simple object list handlers:

class SimpleListHandler(BaseXMLHandler):
    """Class for simple handlers that work with just a single type of element"""
    ITEM_TYPE = Entry
    ITEM_TAG = None

    @classmethod
    def item_tag(klass):
        tag = klass.ITEM_TAG
        if tag is None:
            tag = klass.ITEM_TYPE.MY_TAG
        return tag

    def __init__(self, n):
        type = self.ITEM_TYPE
        tag = self.item_tag()
        super(SimpleListHandler, self).__init__(n,
                 handler_dict={tag:type}, enter_unknown=True)

class EntryList(SimpleListHandler):
    MY_TAG = 'feed'
    ITEM_TYPE = Entry

class UserList(SimpleListHandler):
    MY_TAG = 'users'
    ITEM_TYPE = User

class DirectMessageList(SimpleListHandler):
    MY_TAG = 'direct-messages'
    ITEM_TYPE = DirectMessage

class StatusList(SimpleListHandler):
    MY_TAG = 'statuses'
    ITEM_TYPE = Status

class IDList(SimpleListHandler):
    MY_TAG = 'ids'
    ITEM_TYPE = XMLStringHandler
    ITEM_TAG = 'id'


class ListPage(PredefinedXMLHandler):
    """Base class for the classes of paging items"""
    SIMPLE_PROPS = ['next_cursor', 'previous_cursor']

class UserListPage(ListPage):
    MY_TAG = 'users_list'
    COMPLEX_PROPS = [UserList]

class IDListPage(ListPage):
    MY_TAG = 'id_list'
    COMPLEX_PROPS = [IDList]


def topLevelXMLHandler(toplevel_type):
    """Used to create a BaseXMLHandler object that just handles a single type of tag"""
    return BaseXMLHandler(None,
                          handler_dict={toplevel_type.MY_TAG:toplevel_type},
                          enter_unknown=True)


class Parser(sux.XMLParser):

    """A file-like thingy that parses a friendfeed feed with SUX."""
    def __init__(self, handler):
        self.connectionMade()
        self.data=[]
        self.handler=handler

    def write(self, b):
        self.dataReceived(b)
    def close(self):
        self.connectionLost(error.ConnectionDone())
    def open(self):
        pass
    def read(self):
        return None

    # XML Callbacks
    def gotTagStart(self, name, attrs):
        self.data=[]
        self.handler.gotTagStart(name, attrs)

    def gotTagEnd(self, name):
        self.handler.gotTagEnd(name, ''.join(self.data).decode('utf8'))

    def gotText(self, data):
        self.data.append(data)

    def gotEntityReference(self, data):
        e = {'quot': '"', 'lt': '&lt;', 'gt': '&gt;', 'amp': '&amp;'}
        if e.has_key(data):
            self.data.append(e[data])
        elif data[0] == '#':
            self.data.append('&' + data + ';')
        else:
            logger.error("Unhandled entity reference: %s\n" % (data))


def listParser(list_type, delegate, extra_args=None):
    toplevel_type = list_type.ITEM_TYPE

    if extra_args:
        args = (extra_args,)
    else:
        args = ()

    def do_delegate(e):
        delegate(e, *args)

    handler = list_type(None)
    handler.setPredefDelegate(toplevel_type, after=do_delegate)
    return Parser(handler)

def simpleListFactory(list_type):
    """Used for simple parsers that support only one type of object"""
    def create(delegate, extra_args=None):
        """Create a Parser object for the specific tag type, on the fly"""
        return listParser(list_type, delegate, extra_args)
    return create



Feed     = simpleListFactory(EntryList)

Users    = simpleListFactory(UserList)

Direct   = simpleListFactory(DirectMessageList)

Statuses = simpleListFactory(StatusList)

HoseFeed = simpleListFactory(StatusList)


class Pager:
    """Able to create parsers that support paging, and parsers that don't"""
    def __init__(self, page_type, list_type):
        self.page_type = page_type
        self.list_type = list_type

    def pagingParser(self, delegate, page_delegate):
        item_tag = self.list_type.item_tag()
        root_handler = topLevelXMLHandler(self.page_type)
        root_handler.setPredefDelegate(self.page_type, after=page_delegate)
        root_handler.setSubDelegates([self.page_type.MY_TAG, self.list_type.MY_TAG, item_tag], after=delegate)
        return Parser(root_handler)

    def noPagingParser(self, delegate):
        item_tag = self.list_type.item_tag()
        root_handler = topLevelXMLHandler(self.list_type)
        root_handler.setSubDelegates([self.list_type.MY_TAG, item_tag], after=delegate)
        return Parser(root_handler)


PagedUserList = Pager(UserListPage, UserList)
PagedIDList = Pager(IDListPage, IDList)


def parseXML(xml):
    return microdom.parseXMLString(xml)

def parseUpdateResponse(xml):
    return parseXML(xml).getElementsByTagName("id")[0].firstChild().data

# vim: set expandtab:
