/* Static Javascript stuff to support the Time Machine :) */
Ext.onReady( function(){

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
    renderTo : 'yearslider',
    width    : 214,
    minValue : 2001,
    maxValue : 2009
});
ys.on('change', function(){ updateDT() });

var ds = new Ext.Slider({
    id       : 'DaySlider',
    renderTo : 'dayslider',
    width    : 366,
    minValue : 0,
    maxValue : 365
});
ds.on('change', function(){ updateDT() });

var tm = new Ext.Slider({
    id       : 'TimeSlider',
    renderTo : 'timeslider',
    width    : 366,
    minValue : 0,
    maxValue : 268,
    increment: 12
});
tm.on('change', function(){ updateDT() });


var displayDT = new Ext.form.TextField({
    renderTo : 'displaydt',
    width    :  400
});

function updateDT(){
  y = ys.getValue();
  d = ds.getValue();
  t = tm.getValue();

  dt = new Date('01/01/'+y).add(Date.DAY, d).add(Date.MINUTE, t*5);
  displayDT.setValue( dt );
  gdt = dt.toUTC();

  Ext.get("imagedisplay").dom.src = String.format("http://mesonet.agron.iastate.edu/archive/data/{0}/mesonet_{1}.gif", gdt.format("Y/m/d"), gdt.format("Hi"));
}

});
