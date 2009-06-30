/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */

// Application instance for showing user-feedback messages.
var App = new Ext.App({});

// Create HttpProxy instance.  Notice new configuration parameter "api" here instead of load.  However, you can still use
// the "url" paramater -- All CRUD requests will be directed to your single url instead.
var proxy = new Ext.data.HttpProxy({
    api: {
        read : 'app.php/users/view',
        create : 'app.php/users/create',
        update: 'app.php/users/update',
        destroy: 'app.php/users/destroy'
    }
});

// Typical JsonReader.  Notice additional meta-data params for defining the core attributes of your json-response
var reader = new Ext.data.JsonReader({
    totalProperty: 'total',
    successProperty: 'success',
    idProperty: 'id',
    root: 'data'
}, [
    {name: 'id'},
    {name: 'email', allowBlank: false},
    {name: 'first', allowBlank: false},
    {name: 'last', allowBlank: false}
]);

// The new DataWriter component.
var writer = new Ext.data.JsonWriter({
    returnJson: true,
    writeAllFields: false
});

// Typical Store collecting the Proxy, Reader and Writer together.
var store = new Ext.data.Store({
    id: 'user',
    proxy: proxy,
    reader: reader,
    writer: writer,  // <-- plug a DataWriter into the store just as you would a Reader
    autoSave: true,  // <-- false would delay executing create, update, destroy requests until specifically told to do so with some [save] buton.
    listeners: {
        write : function(store, action, result, res, rs) {
            App.setAlert(res.success, res.message); // <-- show user-feedback for all write actions
        },
        exception : function(proxy, type, action, options, res, arg) {
            if (type === 'remote') {
                Ext.Msg.show({
                    title: 'REMOTE EXCEPTION',
                    msg: res.message,
                    icon: Ext.MessageBox.ERROR
                });
            }
        }
    }
});


// A new generic text field
var textField =  new Ext.form.TextField();

// Let's pretend we rendered our grid-columns with meta-data from our ORM framework.
var userColumns =  [
    {header: "ID", width: 40, sortable: true, dataIndex: 'id'},
    {header: "Email", width: 100, sortable: true, dataIndex: 'email', editor: textField},
    {header: "First", width: 50, sortable: true, dataIndex: 'first', editor: textField},
    {header: "Last", width: 50, sortable: true, dataIndex: 'last', editor: textField}
];

// load the store immeditately
store.load();


Ext.onReady(function() {
    Ext.QuickTips.init();

    // create user.Form instance (@see UserForm.js)
    var userForm = new App.user.Form({
        renderTo: 'user-form',
        listeners: {
            create : function(fpanel, data) {   // <-- custom "create" event defined in App.user.Form class
                var rec = new userGrid.store.recordType(data);
                userGrid.store.insert(0, rec);
            }
        }
    });

    // create user.Grid instance (@see UserGrid.js)
    var userGrid = new App.user.Grid({
        renderTo: 'user-grid',
        store: store,
        columns : userColumns,
        listeners: {
            rowclick: function(g, index, ev) {
                var rec = g.store.getAt(index);
                userForm.loadRecord(rec);
            },
            destroy : function() {
                userForm.getForm().reset();
            }
        }
    });
});
