Ext.onReady(function(){

var options, layer, store, gridPanel;
var extent = new OpenLayers.Bounds(-5, 35, 15, 55);

var expander = new Ext.grid.RowExpander({
        id: 'testexp',
        width: 30,
        tpl : new Ext.Template(
            '<p><b>Remark:</b> {remark}<br><b>Active Products:</b> {prodlinks}'
        )
});


/* URL format #DMX,DVN,FSD/201001010101/201001010201 */
function reloadData(){
  console.log( Ext.getCmp("wfoselector").getValue() );

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
            "Google Satellite",
            {type: G_SATELLITE_MAP, sphericalMercator: true}
        );

        extent.transform(
            new OpenLayers.Projection("EPSG:4326"), options.projection
        );

var map = new OpenLayers.Map(options);

/* Create LSR styler */
var styleMap = new OpenLayers.StyleMap({
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
styleMap.addUniqueValueRules('default', 'type', lsrLookup);



    // create vector layer
    var vecLayer = new OpenLayers.Layer.Vector("vector",{
          styleMap: styleMap
        });
    map.addLayers([vecLayer])

    // create feature store, binding it to the vector layer
    store = new GeoExt.data.FeatureStore({
        layer: vecLayer,
        fields: [
            {name: 'wfo', type: 'string'},
            {name: 'valid'},
            {name: 'county'},
            {name: 'city'},
            {name: 'typetext'},
            {name: 'remark'},
            {name: 'prodlinks'},
            {name: 'wfo'},
            {name: 'magnitude', type: 'float'}
        ],
        proxy: new GeoExt.data.ProtocolProxy({
            protocol: new OpenLayers.Protocol.HTTP({
                url: "../geojson/lsr.php?inc_ap=yes",
                format: new OpenLayers.Format.GeoJSON({
                   externalProjection: new OpenLayers.Projection("EPSG:4326"),
                   internalProjection: new OpenLayers.Projection("EPSG:900913")
                })
            })
        }),
        autoLoad: true
    });
    store.on("load", function(mystore, records, options){
       map.zoomToExtent( vecLayer.getDataExtent() );
    });

gridPanel = new Ext.grid.GridPanel({
   title    : "Local Storm Report Information",
   region   : "west",
   tbar     : [{
         id              : 'wfoselector',
         xtype           : 'multiselect',
         store           : new Ext.data.SimpleStore({
           fields: ['abbr', 'wfo'],
           data : iemdata.wfos
         }),
         valueField      : 'abbr',
         displayField    : 'wfo',
         height          : 200,
         mode            : 'local'
       },{
          xtype     : 'datefield',
          id        : 'datepicker1',
          maxValue  : new Date(),
          emptyText : 'Select Date',
          minValue  : '07/23/2003',
          value     : new Date(),
          disabled  : false,
          listeners : {
              select : function(field, value){
                  ts = Ext.getCmp("datepicker1").getValue().format('m/d/Y')
                     +" "+ Ext.getCmp("timepicker1").getValue();
                  var dt = new Date(ts);
                  store.reload({
                      add    : false,
                      params : {'ts': dt.format('YmdHi')
                      }
                  });
                  window.location.href = "#"+ dt.format('YmdHi');
              }
          }
       },{
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
                  ts = Ext.getCmp("datepicker1").getValue().format('m/d/Y')
                     +" "+ Ext.getCmp("timepicker1").getValue();
                  var dt = new Date(ts);
                  store.reload({
                      add    : false,
                      params : {'ts': dt.format('YmdHi')
                  }
                  });
                   window.location.href = "#"+ dt.format('YmdHi');
              }
          }
       }," to ",{
          xtype     : 'datefield',
          id        : 'datepicker2',
          maxValue  : new Date(),
          emptyText : 'Select Date',
          minValue  : '07/23/2003',
          value     : new Date(),
          disabled  : false,
          listeners : {
              select : function(field, value){
                  ts = Ext.getCmp("datepicker2").getValue().format('m/d/Y')
                     +" "+ Ext.getCmp("timepicker2").getValue();
                  var dt = new Date(ts);
                  store.reload({
                      add    : false,
                      params : {'ts': dt.format('YmdHi')
                      }
                  });
                  window.location.href = "#"+ dt.format('YmdHi');
              }
          }
       },{
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
                  ts = Ext.getCmp("datepicker2").getValue().format('m/d/Y')
                     +" "+ Ext.getCmp("timepicker2").getValue();
                  var dt = new Date(ts);
                  store.reload({
                      add    : false,
                      params : {'ts': dt.format('YmdHi')
                  }
                  });
                   window.location.href = "#"+ dt.format('YmdHi');
              }
          }
       }, {
         xtype           : 'button',
         text            : 'Refresh',
         listeners       : {
           click: function(){
               reloadData();
           }
         }
       }
   ],
        width: 600,
        store: store,
        plugins: [expander],
        columns: [expander,{
            header: "Office",
            dataIndex: "wfo"
        }, {
            header: "Report Time",
            dataIndex: "valid"
        }, {
            header: "County",
            dataIndex: "county"
        }, {
            header: "Location",
            dataIndex: "city"
        }, {
            header: "Event Type",
            dataIndex: "typetext"
        }, {
            header: "Magnitude",
            dataIndex: "magnitude"
        }],
        sm: new GeoExt.grid.FeatureSelectionModel() 
    });


/* Construct the viewport */
var viewport = new Ext.Viewport({
    layout:'border',
    items:[{
        region      : 'north',
        title       : 'Local Storm Report Application',
        collapsible : true,
        collapsed   : true,
        contentEl   :'iem-header'
    },gridPanel,{
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
