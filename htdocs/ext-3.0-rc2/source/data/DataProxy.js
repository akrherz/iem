/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */

/**
 * @class Ext.data.DataProxy
 * @extends Ext.util.Observable
 * <p>Abstract base class for implementations which provide retrieval of unformatted data objects.
 * This class is intended to be extended and should not be created directly. For existing implementations,
 * see {@link Ext.data.DirectProxy}, {@link Ext.data.HttpProxy}, {@link Ext.data.ScriptTagProxy} and
 * {@link Ext.data.MemoryProxy}.</p>
 * <p>DataProxy implementations are usually used in conjunction with an implementation of {@link Ext.data.DataReader}
 * (of the appropriate type which knows how to parse the data object) to provide a block of
 * {@link Ext.data.Records} to an {@link Ext.data.Store}.</p>
 * <p>The parameter to a DataProxy constructor may be an {@link Ext.data.Connection} or can also be the
 * config object to an {@link Ext.data.Connection}.</p>
 * <p>Custom implementations must implement either the <code><b>doRequest</b></code> method (preferred) or the
 * <code>load</code> method (deprecated). See
 * {@link Ext.data.HttpProxy}.{@link Ext.data.HttpProxy#doRequest doRequest} or
 * {@link Ext.data.HttpProxy}.{@link Ext.data.HttpProxy#load load} for additional details.</p>
 * <p><b><u>Example 1</u></b></p>
 * <pre><code>
proxy: new Ext.data.ScriptTagProxy({
    {@link Ext.data.Connection#url url}: 'http://extjs.com/forum/topics-remote.php'
}),
 * </code></pre>
 * <p><b><u>Example 2</u></b></p>
 * <pre><code>
proxy : new Ext.data.HttpProxy({
    {@link Ext.data.Connection#method method}: 'GET',
    {@link Ext.data.HttpProxy#prettyUrls prettyUrls}: false,
    {@link Ext.data.Connection#url url}: 'local/default.php', // see options parameter for {@link Ext.Ajax#request}
    {@link #api}: {
        // all actions except the following will use above url
        create  : 'local/new.php',
        update  : 'local/update.php'
    }
}),
 * </code></pre>
 */
