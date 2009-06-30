/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */

Ext.ux.SpinnerField = Ext.extend(Ext.form.NumberField, {
    deferHeight: true,
    autoSize: Ext.emptyFn,
    onBlur: Ext.emptyFn,
    adjustSize: Ext.BoxComponent.prototype.adjustSize,
        
	constructor: function(config) {
		var spinnerConfig = Ext.copyTo({}, config, 'incrementValue,alternateIncrementValue,accelerate,defaultValue,triggerClass,splitterClass');
		
		var spl = this.spinner = new Ext.form.Spinner(spinnerConfig);
		
		var plugins = config.plugins 
			? (Ext.isArray(config.plugins) 
				? config.plugins.push(spl)
				: [config.plugins, spl])
			: spl;
			
		Ext.ux.SpinnerField.superclass.constructor.call(this, Ext.apply(config, {plugins: plugins}));	
	},

    onShow: function(){
        if (this.wrap) {
            this.wrap.dom.style.display = '';
            this.wrap.dom.style.visibility = 'visible';
        }
    },
    
    onHide: function(){
        this.wrap.dom.style.display = 'none';
    },
        
    // private
    getResizeEl: function(){
        return this.wrap;
    },
    
    // private
    getPositionEl: function(){
        return this.wrap;
    },
    
    // private
    alignErrorIcon: function(){
        if (this.wrap) {
            this.errorIcon.alignTo(this.wrap, 'tl-tr', [2, 0]);
        }
    },

    validateBlur: function(){
        return true;
    }
});

Ext.reg('spinner', Ext.ux.SpinnerField);
//backwards comapt
Ext.form.SpinnerField = Ext.ux.SpinnerField;