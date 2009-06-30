/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.data.ArrayStore=Ext.extend(Ext.data.Store,{constructor:function(config){Ext.data.ArrayStore.superclass.constructor.call(this,Ext.apply(config,{reader:new Ext.data.ArrayReader(config)}));},loadData:function(data,append){if(this.expandData===true){var r=[];for(var i=0,len=data.length;i<len;i++){r[r.length]=[data[i]];}
data=r;}
Ext.data.ArrayStore.superclass.loadData.call(this,data,append);}});Ext.reg('arraystore',Ext.data.ArrayStore);Ext.data.SimpleStore=Ext.data.ArrayStore;Ext.reg('simplestore',Ext.data.SimpleStore);