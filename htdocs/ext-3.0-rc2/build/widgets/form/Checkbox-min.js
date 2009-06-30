/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.form.Checkbox=Ext.extend(Ext.form.Field,{focusClass:undefined,fieldClass:"x-form-field",checked:false,defaultAutoCreate:{tag:"input",type:'checkbox',autocomplete:"off"},initComponent:function(){Ext.form.Checkbox.superclass.initComponent.call(this);this.addEvents('check');},onResize:function(){Ext.form.Checkbox.superclass.onResize.apply(this,arguments);if(!this.boxLabel){this.el.alignTo(this.wrap,'c-c');}},initEvents:function(){Ext.form.Checkbox.superclass.initEvents.call(this);this.mon(this.el,'click',this.onClick,this);this.mon(this.el,'change',this.onClick,this);},getResizeEl:function(){return this.wrap;},getPositionEl:function(){return this.wrap;},markInvalid:Ext.emptyFn,clearInvalid:Ext.emptyFn,onRender:function(ct,position){Ext.form.Checkbox.superclass.onRender.call(this,ct,position);if(this.inputValue!==undefined){this.el.dom.value=this.inputValue;}
this.wrap=this.el.wrap({cls:"x-form-check-wrap"});if(this.boxLabel){this.wrap.createChild({tag:'label',htmlFor:this.el.id,cls:'x-form-cb-label',html:this.boxLabel});}
if(this.checked){this.setValue(true);}else{this.checked=this.el.dom.checked;}},onDestroy:function(){Ext.destroy(this.wrap);Ext.form.Checkbox.superclass.onDestroy.call(this);},initValue:Ext.emptyFn,getValue:function(){if(this.rendered){return this.el.dom.checked;}
return false;},onClick:function(){if(this.el.dom.checked!=this.checked){this.setValue(this.el.dom.checked);}},setValue:function(v){var checked=this.checked=(v===true||v==='true'||v=='1'||String(v).toLowerCase()=='on');if(this.el&&this.el.dom){this.el.dom.checked=checked;this.el.dom.defaultChecked=checked;}
this.fireEvent("check",this,checked);if(this.handler){this.handler.call(this.scope||this,this,checked);}
return this;}});Ext.reg('checkbox',Ext.form.Checkbox);