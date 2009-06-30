/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */

// Application instance for showing user-feedback messages.
var App = new Ext.App({});

// Create a standard HttpProxy instance.
var proxy = new Ext.data.HttpProxy({
    url: 'app.php/users'
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
var writer = new Ext.data.JsonWriter();

// Typical Store collecting the Proxy, Reader and Writer together.
var store = new Ext.data.Store({
    id: 'user',
    restful: true,     // <-- This Store is RESTful
    proxy: proxy,
    reader: reader,
    writer: writer,    // <-- plug a DataWriter into the store just as you would a Reader
    listeners: {
        write : function(store, action, result, response, rs) {
            App.setAlert(response.success, response.message);
        }
    }
});

// Let's pretend we rendered our grid-columns with meta-data from our ORM framework.
var userColumns =  [
    {header: "ID", width: 40, sortable: true, dataIndex: 'id'},
    {header: "Email", width: 100, sortable: true, dataIndex: 'email', editor: new Ext.form.TextField({})},
    {header: "First", width: 50, sortable: true, dataIndex: 'first', editor: new Ext.form.TextField({})},
    {header: "Last", width: 50, sortable: true, dataIndex: 'last', editor: new Ext.form.TextField({})}
];

// load the store immeditately
store.load();

Ext.onReady(function() {
    Ext.QuickTips.init();

    // We'll use the new RowEditor for this example.
    var editor = new Ext.ux.RowEditor({
        saveText: 'Update'
    });

    // Create a typical GridPanel with RowEditor plugin
    var userGrid = new Ext.grid.GridPanel({
        renderTo: 'user-grid',
        iconCls: 'icon-grid',
        frame: true,
        title: 'Users',
        autoScroll: true,
        height: 300,
        store: store,
        plugins: [editor],
        columns : userColumns,
        tbar: [{
            text: 'Add',
            iconCls: 'silk-add',
            handler: onAdd
        }, '-', {
            text: 'Delete',
            iconCls: 'silk-delete',
            handler: onDelete
        }, '-'],
        viewConfig: {
            forceFit: true
        }
    });

    /**
     * onAdd
     */
    function onAdd(btn, ev) {
        var u = new userGrid.store.recordType({
            first : '',
            last: '',
            email : ''
        });
        editor.stopEditing();
        userGrid.store.insert(0, u);
        editor.startEditing(0);
    }
    /**
     * onDelete
     */
    function onDelete() {
        var rec = userGrid.getSelectionModel().getSelected();
        if (!rec) {
            return false;
        }
        userGrid.store.remove(rec);
    }

});
