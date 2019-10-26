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
  var now = new Date();
  var gmt = now.toUTC();
  var gmtl5 = gmt.add(Date.MINUTE, 0 - (parseInt(gmt.format('i')) % 5));
  Ext.getCmp('nexradslider').setMaxValue(gmtl5.fromUTC().getTime());
  Ext.getCmp('nexradslider').setValue(gmtl5.fromUTC().getTime());
}

function genSettings(){ 
  /* Generate URL options set on this page */
  var s = "";
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
  var s = Ext.getCmp("wfoselector").getValue();

  var sts = Ext.getCmp("datepicker1").getValue().format('m/d/Y')
                     +" "+ Ext.getCmp("timepicker1").getValue();
  var sdt = new Date(sts);
  var start_utc = sdt.toUTC();
  /* Set the nexradSlider to the top of the hour */
  Ext.getCmp("nexradslider").setMinValue(
		  (start_utc.fromUTC()).add(Date.MINUTE, 
                          0 - parseInt(start_utc.format('i')) ).getTime());

  var ets = Ext.getCmp("datepicker2").getValue().format('m/d/Y')
                     +" "+ Ext.getCmp("timepicker2").getValue();
  var edt = new Date(ets);
  var end_utc = edt.toUTC();
  /* Set the nexradSlider to the top of the next hour */
  Ext.getCmp("nexradslider").setMaxValue(
		  (end_utc.fromUTC()).add(Date.MINUTE, 
                          60 - parseInt(start_utc.format('i')) ).getTime());
  if (Ext.getCmp('rtcheckbox').checked) {
    setLastNEXRAD();
  } else if (start_utc.getTime() == end_utc.getTime()){
	  // Mod back 5
	  var time = (start_utc.fromUTC()).add(Date.MINUTE, 
              0 - (parseInt(start_utc.format('i')) % 5) ).getTime();
	  Ext.getCmp("nexradslider").setValue(time);
  } else {
	Ext.getCmp("nexradslider").setValue(nexradSlider.minValue);
  }
  Ext.getCmp("nexradslider").fireEvent('changecomplete');

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
   var s = Ext.getCmp("wfoselector").getValue();
   var sts = Ext.getCmp("datepicker1").getValue().format('m/d/Y')
                     +" "+ Ext.getCmp("timepicker1").getValue();
   var sdt = new Date(sts);
   var start_utc = sdt.toUTC();

   var ets = Ext.getCmp("datepicker2").getValue().format('m/d/Y')
                     +" "+ Ext.getCmp("timepicker2").getValue();
   var edt = new Date(ets);
   var end_utc = edt.toUTC();

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

nexradSlider = {
	xtype: 'slider',
  id          : 'nexradslider',
  minValue    : (new Date()).getTime(),
  value       : (new Date()).getTime(),
  maxValue    : (new Date()).getTime() + 600000,
  increment   : 300000,
  isFormField : true,
  width       : 360,
  colspan     : 4,
  plugins  : [new Ext.slider.Tip({
	  getText: function(thumb){
		  return String.format('<b>{0} Local Time</b>',
	            (new Date(thumb.value)).format('Y-m-d g:i a'));
	  }
  })],
  listeners   : {
	  changecomplete: function(){
            var dt = new Date(this.getValue());
            // Need to rectify date to modulo 5
            dt.setMinutes(5 * parseInt(dt.getMinutes() / 5));
			nexradWMS.mergeNewParams({
			     time: dt.toUTC().format('Y-m-d\\TH:i')
			});
		    Ext.getCmp("appTime").setText("NEXRAD Valid: "+ dt.format('Y-m-d g:i A'));
	  }
  }
};

var nexradWMS = new OpenLayers.Layer.WMS("NEXRAD",
   "https://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r-t.cgi?",
   {
     layers      : "nexrad-n0r-wmst",
     maxExtent : new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
     transparent : true,
     sphericalMercator: true,
     format      : 'image/png',
     time        : '2017-01-01T00:00'
   },{
     singleTile  : true,
     visibility  : false,
     eventListeners: {
      'visibilitychanged': function(){
         updateURL();
      }
     }
});


var counties = new OpenLayers.Layer.WMS("Counties", "https://mesonet.agron.iastate.edu/c/c.py/",
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

var states = new OpenLayers.Layer.WMS("States", "https://mesonet.agron.iastate.edu/c/c.py/",
	    {layers      : 's-900913',
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
var ls = new OpenLayers.Control.LayerSwitcher();
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
 "0": "icons/tropicalstorm.gif",
 "1": "icons/flood.png",
 "x": "icons/flood.png",
 "2": "icons/other.png",
 "3": "icons/other.png",
 "4": "icons/other.png",
 "5": "icons/ice.png",
 "6": "icons/cold.png",
 "7": "icons/cold.png",
 "8": "icons/fire.png",
 "9": "icons/other.png",
 "a": "icons/other.png",
 "A": "icons/wind.png",
 "B": "icons/downburst.png",
 "C": "icons/funnelcloud.png",
 "D": "icons/winddamage.png",
 "E": "icons/flood.png",
 "F": "icons/flood.png",
 "v": "icons/flood.png",
 "G": "icons/wind.png",
 "H": "icons/hail.png",
 "I": "icons/hot.png",
 "J": "icons/fog.png",
 "K": "icons/lightning.gif",
 "L": "icons/lightning.gif",
 "M": "icons/wind.png",
 "N": "icons/wind.png",
 "O": "icons/wind.png",
 "P": "icons/other.png",
 "Q": "icons/tropicalstorm.gif",
 "s": "icons/sleet.png",
 "T": "icons/tornado.png",
 "U": "icons/fire.png",
 "V": "icons/avalanche.gif",
 "W": "icons/waterspout.png",
 "X": "icons/funnelcloud.png",
 "Z": "icons/blizzard.png"};
sbwStyleMap.addUniqueValueRules('default', 'phenomena', sbwLookup);


var lsr_context = {
    getText: function(feature) {
    	if (feature.attributes['type'] == 'S'){
        	return feature.attributes["magnitude"];
    	} else if (feature.attributes['type'] == 'R'){
        	return feature.attributes["magnitude"];    		
    	}
    	return "";
    },
    getExternalGraphic: function(feature) {
    	if (feature.attributes['type'] == 'S' ||
    	    feature.attributes['type'] == 'R'){
    		return "";
    	} 
        return lsrLookup[feature.attributes['type']];
    }
};
var lsr_template = {
	externalGraphic: "${getExternalGraphic}",
	graphicWidth: 20,
	graphicHeight: 20,
	graphicOpacity: 1,
    label: "${getText}",
    strokeColor: "#FFFFFF",
    strokeOpacity: 0,
    //strokeWidth: 3,
    fillColor: "#FFFFFF",
    fillOpacity: 0,
    pointRadius: 10,
    //pointerEvents: "visiblePainted",    
    fontColor: "#000",
    fontSize: "14px",
    fontFamily: "Courier New, monospace",
    fontWeight: "bold",
    labelOutlineColor: "white",
    labelOutlineWidth: 3
};
var lsr_style = new OpenLayers.Style(lsr_template, {context: lsr_context});
// create vector layer
lsrLayer = new OpenLayers.Layer.Vector("Local Storm Reports",{
     styleMap  : new OpenLayers.StyleMap(lsr_style),
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
      var html = "Time: "+ feature.data.valid +" UTC"
           +"<br />Event: "+ feature.data.magnitude +" "+ feature.data.typetext
           +"<br />Source: "+ feature.data.source
           +"<br />Remark: "+ feature.data.remark ;
      var popup = new GeoExt.Popup({
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
         var params =[{
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
                  var uri = "https://mesonet.agron.iastate.edu/cgi-bin/request/gis/watchwarn.py?";
                  var s = Ext.getCmp("wfoselector").getValue();
                  var sts = Ext.getCmp("datepicker1").getValue().format('m/d/Y')
                     +" "+ Ext.getCmp("timepicker1").getValue();
                  var sdt = new Date(sts);
                  var start_utc = sdt.toUTC();
                  var ets = Ext.getCmp("datepicker2").getValue().format('m/d/Y')
                     +" "+ Ext.getCmp("timepicker2").getValue();
                  var edt = new Date(ets);
                  var end_utc = edt.toUTC();
                  if (s != ""){
                    var tokens = s.split(",");
                    for (var i=0;i<tokens.length;i++){
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
                var nRows=sbwGridPanel.getStore().getCount();
                for(var i=0;i< nRows;i++)
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
              var params =[{
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
                  var uri = "https://mesonet.agron.iastate.edu/cgi-bin/request/gis/lsr.py?";
                  var s = Ext.getCmp("wfoselector").getValue();
                  var sts = Ext.getCmp("datepicker1").getValue().format('m/d/Y')
                     +" "+ Ext.getCmp("timepicker1").getValue();
                  var sdt = new Date(sts);
                  var start_utc = sdt.toUTC();
                  var ets = Ext.getCmp("datepicker2").getValue().format('m/d/Y')
                     +" "+ Ext.getCmp("timepicker2").getValue();
                  var edt = new Date(ets);
                  var end_utc = edt.toUTC();
                  if (s != ""){
                    var tokens = s.split(",");
                    for (var i=0;i<tokens.length;i++){
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
                var nRows=lsrGridPanel.getStore().getCount();
                for(var i=0;i< nRows;i++)
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
    if (records.length == 1){ 
        map.setCenter(lsrLayer.getDataExtent().getCenterLonLat(), 9);
    } else if (records.length > 0){ 
        map.zoomToExtent( lsrLayer.getDataExtent() );
    } else {
        Ext.Msg.alert('Alert', 'No LSRs found, sorry.');
    }
});


/* SuperBoxSelector to do a multi pick */
var wfoSelector = {
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


var startDateSelector = {
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

var startTimeSelector = {
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

var loadButton = {
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

var endDateSelector = {
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

var endTimeSelector = {
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







var myForm = {
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

var osmgray = new OpenLayers.Layer.OSM('Open Street Map (gray)', null, {
	visible: false,
    eventListeners: {
        tileloaded: function(evt) {
            var ctx = evt.tile.getCanvasContext();
            if (ctx) {
                var imgd = ctx.getImageData(0, 0, evt.tile.size.w, evt.tile.size.h);
                var pix = imgd.data;
                for (var i = 0, n = pix.length; i < n; i += 4) {
                    pix[i] = pix[i + 1] = pix[i + 2] = (3 * pix[i] + 4 * pix[i + 1] + pix[i + 2]) / 8;
                }
                ctx.putImageData(imgd, 0, 0);
                evt.tile.imgDiv.removeAttribute("crossorigin");
                evt.tile.imgDiv.src = ctx.canvas.toDataURL();
            }
        }
    }
});

/* Construct the viewport */
new Ext.Viewport({
    layout:'border',
    items:[{
        region      : 'north',
        title       : 'IEM Local Storm Report (LSR) Application',
        collapsible : true,
        collapsed   : false,
        contentEl   : 'iem-header'
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
        			new OpenLayers.Layer("Blank",{
        				isBaseLayer: true,
        				visible: false
        			}), osmgray,
                    nexradWMS, states, counties, lsrLayer, sbwLayer],
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
