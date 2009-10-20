/* Static Javascript stuff to support the Time Machine :) */
Ext.onReady( function(){

var currentURI = "";

// http://www.extjs.com/forum/showthread.php?t=52585
Ext.override(Ext.form.ComboBox, {
    // private
    initValue: Ext.form.ComboBox.prototype.initValue.createSequence(function() {
        /**  
         * @cfg displayValue
         * A display value to initialise this {@link Ext.form.ComboBox}
         * (only useful for ComboBoxes with remote Stores, and having valueField != displayField).
         */
        if (this.mode == 'local' && !!this.valueField && this.valueField != this.displayField && this.displayValue) {
            if (this.forceSelection) {
                this.lastSelectionText = this.displayValue;
            }    
            this.setRawValue(this.displayValue);
        }    
    })
});

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
var appDT = new Date();

var ys = new Ext.Slider({
    id       : 'YearSlider',
    width    : 214,
    minValue : 2001,
    maxValue : 2009
});
ys.on('change', function(){ updateDT() });

var ds = new Ext.Slider({
    id       : 'DaySlider',
    width    : 732,
    minValue : 0,
    maxValue : 365,
    colspan  : 7
});
ds.on('change', function(){ updateDT() });

var ms = new Ext.Slider({
        id       : 'MinuteSlider',
        width    : 120,
        minValue : 0,
        maxValue : 59,
        increment: 60,
        listeners: {
          'change': function(){ updateDT(); }
        }
      });
var hs = new Ext.Slider({
        id       : 'HourSlider',
        width    : 120,
        minValue : 0,
        maxValue : 23,
        increment: 1,
        listeners: {
          'change': function(){ updateDT(); }
        }
       });

var store = new Ext.data.JsonStore({
    autoLoad: true,
        fields: [
            {name: 'id', type: 'int'},
            'name',
            'template',
            'sts',
            {name: 'interval', type: 'int'}
        ],
        idProperty: 'id',
        root: 'products',
        url: '../json/products.php'
    });

var combo = new Ext.form.ComboBox({
    id : 'cb',
    typeAhead: true,
    triggerAction: 'all',
    lazyRender:false,
    mode: 'local',
    editable : false,
    allowBlank : false,
    forceSelection: true,
    store: store,
    valueField: 'id',
    displayField: 'name'
});
/* This will be our hacky initializer */
combo.store.on('load', function(){ 
  var tokens = window.location.href.split('#');
  if (tokens.length == 2){
    var tokens2 = tokens[1].split(".");
    combo.setValue( tokens2[0] );
    if (tokens2[1] != "0"){
      gts = Date.parseDate( tokens2[1], "YmdHi" );
      lts = gts.fromUTC();
      ys.setValue( lts.format('Y') );
      ds.setValue( lts.format('z') );
      hs.setValue( lts.format('G') );
      if (lts.format('i') != "00"){
        ms.setValue( lts.format('i') );
      }
    } else {
      lts = new Date();
      ys.setValue( lts.format('Y') );
      ds.setValue( lts.format('z') );
      hs.setValue( lts.format('G') );
      if (lts.format('i') != "00"){
        ms.setValue( lts.format('i') );
      }
    }
  } else {
    /* We are going to default to the IEM Plot */
    combo.setValue( 1 );
    lts = new Date();
    ys.setValue( lts.format('Y') );
    ds.setValue( lts.format('z') );
    hs.setValue( lts.format('G') );
    ms.setValue( 0 );
    ms.disable();
  }
});
combo.on('select', function(cb, record, idx){
  if (record.data.interval >= 60){  ms.disable(); }
  else { ms.enable(); }
  ms.interval = record.data.interval;
  updateDT();
});


var displayDT = new Ext.Toolbar.TextItem({
    text  : 'Application Loading.....',
    width : 220,
    style:{'font-weight': 'bold'}
});

function updateDT(){
  y = ys.getValue();
  d = ds.getValue();
  h = Ext.getCmp('HourSlider').getValue();
  i = Ext.getCmp('MinuteSlider').getValue();

  dt = new Date('01/01/'+y).add(Date.DAY, d).add(Date.HOUR, h).add(Date.MINUTE,i);
  displayDT.setText( dt.format('l M d Y g:i A T') );
  gdt = dt.toUTC();

  meta = combo.getStore().getById( combo.getValue() );
  tpl = meta.data.template.replace(/%Y/g, '{0}').replace(/%m/g, '{1}').replace(/%d/g, '{2}').replace(/%H/g,'{3}').replace(/%i/g,'{4}');

  uri = String.format("http://mesonet.agron.iastate.edu/archive/data/"+tpl, gdt.format("Y"), gdt.format("m"), gdt.format("d"), gdt.format("H"), gdt.format("i") );
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
        text: '<< One Year',
        handler: function(){
            ys.setValue( ys.getValue() - 1);
        }
      }),
      new Ext.Button({
        text: '<< One Day',
        handler: function(){
            ds.setValue( ds.getValue() - 1);
        }
      }),
      new Ext.Button({
        text: '<< One Hour',
        handler: function(){
            hs.setValue( hs.getValue() - 1);
        }
      }),
      displayDT,
      new Ext.Button({
        text: 'One Hour >>',
        handler: function(){
            hs.setValue( hs.getValue() + 1);
        }
      }),
      new Ext.Button({
        text: 'One Day >>',
        handler: function(){
            ds.setValue( ds.getValue() + 1);
        }
      }),
      new Ext.Button({
        text: 'One Year >>',
        handler: function(){
            ys.setValue( ys.getValue() + 1);
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
