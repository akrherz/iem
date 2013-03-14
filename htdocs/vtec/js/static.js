Ext.BLANK_IMAGE_URL = '../ext/resources/images/default/s.gif';
Ext.ns("App");

Ext.onReady(function(){

/**
 * Prints the contents of an Ext.Panel
 */
Ext.ux.Printer.PanelRenderer = Ext.extend(Ext.ux.Printer.BaseRenderer, {

 /**
  * Generates the HTML fragment that will be rendered inside the <html> 
  * element of the printing window
  */
 generateBody: function(panel) {
   return String.format("<div class='x-panel-print'>{0}</div>", panel.body.dom.innerHTML);
 }
});

Ext.ux.Printer.registerRenderer("panel", Ext.ux.Printer.PanelRenderer);
Ext.ux.Printer.BaseRenderer.prototype.stylesheetPath = 'print.css';

/* Here are my Panels that appear in tabs */
var helpPanel;
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
// Selectors
var wfo_selector;
/* Misc */
var delayedTaskSpinner;

function getVTEC(){
	//console.log("year_selector is"+ year_selector.getValue());
  return {
      year         : year_selector.getValue(),
      wfo          :  wfo_selector.getValue(),
      phenomena    : phenomena_selector.getValue(), 
      eventid      : eventid_selector.getValue(),
      significance : sig_selector.getValue()
   };
};

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
           {name: 'eventid', type: 'int'},
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
  tpl: '<tpl for="."><div class="x-combo-list-item">[{abbr}] {name}</div></tpl>',
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

var eventid_selector = new Ext.ux.form.Spinner({
     fieldLabel: 'Event Number',
     name: 'eventid',
     id: 'eventid',
     width: 60,
     strategy: new Ext.ux.form.Spinner.NumberStrategy({minValue:'1', maxValue:'9999'})
});
eventid_selector.on('spin', function(){
   if(!delayedTaskSpinner){
	 delayedTaskSpinner = new Ext.util.DelayedTask(function()
	 {
       metastore.load( {params:getVTEC()} );
	   delayedTaskSpinner = null;	
	});
   delayedTaskSpinner.delay(500);
  }

});

var year_selector = new Ext.ux.form.Spinner({
     fieldLabel : 'Year',
     name       : 'year',
     id         : 'yearselector',
     width      : 60,
     strategy   : new Ext.ux.form.Spinner.NumberStrategy({
       minValue : cfg.startYear, 
       maxValue : new Date("Y")
     })
});
year_selector.on('spin', function(){
   if(!delayedTaskSpinner){
     delayedTaskSpinner = new Ext.util.DelayedTask(function()
     {
       metastore.load( {params:getVTEC()} );
       delayedTaskSpinner = null;
    });
   delayedTaskSpinner.delay(500);
  }

});


var metastore = new Ext.data.Store({
    root      : 'meta',
    autoLoad  : false,
    id        : 'metastore',
    recordType: Ext.grid.PropertyRecord,
    proxy     : new Ext.data.HttpProxy({
       url    : 'json-meta.php',
       method :'GET'
       }),
    reader    : new Ext.data.JsonReader({
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
/*
 * Need to adjust various things when data is loaded into the metastore
 */
metastore.on('load', function(mystore, records, options){
	//console.log("metastore load!");
  cachedNexradTime = false;
  //Ext.fly(vDescription.getEl()).update('');

  /* If we got no results from the server, show the events tab */
  if (metastore.getCount() == 0){
    //Ext.fly(vDescription.getEl()).update('Event not found on server, here is a list of other '+  phenomena_selector.getRawValue() + ' '+ sig_selector.getRawValue() +' issued by '+ wfo_selector.getRawValue() );
    Ext.getCmp("mainPanel").items.each(function(c){
         if (c.saveme){}
         else{ c.disable(); }
    });
    Ext.getCmp("mainPanel").activate('products-grid');
    eventsPanel.getStore().load({params:getVTEC()});
    return;
  }
  /* Activate the Google Panel by default :) */
  Ext.getCmp("mainPanel").activate(3);
  var q = mystore.getAt(0);
  	Ext.getCmp("googlepanel").setVTEC({
  	     year         : year_selector.getValue(),
  	      wfo          :  wfo_selector.getValue(),
  	      phenomena    : phenomena_selector.getValue(), 
  	      eventid      : eventid_selector.getValue(),
  	      significance : sig_selector.getValue(),
	      x0			: q.data.x0,
	      x1			: q.data.x1,
	      y0			: q.data.y0,
	      y1			: q.data.y1,
	      issue			: q.data.issue,
	      expire		: q.data.expire
  	});


  /* Update the toolbar */
  Ext.fly(vDescription.getEl()).update(wfo_selector.getRawValue() + ' '
		  + phenomena_selector.getRawValue() + ' '+ sig_selector.getRawValue() 
		  + ' #'+ eventid_selector.getValue()  +' issued '+ 
		  metastore.getAt(0).data.issue.format('Y-m-d H:i') +' UTC expires '+ 
		  metastore.getAt(0).data.expire.format('Y-m-d H:i') + ' UTC');
  Ext.getCmp("mainPanel").items.each(function(c){c.enable();});

  /* Now we check the various panels to see if they should be reloaded */
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


  
});


var tip = new Ext.ux.SliderTip({
  getText: function(slider){
    return String.format('<b>{0} GMT</b>', 
           (new Date(slider.getValue())).format('Y-m-d H:i'));
    }
});

var selectform = new Ext.FormPanel({
    frame      : true,
    id         : 'mainform',
    labelAlign : 'top',
    items      : [
         wfo_selector,
         phenomena_selector,
         sig_selector,
         eventid_selector,
         year_selector, 
         {
            xtype     : 'button',
            text      : 'Update Page',
            id        : 'mainbutton',
            style     : {marginBottom:'10px'},
            listeners : {
               click  : function() {
            	   //console.log("Click fired!");
                  metastore.load( {params:getVTEC()} );
               }  // End of handler
            }
          },{
            xtype     : 'button',
            text      : 'LSR KML Source',
            icon      : 'icons/kml.jpg',
            cls       : 'x-btn-text-icon',
            style     : {marginBottom:'10px'},
            listeners : {
               click  : function() {
                  window.location.href = Ext.getCmp("googlepanel").lsrkml;
               }  // End of handler
            }
          },{
            xtype     : 'button',
            text      : 'Warning KML Source',
            icon      : 'icons/kml.jpg',
            cls       : 'x-btn-text-icon',
            style     : {marginBottom:'10px'},
            listeners : {
               click  : function() {
                  window.location.href = Ext.getCmp("googlepanel").vteckml;
               }  // End of handler
            }
          },{
            xtype     : 'button',
            text      : 'County Intersection KML',
            icon      : 'icons/kml.jpg',
            cls       : 'x-btn-text-icon',
            style     : {marginBottom:'10px'},
            listeners : {
               click  : function() {
                  window.location.href = Ext.getCmp("googlepanel").countykml;
               }  // End of handler
            }
          },{
              xtype     : 'button',
              text      : 'GR Placefile Format',
              icon      : 'icons/kml.jpg',
              cls       : 'x-btn-text-icon',
              listeners : {
                 click  : function() {
                    window.location.href = Ext.getCmp("googlepanel").placefile;
                 }  // End of handler
              }
            }
    ]
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
          title      : 'Issuance',
          html       : '<pre>'+ jsonData.data[0].report  +'</pre>',
          xtype      : 'panel',
          autoScroll : true,
          tbar       : [
          {
            text    : 'Print Text',
            icon    : 'icons/print.png',
            cls     : 'x-btn-text-icon',
            handler : function(){
              Ext.ux.Printer.print(Ext.getCmp("textTabPanel").getActiveTab());
            }
          }
          ]
        });
        for ( var i = 0; i < jsonData.data[0].svs.length; i++ ){
            textTabPanel.add({
              title: 'Update '+ (i+1),
              html: '<pre>'+ jsonData.data[0].svs[i]  +'</pre>',
             xtype: 'panel',
             autoScroll:true,
             tbar       : [
             {
            text    : 'Print Text',
            icon    : 'icons/print.png',
            cls     : 'x-btn-text-icon',
            handler : function(){
              Ext.ux.Printer.print(Ext.getCmp("textTabPanel").getActiveTab());
              }
            } 
           ]  
          });
        }
        textTabPanel.activate(i);
        textTabPanel.isLoaded=true;
     }
});
}

lsrGridPanel = new Ext.grid.GridPanel({
    id:'lsrGridPanel',
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
     p = getVTEC();
     p.sbw = "1";
     this.getStore().load({
        params:p
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
   	 p = getVTEC();
   	 p.sbw = "1";
     this.getStore().load({
        params:p 
     });
     this.isLoaded=true;
   }
});

/* 
 * GridPanel that displays the events for a WFO,Phenomena,Signifcance
 */
eventsPanel = new Ext.grid.GridPanel({
    id       : 'products-grid',
    tbar     : [
          {
            text    : 'Print Grid',
            icon    : 'icons/print.png',
            cls     : 'x-btn-text-icon',
            handler : function(){
              Ext.ux.Printer.print(Ext.getCmp("products-grid"));
            }
          }
    ],
    store    : pstore,
    saveme   : true,
    disabled : false,
    loadMask : {msg:'Loading Data...'},
    cm       : new Ext.grid.ColumnModel([
        {header: "Event", width: 40, sortable: true, dataIndex: 'eventid'},
        {header: "Issued (UTC)", width: 140, sortable: true, 
         dataIndex: 'issued'},
        {header: "Expired (UTC)", width: 140, sortable: true, 
         dataIndex: 'expired'},
        {header: "Area km**2", width: 70, sortable: true, 
         dataIndex: 'area'},
        {header: "Locations", id:"locations", width: 250, sortable: true, 
         dataIndex: 'locations'}
    ]),
    plugins      : filters,
    stripeRows   : true,
    autoScroll   : true,
    title        : 'List Events',
    collapsible  : false,
    animCollapse : false,
    listeners    : {
        rowclick: function(self, rowIndex){
            record = self.getStore().getAt(rowIndex);
            Ext.getCmp("eventid").setValue( record.get("eventid") );
            Ext.getCmp('mainbutton').fireEvent('click', {});
        },
        activate: function(q){
            if (! this.isLoaded){
                this.getStore().load({
                    params:getVTEC()
                 });
                 this.isLoaded=true;
            }
        }
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

function sbwgenerator(){
 switch ( phenomena_selector.getValue() ){
  case 'TO': break;
  case 'SV': break;
  case 'MA': break;
  case 'FF': break;
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
 return "<p><img style=\"width:640px;height:480px;\" src=\"../GIS/radmap.php?"+ r +"layers[]=uscounties&vtec="+ year_selector.getValue() +".O.NEW.K"+ wfo_selector.getValue()  +"."+ phenomena_selector.getValue() +"."+ sig_selector.getValue() +"."+ String.leftPad(eventid_selector.getValue(),4,"0") +"\" /></p>";
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



var viewport = new Ext.Viewport({
    layout:'border',
    items:[{ 
             region:'north',
             height:110,
             contentEl: cfg.header
         },{
            region      : 'west',
            width       : 210,
            collapsible : true,
            autoScroll  : true,
            title:'VTEC Options',
            items:[
                selectform,
                {
                  contentEl  : 'boilerplate'
                }
            ]
         },
         new Ext.TabPanel({
           id              : 'mainPanel',
           region          : 'center',
           plain           : true,
           enableTabScroll : true,
           defaults        : {bodyStyle:'padding-left:5px'},
           tbar            : new Ext.Toolbar({
                id          : 'main-status',
                defaultText : '',
                items       : [vDescription]
           }),
           listeners 	: {
        	 render : function(){
        		 //console.log("panel rendered");
        		 
        	 }  
           },
           items           : [{
        	   contentEl		: 'help', 
        	   title			: 'Help',
        	   saveme			: true,
        	   preventBodyReset : true},
              radarPanel,
              textTabPanel,
              new App.RadarPanel({
            	  title: 'Google Map',
            	  id : 'googlepanel',
      			  listeners : {
      				render : function(){
      					//console.log("gmap rendered!");
      					Ext.getCmp('mainbutton').fireEvent('click', {});
      				}  
      			  },
      			  zoomLevel: 9
      			  }),
              sbwPanel,
              lsrGridPanel,
              allLsrGridPanel,
              geoPanel,
              eventsPanel
           ],
           activeTab       : 0
         })
         ]
});

// End of static.js
});
