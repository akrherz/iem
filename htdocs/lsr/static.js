Ext.override(Date, {
    toUTC : function() {
                        // Convert the date to the UTC date
        return this.add(Date.MINUTE, this.getTimezoneOffset());
    },

    fromUTC : function() {
                        // Convert the date from the UTC date
        return this.add(Date.MINUTE, -this.getTimezoneOffset());
    }
});


Ext.onReady(function(){

Ext.QuickTips.init();

var options, layer, lsrGridPanel, sbwGridPanel;
var extent = new OpenLayers.Bounds(-120, 28, -60, 55);

var expander = new Ext.grid.RowExpander({
        width: 20,
        tpl : new Ext.Template(
            '<p><b>Remark:</b> {remark}<br><b>Active Products:</b> {prodlinks}'
        )
});

var sbw_expander = new Ext.grid.RowExpander({
        width: 20,
        tpl : new Ext.Template(
            '<p><b>Link:</b> {link}'
        )
});


/* URL format #DMX,DVN,FSD/201001010101/201001010201 */
function reloadData(){
  s = Ext.getCmp("wfoselector").getValue();

  sts = Ext.getCmp("datepicker1").getValue().format('m/d/Y')
                     +" "+ Ext.getCmp("timepicker1").getValue();
  sdt = new Date(sts);
  start_utc = sdt.toUTC();

  ets = Ext.getCmp("datepicker2").getValue().format('m/d/Y')
                     +" "+ Ext.getCmp("timepicker2").getValue();
  edt = new Date(ets);
  end_utc = edt.toUTC();


  lsrGridPanel.getStore().reload({
      add    : false,
      params : {
         'sts': start_utc.format('YmdHi'),
         'ets': end_utc.format('YmdHi'),
         'wfos': s
       }
   });
  sbwGridPanel.getStore().reload({
      add    : false,
      params : {
         'sts': start_utc.format('YmdHi'),
         'ets': end_utc.format('YmdHi'),
         'wfos': s
       }
   });
   window.location.href = "#"+ s +"/"+ start_utc.format('YmdHi') +
                                  "/"+ end_utc.format('YmdHi');
}



        options = {
            projection: new OpenLayers.Projection("EPSG:900913"),
            units: "m",
            numZoomLevels: 18,
            maxResolution: 156543.0339,
            maxExtent: new OpenLayers.Bounds(-20037508, -20037508,
                                             20037508, 20037508.34)
        };

        layer = new OpenLayers.Layer.Google(
            "Google Maps",
            {type: G_NORMAL_MAP, sphericalMercator: true}
        );

        extent.transform(
            new OpenLayers.Projection("EPSG:4326"), options.projection
        );

var map = new OpenLayers.Map(options);

/* Create LSR styler */
var sbwStyleMap = new OpenLayers.StyleMap({
       'default': {
           strokeColor: 'black',
           strokeWidth: 3,
           fillOpacity  : 0,
           strokeOpacity: 1
       },
       'select': {
           strokeWidth: 5
       }
});
/* Create SBW styler */
var lsrStyleMap = new OpenLayers.StyleMap({
       'default': {
           externalGraphic: 'icons/other.png',
           fillOpacity: 1,
           pointRadius: 10
       },
       'select': {
           fillOpacity: 1,
           pointRadius: 15
       }
});

var sbwLookup = {
 "TO": {strokeColor: 'red'},
 "MA": {strokeColor: 'purple'},
 "FF": {strokeColor: 'green'},
 "EW": {strokeColor: 'green'},
 "FA": {strokeColor: 'green'},
 "FL": {strokeColor: 'green'},
 "FF": {strokeColor: 'green'},
 "SV": {strokeColor: 'yellow'}
}

// Lookup 'table' for styling
var lsrLookup = {
 "0": {externalGraphic: "icons/tropicalstorm.gif"},
 "1": {externalGraphic: "icons/tropicalstorm.gif"},
 "2": {externalGraphic: "icons/other.png"},
 "3": {externalGraphic: "icons/other.png"},
 "4": {externalGraphic: "icons/other.png"},
 "5": {externalGraphic: "icons/ice.png"},
 "6": {externalGraphic: "icons/cold.png"},
 "7": {externalGraphic: "icons/cold.png"},
 "8": {externalGraphic: "icons/fire.png"},
 "9": {externalGraphic: "icons/other.png"},
 "a": {externalGraphic: "icons/other.png"},
 "A": {externalGraphic: "icons/wind.png"},
 "B": {externalGraphic: "icons/downburst.png"},
 "C": {externalGraphic: "icons/funnelcloud.png"},
 "D": {externalGraphic: "icons/winddamage.png"},
 "E": {externalGraphic: "icons/flood.png"},
 "F": {externalGraphic: "icons/flood.png"},
 "G": {externalGraphic: "icons/wind.png"},
 "H": {externalGraphic: "icons/hail.png"},
 "I": {externalGraphic: "icons/hot.png"},
 "J": {externalGraphic: "icons/fog.png"},
 "K": {externalGraphic: "icons/lightning.gif"},
 "L": {externalGraphic: "icons/lightning.gif"},
 "M": {externalGraphic: "icons/wind.png"},
 "N": {externalGraphic: "icons/wind.png"},
 "O": {externalGraphic: "icons/wind.png"},
 "P": {externalGraphic: "icons/other.png"},
 "Q": {externalGraphic: "icons/tropicalstorm.gif"},
 "R": {externalGraphic: "icons/heavyrain.png"},
 "s": {externalGraphic: "icons/sleet.png"},
 "S": {externalGraphic: "icons/snow.png"},
 "T": {externalGraphic: "icons/tornado.png"},
 "U": {externalGraphic: "icons/fire.png"},
 "V": {externalGraphic: "icons/avalanche.gif"},
 "W": {externalGraphic: "icons/waterspout.png"},
 "X": {externalGraphic: "icons/funnelcloud.png"},
 "Z": {externalGraphic: "icons/blizzard.png"}
};
lsrStyleMap.addUniqueValueRules('default', 'type', lsrLookup);
sbwStyleMap.addUniqueValueRules('default', 'phenomena', sbwLookup);


// create vector layer
var lsrLayer = new OpenLayers.Layer.Vector("Local Storm Reports",{
      styleMap: lsrStyleMap
});
var sbwLayer = new OpenLayers.Layer.Vector("Storm Based Warnings",{
      styleMap: sbwStyleMap
});

map.addLayers([lsrLayer, sbwLayer])

// create feature store, binding it to the vector layer
;

sbwGridPanel = new Ext.grid.GridPanel({
   autoScroll : true,
   title      : "Storm Based Warnings",
   loadMask   : {msg:'Loading Data...'},
   viewConfig : {forceFit: true},
   store      : new GeoExt.data.FeatureStore({
      layer     : sbwLayer,
      fields    : [
         {name: 'wfo'},
         {name: 'issue', type: 'date', dateFormat: 'Y-m-d H:i'},
         {name: 'expire', type: 'date', dateFormat: 'Y-m-d H:i'},
         {name: 'phenomena'},
         {name: 'significance'},
         {name: 'eventid', type:'int'},
         {name: 'link'}
      ],
      proxy: new GeoExt.data.ProtocolProxy({
            protocol : new OpenLayers.Protocol.HTTP({
              url      : "../geojson/sbw.php",
              format   : new OpenLayers.Format.GeoJSON({
                   externalProjection: new OpenLayers.Projection("EPSG:4326"),
                   internalProjection: new OpenLayers.Projection("EPSG:900913")
               })
             })
      }),
      autoLoad  : false
   }), 
   plugins: [sbw_expander],
   columns: [sbw_expander,{
            header    : "Office",
            width     : 50,
            sortable  : true,
            dataIndex : "wfo" 
         }, {
            header    : "Event",
            sortable  : true,
            dataIndex : "phenomena",
            renderer  : function(value){
                return iemdata.vtecPhenomenaStore.getById(value).data.name;
            }
         }, {
            header    : "Significance",
            sortable  : true,
            dataIndex : "significance",
            renderer  : function(value){
                return iemdata.vtecSignificanceStore.getById(value).data.name;
            }
         }, {
            header    : "Event ID",
            sortable  : true,
            dataIndex : "eventid",
            width     : 50
        }, {
            header    : "Issued",
            sortable  : true,
            dataIndex : "issue",
            renderer  : function(value){
                return value.fromUTC().format('Y-m-d g:i A');
            }
        }, {
            header    : "Expired",
            sortable  : true,
            dataIndex : "expire",
            renderer  : function(value){
                return value.fromUTC().format('Y-m-d g:i A');
        }
   }],
   sm: new GeoExt.grid.FeatureSelectionModel() 
});


lsrGridPanel = new Ext.grid.GridPanel({
   autoScroll : true,
   title      : "Local Storm Report Information",
   loadMask   : {msg:'Loading Data...'},
   viewConfig : {forceFit: true},
   store      : new GeoExt.data.FeatureStore({
      layer     : lsrLayer,
      fields    : [
         {name: 'wfo', type: 'string'},
         {name: 'valid', type: 'date', dateFormat: 'Y-m-d H:i'},
         {name: 'county'},
         {name: 'city'},
         {name: 'typetext'},
         {name: 'remark'},
         {name: 'prodlinks'},
         {name: 'wfo'},
         {name: 'magnitude', type: 'float'}
      ],
      proxy: new GeoExt.data.ProtocolProxy({
            protocol : new OpenLayers.Protocol.HTTP({
              url      : "../geojson/lsr.php?inc_ap=yes",
              format   : new OpenLayers.Format.GeoJSON({
                   externalProjection: new OpenLayers.Projection("EPSG:4326"),
                   internalProjection: new OpenLayers.Projection("EPSG:900913")
               })
             })
      }),
      autoLoad  : false
   }), 
   plugins: [expander],
   columns: [expander,{
            header    : "Office",
            width     : 50,
            sortable  : true,
            dataIndex : "wfo"
        }, {
            header    : "Report Time",
            sortable  : true,
            dataIndex : "valid",
            renderer  : function(value){
                return value.fromUTC().format('Y-m-d g:i A');
            }
        }, {
            header: "County",
            sortable  : true,
            dataIndex: "county"
        }, {
            header: "Location",
            sortable  : true,
            dataIndex: "city"
        }, {
            header: "Event Type",
            sortable  : true,
            dataIndex: "typetext"
        }, {
            header    : "Mag.",
            sortable  : true,
            dataIndex : "magnitude",
            width     : 50
   }],
   sm: new GeoExt.grid.FeatureSelectionModel() 
});

lsrGridPanel.getStore().on("load", function(mystore, records, options){
              if (records.length > 0){ 
                map.zoomToExtent( lsrLayer.getDataExtent() );
              }
        });


/* SuperBoxSelector to do a multi pick */
wfoSelector = {
    store           : new Ext.data.SimpleStore({
       fields : ['abbr', 'wfo'],
       data   : iemdata.wfos
    }),
    rowspan         : 2,
    allowBlank      : false,
    width           : 200,
    id              : 'wfoselector',
    xtype           : 'superboxselect',
    emptyText       : 'Select Weather Office',
    resizable       : true,
    name            : 'wfo',
    mode            : 'local',
    displayFieldTpl : '{abbr}',
    tpl             : '<tpl for="."><div class="x-combo-list-item">[{abbr}] {wfo}</div></tpl>',
    valueField      : 'abbr',
    forceSelection  : true
};

startDateSelector = {
    xtype     : 'datefield',
    id        : 'datepicker1',
    maxValue  : new Date(),
    minValue  : '07/23/2003',
    value     : new Date(),
    disabled  : false,
    width     : 105,
    listeners : {
       select : function(field, value){
          reloadData();
       }
    }
}

startTimeSelector = {
    xtype     : 'timefield',
    allowBlank: false,
    increment : 1,
    width     : 100,
    emptyText : 'Select Time',
    id        : 'timepicker1',
    value     : new Date(),
    disabled  : false,
    listeners : {
       select : function(field, value){
          reloadData();
       }
    }
}

loadButton = {
    xtype           : 'button',
    id              : 'refresh',
    text            : 'Load',
    rowspan         : 2,
    listeners       : {
        click: function(){
           reloadData();
        }
    }
}

endDateSelector = {
    xtype     : 'datefield',
    id        : 'datepicker2',
    maxValue  : new Date(),
    emptyText : 'Select Date',
    minValue  : '07/23/2003',
    value     : new Date(),
    disabled  : false,
    width     : 105,
    listeners : {
       select : function(field, value){
         reloadData();
       }
    }
}

endTimeSelector = {
    xtype     : 'timefield',
    allowBlank: false,
    increment : 1,
    width     : 100,
    emptyText : 'Select Time',
    id        : 'timepicker2',
    value     : new Date(),
    disabled  : false,
    listeners : {
       select : function(field, value){
          reloadData();
       }
    }
}

myForm = {
   xtype       : 'form',
   labelAlign  : 'top',
   layout      : 'table',
   bodyStyle   : 'padding: 3px;',
   defaults    : {
      bodyStyle : 'padding: 3px;'
   },
   layoutConfig: {
       columns  : 5
   },
   items       : [
       wfoSelector,
       {html: 'Start Datetime', border: false},
       startDateSelector,
       startTimeSelector,
       loadButton,
       {html: 'Ending Datetime', border: false},
       endDateSelector,
       endTimeSelector
   ]
}

/* Construct the viewport */
var viewport = new Ext.Viewport({
    layout:'border',
    items:[{
        region      : 'north',
        title       : 'Local Storm Report Application',
        collapsible : true,
        collapsed   : true,
        contentEl   :'iem-header'
    },{
        xtype       : 'panel',
        region      : 'west',
        width       : 600,
        layout      : 'border',
        items       : [{
              xtype       : 'panel',
              layout      : 'fit',
              height      : 70,
              region      : 'north',
              items       : myForm
           },{
              layout      : 'fit',
              xtype       : 'panel',
              region      : 'center',
              items       : [{
                xtype       : 'tabpanel',
                activeTab   : 0,
                items       : [
                   {title: 'Help', contentEl: 'help'}, 
                   lsrGridPanel,
                   sbwGridPanel
                ]
              }]
          }]
    },{
        region   : "center",
        id       : "mappanel",
        title    : "Map",
        xtype    : "gx_mappanel",
        map      : map,
        layers   : [layer],
        extent   : extent,
        split    : true
    }]
});

}); /* End of onReady */
