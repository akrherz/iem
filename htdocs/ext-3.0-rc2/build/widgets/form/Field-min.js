/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.form.Field=Ext.extend(Ext.BoxComponent,{invalidClass:"x-form-invalid",invalidText:"The value in this field is invalid",focusClass:"x-form-focus",validationEvent:"keyup",validateOnBlur:true,validationDelay:250,defaultAutoCreate:{tag:"input",type:"text",size:"20",autocomplete:"off"},fieldClass:"x-form-field",msgTarget:'qtip',msgFx:'normal',readOnly:false,disabled:false,isFormField:true,hasFocus:false,initComponent:function(){Ext.form.Field.superclass.initComponent.call(this);this.addEvents('focus','blur','specialkey','change','invalid','valid');},getName:function(){return this.rendered&&this.el.dom.name?this.el.dom.name:this.name||this.id||'';},onRender:function(ct,position){if(!this.el){var cfg=this.getAutoCreate();if(!cfg.name){cfg.name=this.name||this.id;}
if(this.inputType){cfg.type=this.inputType;}
this.autoEl=cfg;}
Ext.form.Field.superclass.onRender.call(this,ct,position);var type=this.el.dom.type;if(type){if(type=='password'){type='text';}
this.el.addClass('x-form-'+type);}
if(this.readOnly){this.el.dom.readOnly=true;}
if(this.tabIndex!==undefined){this.el.dom.setAttribute('tabIndex',this.tabIndex);}
this.el.addClass([this.fieldClass,this.cls]);},getItemCt:function(){return this.el.up('.x-form-item',4);},initValue:function(){if(this.value!==undefined){this.setValue(this.value);}else if(!Ext.isEmpty(this.el.dom.value)&&this.el.dom.value!=this.emptyText){this.setValue(this.el.dom.value);}
this.originalValue=this.getValue();},isDirty:function(){if(this.disabled||!this.rendered){return false;}
return String(this.getValue())!==String(this.originalValue);},afterRender:function(){Ext.form.Field.superclass.afterRender.call(this);this.initEvents();this.initValue();},fireKey:function(e){if(e.isSpecialKey()){this.fireEvent("specialkey",this,e);}},reset:function(){this.setValue(this.originalValue);this.clearInvalid();},initEvents:function(){this.mon(this.el,Ext.isIE||Ext.isSafari3||Ext.isChrome?"keydown":"keypress",this.fireKey,this);this.mon(this.el,'focus',this.onFocus,this);var o=this.inEditor&&Ext.isWindows&&Ext.isGecko?{buffer:10}:null;this.mon(this.el,'blur',this.onBlur,this,o);},onFocus:function(){if(this.focusClass){this.el.addClass(this.focusClass);}
if(!this.hasFocus){this.hasFocus=true;this.startValue=this.getValue();this.fireEvent("focus",this);}},beforeBlur:Ext.emptyFn,onBlur:function(){this.beforeBlur();if(this.focusClass){this.el.removeClass(this.focusClass);}
this.hasFocus=false;if(this.validationEvent!==false&&this.validateOnBlur&&this.validationEvent!="blur"){this.validate();}
var v=this.getValue();if(String(v)!==String(this.startValue)){this.fireEvent('change',this,v,this.startValue);}
this.fireEvent("blur",this);},isValid:function(preventMark){if(this.disabled){return true;}
var restore=this.preventMark;this.preventMark=preventMark===true;var v=this.validateValue(this.processValue(this.getRawValue()));this.preventMark=restore;return v;},validate:function(){if(this.disabled||this.validateValue(this.processValue(this.getRawValue()))){this.clearInvalid();return true;}
return false;},processValue:function(value){return value;},validateValue:function(value){return true;},markInvalid:function(msg){if(!this.rendered||this.preventMark){return;}
msg=msg||this.invalidText;var mt=this.getMessageHandler();if(mt){mt.mark(this,msg);}else if(this.msgTarget){this.el.addClass(this.invalidClass);var t=Ext.getDom(this.msgTarget);if(t){t.innerHTML=msg;t.style.display=this.msgDisplay;}}
this.fireEvent('invalid',this,msg);},clearInvalid:function(){if(!this.rendered||this.preventMark){return;}
this.el.removeClass(this.invalidClass);var mt=this.getMessageHandler();if(mt){mt.clear(this);}else if(this.msgTarget){this.el.removeClass(this.invalidClass);var t=Ext.getDom(this.msgTarget);if(t){t.innerHTML='';t.style.display='none';}}
this.fireEvent('valid',this);},getMessageHandler:function(){return Ext.form.MessageTargets[this.msgTarget];},getErrorCt:function(){return this.el.findParent('.x-form-element',5,true)||this.el.findParent('.x-form-field-wrap',5,true);},alignErrorIcon:function(){this.errorIcon.alignTo(this.el,'tl-tr',[2,0]);},getRawValue:function(){var v=this.rendered?this.el.getValue():Ext.value(this.value,'');if(v===this.emptyText){v='';}
return v;},getValue:function(){if(!this.rendered){return this.value;}
var v=this.el.getValue();if(v===this.emptyText||v===undefined){v='';}
return v;},setRawValue:function(v){return this.el.dom.value=(Ext.isEmpty(v)?'':v);},setValue:function(v){this.value=v;if(this.rendered){this.el.dom.value=(Ext.isEmpty(v)?'':v);this.validate();}
return this;},append:function(v){this.setValue([this.getValue(),v].join(''));},adjustSize:function(w,h){var s=Ext.form.Field.superclass.adjustSize.call(this,w,h);s.width=this.adjustWidth(this.el.dom.tagName,s.width);if(this.offsetCt){var ct=this.getItemCt();s.width-=ct.getFrameWidth('lr');s.height-=ct.getFrameWidth('tb');}
return s;},adjustWidth:function(tag,w){if(typeof w=='number'&&(Ext.isIE&&(Ext.isIE6||!Ext.isStrict))&&/input|textarea/i.test(tag)&&!this.inEditor){return w-3;}
return w;}});Ext.form.MessageTargets={'qtip':{mark:function(field,msg){field.el.addClass(field.invalidClass);field.el.dom.qtip=msg;field.el.dom.qclass='x-form-invalid-tip';if(Ext.QuickTips){Ext.QuickTips.enable();}},clear:function(field){field.el.removeClass(field.invalidClass);field.el.dom.qtip='';}},'title':{mark:function(field,msg){field.el.addClass(field.invalidClass);field.el.dom.title=msg;},clear:function(field){field.el.dom.title='';}},'under':{mark:function(field,msg){field.el.addClass(field.invalidClass);if(!field.errorEl){var elp=field.getErrorCt();if(!elp){field.el.dom.title=msg;return;}
field.errorEl=elp.createChild({cls:'x-form-invalid-msg'});field.errorEl.setWidth(elp.getWidth(true)-20);}
field.errorEl.update(msg);Ext.form.Field.msgFx[field.msgFx].show(field.errorEl,field);},clear:function(field){field.el.removeClass(field.invalidClass);if(field.errorEl){Ext.form.Field.msgFx[field.msgFx].hide(field.errorEl,field);}else{field.el.dom.title='';}}},'side':{mark:function(field,msg){field.el.addClass(field.invalidClass);if(!field.errorIcon){var elp=field.getErrorCt();if(!elp){field.el.dom.title=msg;return;}
field.errorIcon=elp.createChild({cls:'x-form-invalid-icon'});}
field.alignErrorIcon();field.errorIcon.dom.qtip=msg;field.errorIcon.dom.qclass='x-form-invalid-tip';field.errorIcon.show();field.on('resize',field.alignErrorIcon,field);},clear:function(field){field.el.removeClass(field.invalidClass);if(field.errorIcon){field.errorIcon.dom.qtip='';field.errorIcon.hide();field.un('resize',field.alignErrorIcon,field);}else{field.el.dom.title='';}}}};Ext.form.Field.msgFx={normal:{show:function(msgEl,f){msgEl.setDisplayed('block');},hide:function(msgEl,f){msgEl.setDisplayed(false).update('');}},slide:{show:function(msgEl,f){msgEl.slideIn('t',{stopFx:true});},hide:function(msgEl,f){msgEl.slideOut('t',{stopFx:true,useDisplay:true});}},slideRight:{show:function(msgEl,f){msgEl.fixDisplay();msgEl.alignTo(f.el,'tl-tr');msgEl.slideIn('l',{stopFx:true});},hide:function(msgEl,f){msgEl.slideOut('l',{stopFx:true,useDisplay:true});}}};Ext.reg('field',Ext.form.Field);