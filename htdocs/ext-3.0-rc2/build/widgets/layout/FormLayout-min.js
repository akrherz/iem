/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.layout.FormLayout=Ext.extend(Ext.layout.AnchorLayout,{labelSeparator:':',setContainer:function(ct){Ext.layout.FormLayout.superclass.setContainer.call(this,ct);if(ct.labelAlign){ct.addClass('x-form-label-'+ct.labelAlign);}
if(ct.hideLabels){this.labelStyle="display:none";this.elementStyle="padding-left:0;";this.labelAdjust=0;}else{this.labelSeparator=ct.labelSeparator||this.labelSeparator;ct.labelWidth=ct.labelWidth||100;if(typeof ct.labelWidth=='number'){var pad=(typeof ct.labelPad=='number'?ct.labelPad:5);this.labelAdjust=ct.labelWidth+pad;this.labelStyle="width:"+ct.labelWidth+"px;";this.elementStyle="padding-left:"+(ct.labelWidth+pad)+'px';}
if(ct.labelAlign=='top'){this.labelStyle="width:auto;";this.labelAdjust=0;this.elementStyle="padding-left:0;";}}},getLabelStyle:function(s){var ls='',items=[this.labelStyle,s];for(var i=0,len=items.length;i<len;++i){if(items[i]){ls+=items[i];if(ls.substr(-1,1)!=';'){ls+=';'}}}
return ls;},renderItem:function(c,position,target){if(c&&!c.rendered&&(c.isFormField||c.fieldLabel)&&c.inputType!='hidden'){var args=this.getTemplateArgs(c);if(typeof position=='number'){position=target.dom.childNodes[position]||null;}
if(position){this.fieldTpl.insertBefore(position,args);}else{this.fieldTpl.append(target,args);}
c.render('x-form-el-'+c.id);}else{Ext.layout.FormLayout.superclass.renderItem.apply(this,arguments);}},getTemplateArgs:function(field){var noLabelSep=!field.fieldLabel||field.hideLabel;return{id:field.id,label:field.fieldLabel,labelStyle:field.labelStyle||this.labelStyle||'',elementStyle:this.elementStyle||'',labelSeparator:noLabelSep?'':(typeof field.labelSeparator=='undefined'?this.labelSeparator:field.labelSeparator),itemCls:(field.itemCls||this.container.itemCls||'')+(field.hideLabel?' x-hide-label':''),clearCls:field.clearCls||'x-form-clear-left'};},adjustWidthAnchor:function(value,comp){return value-(comp.isFormField||comp.fieldLabel?(comp.hideLabel?0:this.labelAdjust):0);},isValidParent:function(c,target){return true;}});Ext.Container.LAYOUTS['form']=Ext.layout.FormLayout;