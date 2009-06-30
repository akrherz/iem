/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.form.RadioGroup=Ext.extend(Ext.form.CheckboxGroup,{allowBlank:true,blankText:"You must select one item in this group",defaultType:'radio',groupCls:'x-form-radio-group',getValue:function(){var out=null;if(this.items){this.items.each(function(item){if(item.checked){out=item;return false;}});}
return out;},setValue:function(id,value){if(this.rendered){var f=this.getBox(id);if(f){f.setValue(value);if(f.checked){this.items.each(function(item){if(item!==f){item.setValue(false);}},this);}}}else{this.values=[id,value];}
return this;}});Ext.reg('radiogroup',Ext.form.RadioGroup);