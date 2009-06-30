/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.data.DirectProxy=function(config){Ext.apply(this,config);if(typeof this.paramOrder=='string'){this.paramOrder=this.paramOrder.split(/[\s,|]/);}
Ext.data.DirectProxy.superclass.constructor.call(this,config);};Ext.extend(Ext.data.DirectProxy,Ext.data.DataProxy,{paramOrder:undefined,paramsAsHash:true,directFn:undefined,doRequest:function(action,rs,params,reader,callback,scope,options){var args=[];var directFn=this.api[action]||this.directFn;switch(action){case Ext.data.Api.actions.create:args.push(params[reader.meta.root]);break;case Ext.data.Api.actions.read:if(this.paramOrder){for(var i=0,len=this.paramOrder.length;i<len;i++){args.push(params[this.paramOrder[i]]);}}else if(this.paramsAsHash){args.push(params);}
break;case Ext.data.Api.actions.update:args.push(params[reader.meta.idProperty]);args.push(params[reader.meta.root]);break;case Ext.data.Api.actions.destroy:args.push(params[reader.meta.root]);break;}
var trans={params:params||{},callback:callback,scope:scope,arg:options,reader:reader};args.push(this.createCallback(action,rs,trans),this);directFn.apply(window,args);},createCallback:function(action,rs,trans){return function(result,res){if(!res.status){if(action===Ext.data.Api.actions.read){this.fireEvent("loadexception",this,trans,res,null);}
this.fireEvent('exception',this,'remote',action,trans,res,null);trans.callback.call(trans.scope,null,trans.arg,false);return;}
if(action===Ext.data.Api.actions.read){this.onRead(action,trans,result,res);}else{this.onWrite(action,trans,result,res,rs);}}},onRead:function(action,trans,result,res){var records;try{records=trans.reader.readRecords(result);}
catch(ex){this.fireEvent("loadexception",this,trans,res,ex);this.fireEvent('exception',this,'response',action,trans,res,ex);trans.callback.call(trans.scope,null,trans.arg,false);return;}
this.fireEvent("load",this,res,trans.arg);trans.callback.call(trans.scope,records,trans.arg,true);},onWrite:function(action,trans,result,res,rs){this.fireEvent("write",this,action,result,res,rs,trans.arg);trans.callback.call(trans.scope,result,res,true);}});