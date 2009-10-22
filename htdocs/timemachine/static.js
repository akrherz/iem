/*
 * Static Javascript stuff to support the Time Machine :) 
 * daryl herzmann akrherz@iastate.edu
 */
Ext.onReady( function(){

var currentURI = "";
var appTime = new Date();
var appDT   = 60;

/* Provides handy way to convert from local browser time to UTC */
Ext.override(Date, {
    toUTC : function() {
        return this.add(Date.MINUTE, this.getTimezoneOffset());
    },
    fromUTC : function() {
        return this.add(Date.MINUTE, -this.getTimezoneOffset());
    }
}); 

var ys = new Ext.Slider({
    id       : 'YearSlider',
    width    : 214,
    minValue : 2001,
    maxValue : (new Date()).format("Y"),
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
    increment: 60,
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

var store = new Ext.data.JsonStore({
    autoLoad  : true,
    fields    : [
            'id',
            {name: 'time_offset', type: 'int'},
            'name',
            'groupname',
            'template',
            {name: 'sts', type: 'date', dateFormat: 'Y-m-d'},
            {name: 'interval', type: 'int'}
    ],
    idProperty : 'id',
    root       : 'products',
    url        : '../json/products.php'
    });

var combo = new Ext.form.ComboBox({
    id            : 'cb',
    triggerAction : 'all',
    lazyRender    : false,
    autoLoad      : true,
    mode          : 'local',
    editable      : false,
    allowBlank    : false,
    forceSelection: true,
    store         : store,
    valueField    : 'id',
    tpl           : new Ext.XTemplate(
		'<tpl for=".">',
		'<tpl if="this.groupname != values.groupname">',
		'<tpl exec="this.groupname = values.groupname"></tpl>',
		'<h1>{groupname}</h1>',
		'</tpl>',
		'<div class="x-combo-list-item">{name}</div>',
		'</tpl>'
	),
    displayField  : 'name',
    listeners     : {
      select      : function(cb, record, idx){
        appDT = record.data.interval ;

      /* If we don't have sub hourly data, disable the minute selector */
      if (record.data.interval >= 60){ ms.disable(); }
      else { ms.enable(); }
      /* If we don't have sub daily data, disable the hour selector */
      if (record.data.interval >= (60*24)){  hs.disable(); }
      else { hs.enable(); }

      /* If we don't have hourly data */
      if (record.data.interval > 60){  
         Ext.getCmp('plushour').disable();
         Ext.getCmp('minushour').disable();
      }
      else {
         Ext.getCmp('plushour').enable();
         Ext.getCmp('minushour').enable();
      }

      ms.increment = record.data.interval;
      ys.minValue = record.data.sts.format("Y");
      ys.setValue( ys.getValue()-1 );
      ys.setValue( ys.getValue()+1 );
      updateDT();
      }
   }
});


/* This will be our hacky initializer */
store.on('load', function(){ 
  var tokens = window.location.href.split('#');
  if (tokens.length == 2){
    var tokens2 = tokens[1].split(".");
    idx = tokens2[0];
    if (tokens2[1] != "0"){
      gts = Date.parseDate( tokens2[1], "YmdHi" );
      appTime = gts.fromUTC();
    }
  } else {
    /* We are going to default to the IEM Plot */
    idx = 1;
  }
  /* Make sure that our form gets reset based on settings for record */
  setTime();
  combo.setValue( idx );
  combo.fireEvent('select', combo, store.getById(idx), idx);
});



var displayDT = new Ext.Toolbar.TextItem({
    text  : 'Application Loading.....',
    width : 220,
    style:{'font-weight': 'bold'}
});

/* Helper function to set the sliders to a given time! */
function setTime(){
  //console.log("setTime() appTime is "+ appTime );
  /* Our new values */
  g = parseInt( appTime.format('G') );
  z = parseInt( appTime.format('z') );
  y = parseInt( appTime.format('Y') );
  i = parseInt( appTime.format('i') );

  hs.setValue( g );
  ds.setValue( z ); 
  ys.setValue( y );
  ms.setValue( i );
}

/* Called whenever either the sliders update, the combobox */
function updateDT(){
  //console.log("updateDT() appTime is "+ appTime );
  y = ys.getValue();
  d = ds.getValue();
  h = hs.getValue();
  i = ms.getValue();

  newTime = new Date('01/01/'+y).add(Date.DAY, d).add(Date.HOUR, h).add(Date.MINUTE,i);
  if (newTime == appTime){ return; }
  appTime = newTime;
  meta = store.getById( combo.getValue() );
  if (! meta ){ return; }
  /* Make sure we aren't in the future! */
  if (appTime > (new Date())){ appTime = new Date(); setTime(); return; }

  /* Make sure we aren't in the past! */
  if (appTime < meta.data.sts){ appTime = meta.data.sts; setTime(); return; }

  /* 
   * We need to make sure that we are lined up with where we have data...
   */
  gdt = appTime.toUTC();
  min_from_0z = parseInt( gdt.format('G') ) * 60 + parseInt(gdt.format('i')) - meta.data.time_offset;
  offset = min_from_0z % meta.data.interval;
  console.log("TmCheck gdt= "+ gdt +" offset= "+ offset +", min_from_0z= "+ min_from_0z);
  if (offset != 0){
    gdt = gdt.add(Date.MINUTE, 0 - offset); 
    appTime = gdt.fromUTC();
    setTime();
  }

  displayDT.setText( appTime.format('l M d Y g:i A T') );

  tpl = meta.data.template.replace(/%Y/g, '{0}').replace(/%m/g, '{1}').replace(/%d/g, '{2}').replace(/%H/g,'{3}').replace(/%i/g,'{4}').replace(/%y/g, '{5}');

  uri = String.format(tpl, gdt.format("Y"), gdt.format("m"), gdt.format("d"), gdt.format("H"), gdt.format("i"), gdt.format("y") );
  if (uri != currentURI){
    Ext.get("imagedisplay").dom.src = uri;
    currentURI = uri;
  }
  window.location.href = String.format("#{0}.{1}", combo.getValue(), gdt.format('YmdHi')); 
}

new Ext.form.FormPanel({
    renderTo: 'theform',
    layout  : 'table',
    layoutConfig: {
        columns: 8
    },
    buttonAlign: 'left',
    fbar: [
      new Ext.Button({
        text: '<< Year',
        handler: function(){
            appTime = appTime.add(Date.YEAR, -1);
            setTime();
            updateDT();
        }
      }),
      new Ext.Button({
        text: '<< Day',
        handler: function(){
            appTime = appTime.add(Date.DAY, -1);
            setTime();
            updateDT();
        }
      }),
      new Ext.Button({
        id      : 'minushour',
        text    : '<< Hour',
        handler : function(){
            appTime = appTime.add(Date.HOUR, -1);
            setTime();
            updateDT();
        }
      }),
      new Ext.Button({
        text    : '<< Prev',
        handler : function(){
            appTime = appTime.add(Date.MINUTE, - appDT );
            setTime();
            updateDT();
        }
      }),
      displayDT,
      new Ext.Button({
        text    : 'Next >>',
        handler : function(){
            appTime = appTime.add(Date.MINUTE, appDT );
            setTime();
            updateDT();
        }
      }),
      new Ext.Button({
        id      : 'plushour',
        text: 'Hour >>',
        handler: function(){
            appTime = appTime.add(Date.HOUR, 1);
            setTime();
            updateDT();
        }
      }),
      new Ext.Button({
        text: 'Day >>',
        handler: function(){
            appTime = appTime.add(Date.DAY, 1);
            setTime();
            updateDT();
        }
      }),
      new Ext.Button({
        text: 'Year >>',
        handler: function(){
            appTime = appTime.add(Date.YEAR, 1);
            setTime();
            updateDT();
        }
      }),
      '->'],
    defaults : {
      bodyStyle: 'border:0px;padding-left:5px;'
    },
    items: [
      {html: 'Product: '}, combo, {html: 'Year: '}, ys,
      {html: 'Hour: '}, hs,       {html: 'Minute: '}, ms,
      {html: 'Day of Year: '}, ds
    ]
});


});
