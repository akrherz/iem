/*
 * Static Javascript stuff to support the Time Machine :) 
 */
Ext.BLANK_IMAGE_URL = '/ext/resources/images/default/s.gif';

Ext.onReady( function(){

var currentURI = "";
var appTime = new Date();
var pageLoadTime = new Date();
var appDT   = 60;

/*
 * Need a way to prevent missing images from messing up the page!
 */
Ext.get("imagedisplay").dom.onerror = function(){
   Ext.get("imagedisplay").dom.src = "/images/missing-320x240.jpg";
};

/* Provides handy way to convert from local browser time to UTC */
Ext.override(Date, {
    toUTC : function() {
        return Ext.Date.add(this, Ext.Date.MINUTE, this.getTimezoneOffset());
    },
    fromUTC : function() {
        return Ext.Date.add(this, Ext.Date.MINUTE, -this.getTimezoneOffset());
    }
}); 

/*
 * Logic to make the application auto refresh if it believes we are in 
 * auto refreshing mode. 
 */
var task = {
  run: function(){
      if (Ext.getCmp("appMode").realtime){
        //console.log("Refreshing");
        appTime = new Date();
        setTime();
        updateDT();
      } 
  },
  interval: 300000
};

var ys = new Ext.Slider({
    id       : 'YearSlider',
    width    : 214,
    minValue : 1893,
    maxValue : Ext.Date.format(appTime, "Y"),
    listeners: {
          'drag': function(){ updateDT(); }
    }
});

var ds = new Ext.Slider({
    id       : 'DaySlider',
    width    : 732,
    minValue : 0,
    maxValue : 365,
    colspan  : 7,
    listeners: {
          'drag': function(){ updateDT(); }
    }
});

var ms = new Ext.Slider({
    id       : 'MinuteSlider',
    width    : 120,
    minValue : 0,
    maxValue : 59,
    increment: 1,
    listeners: {
          'drag': function(){ updateDT(); }
    }
});

var hs = new Ext.Slider({
    id       : 'HourSlider',
    width    : 120,
    minValue : 0,
    maxValue : 23,
    increment: 1,
    listeners: {
        'drag': function(){ updateDT(); }
    }
 });

Ext.define('Product', {
    extend: 'Ext.data.Model',
    fields: [
        {name: 'id', type: 'string'},
        {name: 'time_offset',  type: 'int'},
        {name: 'name',       type: 'string'},
        {name: 'groupname',  type: 'string'},
        {name: 'template',  type: 'string'},
        {name: 'sts',  type: 'date', dateFormat: 'Y-m-d'},
        {name: 'interval',  type: 'int'},
        {name: 'avail_lag',  type: 'int'}
    ]
});

var store = new Ext.data.JsonStore({
    autoLoad  : true,
    model : 'Product',
    proxy: {
        type: 'ajax',
        url: '/json/products.php',
        reader: {
            type: 'json',
            root: 'products',
            idProperty: 'id'
        }
    }
    });

var displayDT = new Ext.Toolbar.TextItem({
    text      : 'Application Loading.....',
    width     : 180,
    isInitial : true, 
    style     : {'font-weight': 'bold'}
});

var combo = Ext.create('Ext.form.field.ComboBox', {
    id            : 'cb',
    triggerAction : 'all',
    queryMode     : 'local',
    editable      : false,
    matchFieldWidth : false,
    listConfig : {
    	minWidth : 300,
    	getInnerTpl : function(){
    		return '<tpl for=".">'+
    				'<tpl if="this.groupname != values.groupname">' +
    				'<tpl exec="this.groupname = values.groupname"></tpl>' +
    				'<span class="dropdown-header">{groupname}</span>' +
    				'</tpl>' +
    				'<div class="x-combo-list-item">{name}</div>' +
    				'</tpl>';
    	}
    },
    allowBlank    : false,
    forceSelection: true,
    store         : store,
    valueField    : 'id',
    displayField  : 'name',
    listeners     : {
      select      : function(cb, records, idx){
        appDT = records[0].data.interval ;

        /* If we don't have sub hourly data, disable the minute selector */
        if (records[0].data.interval >= 60){ 
          //console.log("Disabling MS"); 
          ms.disable(); 
        } else { ms.enable(); }

        /* If we don't have sub daily data, disable the hour selector */
        if (records[0].data.interval >= (60*24)){  hs.disable(); }
        else { hs.enable(); }

        /* If we don't have hourly data */
        if (records[0].data.interval > 60){  
           Ext.getCmp('plushour').disable();
           Ext.getCmp('minushour').disable();
        }
        else {
           Ext.getCmp('plushour').enable();
           Ext.getCmp('minushour').enable();
        }

        ms.increment = records[0].data.interval;
        //console.log("Setting MS Increment to "+ ms.increment );
        ys.minValue = Ext.Date.format(records[0].data.sts, "Y");
        ys.setValue( ys.getValue()-1 );
        ys.setValue( ys.getValue()+1 );
        updateDT();
      }
   }
});

/*
 * This will be our hacky initializer 
 */
store.on('load', function(){ 
  /* Figure out if the desired product is specified in the URL */
  var tokens = window.location.href.split('#');
  if (tokens.length == 2){
    var tokens2 = tokens[1].split(".");
    idx = tokens2[0];
    if (tokens2[1] != "0"){
      gts = Ext.Date.parseDate( tokens2[1], "YmdHi" );
      appTime = gts.fromUTC();
    } else {
    	lag = store.getById(idx).data.avail_lag;
    	appTime = Ext.Date.add(appTime, Ext.Date.MINUTE, 0 - lag);
    }
  } else {
    /* We are going to default to the IEM Plot */
    idx = 1;
  }
  /* Make sure that our form gets reset based on settings for record */
  setTime();
  combo.setValue( idx );
  combo.fireEvent('select', combo, [store.getById(idx)], idx);
  Ext.util.TaskManager.start(task);
});


function dayofyear(d) {   // d is a Date object
	var yn = d.getFullYear();
	var mn = d.getMonth();
	var dn = d.getDate();
	var d1 = new Date(yn,0,1,12,0,0); // noon on Jan. 1
	var d2 = new Date(yn,mn,dn,12,0,0); // noon on input date
	var ddiff = Math.round((d2-d1)/864e5);
	return ddiff+1;
};

/* Helper function to set the sliders to a given time! */
function setTime(){
  now = new Date();
  if (Ext.getCmp("appMode").realtime &&
      Ext.Date.add(now, Ext.Date.MINUTE, -3.0 * appDT) > appTime ){
    Ext.getCmp("appMode").setText("Archive");
    Ext.getCmp("appMode").realtime = false;
  } 
  if (! Ext.getCmp("appMode").realtime &&
      Ext.Date.add(now, Ext.Date.MINUTE, -3.0 * appDT) < appTime ){
    Ext.getCmp("appMode").setText("Realtime");
    Ext.getCmp("appMode").realtime = true;
  }
  //console.log("setTime() appTime: "+ appTime +" delta3x: "+ 
  //		  Ext.Date.add(now, Ext.Date.MINUTE, -3.0 * appDT) );
  /* Our new values */
  g = parseInt( Ext.Date.format(appTime, 'G') );
  z = dayofyear( appTime ) - 1;
  y = parseInt( Ext.Date.format(appTime, 'Y') );
  i = parseInt( Ext.Date.format(appTime, 'i') );

  hs.setValue( g );
  ds.setValue( z ); 
  ys.setValue( y );
  ms.setValue( i );
  //console.log("Setting ms to "+ i );
}

/* Called whenever either the sliders update, the combobox */
function updateDT(){
  //console.log("updateDT() appTime is "+ appTime );
  y = ys.getValue();
  d = ds.getValue();
  h = hs.getValue();
  i = ms.disabled ? 0:  ms.getValue();
  //console.log("y ["+ y +"] d ["+ d +"] h ["+ h +"] i ["+ i +"]");
  
  newTime = new Date('01/01/'+y);
  newTime = Ext.Date.add(newTime, Ext.Date.DAY, d);
  newTime = Ext.Date.add(newTime, Ext.Date.HOUR, h);
  newTime = Ext.Date.add(newTime, Ext.Date.MINUTE, i);
  //console.log("updateDT() newTime is "+ newTime );
  if (newTime == appTime && ! displayDT.isInitial){ 
    //console.log("Shortcircut!");
    return; 
  }
  displayDT.isInitial = false;
  appTime = newTime;
  meta = store.getById( combo.getValue() );
  //console.log( meta);
  //console.log( combo.getValue() );
  if (! meta ){ 
    //console.log("Couldn't find metadata!");
    return; 
  }
  ceiling = (new Date());
  ceiling = Ext.Date.add(ceiling, Ext.Date.MINUTE, 0 - meta.data.avail_lag);
  //console.log("Ceiling is "+ ceiling);
  /* Make sure we aren't in the future! */
  if (Ext.Date.add(appTime, Ext.Date.MINUTE,-1) > ceiling){
    //console.log("Date is: "+ (new Date()));
    //console.log("appTime is: "+ appTime);
    //console.log("Future timestamp: "+ (appTime.add(Date.MINUTE,-1) - (new Date())) +" diff");
    appTime = ceiling; 
    setTime(); 
    //return; 
  }

  /* Make sure we aren't in the past! */
  if (appTime < meta.data.sts){ 
    //console.log("Timestamp too early...");
    appTime = meta.data.sts; 
    setTime(); 
    //return; 
  }

  /* 
   * We need to make sure that we are lined up with where we have data...
   */
  gdt = appTime.toUTC();
  min_from_0z = parseInt( Ext.Date.format(gdt, 'G') ) * 60 + 
  		parseInt(Ext.Date.format(gdt, 'i')) - meta.data.time_offset;
  offset = min_from_0z % meta.data.interval;
  //console.log("TmCheck gdt= "+ gdt +" offset= "+ offset +", min_from_0z= "+ min_from_0z);
  if (offset != 0){
    gdt = Ext.Date.add(gdt, Ext.Date.MINUTE, 0 - offset); 
    appTime = gdt.fromUTC();
    setTime();
  }

  displayDT.setText( Ext.Date.format(appTime, 'D M d Y g:i A T') );

  tpl = meta.data.template.replace(/%Y/g, '{0}').replace(/%m/g, '{1}').replace(/%d/g, '{2}').replace(/%H/g,'{3}').replace(/%i/g,'{4}').replace(/%y/g, '{5}');

  uri = Ext.String.format(tpl, Ext.Date.format(gdt, "Y"), 
		  Ext.Date.format(gdt, "m"), Ext.Date.format(gdt, "d"), 
		  Ext.Date.format(gdt, "H"), Ext.Date.format(gdt, "i"), 
		  Ext.Date.format(gdt, "y") );
  if (uri != currentURI){
    Ext.get("imagedisplay").dom.src = uri;
    currentURI = uri;
  }
  window.location.href = Ext.String.format("#{0}.{1}", combo.getValue(), Ext.Date.format(gdt, 'YmdHi')); 
}




Ext.create('Ext.form.Panel', {
    renderTo: 'theform',
    layout  : {
    	type: 'table',
    	columns: 8
    },
    defaults : {
        bodyStyle: 'border:0px;padding-left:0px;'
    },
    fbar: {
    	pack : 'left',
    	items : [
      Ext.create('Ext.Button', {
        id       : 'appMode',
        realtime : true,
        text     : 'RealTime',
        handler  : function(btn){
          if (btn.realtime){
            btn.realtime = false;
            btn.setText("Archive");
          } else {
            btn.realtime = true;
            btn.setText("RealTime");
            appTime = new Date();
            setTime();
            updateDT();
          }
        }
      }),
      Ext.create('Ext.Button', {
        text: '<< Year',
        handler: function(){
            appTime = Ext.Date.add(appTime, Ext.Date.YEAR, -1);
            setTime();
            updateDT();
        }
      }),
      Ext.create('Ext.Button', {
        text: '<< Day',
        handler: function(){
            appTime = Ext.Date.add(appTime, Ext.Date.DAY, -1);
            setTime();
            updateDT();
        }
      }),
      Ext.create('Ext.Button', {
        id      : 'minushour',
        text    : '<< Hour',
        handler : function(){
            appTime = Ext.Date.add(appTime, Ext.Date.HOUR, -1);
            setTime();
            updateDT();
        }
      }),
      Ext.create('Ext.Button', {
        text    : '<< Prev',
        handler : function(){
            appTime = Ext.Date.add(appTime, Ext.Date.MINUTE, - appDT );
            setTime();
            updateDT();
        }
      }),
      displayDT,
      Ext.create('Ext.Button', {
        text    : 'Next >>',
        handler : function(){
            appTime = Ext.Date.add(appTime, Ext.Date.MINUTE, appDT );
            setTime();
            updateDT();
        }
      }),
      Ext.create('Ext.Button', {
        id      : 'plushour',
        text: 'Hour >>',
        handler: function(){
            appTime = Ext.Date.add(appTime, Ext.Date.HOUR, 1);
            setTime();
            updateDT();
        }
      }),
      Ext.create('Ext.Button', {
        text: 'Day >>',
        handler: function(){
            appTime = Ext.Date.add(appTime, Ext.Date.DAY, 1);
            setTime();
            updateDT();
        }
      }),
      Ext.create('Ext.Button', {
        text: 'Year >>',
        handler: function(){
            appTime = Ext.Date.add(appTime, Ext.Date.YEAR, 1);
            setTime();
            updateDT();
        }
      }),
      '->']
    },
    items: [
      {html: 'Product: '}, combo, {html: 'Year: '}, ys,
      {html: 'Hour: '}, hs,       {html: 'Minute: '}, ms,
      {html: 'Day of Year: '}, ds
    ]
});


});
