/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.menu.ColorMenu=Ext.extend(Ext.menu.Menu,{enableScrolling:false,initComponent:function(){Ext.apply(this,{plain:true,showSeparator:false,items:this.palette=new Ext.ColorPalette(this.initialConfig)});this.palette.purgeListeners();Ext.menu.ColorMenu.superclass.initComponent.call(this);this.relayEvents(this.palette,['select']);},onClick:function(){this.hide(true);}});Ext.reg('colormenu',Ext.menu.ColorMenu);