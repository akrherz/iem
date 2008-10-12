Ext.onReady(function(){

var tabPanel;
/* Here are my Panels that appear in tabs */
var helpPanel;
var googlePanel;
var textTabPanel;
var lsrGridPanel;
var allLsrGridPanel;
var sbwPanel;
var geoPanel;
var eventsPanel;


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
            {name: 'issue', type:'date', dateFormat: 'Y-m-d H:i'},
            {name: 'expire', type:'date', dateFormat:'Y-m-d H:i'}
            ])
});
metastore.on('load', function(){
  if (metastore.getCount() == 0){
    Ext.MessageBox.alert('Status', 'Event not found on server');
    tabPanel.activate(0);
    tabPanel.items.each(function(c){
         if (c.saveme){}
         else{ c.disable(); }
    });
    Ext.getCmp('propertyGrid').setSource({});
    return;
  }
  tabPanel.items.each(function(c){c.enable();});
  if (lsrGridPanel.isLoaded){ lsrGridPanel.getStore().load({params:getVTEC()}); }
  if (allLsrGridPanel.isLoaded){ allLsrGridPanel.getStore().load({params:getVTEC()}); }
  googlePanel.enable();
  Ext.getCmp('propertyGrid').setSource(metastore.getAt(0).data);
  //if (tabs.items.length == 1){ buildTabs(); }
  //loadTextTabs();
  resetGmap();
});



var propertyGrid = new Ext.grid.PropertyGrid({
    title: 'Product Details',
    id: 'propertyGrid',
    autoHeight: true,
    source: {},
    store: metastore
});
propertyGrid.on('beforeedit', function(){ return false; });

function resetGmap(){
   var q = metastore.getAt(0);
   var point = new GLatLng(q.data.y1,q.data.x1);
   // Only works if the google panel has been loaded :(
   if (Ext.getCmp('mygpanel').gmap){
     Ext.getCmp('mygpanel').gmap.setCenter(point, 9);
   }
};

var selectform = new Ext.FormPanel({
     frame: true,
     title: 'Product Selector',
     id: 'mainform',
     labelWidth:0,
     buttons: [{
         text:'View Product',
         listeners: {
           click: function() {
           metastore.load( {params:getVTEC()} );
          } // End of handler
        }
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
        /* Remove whatever tabs we currently have going */
        textTabPanel.items.each(function(c){textTabPanel.remove(c);});
        textTabPanel.add({
         title: 'Issuance',
          html: '<pre>'+ jsonData.data[0].report  +'</pre>',
          xtype: 'panel',
         autoScroll:true
        });
        for ( var i = 0; i < jsonData.data[0].svs.length; i++ ){
            textTabPanel.add({
              title: 'Update '+ (i+1),
              html: '<pre>'+ jsonData.data[0].svs[i]  +'</pre>',
             xtype: 'panel',
             autoScroll:true
            });
        }
        textTabPanel.activate(i);
     }
   });


};

var textTabPanel = new Ext.TabPanel({
    title: 'Text Data',
    enableTabScroll:true,
    id:'textTabPanel',
    isVisible: false,
    defaults:{bodyStyle:'padding:5px'}
});

