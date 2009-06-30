/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.menu.DateMenu=Ext.extend(Ext.menu.Menu,{enableScrolling:false,cls:'x-date-menu',initComponent:function(){this.on('beforeshow',this.onBeforeShow,this);if(this.strict=(Ext.isIE7&&Ext.isStrict)){this.on('show',this.onShow,this,{single:true,delay:20});}
Ext.apply(this,{plain:true,showSeparator:false,items:this.picker=new Ext.DatePicker(Ext.apply({internalRender:this.strict||!Ext.isIE,ctCls:'x-menu-date-item'},this.initialConfig))});this.picker.purgeListeners();Ext.menu.DateMenu.superclass.initComponent.call(this);this.relayEvents(this.picker,["select"]);},onClick:function(){if(this.hideOnClick){this.hide(true);}},onBeforeShow:function(){if(this.picker){this.picker.hideMonthPicker(true);}},onShow:function(){var el=this.picker.getEl();el.setWidth(el.getWidth());}});Ext.reg('datemenu',Ext.menu.DateMenu);