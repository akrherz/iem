/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */

Ext.ux.SlidingPager = Ext.extend(Object, {
    init : function(pbar){
        Ext.each(pbar.items.getRange(2,6), function(c){
            c.hide();
        });
        var slider = new Ext.Slider({
            width: 114,
            minValue: 1,
            maxValue: 1,
            plugins: new Ext.ux.SliderTip({
                getText : function(s){
                    return String.format('Page <b>{0}</b> of <b>{1}</b>', s.value, s.maxValue);
                }
            }),
            listeners: {
                changecomplete: function(s, v){
                    pbar.changePage(v);
                }
            }
        });
        pbar.insert(5, slider);
        pbar.on({
            change: function(pb, data){
                slider.maxValue = data.pages;
                slider.setValue(data.activePage);
            },
            beforedestroy: function(){
                slider.destroy();
            }
        });
    }
});