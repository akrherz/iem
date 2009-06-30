/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.data.DirectStore=function(c){c.batchTransactions=false;Ext.data.DirectStore.superclass.constructor.call(this,Ext.apply(c,{proxy:(typeof(c.proxy)=='undefined')?new Ext.data.DirectProxy(Ext.copyTo({},c,'paramOrder,paramsAsHash,directFn,api')):c.proxy,reader:(typeof(c.reader)=='undefined'&&typeof(c.fields)=='object')?new Ext.data.JsonReader(Ext.copyTo({},c,'totalProperty,root,idProperty'),c.fields):c.reader}));};Ext.extend(Ext.data.DirectStore,Ext.data.Store,{});Ext.reg('directstore',Ext.data.DirectStore);