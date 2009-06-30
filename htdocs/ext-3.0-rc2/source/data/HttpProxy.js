/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */

/**
 * @class Ext.data.HttpProxy
 * @extends Ext.data.DataProxy
 * <p>An implementation of {@link Ext.data.DataProxy} that processes data requests within the same
 * domain of the originating page.</p>
 * <p><b>Note</b>: this class cannot be used to retrieve data from a domain other
 * than the domain from which the running page was served. For cross-domain requests, use a
 * {@link Ext.data.ScriptTagProxy ScriptTagProxy}.</p>
 * <p>Be aware that to enable the browser to parse an XML document, the server must set
 * the Content-Type header in the HTTP response to "<tt>text/xml</tt>".</p>
 * @constructor
 * @param {Object} conn
 * An {@link Ext.data.Connection} object, or options parameter to {@link Ext.Ajax#request}.
 * <p>Note that if this HttpProxy is being used by a (@link Ext.data.Store Store}, then the
 * Store's call to {@link #load} will override any specified <tt>callback</tt> and <tt>params</tt>
 * options. In this case, use the Store's {@link Ext.data.Store#events events} to modify parameters,
 * or react to loading events. The Store's {@link Ext.data.Store#baseParams baseParams} may also be
 * used to pass parameters known at instantiation time.</p>
 * <p>If an options parameter is passed, the singleton {@link Ext.Ajax} object will be used to make
 * the request.</p>
 */
Ext.data.HttpProxy = function(conn){
    Ext.data.HttpProxy.superclass.constructor.call(this, conn);

    /**
     * The Connection object (Or options parameter to {@link Ext.Ajax#request}) which this HttpProxy
     * uses to make requests to the server. Properties of this object may be changed dynamically to
     * change the way data is requested.
     * @property
     */
    this.conn = conn;

    // nullify the connection url.  The url param has been copied to "this" above.  The connection
    // url will be set during each execution of doRequest when buildUrl is called.  This makes it easier for users to override the
    // connection url during beforeaction events (ie: beforeload, beforesave, etc).  The connection url will be nullified
    // after each request as well.  Url is always re-defined during doRequest.
    this.conn.url = null;

    this.useAjax = !conn || !conn.events;

    //private.  A hash containing active requests, keyed on action [Ext.data.Api.actions.create|read|update|destroy]
    var actions = Ext.data.Api.actions
    this.activeRequest = {};
    for (var verb in actions) {
        this.activeRequest[actions[verb]] = undefined;
    }
};

