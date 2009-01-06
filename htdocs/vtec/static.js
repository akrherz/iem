Ext.onReady(function(){

/**
 * @class Ext.ux.SliderTip
 * @extends Ext.Tip
 * Simple plugin for using an Ext.Tip with a slider to show the slider value
 */
Ext.ux.SliderTip = Ext.extend(Ext.Tip, {
    minWidth: 10,
    offsets : [0, -10],
    init : function(slider){
        slider.on('dragstart', this.onSlide, this);
        slider.on('drag', this.onSlide, this);
        slider.on('dragend', this.hide, this);
        slider.on('destroy', this.destroy, this);
    },

    onSlide : function(slider){
        this.show();
        this.body.update(this.getText(slider));
        this.doAutoWidth();
        this.el.alignTo(slider.thumb, 'b-t?', this.offsets);
    },

    getText : function(slider){
        return slider.getValue();
    }
});

var tabPanel;
/* Here are my Panels that appear in tabs */
var helpPanel;
var googlePanel;
var textTabPanel;
var lsrGridPanel;
var allLsrGridPanel;
var sbwPanel;
var radarPanel;
var geoPanel;
var eventsPanel;
// BAH
var cachedNexradTime = false;
var vDescription;
var tslider;
// Selectors
var wfo_selector;

function getVTEC(){
  return "year="+ year_selector.getValue() +"&wfo="+ wfo_selector.getValue() +"&phenomena="+ phenomena_selector.getValue() +"&eventid="+ eventid_selector.getValue() +"&significance="+ sig_selector.getValue();
}

function getURL(){
  return year_selector.getValue() +"-O-NEW-K"+ wfo_selector.getValue() +"-"+ phenomena_selector.getValue() +"-"+ sig_selector.getValue() +"-"+ String.leftPad(eventid_selector.getValue(),4,'0') +".html";
}

/* Generates the vtec link to this page 
 * "2008-O-NEW-KJAX-TO-W-0048"
 */
function myEventID(val, p, record){
    return "<span><a href=\""+ record.get('year') +"-O-NEW-K"+ record.get('wfo') +"-"+ record.get('phenomena') +"-"+ record.get('significance') +"-"+ String.leftPad(val,4,'0') +".html\">" + val + "</a></span>";
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
           {name: 'id', type: 'int'},
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


wfo_selector = new Ext.form.ComboBox({
  hiddenName:'wfo',
  store: new Ext.data.SimpleStore({
           fields: ['abbr', 'wfo'],
           data : iemdata.wfos 
  }),
  valueField:'abbr',
  width:180,
  fieldLabel: 'Issuing Office',
  displayField: 'wfo',
  typeAhead: true,
  tpl: '<tpl for="."><div class="x-combo-list-item">[{abbr}] {wfo}</div></tpl>',
  mode: 'local',
  triggerAction: 'all',
  emptyText:'Select/or type here...',
  selectOnFocus:true,
  lazyRender: true,
  id: 'wfoselector'
});

var phenomena_selector = new Ext.form.ComboBox({
             hiddenName:'phenomena',
             store: new Ext.data.SimpleStore({
                      fields: ['abbr', 'name'],
                      data : iemdata.vtec_phenomena_dict
             }),
             valueField:'abbr',
             displayField:'name',
             fieldLabel:'Phenomena',
    width:180,
             typeAhead: true,
             mode: 'local',
             triggerAction: 'all',
             emptyText:'Select a Phenomena...',
             selectOnFocus:true,
             lazyRender: true,
    id: 'phenomenaselector'
});

var sig_selector = new Ext.form.ComboBox({
             hiddenName:'significance',
             store: new Ext.data.SimpleStore({
                      fields: ['abbr', 'name'],
                      data : iemdata.vtec_sig_dict
             }),
             valueField:'abbr',
             displayField:'name',
             fieldLabel:'Significance',
             typeAhead: true,
             mode: 'local',
             triggerAction: 'all',
             emptyText:'Select a Significance...',
             selectOnFocus:true,
             lazyRender: true,
    width:100,
    id: 'significanceselector'
});


var eventid_selector = new Ext.form.NumberField({
    allowDecimals:false,
    allowNegative:false,
    maxValue:9999,
    minValue:1,
    width:60,
    id: 'eventid',
    name:'eventid',
    fieldLabel:'Event'
});

var year_selector = new Ext.form.NumberField({
    allowDecimals:false,
    allowNegative:false,
    maxValue: new Date("Y"),
    minValue: 2002,
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
            {name: 'x0', type:'float'},
            {name: 'x1', type:'float'},
            {name: 'y0', type:'float'},
            {name: 'y1', type:'float'},
            {name: 'issue', type:'date', dateFormat: 'Y-m-d H:i'},
            {name: 'expire', type:'date', dateFormat:'Y-m-d H:i'},
            {name: 'radarstart', type:'date', dateFormat: 'Y-m-d H:i'},
            {name: 'radarend', type:'date', dateFormat:'Y-m-d H:i'}
            ])
});
metastore.on('load', function(){
  cachedNexradTime = false;
  Ext.fly(vDescription.getEl()).update('');
  if (metastore.getCount() == 0){
    Ext.fly(vDescription.getEl()).update('Event not found on server, here is a list of other '+  phenomena_selector.getRawValue() + ' '+ sig_selector.getRawValue() +' issued by '+ wfo_selector.getRawValue() );
    tabPanel.items.each(function(c){
         if (c.saveme){}
         else{ c.disable(); }
    });
    tabPanel.activate('products-grid');
    eventsPanel.getStore().load({params:getVTEC()});
    return;
  }
  tslider.minValue = metastore.getAt(0).data.radarstart.getTime();
  tslider.maxValue = metastore.getAt(0).data.radarend.getTime();
  tslider.setValue( tslider.minValue );
  Ext.fly(vDescription.getEl()).update(wfo_selector.getRawValue() + ' '+ phenomena_selector.getRawValue() + ' '+ sig_selector.getRawValue() + ' #'+ eventid_selector.getValue()  +' issued '+ metastore.getAt(0).data.issue.format('Y-m-d H:i\\Z') +' expires '+ metastore.getAt(0).data.expire.format('Y-m-d H:i\\Z'));
  tabPanel.items.each(function(c){c.enable();});
  if (textTabPanel.isLoaded){ 
    textTabPanel.isLoaded = false;
    textTabPanel.fireEvent('activate', {}); 
  }
  if (radarPanel.isLoaded){ 
    radarPanel.isLoaded = false;
    radarPanel.fireEvent('activate', {}); 
  }
  if (sbwPanel.isLoaded){ 
    sbwPanel.isLoaded = false;
    sbwPanel.fireEvent('activate', {});
  }
  if (lsrGridPanel.isLoaded){
    lsrGridPanel.isLoaded = false;
    lsrGridPanel.getStore().load({params:getVTEC()});
  }
  if (allLsrGridPanel.isLoaded){ 
    allLsrGridPanel.isLoaded = false;
    allLsrGridPanel.getStore().load({params:getVTEC()});
  }
  if (geoPanel.isLoaded){ 
    geoPanel.isLoaded = false;
    geoPanel.getStore().load({params:getVTEC()});
  }
  if (eventsPanel.isLoaded){
    eventsPanel.isLoaded = false;
    eventsPanel.getStore().load({params:getVTEC()});
  }
  tabPanel.activate(1);
  resetGmap();
});




function resetGmap(){
   var q = metastore.getAt(0);
   var point = new GLatLng((q.data.y1+q.data.y0)/2,(q.data.x1+q.data.x0)/2);
   // Only works if the google panel has been loaded :(
   if (Ext.getCmp('mygpanel').gmap){
     Ext.getCmp('mygpanel').gmap.setCenter(point, 9);

     Ext.getCmp('mygpanel').gmap.clearOverlays();
     kml = "http://mesonet.agron.iastate.edu/kml/sbw_exact_time.php?"+ getVTEC();
     gxml = new GGeoXml(kml);
     Ext.getCmp('mygpanel').gmap.addOverlay(gxml);
     kml = "http://mesonet.agron.iastate.edu/kml/sbw_lsrs.php?"+ getVTEC();
     gxml2 = new GGeoXml(kml);
     Ext.getCmp('mygpanel').gmap.addOverlay(gxml2);
   }
};

var tip = new Ext.ux.SliderTip({
  getText: function(slider){
    return String.format('<b>{0} GMT</b>', 
           (new Date(slider.getValue())).format('Y-m-d H:i'));
    }
});


tslider = new Ext.Slider({
  minValue: (new Date()).getTime(),
  maxValue: (new Date()).getTime() + 1200,
  increment: 300000,
  isFormField: true,
  fieldLabel: 'Event Timeline',
  width: 180,
  plugins: [tip]
});
tslider.on('changecomplete', function(){
  if (radarPanel.isLoaded){ 
    radarPanel.isLoaded = false;
    radarPanel.fireEvent('activate', {}); 
  }
  if (googlePanel.gmap){
    if (googlePanel.gmap.getCurrentMapType() == custommap4) {
      googlePanel.gmap.setMapType(G_NORMAL_MAP);
      googlePanel.gmap.setMapType(custommap4); 
    }
  }

});


var selectform = new Ext.FormPanel({
    frame: true,
    id: 'mainform',
    labelAlign:'top',
    items: [wfo_selector,phenomena_selector, sig_selector, eventid_selector,
            year_selector, tslider,
          new Ext.Button({
            text:'Update Page',
            id:'mainbutton',
            listeners: {
              click: function() {
                metastore.load( {params:getVTEC()} );
              }  // End of handler
            }
          }),
          new Ext.Button({
            text:'Stable URL',
            id:'stablebutton',
            isFormField:true,
            fieldLabel: 'Create Linkable Page',
            listeners: {
              click: function() {
                window.location = getURL();
              }  // End of handler
            }
          })]
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


textTabPanel = new Ext.TabPanel({
    title: 'Text Data',
    enableTabScroll:true,
    isLoaded:false,
    id:'textTabPanel',
    disabled: true,
    defaults:{bodyStyle:'padding:5px'}
});
textTabPanel.on('activate', function(){
  if (! textTabPanel.isLoaded) {
    textTabsLoad();
    textTabPanel.isLoaded = true;
  }
});

textTabsLoad = function(){
  Ext.Ajax.request({
     waitMsg: 'Loading...',
     url : 'json-text.php' , 
     params:getVTEC(),
     method: 'GET',
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
        textTabPanel.isLoaded=true;
     }
});
}

lsrGridPanel = new Ext.grid.GridPanel({
    id:'lsrGridPanel',
    isVisible: false,
    isLoaded:false,
    store: jstore,
    disabled:true,
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
    title:'Storm Reports within SBW',
    plugins: expander,
    autoScroll:true
});
lsrGridPanel.on('activate', function(q){
   if (! this.isLoaded){
     this.getStore().load({
        params:getVTEC()+"&sbw=1"
     });
     this.isLoaded=true;
   }
});



allLsrGridPanel = new Ext.grid.GridPanel({
    id:'allLsrGridPanel',
    title: 'All Storm Reports',
    isLoaded:false,
    store: jstore2,
    disabled:true,
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
allLsrGridPanel.on('activate', function(q){
   if (! this.isLoaded){
     this.getStore().load({
        params:getVTEC()
     });
     this.isLoaded=true;
   }
});


geoPanel = new Ext.grid.GridPanel({
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
    disabled:true,
        title:'Geography Included',
        collapsible: false,
        animCollapse: false
    });
geoPanel.on('activate', function(q){
   if (! this.isLoaded){
     this.getStore().load({
        params:getVTEC()+"&sbw=1"
     });
     this.isLoaded=true;
   }
});



eventsPanel = new Ext.grid.GridPanel({
        id:'products-grid',
        store: pstore,
  saveme:true,
  disabled:true,
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
        title:'List Events',
        collapsible: false,
        animCollapse: false
    });
eventsPanel.on('activate', function(q){
   if (! this.isLoaded){
     this.getStore().load({
        params:getVTEC()
     });
     this.isLoaded=true;
   }
});



function getX(){
  if (metastore.getCount() == 0) return -95;
  return metastore.getAt(0).data.x1;
}
function getY(){
  if (metastore.getCount() == 0) return 42;
  return metastore.getAt(0).data.y1;
}


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
  lURL+="&TIME="+ (new Date(tslider.getValue())).format('Y-m-d\\TH:i:\\0\\0\\Z');
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
 switch ( phenomena_selector.getValue() ){
  case 'TO': break;
  case 'SV': break;
  default: return "<p>Storm Based Warning history unavailable</p>";
 }
 return "<p><img style=\"width:640px;height:480px;\" src=\"../GIS/sbw-history.php?vtec="+ year_selector.getValue() +".K"+ wfo_selector.getValue()  +"."+ phenomena_selector.getValue() +"."+ sig_selector.getValue() +"."+ String.leftPad(eventid_selector.getValue(),4,"0") +"\" /></p>";
}
function radargenerator(){
 switch ( phenomena_selector.getValue() ){
  case 'TO': r = 'layers[]=nexrad&layers[]=sbw&layers[]=sbwh&';break;
  case 'SV': r = 'layers[]=nexrad&layers[]=sbw&layers[]=sbwh&';break;
  case 'MA': r = 'layers[]=nexrad&layers[]=sbw&layers[]=sbwh&';break;
  case 'BZ': r = 'layers[]=nexrad&';break;
  case 'FF': r = 'layers[]=nexrad&layers[]=sbw&layers[]=sbwh&';break;
  case 'FL': r = 'layers[]=nexrad&';break;
  case 'HS': r = 'layers[]=nexrad&';break;
  case 'HP': r = 'layers[]=nexrad&';break;
  case 'IS': r = 'layers[]=nexrad&';break;
  case 'IP': r = 'layers[]=nexrad&';break;
  case 'SN': r = 'layers[]=nexrad&';break;
  case 'WS': r = 'layers[]=nexrad&';break;
  case 'WW': r = 'layers[]=nexrad&';break;
  case 'ZR': r = 'layers[]=nexrad&';break;
  default: r='layers[]=cbw&layers[]=legend&';
 }
 if (sig_selector.getValue() != 'W'){
   r='layers[]=cbw&layers[]=legend&';
   if( phenomena_selector.getValue() == 'TO' || phenomena_selector.getValue() == 'SV'){
    r = 'layers[]=nexrad&layers[]=cbw&layers[]=legend&';
   }
 }
 return "<p><img style=\"width:640px;height:480px;\" src=\"../GIS/radmap.php?"+ r +"layers[]=uscounties&ts="+ (new Date(tslider.getValue())).format('YmdHi') +"&vtec="+ year_selector.getValue() +".K"+ wfo_selector.getValue()  +"."+ phenomena_selector.getValue() +"."+ sig_selector.getValue() +"."+ String.leftPad(eventid_selector.getValue(),4,"0") +"\" /></p>";
}

sbwPanel = new Ext.Panel({
    title: 'SBW History',
    id: 'sbwhist',
    isLoaded:false,
    disabled:true
});
sbwPanel.on('activate', function(){
  if (! sbwPanel.isLoaded ) {
    sbwPanel.body.update( sbwgenerator() );
    sbwPanel.isLoaded=true;
  }
});

radarPanel = new Ext.Panel({
    title: 'RADAR Map',
    id: 'radarPabel',
    isLoaded:false,
    disabled:true
});
radarPanel.on('activate', function(){
  if (! radarPanel.isLoaded)  radarPanel.body.update( radargenerator() );
  radarPanel.isLoaded=true;
});

vDescription = new Ext.Toolbar.TextItem('');

tabPanel =  new Ext.TabPanel({
    region:'center',
    height:.75,
    plain:true,
    enableTabScroll:true,
    defaults:{bodyStyle:'padding:5px'},
    tbar: new Ext.StatusBar({
      id: 'main-status',
      defaultText: '',
      items:[vDescription]
      }),
    items:[
      {contentEl:'help', title: 'Help', saveme:true},
      radarPanel,
      textTabPanel,
      googlePanel,
      sbwPanel,
      lsrGridPanel,
      allLsrGridPanel,
      geoPanel,
      eventsPanel
    ],
    activeTab:0
});

var viewport = new Ext.Viewport({
    layout:'border',
    items:[{ 
             region:'north',
             height:130,
             contentEl: 'iem-header'
         },{
            region:'west',
            width:200,
            collapsible:true,
            title:'VTEC Options',
            items:[selectform]
         },
         tabPanel
         ]
});

// End of static.js
});