Ext.data.DataProxy = function(conn){
    // make sure we have a config object here to support ux proxies.
    // All proxies should now send config into superclass constructor.
    conn = conn || {};

    // This line caused a bug when people use custom Connection object having its own request method.
    // http://extjs.com/forum/showthread.php?t=67194.  Have to set DataProxy config
    //Ext.applyIf(this, conn);

    this.api     = conn.api;
    this.url     = conn.url;
    this.restful = conn.restful;
    this.listeners = conn.listeners;

    // deprecated
    this.prettyUrls = conn.prettyUrls;

    /**
     * @cfg {Object} api
     * Specific urls to call on CRUD action methods "read", "create", "update" and "destroy".
     * Defaults to:<pre><code>
api: {
    read    : undefined,
    create  : undefined,
    update  : undefined,
    destroy : undefined
}
</code></pre>
     * <p>If the specific URL for a given CRUD action is undefined, the CRUD action request
     * will be directed to the configured <tt>{@link Ext.data.Connection#url url}</tt>.</p>
     * <br><p><b>Note</b>: To modify the URL for an action dynamically the appropriate API
     * property should be modified before the action is requested using the corresponding before
     * action event.  For example to modify the URL associated with the load action:
     * <pre><code>
// modify the url for the action
myStore.on({
    beforeload: {
        fn: function (store, options) {
            // use <tt>{@link Ext.data.HttpProxy#setUrl setUrl}</tt> to change the URL for *just* this request.
            store.proxy.setUrl('changed1.php');

            // set optional second parameter to true to make this URL change permanent, applying this URL for all subsequent requests.
            store.proxy.setUrl('changed1.php', true);

            // manually set the <b>private</b> connection URL.  <b>Warning:</b>  Accessing the private URL property like should be avoided.  Please use the public
            // method <tt>{@link Ext.data.HttpProxy#setUrl setUrl}</tt> instead, shown above.  It should be noted that changing the URL like
            // this will affect the URL for just this request.  Subsequent requests will use the API or URL defined in your initial
            // proxy configuration.
            store.proxy.conn.url = 'changed1.php';

            // proxy URL will be superseded by API (only if proxy created to use ajax):
            // It should be noted that proxy API changes are permanent and will be used for all subsequent requests.
            store.proxy.api.load = 'changed2.php';

            // However, altering the proxy API should be done using the public method <tt>{@link Ext.data.DataProxy#setApi setApi}</tt> instead.
            store.proxy.setApi('load', 'changed2.php');

            // Or set the entire API with a config-object.  When using the config-object option, you must redefine the <b>entire</b> API --
            // not just a specific action of it.
            store.proxy.setApi({
                read    : 'changed_read.php',
                create  : 'changed_create.php',
                update  : 'changed_update.php',
                destroy : 'changed_destroy.php'
            });
        }
    }
});
     * </code></pre>
     * </p>
     */
    // Prepare the proxy api.  Ensures all API-actions are defined with the Object-form.
    try {
        Ext.data.Api.prepare(this);
    } catch (e) {
        if (e instanceof Ext.data.Api.Error) {
            e.toConsole();
        }
    }

    this.addEvents(
        /**
         * @event exception
         * Fires if an exception occurs in the Proxy during a remote request.  This event can be fired for one of two reasons:
         * <ul><li><b>The remote-request failed and the server did not return status === 200</b></li>
         * <li><b>The remote-request succeeded but the reader could not read the response.</b>  This means the server returned
         * data, but the configured Reader threw an error while reading the response.  In this case, this event will be
         * raised and the caught error will be passed along into this event.</li></ul>
         *
         * This event fires with two different contexts based upon the 2nd parameter <tt>type [remote|response]</tt>.  Note that the
         * first four parameters are identical between the two contexts -- only the final two parameters differ.
         *
         * <b>response</b>
         * If the type of exception is "response", an <b>invalid response</b> from the server was returned, either 404, 500 or the response
         * meta-data does not match that defined in your DataReader (eg: root, idProperty, successProperty).
         * The event parameters for this context are:
         * @param {DataProxy} sender
         * @param {String} type [response]
         * @param {String} action [Ext.data.Api.actions.create|read|update|destroy]
         * @param {Object} options The loading options that were specified (see {@link #load} for details)
         * @param {Object} response The raw browser response object (eg: XMLHttpRequest)
         * @param {Error} e The JavaScript Error object caught if the configured Reader could not read the data.
         * If the load call returned success: false, this parameter will be null.
         *
         * <b>remote</b>
         * If the type of exception is "remote", a <b>valid response</b> was returned from the server having successProperty === false.  This
         * response might contain an error-message sent from the server.  For example, the user may have failed
         * authentication/authorization or a database validation error occurred.
         * @param {DataProxy} sender
         * @param {String} type [remote]
         * @param {String} action [Ext.data.Api.actions.create|read|update|destroy]
         * @param {Object} options The loading options that were specified (see {@link #load} for details)
         * @param {Object} response The decoded response object sent from the server.
         * @param {Record/Record[]} rs Records from the Store.  This parameter will only exist if the <tt>action</tt> was a <b>write</b> action
         * (Ext.data.Api.actions.create|update|destroy)
         *
         * Note that this event is also relayed through {@link Ext.data.Store}, so you can listen for it directly
         * on any Store instance.
         */
        'exception',
        /**
         * @event beforeload
         * Fires before a network request is made to retrieve a data object.
         * @param {Object} this
         * @param {Object} params The params object passed to the {@link #request} function
         */
        'beforeload',
        /**
         * @event load
         * Fires before the load method's callback is called.
         * @param {Object} this
         * @param {Object} o The data object
         * @param {Object} arg The callback's arg object passed to the {@link #request} function
         */
        'load',
        /**
         * @event loadexception
         * @deprecated This event is <b>deprecated</b>.  Please use catch-all {@link #exception} event instead.
         * Fires if an exception occurs in the Proxy during data loading.  This event can be fired for one of two reasons:
         * <ul><li><b>The load call returned success: false.</b>  This means the server logic returned a failure
         * status and there is no data to read.  In this case, this event will be raised and the
         * fourth parameter (read error) will be null.</li>
         * <li><b>The load succeeded but the reader could not read the response.</b>  This means the server returned
         * data, but the configured Reader threw an error while reading the data.  In this case, this event will be
         * raised and the caught error will be passed along as the fourth parameter of this event.</li></ul>
         * on any Store instance.
         * @param {Object} this
         * @param {Object} options The loading options that were specified (see {@link #load} for details)
         * @param {Object} response The raw response object (eg: XMLHttpRequest) containing the response data
         * @param {Error} e The JavaScript Error object caught if the configured Reader could not read the data.
         * If the load call returned success: false, this parameter will be null.
         *
         * Note that this event is also relayed through {@link Ext.data.Store}, so you can listen for it directly
         */
        'loadexception',
        /**
         * @event beforewrite
         * Fires before a network request is generated for one of the actions Ext.data.Api.actions.create|update|destroy
         * @param {DataProxy} this
         * @param {String} action [Ext.data.Api.actions.create|update|destroy]
         * @param {Record/Array[Record]} rs
         * @param {Object} params HTTP request-params object.  Edit <code>params</code> to add Http parameters to the request.
         */
        'beforewrite',
        /**
         * @event write
         * Fires before the request-callback is called
         * @param {Object} this
         * @param {String} action [Ext.data.Api.actions.create|read|upate|destroy]
         * @param {Object} data The data object extracted from the server-response
         * @param {Object} response The decoded response from server
         * @param {Record/Record{}} rs The records from Store
         * @param {Object} arg The callback's arg object passed to the {@link #request} function
         */
        'write'
    );
    Ext.data.DataProxy.superclass.constructor.call(this);
};

