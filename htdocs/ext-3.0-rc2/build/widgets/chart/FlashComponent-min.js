/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.FlashComponent=Ext.extend(Ext.BoxComponent,{flashVersion:'9.0.45',backgroundColor:'#ffffff',wmode:'opaque',url:undefined,swfId:undefined,swfWidth:'100%',swfHeight:'100%',expressInstall:false,initComponent:function(){Ext.FlashComponent.superclass.initComponent.call(this);this.addEvents('initialize');},onRender:function(){Ext.FlashComponent.superclass.onRender.apply(this,arguments);var swfId=this.getSwfId();var swf=new deconcept.SWFObject(this.url,swfId,this.swfWidth,this.swfHeight,this.flashVersion,this.backgroundColor);if(this.expressInstall){swf.useExpressInstall(this.expressInstall);}
swf.addParam("allowScriptAccess","always");if(this.wmode!==undefined){swf.addParam("wmode",this.wmode);}
swf.addVariable("allowedDomain",document.location.hostname);swf.addVariable("elementID",this.getId());swf.addVariable("eventHandler","Ext.FlashEventProxy.onEvent");var r=swf.write(this.el.dom);if(r){this.swf=Ext.getDom(swfId);}},getSwfId:function(){return this.swfId||(this.swfId="extswf"+(++Ext.Component.AUTO_ID));},getId:function(){return this.id||(this.id="extflashcmp"+(++Ext.Component.AUTO_ID));},onFlashEvent:function(e){switch(e.type){case"swfReady":this.initSwf();return;case"log":return;}
e.component=this;this.fireEvent(e.type.toLowerCase().replace(/event$/,''),e);},initSwf:function(){this.onSwfReady(!!this.isInitialized);this.isInitialized=true;this.fireEvent('initialize',this);},beforeDestroy:function(){if(Ext.isIE&&this.rendered){var el=this.el.child('object');if(el){el=el.dom;for(var prop in el){if(Ext.isFunction(el[prop])){el[prop]=Ext.emptyFn;}}}}
Ext.FlashComponent.superclass.beforeDestroy.call(this);},onSwfReady:Ext.emptyFn});Ext.reg('flash',Ext.FlashComponent);