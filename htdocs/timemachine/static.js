/*
 * Static Javascript stuff to support the Time Machine :) 
 */
Ext.BLANK_IMAGE_URL = '/ext/resources/images/default/s.gif';

var ys, ds, hs, ms, displayDT, combo;
var currentURI = "";
var appTime = new Date();
var pageLoadTime = new Date();
var appDT = 60;
var realtime = true;
	
/*
 * Logic to make the application auto refresh if it believes we are in 
 * auto refreshing mode. 
 */
var task = {
  run: function(){
      if (realtime){
        appTime = new Date();
        setTime();
        updateDT();
      }
  },
  interval: 300000
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
            rootProperty: 'products',
            idProperty: 'id'
        }
    }
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

// Put us into archive mode, captian
function setArchive(){
	Ext.getCmp("appMode").setText("Archive");
	realtime = false;	
} // End of setArchive()

	
/* Helper function to set the sliders to a given time! */
function setTime(){
	var now = new Date();
	// Figure out if we are switching modes
	if (realtime &&
			Ext.Date.add(now, Ext.Date.MINUTE, -3.0 * appDT) > appTime){
		setArchive();
	} 
	if (! realtime &&
			Ext.Date.add(now, Ext.Date.MINUTE, -3.0 * appDT) < appTime){
		Ext.getCmp("appMode").setText("Realtime");
		realtime = true;
	}
	var g = parseInt(Ext.Date.format(appTime, 'G'));
	var z = dayofyear(appTime) - 1;
	var y = parseInt(Ext.Date.format(appTime, 'Y'));
	var i = parseInt(Ext.Date.format(appTime, 'i'));

	hs.setValue(g);
	ds.setValue(z); 
	ys.setValue(y);
	ms.setValue(i);
} // End of setTime()

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

  if (appDT < 1440){
	  displayDT.setText(Ext.Date.format(appTime, 'D M d Y') +"<br />"
			  + Ext.Date.format(appTime, 'g:i A T') );
  } else{
	  displayDT.setText(Ext.Date.format(appTime.toUTC(), 'D M d Y') );
	  
  }
	  
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
} // End of updateDT()