Ext.extend(Ext.data.HttpProxy, Ext.data.DataProxy, {
    /**
     * @cfg {Boolean} restful
     * <p>If set to <tt>true</tt>, a {@link Ext.data.Record#phantom non-phantom} record's
     * {@link Ext.data.Record#id id} will be appended to the url (defaults to <tt>false</tt>).</p><br>
     * <p>The url is built based upon the action being executed <tt>[load|create|save|destroy]</tt>
     * using the commensurate <tt>{@link #api}</tt> property, or if undefined default to the
     * configured {@link Ext.data.Store}.{@link Ext.data.Store#url url}.</p><br>
     * <p>Some MVC (eg, Ruby on Rails, Merb and Django) support this style of segment based urls
     * where the segments in the URL follow the Model-View-Controller approach.</p><pre><code>
     * someSite.com/controller/action/id
     * </code></pre>
     * Where the segments in the url are typically:<div class="mdetail-params"><ul>
     * <li>The first segment : represents the controller class that should be invoked.</li>
     * <li>The second segment : represents the class function, or method, that should be called.</li>
     * <li>The third segment : represents the ID (a variable typically passed to the method).</li>
     * </ul></div></p>
     * <p>For example:</p>
     * <pre><code>
api: {
    load :    '/controller/load',
    create :  '/controller/new',  // Server MUST return idProperty of new record
    save :    '/controller/update',
    destroy : '/controller/destroy_action'
}

// Alternatively, one can use the object-form to specify each API-action
api: {
    load: {url: 'read.php', method: 'GET'},
    create: 'create.php',
    destroy: 'destroy.php',
    save: 'update.php'
}
     */

    /**
     * Return the {@link Ext.data.Connection} object being used by this Proxy.
     * @return {Connection} The Connection object. This object may be used to subscribe to events on
     * a finer-grained basis than the DataProxy events.
     */
    getConnection : function() {
        return this.useAjax ? Ext.Ajax : this.conn;
    },

    /**
     * Used for overriding the url used for a single request.  Designed to be called during a beforeaction event.  Calling setUrl
     * will override any urls set via the api configuration parameter.  Set the optional parameter makePermanent to set the url for
     * all subsequent requests.  If not set to makePermanent, the next request will use the same url or api configuration defined
     * in the initial proxy configuration.
     * @param {String} url
     * @param {Boolean} makePermanent (Optional) [false]
     *
     * (eg: beforeload, beforesave, etc).
     */
    setUrl : function(url, makePermanent) {
        this.conn.url = url;
        if (makePermanent === true) {
            this.url = url;
            Ext.data.Api.prepare(this);
        }
    },

    /**
     * HttpProxy implementation of DataProxy#doRequest
     * @param {String} action The crud action type (create, read, update, destroy)
     * @param {Ext.data.Record/Ext.data.Record[]} rs If action is load, rs will be null
     * @param {Object} params An object containing properties which are to be used as HTTP parameters
     * for the request to the remote server.
     * @param {Ext.data.DataReader} reader The Reader object which converts the data
     * object into a block of Ext.data.Records.
     * @param {Function} callback
     * <div class="sub-desc"><p>A function to be called after the request.
     * The <tt>callback</tt> is passed the following arguments:<ul>
     * <li><tt>r</tt> : Ext.data.Record[] The block of Ext.data.Records.</li>
     * <li><tt>options</tt>: Options object from the action request</li>
     * <li><tt>success</tt>: Boolean success indicator</li></ul></p></div>
     * @param {Object} scope The scope in which to call the callback
     * @param {Object} arg An optional argument which is passed to the callback as its second parameter.
     */
    doRequest : function(action, rs, params, reader, cb, scope, arg) {
        var  o = {
            params : params || {},
            method: (this.api[action]) ? this.api[action]['method'] : undefined,
            request: {
                callback : cb,
                scope : scope,
                arg : arg
            },
            reader: reader,
            callback : this.createCallback(action, rs),
            scope: this
        };
        // Set the connection url.  If this.conn.url is not null here,
        // the user may have overridden the url during a beforeaction event-handler.
        // this.conn.url is nullified after each request.
        if (this.conn.url === null) {
            this.conn.url = this.buildUrl(action, rs);
        }
        else if (this.restful === true && rs instanceof Ext.data.Record && !rs.phantom) {
            this.conn.url += '/' + rs.id;
        }
        if(this.useAjax){

            Ext.applyIf(o, this.conn);

            // If a currently running request is found for this action, abort it.
            if (this.activeRequest[action]) {
                // Disabled aborting activeRequest while implementing REST.  activeRequest[action] will have to become an array
                //Ext.Ajax.abort(this.activeRequest[action]);
            }
            this.activeRequest[action] = Ext.Ajax.request(o);
        }else{
            this.conn.request(o);
        }
        // request is sent, nullify the connection url in preparation for the next request
        this.conn.url = null;
    },

    /**
     * Returns a callback function for a request.  Note a special case is made for the
     * read action vs all the others.
     * @param {String} action [create|update|delete|load]
     * @param {Ext.data.Record[]} rs The Store-recordset being acted upon
     * @private
     */
    createCallback : function(action, rs) {
        return function(o, success, response) {
            this.activeRequest[action] = undefined;
            if (!success) {
                if (action === Ext.data.Api.actions.read) {
                    // @deprecated: fire loadexception for backwards compat.
                    this.fireEvent("loadexception", this, o, response);
                }
                this.fireEvent('exception', this, 'response', action, o, response);
                o.request.callback.call(o.request.scope, null, o.request.arg, false);
                return;
            }
            if (action === Ext.data.Api.actions.read) {
                this.onRead(action, o, response);
            } else {
                this.onWrite(action, o, response, rs);
            }
        }
    },

    /**
     * Callback for read actions
     * @param {String} action [Ext.data.Api.actions.create|read|update|destroy]
     * @param {Object} trans The request transaction object
     * @param {Object} res The server response
     * @private
     */
    onRead : function(action, o, response) {
        var result;
        try {
            result = o.reader.read(response);
        }catch(e){
            // @deprecated: fire old loadexception for backwards-compat.
            this.fireEvent("loadexception", this, o, response, e);
            this.fireEvent('exception', this, 'response', action, o, response, e);
            o.request.callback.call(o.request.scope, null, o.request.arg, false);
            return;
        }
        if (result.success === false) {
            // @deprecated: fire old loadexception for backwards-compat.
            this.fireEvent('loadexception', this, o, response);

            // Get DataReader read-back a response-object to pass along to exception event
            var res = o.reader.readResponse(action, response);
            this.fireEvent('exception', this, 'remote', action, o, res, null);
        }
        else {
            this.fireEvent("load", this, o, o.request.arg);
        }
        o.request.callback.call(o.request.scope, result, o.request.arg, result.success);
    },
    /**
     * Callback for write actions
     * @param {String} action [Ext.data.Api.actions.create|read|update|destroy]
     * @param {Object} trans The request transaction object
     * @param {Object} res The server response
     * @private
     */
    onWrite : function(action, o, response, rs) {
        var reader = o.reader;
        var res;
        try {
            res = reader.readResponse(action, response);
        } catch (e) {
            this.fireEvent('exception', this, 'response', action, o, response, e);
            o.request.callback.call(o.request.scope, null, o.request.arg, false);
            return;
        }
        if (res[reader.meta.successProperty] === false) {
            this.fireEvent('exception', this, 'remote', action, o, res, rs);
        } else {
            this.fireEvent("write", this, action, res[reader.meta.root], res, rs, o.request.arg);
        }
        o.request.callback.call(o.request.scope, res[reader.meta.root], res, res[reader.meta.successProperty]);
    },

    // inherit docs
    destroy: function(){
        if(!this.useAjax){
            this.conn.abort();
        }else if(this.activeRequest){
            var actions = Ext.data.Api.actions;
            for (var verb in actions) {
                if(this.activeRequest[actions[verb]]){
                    Ext.Ajax.abort(this.activeRequest[actions[verb]]);
                }
            }
        }
        Ext.data.HttpProxy.superclass.destroy.call(this);
    }
});