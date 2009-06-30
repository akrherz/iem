/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.data.HttpProxy=function(conn){Ext.data.HttpProxy.superclass.constructor.call(this,conn);this.conn=conn;this.conn.url=null;this.useAjax=!conn||!conn.events;var actions=Ext.data.Api.actions
this.activeRequest={};for(var verb in actions){this.activeRequest[actions[verb]]=undefined;}};Ext.extend(Ext.data.HttpProxy,Ext.data.DataProxy,{getConnection:function(){return this.useAjax?Ext.Ajax:this.conn;},setUrl:function(url,makePermanent){this.conn.url=url;if(makePermanent===true){this.url=url;Ext.data.Api.prepare(this);}},doRequest:function(action,rs,params,reader,cb,scope,arg){var o={params:params||{},method:(this.api[action])?this.api[action]['method']:undefined,request:{callback:cb,scope:scope,arg:arg},reader:reader,callback:this.createCallback(action,rs),scope:this};if(this.conn.url===null){this.conn.url=this.buildUrl(action,rs);}
else if(this.restful===true&&rs instanceof Ext.data.Record&&!rs.phantom){this.conn.url+='/'+rs.id;}
if(this.useAjax){Ext.applyIf(o,this.conn);if(this.activeRequest[action]){}
this.activeRequest[action]=Ext.Ajax.request(o);}else{this.conn.request(o);}
this.conn.url=null;},createCallback:function(action,rs){return function(o,success,response){this.activeRequest[action]=undefined;if(!success){if(action===Ext.data.Api.actions.read){this.fireEvent("loadexception",this,o,response);}
this.fireEvent('exception',this,'response',action,o,response);o.request.callback.call(o.request.scope,null,o.request.arg,false);return;}
if(action===Ext.data.Api.actions.read){this.onRead(action,o,response);}else{this.onWrite(action,o,response,rs);}}},onRead:function(action,o,response){var result;try{result=o.reader.read(response);}catch(e){this.fireEvent("loadexception",this,o,response,e);this.fireEvent('exception',this,'response',action,o,response,e);o.request.callback.call(o.request.scope,null,o.request.arg,false);return;}
if(result.success===false){this.fireEvent('loadexception',this,o,response);var res=o.reader.readResponse(action,response);this.fireEvent('exception',this,'remote',action,o,res,null);}
else{this.fireEvent("load",this,o,o.request.arg);}
o.request.callback.call(o.request.scope,result,o.request.arg,result.success);},onWrite:function(action,o,response,rs){var reader=o.reader;var res;try{res=reader.readResponse(action,response);}catch(e){this.fireEvent('exception',this,'response',action,o,response,e);o.request.callback.call(o.request.scope,null,o.request.arg,false);return;}
if(res[reader.meta.successProperty]===false){this.fireEvent('exception',this,'remote',action,o,res,rs);}else{this.fireEvent("write",this,action,res[reader.meta.root],res,rs,o.request.arg);}
o.request.callback.call(o.request.scope,res[reader.meta.root],res,res[reader.meta.successProperty]);},destroy:function(){if(!this.useAjax){this.conn.abort();}else if(this.activeRequest){var actions=Ext.data.Api.actions;for(var verb in actions){if(this.activeRequest[actions[verb]]){Ext.Ajax.abort(this.activeRequest[actions[verb]]);}}}
Ext.data.HttpProxy.superclass.destroy.call(this);}});