function buildUI(){
	// Need a way to prevent missing images from messing up the page!
	Ext.get("imagedisplay").dom.onerror = function(){
		Ext.get("imagedisplay").dom.src = "/images/missing-320x240.jpg";
	};
	ys = Ext.create('Ext.slider.Single', {
	    width: '100%',
	    minValue: 1893,
	    renderTo : 'year_select',
	    maxValue: parseInt( Ext.Date.format(appTime, "Y") ),
	    labelAlign: 'top',
	    fieldLabel: 'Year',
	    listeners: {
	    	'drag': function(){ setArchive(); updateDT(); }
	    }
	});
	ds = Ext.create('Ext.slider.Single', {
	    width: '100%',
	    renderTo : 'day_select',
	    minValue: 0,
	    maxValue: 365,
	    labelAlign: 'top',
	    fieldLabel: 'Day of Year',
	    listeners: {
	    	'drag': function(){ setArchive(); updateDT(); }
	    }
	});
	ms = Ext.create('Ext.slider.Single', {
	    minValue: 0,
	    maxValue: 59,
	    width: '100%',
	    renderTo : 'minute_select',
	    labelAlign: 'top',
	    fieldLabel: 'Minute',
	    listeners: {
	    	'drag': function(){ setArchive(); updateDT(); }
	    }
	});
	hs = Ext.create('Ext.slider.Single', {
	    minValue: 0,
	    renderTo : 'hour_select',
	    width: '100%',
	    maxValue: 23,
	    labelAlign: 'top',
	    fieldLabel: 'Hour',
	    listeners: {
	    	'drag': function(){ setArchive(); updateDT(); }
	    }
	});
	displayDT = new Ext.Toolbar.TextItem({
	    html      : 'Loading...',
	    renderTo: 'displaydt',
	    isInitial : true, 
	    style     : {'font-weight': 'bold'}
	});
	
	combo = Ext.create('Ext.form.field.ComboBox', {
    id            : 'cb',
    triggerAction : 'all',
    queryMode     : 'local',
    renderTo : 'product_select',
    editable      : false,
    matchFieldWidth : false,
    fieldLabel: 'Available Products',
    labelAlign: 'top',
    flex: 2,
    margin: '0 10 0 0',
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
      select      : function(cb, record, idx){
        appDT = record.data.interval;

        /* If we don't have sub hourly data, disable the minute selector */
        if (appDT >= 60){ 
          //console.log("Disabling MS"); 
          ms.disable(); 
        } else { ms.enable(); }

        /* If we don't have sub daily data, disable the hour selector */
        if (appDT >= (60*24)){  hs.disable(); }
        else { hs.enable(); }

        /* If we don't have hourly data */
        if (appDT > 60){  
           Ext.getCmp('plushour').disable();
           Ext.getCmp('minushour').disable();
        }
        else {
           Ext.getCmp('plushour').enable();
           Ext.getCmp('minushour').enable();
        }

        ms.increment = appDT;
        //console.log("Setting MS Increment to "+ ms.increment );
        ys.minValue = parseInt( Ext.Date.format(record.data.sts, "Y") );
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
  combo.fireEvent('select', combo, store.getById(idx), idx);
  Ext.util.TaskManager.start(task);
});


	Ext.create('Ext.Button', {
		id : 'appMode',
		renderTo : 'realtime',
		text : 'RealTime',
		handler : function(btn) {
			if (btn.realtime) {
				realtime = false;
				btn.setText("Archive");
			} else {
				realtime = true;
				btn.setText("RealTime");
				appTime = new Date();
				setTime();
				updateDT();
			}
		}
	});

Ext.create('Ext.Button', {
	renderTo: 'pyear',
	text: '<< Year',
	 handler: function(){
		 appTime = Ext.Date.add(appTime, Ext.Date.YEAR, -1);
		 setTime();
		 updateDT();
	 }
});
Ext.create('Ext.Button', {
	 text: '<< Day',
	 renderTo: 'pday',
	 handler: function(){
		 appTime = Ext.Date.add(appTime, Ext.Date.DAY, -1);
		 setTime();
		 updateDT();
	 }
});
Ext.create('Ext.Button', {
	 id      : 'minushour',
	 text    : '<< Hour',
	 renderTo: 'phour',
	 handler : function(){
		 appTime = Ext.Date.add(appTime, Ext.Date.HOUR, -1);
		 setTime();
		 updateDT();
	 }
});
Ext.create('Ext.Button', {
	 text    : '<< Prev',
	 renderTo: 'prev',
	 handler : function(){
		 appTime = Ext.Date.add(appTime, Ext.Date.MINUTE, - appDT );
		 setTime();
		 updateDT();
	 }
});
Ext.create('Ext.Button', {
	 text    : 'Next >>',
	 renderTo: 'next',
	 handler : function(){
		 appTime = Ext.Date.add(appTime, Ext.Date.MINUTE, appDT );
		 setTime();
		 updateDT();
	 }
});
Ext.create('Ext.Button', {
	 id      : 'plushour',
	 text: 'Hour >>',
	 renderTo: 'nhour',
	 handler: function(){
		 appTime = Ext.Date.add(appTime, Ext.Date.HOUR, 1);
		 setTime();
		 updateDT();
	 }
});
Ext.create('Ext.Button', {
	 text: 'Day >>',
	 renderTo: 'nday',
	 handler: function(){
		 appTime = Ext.Date.add(appTime, Ext.Date.DAY, 1);
		 setTime();
		 updateDT();
	 }
});
Ext.create('Ext.Button', {
	 text: 'Year >>',
	 renderTo: 'nyear',
	 handler: function(){
		 appTime = Ext.Date.add(appTime, Ext.Date.YEAR, 1);
		 setTime();
		 updateDT();
	 }
});
	
} // End of buildUI()



Ext.onReady( function(){
	buildUI();
});
