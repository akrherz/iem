/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */

/**
 * Framework-wide error-handler.  Developers can override this method to provide custom exception-handling.  Framework
 * errors will often extend from the base Ext.Error class.
 * @param {Object/Error} e The thrown exception object.
 */
Ext.handleError = function(e) {
    throw e;
};

/**
 * @class Ext.Error
 * @extends Error
 *
<code><pre>
try {
    generateError({
        foo: 'bar'
    });
}
catch (e) {
    console.error(e);
}
function generateError(data) {
    throw new Ext.Error('foo-error', data);
}

</pre></code>
 * @param {String} message
 */
Ext.Error = function(message) {
    // Try to read the message from Ext.Error.lang
    this.message = (this.lang[message]) ? this.lang[message] : message;
}
Ext.Error.prototype = new Error();
Ext.apply(Ext.Error.prototype, {
    // protected.  Extensions place their error-strings here.
    lang: {},

    name: 'Ext.Error',
    /**
     * getName
     * @return {String}
     */
    getName : function() {
        return this.name;
    },
    /**
     * getMessage
     * @return {String}
     */
    getMessage : function() {
        return this.message;
    },
    /**
     * toJson
     * @return {String}
     */
    toJson : function() {
        return Ext.encode(this);
    }
});