var lsrGridPanel = new Ext.grid.GridPanel({
    id:'lsrGridPanel',
    isVisible: false,
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


allLsrGridPanel = new Ext.grid.GridPanel({
    id:'allLsrGridPanel',
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



function getX(){
  if (metastore.getCount() == 0) return -95;
  return metastore.getAt(0).data.x1;
}
function getY(){
  if (metastore.getCount() == 0) return 42;
  return metastore.getAt(0).data.y1;
}

var cachedNexradTime = false;

getNexradTime=function() {
  if (cachedNexradTime) return cachedNexradTime;
  var ts;
  var ts2;
  if (metastore.getCount() == 0){
    ts = new date();
    ts = ts.add(Date.MINUTE, ts.format("Z"));
  } else {
    ts = metastore.getAt(0).data.issue;
  }
  roundDown = parseInt(ts.format('i')) % 5;
  ts2 = ts.add(Date.MINUTE, 0 - roundDown);
  cachedNexradTime = ts2;
  return ts2;
}

CustomGetTileUrl=function(a,b,c) {
  if (typeof(window['this.myMercZoomLevel'])=="undefined") this.myMercZoomLevel=0; 
  if (typeof(window['this.myStyles'])=="undefined") this.myStyles="default"; 
  var lULP = new GPoint(a.x*256,(a.y+1)*256);
  var lLRP = new GPoint((a.x+1)*256,a.y*256);
  var lUL = G_NORMAL_MAP.getProjection().fromPixelToLatLng(lULP,b,c);
  var lLR = G_NORMAL_MAP.getProjection().fromPixelToLatLng(lLRP,b,c);
  // switch between Mercator and DD if merczoomlevel is set
  if (this.myMercZoomLevel!=0 && map.getZoom() < this.myMercZoomLevel) {
    var lBbox=dd2MercMetersLng(lUL.lngDegrees)+","+dd2MercMetersLat(lUL.latDegrees)+","+dd2MercMetersLng(lLR.lngDegrees)+","+dd2MercMetersLat(lLR.latDegrees);
    var lSRS="EPSG:54004";
  } else {
    var lBbox=lUL.x+","+lUL.y+","+lLR.x+","+lLR.y;
    var lSRS="EPSG:4326";
  }
  var ts = new Date();
  var lURL=this.myBaseURL;
  lURL+="&REQUEST=GetMap";
  lURL+="&SERVICE=WMS";
  lURL+="&reaspect=false&VERSION=1.1.1";
  lURL+="&LAYERS="+this.myLayers;
  lURL+="&STYLES="+this.myStyles; lURL+="&FORMAT="+this.myFormat;
  lURL+="&BGCOLOR=0xFFFFFF";
  lURL+="&TRANSPARENT=TRUE";
  lURL+="&SRS="+lSRS;
  lURL+="&TIME="+ getNexradTime().format('Y-m-d\\TH:i:\\0\\0\\Z');
  lURL+="&BBOX="+lBbox;
  lURL+="&WIDTH=256";
  lURL+="&HEIGHT=256";
  lURL+="&GroupName="+this.myLayers;
  lURL+="&bogus="+ts.getTime();
  return lURL;
}


var tileNEX= new GTileLayer(new GCopyrightCollection(''),1,17);
    tileNEX.myLayers='nexrad-n0r-wmst';
    tileNEX.myFormat='image/png';
    tileNEX.myBaseURL='http://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r.cgi?';
    tileNEX.getTileUrl=CustomGetTileUrl;

var layer4=[G_NORMAL_MAP.getTileLayers()[0],tileNEX]; 
var custommap4 = new GMapType(layer4, G_SATELLITE_MAP.getProjection(), 'Nexrad', G_SATELLITE_MAP);


googlePanel = new Ext.ux.GMapPanel({
    gmapType: 'map',
    title: 'Google Map',
    id:'mygpanel',
    disabled:true,
    zoomLevel: 14,
    mapConfOpts: ['enableScrollWheelZoom','enableDoubleClickZoom','enableDragging'],
    mapControls: ['GSmallMapControl','GMapTypeControl','NonExistantControl']
});
googlePanel.on('activate', function(){
  resetGmap();
  googlePanel.gmap.addMapType(custommap4);
});

function sbwgenerator(){
 return "<p><img src=\"../GIS/sbw-history.php?vtec="+ year_selector.getValue() +".K"+ wfo_selector.getValue()  +"."+ phenomena_selector.getValue() +"."+ sig_selector.getValue() +"."+ String.leftPad(eventid_selector.getValue(),4,"0") +"\" /></p>";
}

var sbwhist = new Ext.Panel({
    title: 'SBW History',
    id: 'sbwhist'
});
sbwhist.on('activate', function(){
  sbwhist.body.update( sbwgenerator() );
});

tabPanel =  new Ext.TabPanel({
    region:'center',
    height:.75,
    plain:true,
    enableTabScroll:true,
    defaults:{bodyStyle:'padding:5px'},
    items:[
      {contentEl:'help', title: 'Help', saveme:true},
      googlePanel
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
             id: 'leftside',
             width:210,
             collapsible:true,
             title: 'Settings',
             layoutConfig:{
                animate:true
             },
             items:[selectform, propertyGrid]
         },
         tabPanel
         ]
});

// End of static.js
});
