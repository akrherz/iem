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
var options, lsrGridPanel, sbwGridPanel, nexradSlider, map, lsrLayer;

Ext.onReady(function(){

Ext.QuickTips.init();

//var extent = new OpenLayers.Bounds(-120, 28, -60, 55);

var expander = new Ext.grid.RowExpander({
        width: 20,
        tpl : new Ext.Template(
            '<p><b>Source:</b> {source} <b>Remark:</b> {remark}<br><b>Active Products:</b> {prodlinks}'
        )
});

var sbw_expander = new Ext.grid.RowExpander({
        width: 20,
        tpl : new Ext.Template(
            '<p><b>Link:</b> {link}'
        )
});

/* 
 * Figure out the last valid time for the slider
 */
function setLastNEXRAD(){
  now = new Date();
  gmt = now.toUTC();
  gmtl5 = gmt.add(Date.MINUTE, 0 - (parseInt(gmt.format('i')) % 5));
  Ext.getCmp('nexradslider').maxValue = gmtl5.fromUTC() ;
  Ext.getCmp('nexradslider').setValue( gmtl5.fromUTC() );
  //console.log("Setting last NEXRAD slider to:"+ gmtl5 );
}

function genSettings(){ 
  /* Generate URL options set on this page */
  s = "";
  s += (nexradWMS.visibility ? "1" : "0");
  s += (lsrLayer.visibility ? "1" : "0");
  s += (sbwLayer.visibility ? "1" : "0");
  s += (counties.visibility ? "1" : "0");
  return s;
}

function applySettings(opts){
  if (opts[0] == "1"){ /* Enable Warnings */
    nexradWMS.setVisibility(true);
  }
  if (opts[1] == "1"){ /* Enable Warnings */
    lsrLayer.setVisibility(true);
  }
  if (opts[2] == "1"){ /* Enable Warnings */
    sbwLayer.setVisibility(true);
  }
  if (opts[3] == "1"){ /* Enable Warnings */
    counties.setVisibility(true);
  }
}

/* URL format #DMX,DVN,FSD/201001010101/201001010201 */
function reloadData(){
  /* Switch display to LSR tab */
  Ext.getCmp("tabs").setActiveTab(1);
  s = Ext.getCmp("wfoselector").getValue();

  sts = Ext.getCmp("datepicker1").getValue().format('m/d/Y')
                     +" "+ Ext.getCmp("timepicker1").getValue();
  sdt = new Date(sts);
  start_utc = sdt.toUTC();
  /* Set the nexradSlider to the top of the hour */
  nexradSlider.minValue = (start_utc.fromUTC()).add(Date.MINUTE, 
                          0 - parseInt(start_utc.format('i')) );

  ets = Ext.getCmp("datepicker2").getValue().format('m/d/Y')
                     +" "+ Ext.getCmp("timepicker2").getValue();
  edt = new Date(ets);
  end_utc = edt.toUTC();
  /* Set the nexradSlider to the top of the next hour */
  nexradSlider.maxValue = (end_utc.fromUTC()).add(Date.MINUTE, 
                          60 - parseInt(start_utc.format('i')) );
  if (Ext.getCmp('rtcheckbox').checked) {
    setLastNEXRAD();
  } else {
    nexradSlider.setValue( 0 );
  }
  nexradSlider.fireEvent('changecomplete');

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
   updateURL();
}

function updateURL(){
   s = Ext.getCmp("wfoselector").getValue();
   sts = Ext.getCmp("datepicker1").getValue().format('m/d/Y')
                     +" "+ Ext.getCmp("timepicker1").getValue();
   sdt = new Date(sts);
   start_utc = sdt.toUTC();

   ets = Ext.getCmp("datepicker2").getValue().format('m/d/Y')
                     +" "+ Ext.getCmp("timepicker2").getValue();
   edt = new Date(ets);
   end_utc = edt.toUTC();

   window.location.href = "#"+ s +"/"+ start_utc.format('YmdHi') +
                                  "/"+ end_utc.format('YmdHi') +
                                  "/"+ genSettings();

}

options = {
    projection    : new OpenLayers.Projection("EPSG:900913"),
    units         : "m",
    numZoomLevels : 18,
    maxResolution : 156543.0339,
    maxExtent     : new OpenLayers.Bounds(-20037508, -20037508,
                                             20037508, 20037508.34)
}

var tip = new Ext.ux.SliderTip({
  getText: function(slider){
    return String.format('<b>{0} Local Time</b>',
           (new Date(slider.getValue())).format('Y-m-d g:i a'));
    }
});


nexradSlider = new Ext.Slider({
  id          : 'nexradslider',
  minValue    : (new Date()).getTime(),
  value       : (new Date()).getTime(),
  maxValue    : (new Date()).getTime() + 1200,
  increment   : 300000,
  isFormField : true,
  width       : 360,
  colspan     : 4,
  plugins     : [tip]
});

nexradSlider.on('changecomplete', function(){
   nexradWMS.mergeNewParams({
     time: (new Date(nexradSlider.getValue())).toUTC().format('Y-m-d\\TH:i')
   });
   Ext.getCmp("appTime").setText("NEXRAD Valid: "+ (new Date(nexradSlider.getValue())).format('Y-m-d g:i A'));
});

var nexradWMS = new OpenLayers.Layer.WMS("NEXRAD",
   "http://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r-t.cgi?",
   {
     layers      : "nexrad-n0r-wmst",
     maxExtent : new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
     transparent : true,
     sphericalMercator: true,
     format      : 'image/png',
     time        : (new Date(nexradSlider.getValue())).toUTC().format('Y-m-d\\TH:i')
   },{
     singleTile  : true,
     visibility  : false,
     eventListeners: {
      'visibilitychanged': function(){
         updateURL();
      }
     }
});


var counties = new OpenLayers.Layer.WMS("Counties", "http://mesonet.agron.iastate.edu/c/c.py/",
    {layers      : 'c-900913',
     format      : 'image/png',
     transparent : 'true'},{
     opacity     : 1.0,
     singleTile  : false,
     isBaseLayer : false,
     visibility  : false,
     buffer      : 0,
     eventListeners: {
      'visibilitychanged': function(){
         updateURL();
      }
     }
});


map = new OpenLayers.Map(options);
ls = new OpenLayers.Control.LayerSwitcher();
map.addControl(ls);

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
 "SV": {strokeColor: 'yellow'}
}

// Lookup 'table' for styling
var lsrLookup = {
 "0": {externalGraphic: "icons/tropicalstorm.gif"},
 "1": {externalGraphic: "icons/flood.png"},
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
 "v": {externalGraphic: "icons/flood.png"},
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
 "R": {externalGraphic: "http://www.wrh.noaa.gov/sgx/data/kml/precip_icons/${magnitude}.png",
 	graphicWidth: 40},
 "s": {externalGraphic: "icons/sleet.png"},
 "S": {externalGraphic: "http://www.wrh.noaa.gov/sgx/data/kml/snow_icons/${magnitude}.png",
 	graphicWidth: 30},
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
lsrLayer = new OpenLayers.Layer.Vector("Local Storm Reports",{
     styleMap  : lsrStyleMap,
     sphericalMercator: true,
     maxExtent : new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
     eventListeners: {
      'visibilitychanged': function(){
         updateURL();
      }
     }
});

function createPopup(feature) {
      // Can't get valid as an object :(
      html = "Time: "+ feature.data.valid +" UTC"
           +"<br />Event: "+ feature.data.magnitude +" "+ feature.data.typetext
           +"<br />Source: "+ feature.data.source
           +"<br />Remark: "+ feature.data.remark ;
      popup = new GeoExt.Popup({
            title: feature.data.wfo +": "+ feature.data.city,
            feature: feature,
            width:200,
            html: html,
            maximizable: true,
            collapsible: true
        });
        // unselect feature when the popup
        // is closed
        popup.show();
}

lsrLayer.events.on({
        featureselected: function(e) {
            createPopup(e.feature);
        }
});


var sbwLayer = new OpenLayers.Layer.Vector("Storm Based Warnings",{
      styleMap: sbwStyleMap,
     sphericalMercator: true,
      visibility: false,
     maxExtent : new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
     eventListeners: {
      'visibilitychanged': function(){
         updateURL();
      }
     }
});


// create feature store, binding it to the vector layer
;

sbwGridPanel = new Ext.grid.GridPanel({
   autoScroll : true,
   id         : 'sbwGridPanel',
   title      : "Storm Based Warnings",
   loadMask   : {msg:'Loading Data...'},
   viewConfig : {forceFit: true},
   tbar       : [{
            text    : 'Print Data Grid',
            icon    : 'icons/print.png',
            cls     : 'x-btn-text-icon',
            handler : function(){
              Ext.ux.Printer.print(Ext.getCmp("sbwGridPanel"));
            }
    },{
        id      : 'grid-excel-button',
        icon    : 'icons/excel.png',
        text    : 'Export to Excel...',
        handler : function(){
           var xd = sbwGridPanel.getExcelXml(true);
         var dataURL = 'exportexcel.php';
         params =[{
              name: 'ex',
              value: xd
         }];
         post_to_url(dataURL, params, 'post');
        }
      },{
            xtype     : 'button',
            text      : 'Save Shapefile',
            icon      : 'icons/shapefile.gif',
            cls       : 'x-btn-text-icon',
            listeners : {
               click  : function() {
                  uri = "http://mesonet.agron.iastate.edu/cgi-bin/request/gis/watchwarn.py?";
                  s = Ext.getCmp("wfoselector").getValue();
                  sts = Ext.getCmp("datepicker1").getValue().format('m/d/Y')
                     +" "+ Ext.getCmp("timepicker1").getValue();
                  sdt = new Date(sts);
                  start_utc = sdt.toUTC();
                  ets = Ext.getCmp("datepicker2").getValue().format('m/d/Y')
                     +" "+ Ext.getCmp("timepicker2").getValue();
                  edt = new Date(ets);
                  end_utc = edt.toUTC();
                  if (s != ""){
                    tokens = s.split(",");
                    for (i=0;i<tokens.length;i++){
                      uri += "&wfo[]="+ tokens[i];
                    }
                  }
                  uri += "&year1="+ start_utc.format('Y');
                  uri += "&month1="+ start_utc.format('m');
                  uri += "&day1="+ start_utc.format('d');
                  uri += "&hour1="+ start_utc.format('H');
                  uri += "&minute1="+ start_utc.format('i');
                  uri += "&year2="+ end_utc.format('Y');
                  uri += "&month2="+ end_utc.format('m');
                  uri += "&day2="+ end_utc.format('d');
                  uri += "&hour2="+ end_utc.format('H');
                  uri += "&minute2="+ end_utc.format('i');
                  window.location.href = uri;
               }  // End of handler
            }
   },{
       xtype     : 'button',
       text      : 'Expand All',
       listeners : {
           click : function() {
                nRows=sbwGridPanel.getStore().getCount();
                for(i=0;i< nRows;i++)
                   sbw_expander.expandRow(sbwGridPanel.view.getRow(i));
           }
       }
   }],
     store      : new GeoExt.data.FeatureStore({
      layer     : sbwLayer,
      fields    : [
         {name: 'wfo'},
         {name: 'issue', type: 'date', dateFormat: 'c'},
         {name: 'utc_issue', type: 'date', mapping: 'issue', convert: utcdate},
         {name: 'expire', type: 'date', dateFormat: 'c'},
         {name: 'utc_expire', type: 'date', mapping: 'expire', convert: utcdate},
         {name: 'phenomena'},
         {name: 'significance'},
         {name: 'eventid', type:'int'},
         {name: 'link'}
      ],
      proxy: new GeoExt.data.ProtocolProxy({
            protocol : new OpenLayers.Protocol.HTTP({
              url      : "/geojson/sbw.php",
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
                return value.format('Y-m-d g:i A');
            }
        }, {
            header    : "Issued UTC",
            sortable  : true,
            hidden : true,
            dataIndex : "utc_issue",
            renderer  : function(value){
                return value.format('Y-m-d g:i');
            }
        }, {
            header    : "Expired",
            sortable  : true,
            dataIndex : "expire",
            renderer  : function(value){
                return value.format('Y-m-d g:i A');
            }
        }, {
            header    : "Expired UTC",
            sortable  : true,
            hidden : true,
            dataIndex : "utc_expire",
            renderer  : function(value){
                return value.format('Y-m-d g:i');
        }
   }],
   sm: new GeoExt.grid.FeatureSelectionModel() 
});

function post_to_url(path, params, method) {
     method = method || "post"; 
     var form = document.createElement("form");
     form.setAttribute("method", method);
     form.setAttribute("action", path);
     for(var i=0; i<params.length; i++) {
         var hiddenField = document.createElement("input");
         hiddenField.setAttribute("type", "hidden");
         hiddenField.setAttribute("name", params[i].name);
         hiddenField.setAttribute("value", params[i].value);            
         form.appendChild(hiddenField);
     }   
     document.body.appendChild(form);   
     form.submit();
}

function utcdate(v, record){
	return (new Date.parseDate(v, 'c')).toUTC();
}

lsrGridPanel = new Ext.grid.GridPanel({
   autoScroll : true,
   id         : 'lsrGridPanel',
   title      : "Local Storm Report Information",
   loadMask   : {msg:'Loading Data...'},
   viewConfig : {forceFit: true},
   tbar       : [{
            text    : 'Print Data Grid',
            icon    : 'icons/print.png',
            cls     : 'x-btn-text-icon',
            handler : function(){
              Ext.ux.Printer.print(Ext.getCmp("lsrGridPanel"));
            }
    },{
     id      : 'grid-excel-button',
     icon    : 'icons/excel.png',
     text    : 'Export to Excel...',
     handler : function(){
        var xd = lsrGridPanel.getExcelXml(true);
              var dataURL = 'exportexcel.php';
              params =[{
                   name: 'ex',
                   value: xd
              }];
              post_to_url(dataURL, params, 'post');
     }
   },{
            xtype     : 'button',
            text      : 'Save Shapefile',
            icon      : 'icons/shapefile.gif',
            cls       : 'x-btn-text-icon',
            listeners : {
               click  : function() {
                  uri = "http://mesonet.agron.iastate.edu/cgi-bin/request/gis/lsr.py?";
                  s = Ext.getCmp("wfoselector").getValue();
                  sts = Ext.getCmp("datepicker1").getValue().format('m/d/Y')
                     +" "+ Ext.getCmp("timepicker1").getValue();
                  sdt = new Date(sts);
                  start_utc = sdt.toUTC();
                  ets = Ext.getCmp("datepicker2").getValue().format('m/d/Y')
                     +" "+ Ext.getCmp("timepicker2").getValue();
                  edt = new Date(ets);
                  end_utc = edt.toUTC();
                  if (s != ""){
                    tokens = s.split(",");
                    for (i=0;i<tokens.length;i++){
                      uri += "&wfo[]="+ tokens[i];
                    }
                  }
                  uri += "&year1="+ start_utc.format('Y');
                  uri += "&month1="+ start_utc.format('m');
                  uri += "&day1="+ start_utc.format('d');
                  uri += "&hour1="+ start_utc.format('H');
                  uri += "&minute1="+ start_utc.format('i');
                  uri += "&year2="+ end_utc.format('Y');
                  uri += "&month2="+ end_utc.format('m');
                  uri += "&day2="+ end_utc.format('d');
                  uri += "&hour2="+ end_utc.format('H');
                  uri += "&minute2="+ end_utc.format('i');
                  window.location.href = uri;
               }  // End of handler
            }
   },{
       xtype     : 'button',
       text      : 'Expand All',
       listeners : {
           click : function() {
                nRows=lsrGridPanel.getStore().getCount();
                for(i=0;i< nRows;i++)
                   expander.expandRow(lsrGridPanel.view.getRow(i));
           }
       }
   }],
   store      : new GeoExt.data.FeatureStore({
      layer     : lsrLayer,
      fields    : [
         {name: 'wfo', type: 'string'},
         {name: 'valid', type: 'date', mapping: 'valid', dateFormat: 'c'},
         {name: 'utc_valid', type: 'date', mapping: 'valid', convert: utcdate},
         {name: 'county'},
         {name: 'city'},
         {name: 'st', type: 'string'},
         {name: 'typetext', type: 'string'},
         {name: 'remark'},
         {name: 'prodlinks'},
         {name: 'wfo'},
         {name: 'source'},
         {name: 'magnitude', type: 'float'},
         {name: 'lat', type: 'float'},
         {name: 'lon', type: 'float'}
      ],
      proxy: new GeoExt.data.ProtocolProxy({
            protocol : new OpenLayers.Protocol.HTTP({
              url      : "/geojson/lsr.php?inc_ap=yes",
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
            renderer  : function(value, metadata, record){
                return value.format('Y-m-d g:i A');
            }
        }, {
            header    : "Report Time UTC",
            sortable  : true,
            hidden : true,
            dataIndex : "utc_valid",
            renderer  : function(value){
                return value.format('Y-m-d g:i');
            }
        },{
            header: "County",
            sortable  : true,
            dataIndex: "county"
        }, {
            header: "Location",
            sortable  : true,
            dataIndex: "city"
        }, {
            header: "ST",
            width: 30,
            sortable  : true,
            dataIndex: "st"
        }, {
            header: "Event Type",
            sortable  : true,
            dataIndex: "typetext"
        }, {
            header    : "Mag.",
            sortable  : true,
            dataIndex : "magnitude",
            width     : 50
        }, {
            header    : "Source",
            sortable  : true,
            dataIndex : "source",
            hidden    : true
        }, {
            header    : "Lat",
            sortable  : true,
            dataIndex : "lat",
            hidden    : true
        }, {
            header    : "Lon",
            sortable  : true,
            dataIndex : "lon",
            hidden    : true
        },{
        	header: 'Remark',
        	sortable: true,
        	dataIndex: 'remark',
        	hidden: true
        }],
   sm: new GeoExt.grid.FeatureSelectionModel() 
});

lsrGridPanel.getStore().on("load", function(mystore, records, options){
    if (records.length > 2999){
        Ext.Msg.alert('Warning', 'Request exceeds 3000 size limit, sorry.');
    }
    if (records.length > 0){ 
        map.zoomToExtent( lsrLayer.getDataExtent() );
    } else {
        Ext.Msg.alert('Alert', 'No LSRs found, sorry.');
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
    emptyText       : 'NWS Office(s), default all',
    resizable       : true,
    name            : 'wfo',
    mode            : 'local',
    displayFieldTpl : '{abbr}',
    tpl             : '<tpl for="."><div class="x-combo-list-item">[{abbr}] {wfo}</div></tpl>',
    valueField      : 'abbr',
    forceSelection  : true,
    listeners       : {
      collapse : function(){  }
    }
};


startDateSelector = {
    xtype     : 'datefield',
    id        : 'datepicker1',
    maxValue  : new Date(),
    minValue  : '07/23/2003',
    format    : 'j M Y',
    value     : new Date(),
    disabled  : false,
    width     : 105,
    listeners : {
       select : function(field, value){
          Ext.getCmp("datepicker2").minValue = value;
          if (value > Ext.getCmp("datepicker2").getValue()){
            Ext.getCmp("datepicker2").setValue( value );
          }
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
    value     : "12:00 AM",
    disabled  : false,
    listeners : {
       select : function(field, value){
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
        },
        boilerup: function(opts){
           applySettings(opts);
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
    format    : 'j M Y',
    listeners : {
       select : function(field, value){
         Ext.getCmp("datepicker1").maxValue = value;
         if (value < Ext.getCmp("datepicker1").getValue()){
           Ext.getCmp("datepicker1").setValue( value );
         }
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
    value     : "12:00 PM",
    disabled  : false,
    listeners : {
       select : function(field, value){
       }
    }
}







myForm = {
   autoScroll  : true,
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
       {html: 'Event Time Slider', border: false},
       nexradSlider,
       wfoSelector,
       {html: 'Start', border: false},
       startDateSelector,
       startTimeSelector,
       loadButton,
       {html: 'End', border: false},
       endDateSelector,
       endTimeSelector
   ]
}

/* Construct the viewport */
new Ext.Viewport({
    layout:'border',
    items:[{
        region      : 'north',
        title       : 'Local Storm Report Application',
        collapsible : true,
        collapsed   : true,
        contentEl   : 'iem-header'
    },{
        region:'south',
        height: 10,
        contentEl: 'iem-footer'
    },{
        xtype       : 'panel',
        region      : 'west',
        width       : 600,
        split       : true,
        layout      : 'border',
        items       : [{
              xtype       : 'panel',
              layout      : 'fit',
              height      : 100,
              region      : 'north',
              items       : myForm
           },{
              layout      : 'fit',
              xtype       : 'panel',
              region      : 'center',
              items       : [{
                xtype       : 'tabpanel',
                id          : 'tabs',
                activeTab   : 0,
                items       : [{
                    title     : 'Help', 
                    contentEl : 'help', 
                    unstyled  : true,
                    autoScroll: true,
                    padding   : 5}, 
                   lsrGridPanel,
                   sbwGridPanel
                ]
              }]
          }]
    },{
        region   : "center",
        id       : "mappanel",
        title    : "Map",
        tbar     : [{
          xtype    : 'checkbox',
          boxLabel : 'Real Time Mode',
          id       : 'rtcheckbox',
          handler  : function(box, checked){
            if (checked){
              setLastNEXRAD();
              Ext.getCmp("datepicker2").setValue( new Date() );
              Ext.getCmp("timepicker2").setValue( new Date() );
              Ext.getCmp("datepicker2").disable();
              Ext.getCmp("timepicker2").disable();
            } else {
              Ext.getCmp("datepicker2").enable();
              Ext.getCmp("timepicker2").enable();
            }
          }
        },{xtype: 'tbseparator'},{
          xtype  : 'tbtext',
          text   : 'NEXRAD Valid:',
          id     : 'appTime'
        },{
         xtype: "gx_opacityslider",
         layer: nexradWMS,
         aggressive: true,
         vertical: false,
         width: 100
        }],
        xtype    : "gx_mappanel",
        map      : map,
        layers   : [new OpenLayers.Layer.OSM("Open Street Map"),
                    nexradWMS, lsrLayer, sbwLayer, counties],
        extent   : new OpenLayers.Bounds(-20037508, -20037508,
                                             20037508, 20037508.34),
        split    : true
    }]
});

ls.maximizeControl();

var task = {
  run: function(){
    if (Ext.getCmp('rtcheckbox').checked) {
      Ext.getCmp("datepicker2").setValue( new Date() );
      Ext.getCmp("timepicker2").setValue( new Date() );
      reloadData();
    }
  },
  interval: 300000
}
Ext.TaskMgr.start(task);


}); /* End of onReady */
