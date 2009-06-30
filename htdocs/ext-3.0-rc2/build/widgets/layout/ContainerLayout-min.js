/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.layout.ContainerLayout=function(config){Ext.apply(this,config);};Ext.layout.ContainerLayout.prototype={monitorResize:false,activeItem:null,layout:function(){var target=this.container.getLayoutTarget();this.onLayout(this.container,target);this.container.fireEvent('afterlayout',this.container,this);},onLayout:function(ct,target){this.renderAll(ct,target);},isValidParent:function(c,target){return target&&c.getDomPositionEl().dom.parentNode==(target.dom||target);},renderAll:function(ct,target){var items=ct.items.items;for(var i=0,len=items.length;i<len;i++){var c=items[i];if(c&&(!c.rendered||!this.isValidParent(c,target))){this.renderItem(c,i,target);}}},renderItem:function(c,position,target){if(c&&!c.rendered){c.render(target,position);this.configureItem(c,position);}else if(c&&!this.isValidParent(c,target)){if(typeof position=='number'){position=target.dom.childNodes[position];}
target.dom.insertBefore(c.getDomPositionEl().dom,position||null);c.container=target;this.configureItem(c,position);}},configureItem:function(c,position){if(this.extraCls){var t=c.getPositionEl?c.getPositionEl():c;t.addClass(this.extraCls);}
if(this.renderHidden&&c!=this.activeItem){c.hide();}
if(position!==undefined&&c.doLayout){c.doLayout(false,true);}},onResize:function(){if(this.container.collapsed){return;}
var b=this.container.bufferResize;if(b){if(!this.resizeTask){this.resizeTask=new Ext.util.DelayedTask(this.layout,this);this.resizeBuffer=typeof b=='number'?b:100;}
this.resizeTask.delay(this.resizeBuffer);}else{this.layout();}},setContainer:function(ct){if(this.monitorResize&&ct!=this.container){if(this.container){this.container.un('resize',this.onResize,this);}
if(ct){ct.on({scope:this,resize:this.onResize,bodyresize:this.onResize});}}
this.container=ct;},parseMargins:function(v){if(typeof v=='number'){v=v.toString();}
var ms=v.split(' ');var len=ms.length;if(len==1){ms[1]=ms[0];ms[2]=ms[0];ms[3]=ms[0];}
if(len==2){ms[2]=ms[0];ms[3]=ms[1];}
if(len==3){ms[3]=ms[1];}
return{top:parseInt(ms[0],10)||0,right:parseInt(ms[1],10)||0,bottom:parseInt(ms[2],10)||0,left:parseInt(ms[3],10)||0};},fieldTpl:(function(){var t=new Ext.Template('<div class="x-form-item {itemCls}" tabIndex="-1">','<label for="{id}" style="{labelStyle}" class="x-form-item-label">{label}{labelSeparator}</label>','<div class="x-form-element" id="x-form-el-{id}" style="{elementStyle}">','</div><div class="{clearCls}"></div>','</div>');t.disableFormats=true;return t.compile();})(),destroy:Ext.emptyFn};Ext.Container.LAYOUTS['auto']=Ext.layout.ContainerLayout;