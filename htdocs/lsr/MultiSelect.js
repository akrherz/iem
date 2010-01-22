/**
 * Provides a drop down field with multiple checkboxes
 * @author Tony Landis http://www.tonylandis.com/
 * @copyright Free for all use and modification. The author and copyright must be remain intact here.
 *
 * @class Ext.form.MultiSelectField
 * @extends Ext.form.TriggerField
 */

var assertMenuHeight = function(m) {

    var maxHeight = Ext.getBody().getHeight() - 300;

    if (m.el.getHeight() > maxHeight) {

        m.el.setHeight(maxHeight);

        m.el.applyStyles('overflow:auto;');

    }

}; 

Ext.form.MultiSelectField = Ext.extend(Ext.form.TriggerField,  {
    triggerClass : 'x-form-trigger', 
    defaultAutoCreate : {tag: "input", type: "text", size: "10", autocomplete: "off"},
    readOnly: true, 
    lazyInit : false,
    hiddenValue: '',
    value: null,
    valueSeparator: ',',
    textSeparator: ';',
    loadingText: 'Loading list...', 
    
    // store defaults
    store: null, 
    mode: 'remote',
    valueField: 'value',
    displayField: 'text',
           
    initComponent : function(){  
        Ext.form.MultiSelectField.superclass.initComponent.call(this);  
 
        //auto-configure store from local array data 
        if(Ext.isArray(this.store)){ 
			if (Ext.isArray(this.store[0])){
				this.store = new Ext.data.SimpleStore({
					id: 'value',
				    fields: ['value','text'],
				    data: this.store
				});
		        this.valueField = 'value';
			}else{
				this.store = new Ext.data.Store({
					id: 'text',
				    fields: ['text'],
				    data: this.store,
				    expandData: true
				});
		        this.valueField = 'text';
			}
			this.displayField = 'text';
			this.mode = 'local';
		} 
    }, 
    
     
    onRender : function(ct, position){ 
        Ext.form.MultiSelectField.superclass.onRender.call(this, ct, position);
        
        if(this.hiddenName){ 
            this.hiddenField = this.el.insertSibling({tag:'input', type:'hidden', name: this.hiddenName, id: (this.hiddenId||this.hiddenName)},
                    'before', true);
            this.hiddenField.value =
                this.hiddenValue !== undefined ? this.hiddenValue :
                this.value !== undefined ? this.value : '';

            // prevent input submission
            this.el.dom.removeAttribute('name');
        }
        
		// build the menu
        if(this.menu == null) 	
        { 
        	this.menu = new Ext.menu.Menu({listeners: { beforeshow: assertMenuHeight}}); 
        	this.store.each(function(r) { 
        		this.menu.add(
        			new Ext.menu.CheckItem({
        				text: r.data[this.displayField],
        				value: r.data[this.valueField], 
        				hideOnClick: false 
        			})
        		).on('click', this.clickHandler, this);  
        	}, this); 
        }
 
        if(!this.lazyInit){
           //this.populateList(this.value);
        }else{
            //this.on('focus', this.setValues, this, {single: true});
        } 
    },  
     
    
    
    onTriggerClick : function(){ 
        if(this.disabled){
            return;
        } 
        this.menu.show(this.el, "tl-bl?");
        this.populateList(this.value); 
    },    
     
    validateBlur : function(){ 
        return !this.menu || !this.menu.isVisible();
    },
     
    getValue : function(){   
    	if(this.hiddenField){
    		return this.hiddenField.value || "";    	
    	}else if(this.valueField){
            return typeof this.value != 'undefined' ? this.value : '';
        }else{
            return Ext.form.MultiSelectField.superclass.getValue.call(this);
        } 
    },
    
    setValue : function(value, text){ 
    	if(text == undefined && value != undefined) {  
    		this.setValues(value.split(this.valueSeparator));
    		return;
    	} if(value==undefined) {
    		value='';
    		text='';
    	}
    	
    	this.lastSelectionText = text;
        if(this.hiddenField){
            this.hiddenField.value = value;
        }
        Ext.form.MultiSelectField.superclass.setValue.call(this, text);
        this.value = value;    	
    },
    
    setValues : function(keys){ 
    	// assemble full text and hidden value
    	var text  = '';
    	var value = '';
    	for(var i=0; i<keys.length; i++) 
    	{
    		if(keys[i] != undefined)
    		{
	    		// get the full store object
	    		var item = this.store.query(this.valueField, keys[i]).items[0];
	    		if(item != undefined) {
		   			value += (value!='' ? this.valueSeparator:'') + item.data[this.valueField] ;
		    		text += (text!='' ? this.textSeparator:'') + item.data[this.displayField];  
	    		}
    		}
    	}
		this.setValue(value,text);   
    },  
    
    selPush : function(key) {   
    	// rip current value into array
    	var keys = this.value.split(this.valueSeparator);
    	var i = keys.length++;
    	keys[i] = key; 
    	this.setValues(keys);
    },
    
    selDrop : function(key) {
    	// rip current value into array
    	var keys = this.value.split(this.valueSeparator);
    	for(var i=0; i<keys.length; i++) { 
    		if(keys[i].toString() == key.toString()) { 
    			keys[i]=undefined;
    		}
    	}  
    	this.setValues(keys);
    }, 

    onDestroy : function(){  
        if(this.menu) {
            this.menu.destroy();
        }
        if(this.wrap){
            this.wrap.remove();
        }
        Ext.form.MultiSelectField.superclass.onDestroy.call(this);
    }, 
    
    clickHandler: function(i,c){ 
        if(i.checked == false){ 
        	this.selPush(i.value, i.text); 
        } else { 
        	this.selDrop(i.value);
        }
   	}, 

    populateList: function(v)  { 
    	if(v==undefined || v==null) v=this.value;
    	 
    	// uncheck everything
    	if(this.menu) {
	    	this.menu.items.each(function(item) 
	    	{
	    		item.setChecked(false);
	    	});
    	}  
    	  
		// populate preset values
		if(v != undefined && v != '' && v!=null) 
		{   
			var sel = v.split(this.valueSeparator); 
			for(i=0; i<sel.length; i++) 
			{  
				try {
					var value = this.store.query(this.valueField, sel[i]).items[0].data[this.valueField];
					this.menu.items.each(function(mi){ 
						if(mi.value == value) mi.setChecked(true); 
					}, this); 
				}catch(e) { }
			} 
		} 
    }
});

Ext.reg('multiselect', Ext.form.MultiSelectField);
