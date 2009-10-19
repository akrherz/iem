/* Static Javascript stuff to support the Time Machine :) */
Ext.onReady( function(){

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
    width    : 366,
    minValue : 0,
    maxValue : 365
});
ds.on('change', function(){ updateDT() });

var tm = new Ext.Slider({
    id       : 'TimeSlider',
    width    : 366,
    minValue : 0,
    maxValue : 276,
    increment: 12
});
tm.on('change', function(){ updateDT() });

var store = new Ext.data.JsonStore({
    autoLoad: true,
        fields: [
            {name: 'id', type: 'int'},
            'name',
            'template',
            'sts'
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
    gts = Date.parseDate( tokens2[1], "YmdHi" );
    lts = gts.fromUTC();
    ys.setValue( lts.format('Y') );
    ds.setValue( lts.format('z') );
    tm.setValue( (lts.format('G') * 12) + (lts.format('i') / 5) );
  } else {
    combo.setValue( 1 );
    lts = new Date();
    ys.setValue( lts.format('Y') );
    ds.setValue( lts.format('z') );
    tm.setValue( (lts.format('G') * 12) + (lts.format('i') / 5) );
  }
});


var displayDT = new Ext.form.TextField({
    width    :  600,
    editable : false,
    colspan  : 4
});

function updateDT(){
  y = ys.getValue();
  d = ds.getValue();
  t = tm.getValue();

  dt = new Date('01/01/'+y).add(Date.DAY, d).add(Date.MINUTE, t*5);
  displayDT.setValue( dt.format('l M d Y g:i A T') );
  gdt = dt.toUTC();

  meta = combo.getStore().getById( combo.getValue() );
  tpl = meta.data.template.replace('%Y', '{0}').replace('%m', '{1}').replace('%d', '{2}').replace('%H','{3}').replace('%i','{4}');

  Ext.get("imagedisplay").dom.src = String.format("http://mesonet.agron.iastate.edu/archive/data/"+tpl, gdt.format("Y"), gdt.format("m"), gdt.format("d"), gdt.format("H"), gdt.format("i") );

  window.location.href = String.format("#{0}.{1}", combo.getValue(), gdt.format('YmdHi')); 

}

new Ext.form.FormPanel({
    renderTo: 'theform',
    layout  : 'table',
    layoutConfig: {
        columns: 4
    },
    items: [{html: 'Year'}, ys, {html: 'Day:'},ds,
            {html: 'Time:'}, tm, {html: 'Product'}, combo, displayDT]
});

});
