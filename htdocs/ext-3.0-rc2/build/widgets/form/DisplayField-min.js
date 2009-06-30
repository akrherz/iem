/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.form.DisplayField=Ext.extend(Ext.form.Field,{validationEvent:false,validateOnBlur:false,defaultAutoCreate:{tag:"div"},fieldClass:"x-form-display-field",htmlEncode:false,initEvents:Ext.emptyFn,isValid:function(){return true;},validate:function(){return true;},getRawValue:function(){var v=this.rendered?this.el.dom.innerHTML:Ext.value(this.value,'');if(v===this.emptyText){v='';}
if(this.htmlEncode){v=Ext.util.Format.htmlDecode(v);}
return v;},getValue:function(){return this.getRawValue();},getName:function(){return this.name;},setRawValue:function(v){if(this.htmlEncode){v=Ext.util.Format.htmlEncode(v);}
return this.rendered?(this.el.dom.innerHTML=(Ext.isEmpty(v)?'':v)):(this.value=v);},setValue:function(v){this.setRawValue(v);return this;}});Ext.reg('displayfield',Ext.form.DisplayField);