Ext.extend(Ext.data.DataProxy, Ext.util.Observable, {
    /**
     * @cfg {Boolean} restful
     * <p>Defaults to <tt>false</tt>.  Set to <tt>true</tt> to operate in a RESTful manner.</p>
     * <br><p> Note: this parameter will automatically be set to <tt>true</tt> if the
     * {@link Ext.data.Store} it is plugged into is set to <code>restful: true</code>. If the
     * Store is RESTful, there is no need to set this option on the proxy.</p>
     * <br><p>RESTful implementations enable the serverside framework to automatically route
     * actions sent to one url based upon the HTTP method, for example:
     * <pre><code>
store: new Ext.data.Store({
    restful: true,
    proxy: new Ext.data.HttpProxy({url:'/users'}); // all requests sent to /users
    ...
)}
     * </code></pre>
     * There is no <code>{@link #api}</code> specified in the configuration of the proxy,
     * all requests will be marshalled to a single RESTful url (/users) so the serverside
     * framework can inspect the HTTP Method and act accordingly:
     * <pre>
<u>Method</u>   <u>url</u>        <u>action</u>
POST     /users     create
GET      /users     read
PUT      /users/23  update
DESTROY  /users/23  delete
     * </pre></p>
     */
    restful: false,

    /**
     * <p>Redefines the Proxy's API or a single action of an API. Can be called with two method signatures.</p>
     * <p>If called with an object as the only parameter, the object should redefine the <b>entire</b> API, eg:</p><code><pre>
proxy.setApi({
    read    : '/users/read',
    create  : '/users/create',
    update  : '/users/update',
    destroy : '/users/destroy'
});
</pre></code>
     * <p>If called with two parameters, the first parameter should be a string specifying the API action to
     * redefine and the second parameter should be the URL (or function if using DirectProxy) to call for that action, eg:</p><code><pre>
proxy.setApi(Ext.data.Api.actions.read, '/users/new_load_url');
</pre></code>
     * @param {String/Object} api An API specification object, or the name of an action.
     * @param {String/Function} url The URL (or function if using DirectProxy) to call for the action.
     */
    setApi : function() {
        if (arguments.length == 1) {
            var valid = Ext.data.Api.isValid(arguments[0]);
            if (valid === true) {
                this.api = arguments[0];
            }
            else {
                throw new Ext.data.Api.Error('invalid', valid);
            }
        }
        else if (arguments.length == 2) {
            if (!Ext.data.Api.isAction(arguments[0])) {
                throw new Ext.data.Api.Error('invalid', arguments[0]);
            }
            this.api[arguments[0]] = arguments[1];
        }
        Ext.data.Api.prepare(this);
    },

    /**
     * Returns true if the specified action is defined as a unique action in the api-config.
     * request.  If all API-actions are routed to unique urls, the xaction parameter is unecessary.  However, if no api is defined
     * and all Proxy actions are routed to DataProxy#url, the server-side will require the xaction parameter to perform a switch to
     * the corresponding code for CRUD action.
     * @param {String [Ext.data.Api.CREATE|READ|UPDATE|DESTROY]} action
     * @return {Boolean}
     */
    isApiAction : function(action) {
        return (this.api[action]) ? true : false;
    },

    /**
     * All proxy actions are executed through this method.  Automatically fires the "before" + action event
     * @param {String} action
     * @param {Ext.data.Record/Ext.data.Record[]/null} rs Will be null when action is 'load'
     * @param {Object} params
     * @param {Ext.data.DataReader} reader
     * @param {Function} callback
     * @param {Object} scope Scope with which to call the callback (defaults to the Proxy object)
     * @param {Object} options
     */
    request : function(action, rs, params, reader, callback, scope, options) {
        if (!this.api[action]) {
            throw new Ext.data.DataProxy.Error('action-undefined', action);
        }
        params = params || {};
        if ((action === Ext.data.Api.actions.read) ? this.fireEvent("beforeload", this, params) : this.fireEvent("beforewrite", this, action, rs, params) !== false) {
            this.doRequest.apply(this, arguments);
        }
        else {
            callback.call(scope || this, null, options, false);
        }
    },


    /**
     * <b>Deprecated</b> load method using old method signature. See {@doRequest} for preferred method.
     * @deprecated
     * @param {Object} params
     * @param {Object} reader
     * @param {Object} callback
     * @param {Object} scope
     * @param {Object} arg
     */
    load : function(params, reader, callback, scope, arg) {
        this.doRequest(Ext.data.Api.actions.read, null, params, reader, callback, scope, arg);
    },

    /**
     * @cfg {Function} doRequest Abstract method that should be implemented in all subclasses
     * (eg: {@link Ext.data.HttpProxy#doRequest HttpProxy.doRequest},
     * {@link Ext.data.DirectProxy#doRequest DirectProxy.doRequest}).
     */
    doRequest : function(action, rs, params, reader, callback, scope, options) {
        // default implementation of doRequest for backwards compatibility with 2.0 proxies.
        // If we're executing here, the action is probably "load".
        // Call with the pre-3.0 method signature.
        // WARNING:  Potentially infinitely recursive:  See load above which calls this.doRequest
        this.load(params, reader, callback, scope, options);
    },

    /**
     * buildUrl
     * Sets the appropriate url based upon the action being executed.  If restful is true, and only a single record is being acted upon,
     * url will be built Rails-style, as in "/controller/action/32".  restful will aply iff the supplied record is an
     * instance of Ext.data.Record rather than an Array of them.
     * @param {String} action The api action being executed [load|create|update|destroy]
     * @param {Ext.data.Record/Array[Ext.data.Record]} The record or Array of Records being acted upon.
     * @return {String} url
     * @private
     */
    buildUrl : function(action, record) {
        record = record || null;
        var url = (this.api[action]) ? this.api[action]['url'] : this.url;
        if (!url) {
            throw new Ext.data.Api.Error('invalid-url', action);
        }
        // prettyUrls is deprectated in favor of restful-config
        if ((this.prettyUrls === true || this.restful === true) && record instanceof Ext.data.Record && !record.phantom) {
            url += '/' + record.id;
        }
        return url;
    },

    /**
     * Destroys the proxy by purging any event listeners and cancelling any active requests.
     */
    destroy: function(){
        this.purgeListeners();
    }
});

/**
 * DataProxy Error extension.
 * constructor
 * @param {String} name
 * @param {Record/Array[Record]/Array}
 */
Ext.data.DataProxy.Error = Ext.extend(Ext.Error, {
    constructor : function(message, arg) {
        this.arg = arg;
        Ext.Error.call(this, message);
    },
    name: 'Ext.data.DataProxy'
});
Ext.apply(Ext.data.DataProxy.Error.prototype, {
    lang: {
        'action-undefined': "DataProxy attempted to execute an API-action but found an undefined url / function.  Please review your Proxy url/api-configuration.",
        'api-invalid': 'Recieved an invalid API-configuration.  Please ensure your proxy API-configuration contains only the actions from Ext.data.Api.actions.'
    }
});
