/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.data.JsonStore=Ext.extend(Ext.data.Store,{constructor:function(config){Ext.data.JsonStore.superclass.constructor.call(this,Ext.apply(config,{reader:new Ext.data.JsonReader(config)}));}});Ext.reg('jsonstore',Ext.data.JsonStore);