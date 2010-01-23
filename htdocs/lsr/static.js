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

var options, layer, store, gridPanel;
var extent = new OpenLayers.Bounds(-120, 28, -60, 55);

var expander = new Ext.grid.RowExpander({
        id: 'testexp',
        width: 30,
        tpl : new Ext.Template(
            '<p><b>Remark:</b> {remark}<br><b>Active Products:</b> {prodlinks}'
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


  store.reload({
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
        autoLoad: false
    });
    store.on("load", function(mystore, records, options){
       map.zoomToExtent( vecLayer.getDataExtent() );
    });

gridPanel = new Ext.grid.GridPanel({
   title    : "Local Storm Report Information",
   region   : "west",
   viewConfig : {forceFit: true},
   tbar     : [{
         id              : 'wfoselector',
         xtype           : 'multiselect',
         store           : new Ext.data.SimpleStore({
           fields: ['abbr', 'wfo'],
           data : iemdata.wfos
         }),
         valueField      : 'abbr',
         displayField    : 'wfo',
         width           : 200,
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
                  reloadData();
              }
          }
       },{
          xtype     : 'timefield',
          allowBlank: false,
          increment : 1,
          width     : 60,
          emptyText : 'Select Time',
          id        : 'timepicker1',
          value     : new Date(),
          disabled  : false,
          listeners : {
              select : function(field, value){
                  reloadData();
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
                  reloadData();
              }
          }
       },{
          xtype     : 'timefield',
          allowBlank: false,
          increment : 1,
          width     : 60,
          emptyText : 'Select Time',
          id        : 'timepicker2',
          value     : new Date(),
          disabled  : false,
          listeners : {
              select : function(field, value){
                   reloadData();
              }
          }
       }, {
         xtype           : 'button',
         id              : 'refresh',
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
            header    : "Office",
            width     : 50,
            sortable  : true,
            dataIndex : "wfo"
        }, {
            header: "Report Time",
            sortable  : true,
            dataIndex: "valid"
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
            header: "Magnitude",
            sortable  : true,
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
