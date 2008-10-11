Ext.onReady(function(){

    function myEventID(val, p, record){
        return "<span><a href=\"warnings_cat.phtml?year="+ record.get('year') +"&wfo="+ record.get('wfo') +"&phenomena="+ record.get('phenomena') +"&significance="+ record.get('significance') +"&eventid="+ val +"\">" + val + "</a></span>";
    }

   var filters = new Ext.ux.grid.GridFilters({
        filters:[
               {type: 'string',
                dataIndex: 'locations'
                }
                ],
        phpMode:false,
        local:true
        });


var expander = new Ext.grid.RowExpander({
        id: 'testexp',
        width: 30,
        tpl : new Ext.Template(
            '<p><b>Remark:</b> {remark}<br>'
        )
});


var expander2 = new Ext.grid.RowExpander({
    id: 'testexp2',
    width: 30,
    tpl : new Ext.Template(
         '<p><b>Remark:</b> {remark}<br>'
    )
});

    var pstore = new Ext.data.Store({
          root:'products',
          autoLoad:false,
          proxy: new Ext.data.HttpProxy({
                url: '../json/json-list.php',
                method: 'GET'
          }),
          reader:  new Ext.data.JsonReader({
            root: 'products',
            id: 'id'
           }, [
           {name: 'id'},
           {name: 'locations'},
           {name: 'wfo'},
           {name: 'year'},
           {name: 'area', type: 'float'},
           {name: 'significance'},
           {name: 'phenomena'},
           {name: 'eventid'},
           {name: 'issued'},
           {name: 'expired'}
          ])
        });


    var ustore = new Ext.data.Store({
          root:'ugcs',
          autoLoad:false,
          proxy: new Ext.data.HttpProxy({
                url: '../json/json-ugc.php',
                method: 'GET'
          }),
          reader:  new Ext.data.JsonReader({
            root: 'ugcs',
            id: 'id'
           }, [
           {name: 'id'},
           {name: 'ugc'},
           {name: 'name'},
           {name: 'status'},
           {name: 'issue'},
           {name: 'expire'}
          ])
        });

    var jstore = new Ext.data.Store({
          autoLoad:false,
          proxy: new Ext.data.HttpProxy({
                url: '../json/json-lsrs.php',
                method: 'GET'
          }),
          reader:  new Ext.data.JsonReader({
            root: 'lsrs',
            id: 'id'
           }, [
           {name: 'id'},
           {name: 'valid'},
           {name: 'type'},
           {name: 'event'},
           {name: 'magnitude'},
           {name: 'city'},
           {name: 'county'},
           {name: 'remark'}
          ])
        });


var jstore2 = new Ext.data.Store({
    autoLoad:false,
    proxy: new Ext.data.HttpProxy({
           url: '../json/json-lsrs.php',
           method: 'GET'
    }),
    reader:  new Ext.data.JsonReader({
            root: 'lsrs',
            id: 'id'
           }, [
           {name: 'id'},
           {name: 'valid'},
           {name: 'type'},
           {name: 'event'},
           {name: 'magnitude'},
           {name: 'city'},
           {name: 'county'},
           {name: 'remark'}
          ])
});



var wfo_selector = new Ext.form.ComboBox({
             hiddenName:'wfo',
             store: new Ext.data.SimpleStore({
                      fields: ['abbr', 'wfo'],
                      data : iemdata.wfos 
             }),
             valueField:'abbr',
             displayField:'wfo',
             hideLabel: true,
             typeAhead: true,
             mode: 'local',
             triggerAction: 'all',
             emptyText:'Select a WFO...',
             selectOnFocus:true,
             lazyRender: true,
             width:190
});

var phenomena_selector = new Ext.form.ComboBox({
             hiddenName:'phenomena',
             store: new Ext.data.SimpleStore({
                      fields: ['abbr', 'name'],
                      data : iemdata.vtec_phenomena_dict
             }),
             valueField:'abbr',
             displayField:'name',
             hideLabel: true,
             typeAhead: true,
             mode: 'local',
             triggerAction: 'all',
             emptyText:'Select a Phenomena...',
             selectOnFocus:true,
             lazyRender: true,
             width:190
});

var sig_selector = new Ext.form.ComboBox({
             hiddenName:'significance',
             store: new Ext.data.SimpleStore({
                      fields: ['abbr', 'name'],
                      data : iemdata.vtec_sig_dict
             }),
             valueField:'abbr',
             displayField:'name',
             hideLabel: true,
             typeAhead: true,
             mode: 'local',
             triggerAction: 'all',
             emptyText:'Select a Significance...',
             selectOnFocus:true,
             lazyRender: true,
             width:190
});


var eventid_selector = new Ext.form.NumberField({
    allowDecimals:false,
    allowNegative:false,
    maxValue:9999,
    minValue:1,
    width: 50,
    name:'eventid',
    fieldLabel:'Event ID'
});

var year_selector = new Ext.form.NumberField({
    allowDecimals:false,
    allowNegative:false,
    maxValue: new Date("Y"),
    minValue: 2005,
    width: 50,
    name:'year',
    fieldLabel:'Year'
});

var properties = new Ext.grid.PropertyGrid({
    title: 'Product Details',
    autoHeight: true,
    width: 190,
    source: {
        "(name)": "My Object",
        "Created": new Date(Date.parse('10/15/2006')),
        "Available": false,
        "Version": .01,
        "Description": "A test object"
    }
});

var mygpanel = new Ext.ux.GMapPanel({
    gmapType: 'map',
    title: 'Google Map',
    zoomLevel: 14,
    setCenter: {
       geoCodeAddr: '4 Yawkey Way, Boston, MA, 02215-3409, USA',
       marker: {title: 'Fenway Park'}
    },
    mapConfOpts: ['enableScrollWheelZoom','enableDoubleClickZoom','enableDragging'],
    mapControls: ['GSmallMapControl','GMapTypeControl','NonExistantControl']
});

var selectform = new Ext.FormPanel({
     frame: true,
     title: 'Product Selector',
     labelWidth:0,
     buttons: [{
         text:'View Product',
         handler: function() {
           //var wfo = myform2.getForm().findField('wfo').getValue();
           //var afos = myform2.getForm().findField('afos').getValue();
          } // End of handler
     }],
     items: [wfo_selector,phenomena_selector,sig_selector,eventid_selector,year_selector]
});

var texttabs = new Ext.TabPanel({
    title: 'Text Data',
    enableTabScroll:true,
    defaults:{bodyStyle:'padding:5px'}
});

var lsrs = new Ext.grid.GridPanel({
        id:'lsr-grid',
        isLoaded:false,
        store: jstore,
        loadMask: {msg:'Loading Data...'},
        cm: new Ext.grid.ColumnModel([
            expander,
            {header: "Time", sortable: true, dataIndex: 'valid'},
            {header: "Event", width: 100, sortable: true, dataIndex: 'event'},
            {header: "Magnitude", sortable: true, dataIndex: 'magnitude'},
            {header: "City", width: 200, sortable: true, dataIndex: 'city'},
            {header: "County", sortable: true, dataIndex: 'county'}
        ]),
        stripeRows: true,
        title:'Storm Reports within Polygon',
        plugins: expander,
        autoScroll:true
    });


var alllsrs = new Ext.grid.GridPanel({
    id:'all-lsr-grid',
    title: 'All Storm Reports',
    isLoaded:false,
    store: jstore2,
    loadMask: {msg:'Loading Data...'},
    cm: new Ext.grid.ColumnModel([
            expander2,
            {header: "Time (UTC)", sortable: true, dataIndex: 'valid'},
            {header: "Event", width: 100, sortable: true, dataIndex: 'event'},
            {header: "Magnitude", sortable: true, dataIndex: 'magnitude'},
            {header: "City", width: 200, sortable: true, dataIndex: 'city'},
            {header: "County", sortable: true, dataIndex: 'county'}
    ]),
    stripeRows: true,
    plugins: expander2,
    autoScroll:true
});

var geo = new Ext.grid.GridPanel({
        id:'ugc-grid',
        store: ustore,
        loadMask: {msg:'Loading Data...'},
        cm: new Ext.grid.ColumnModel([
            {header: "UGC", width: 50, sortable: true, dataIndex: 'ugc'},
            {header: "Name", width: 200, sortable: true, dataIndex: 'name'},
            {header: "Status", width: 50, sortable: true, dataIndex: 'status'},
            {header: "Issue (UTC)", sortable: true, dataIndex: 'issue'},
            {header: "Expire (UTC)", sortable: true, dataIndex: 'expire'}
        ]),
        stripeRows: true,
        autoScroll:true,
        title:'Geography Included',
        collapsible: false,
        animCollapse: false
    });

    var grid4 = new Ext.grid.GridPanel({
        id:'products-grid',
        store: pstore,
        width:640,
        loadMask: {msg:'Loading Data...'},
        cm: new Ext.grid.ColumnModel([
          {header: "Event", renderer: myEventID, width: 40, sortable: true, dataIndex: 'eventid'},
          {header: "Issued (UTC)", width: 140, sortable: true, dataIndex: 'issued'},
          {header: "Expired (UTC)", width: 140, sortable: true, dataIndex: 'expired'},
          {header: "Area km**2", width: 70, sortable: true, dataIndex: 'area'},
          {header: "Locations", id:"locations", width: 250, sortable: true, dataIndex: 'locations'}
        ]),
        plugins: filters,
        stripeRows: true,
        autoScroll:true,
        title:'Other Events',
        collapsible: false,
        animCollapse: false
    });


var sbwhist = new Ext.Panel({
    title: 'SBW History',
    id: 'sbwhist'
});

var tabs =  new Ext.TabPanel({
         region:'center',
         height:.75,
         plain:true,
         enableTabScroll:true,
         defaults:{bodyStyle:'padding:5px'},
         items:[
            {contentEl:'help', title: 'Help'},
            mygpanel,
            texttabs,
            alllsrs,
            lsrs,
            sbwhist,
            geo,
            grid4
         ],
         activeTab:0
});


var viewport = new Ext.Viewport({
    layout:'border',
    items:[
         new Ext.BoxComponent({ // raw
             region:'north',
             el: 'header',
             height:60
         }),
         new Ext.BoxComponent({ // raw
             region:'south',
             el: 'footer',
             height:32
         }),
          { 
             region:'west',
             width:210,
             collapsible:true,
             title: 'Settings',
             layoutConfig:{
                animate:true
             },
             items:[properties,selectform]
         },
         tabs
         ]
});

// End of static.js
});
