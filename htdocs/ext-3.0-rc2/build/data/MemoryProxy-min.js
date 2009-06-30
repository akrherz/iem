/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.data.MemoryProxy=function(data){var api={};api[Ext.data.Api.actions.read]=true;Ext.data.MemoryProxy.superclass.constructor.call(this,{api:api});this.data=data;};Ext.extend(Ext.data.MemoryProxy,Ext.data.DataProxy,{doRequest:function(action,rs,params,reader,callback,scope,arg){params=params||{};var result;try{result=reader.readRecords(this.data);}catch(e){this.fireEvent("loadexception",this,null,arg,e);this.fireEvent('exception',this,'response',action,arg,null,e);callback.call(scope,null,arg,false);return;}
callback.call(scope,result,arg,true);}});