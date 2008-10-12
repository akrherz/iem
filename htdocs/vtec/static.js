Ext.onReady(function(){

function getVTEC(){
  return "year="+ year_selector.getValue() +"&wfo="+ wfo_selector.getValue() +"&phenomena="+ phenomena_selector.getValue() +"&eventid="+ eventid_selector.getValue() +"&significance="+ sig_selector.getValue();
};

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
                url: 'json-list.php',
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
                url: 'json-ugc.php',
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
                url: 'json-lsrs.php',
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
           url: 'json-lsrs.php',
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
    id: 'wfoselector',
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
    id: 'phenomenaselector',
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
    id: 'significanceselector',
             width:190
});


var eventid_selector = new Ext.form.NumberField({
    allowDecimals:false,
    allowNegative:false,
    maxValue:9999,
    minValue:1,
    width: 50,
    id: 'eventid',
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
    id:'yearselector',
    fieldLabel:'Year'
});

var metastore = new Ext.data.Store({
    root:'meta',
    autoLoad:false,
    id:'metastore',
    recordType: Ext.grid.PropertyRecord,
    proxy: new Ext.data.HttpProxy({
           url: 'json-meta.php',
           params: getVTEC(),
           method:'GET'
           }),
    reader: new Ext.data.JsonReader({
            root: 'meta',
            id:'id'
            }, [
            {name: 'x0'},
            {name: 'x1'},
            {name: 'y0'},
            {name: 'y1'},
            {name: 'issued'}
            ])
});
metastore.on('load', function(){
  if (metastore.getCount() == 0){
    Ext.MessageBox.alert('Status', 'Event not found on server');
    return;
  }

  Ext.getCmp('pgrid').setSource(metastore.getAt(0).data);
  if (tabs.items.length == 1){ buildTabs(); }
  loadTextTabs();
  resetGmap();
});


var propertyCM = new Ext.grid.PropertyColumnModel([
    {header:'x1', dataIndex: 'x1', hidden:false},
    {header:'x0', dataIndex: 'x0', hidden:false}
]);

var properties = new Ext.grid.PropertyGrid({
    title: 'Product Details',
    id: 'pgrid',
    height: 200,
    width: 200,
    cm: propertyCM,
    source: {},
    store: metastore
});

function resetGmap(){
   var q = metastore.getAt(0);
   var point = new GLatLng(q.data.y1,q.data.x1);
   // Only works if the google panel has been loaded :(
   if (Ext.getCmp('mygpanel').gmap){
     Ext.getCmp('mygpanel').gmap.setCenter(point, 12);
   }
};

var selectform = new Ext.FormPanel({
     frame: true,
     title: 'Product Selector',
     labelWidth:0,
     buttons: [{
         text:'View Product',
         handler: function() {
           metastore.load( {params:getVTEC()} );
           //var wfo = myform2.getForm().findField('wfo').getValue();
           //var afos = myform2.getForm().findField('afos').getValue();
          } // End of handler
     }],
     items: [wfo_selector,phenomena_selector,sig_selector,eventid_selector,year_selector]
});

function loadVTEC(){

  Ext.Ajax.request({
     waitMsg: 'Loading...',
     url : 'json-meta.php' , 
     params:getVTEC(),
     method: 'GET',
     scope: this,
     success: function ( result, request) { 
        var jsonData = Ext.util.JSON.decode(result.responseText);
        vtec.significance = jsonData.data[0].meta[0].significance;
     }
   });

};


function loadTextTabs(){

  Ext.Ajax.request({
     waitMsg: 'Loading...',
     url : 'json-text.php' , 
     params:getVTEC(),
     method: 'GET',
     scope: this,
     success: function ( result, request) { 
        var jsonData = Ext.util.JSON.decode(result.responseText);
        ttabs = Ext.getCmp('texttabs');
        ttabs.items.each(function(c){ttabs.remove(c);});
        ttabs.add({
         title: 'Issuance',
          html: '<pre>'+ jsonData.data[0].report  +'</pre>',
          xtype: 'panel',
         autoScroll:true
        });
        for ( var i = 0; i < jsonData.data[0].svs.length; i++ ){
            ttabs.add({
              title: 'Update '+ (i+1),
              html: '<pre>'+ jsonData.data[0].svs[i]  +'</pre>',
             xtype: 'panel',
             autoScroll:true
            });
        }
        ttabs.activate(i);
     }
   });


};

var texttabs = new Ext.TabPanel({
    title: 'Text Data',
    enableTabScroll:true,
    id:'texttabs',
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
            {contentEl:'help', title: 'Help'}
         ],
         activeTab:0
});

function buildTabs(){
  tabs.add( new Ext.ux.GMapPanel({
    gmapType: 'map',
    title: 'Google Map',
    id:'mygpanel',
    zoomLevel: 14,
    setCenter: {
       lat: metastore.getAt(0).data.y1,
       lng: metastore.getAt(0).data.x1,
       zoomLevel: 9
    },
    mapConfOpts: ['enableScrollWheelZoom','enableDoubleClickZoom','enableDragging'],
    mapControls: ['GSmallMapControl','GMapTypeControl','NonExistantControl']
})
);
  tabs.add(texttabs);
  tabs.add(alllsrs);
  tabs.add(lsrs);
  tabs.add(sbwhist);
  tabs.add(geo);
  tabs.add(grid4);
};


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
             id: 'leftside',
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
