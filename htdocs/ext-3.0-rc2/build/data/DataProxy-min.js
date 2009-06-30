/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.data.DataProxy=function(conn){conn=conn||{};this.api=conn.api;this.url=conn.url;this.restful=conn.restful;this.listeners=conn.listeners;this.prettyUrls=conn.prettyUrls;try{Ext.data.Api.prepare(this);}catch(e){if(e instanceof Ext.data.Api.Error){e.toConsole();}}
this.addEvents('exception','beforeload','load','loadexception','beforewrite','write');Ext.data.DataProxy.superclass.constructor.call(this);};Ext.extend(Ext.data.DataProxy,Ext.util.Observable,{restful:false,setApi:function(){if(arguments.length==1){var valid=Ext.data.Api.isValid(arguments[0]);if(valid===true){this.api=arguments[0];}
else{throw new Ext.data.Api.Error('invalid',valid);}}
else if(arguments.length==2){if(!Ext.data.Api.isAction(arguments[0])){throw new Ext.data.Api.Error('invalid',arguments[0]);}
this.api[arguments[0]]=arguments[1];}
Ext.data.Api.prepare(this);},isApiAction:function(action){return(this.api[action])?true:false;},request:function(action,rs,params,reader,callback,scope,options){if(!this.api[action]){throw new Ext.data.DataProxy.Error('action-undefined',action);}
params=params||{};if((action===Ext.data.Api.actions.read)?this.fireEvent("beforeload",this,params):this.fireEvent("beforewrite",this,action,rs,params)!==false){this.doRequest.apply(this,arguments);}
else{callback.call(scope||this,null,options,false);}},load:function(params,reader,callback,scope,arg){this.doRequest(Ext.data.Api.actions.read,null,params,reader,callback,scope,arg);},doRequest:function(action,rs,params,reader,callback,scope,options){this.load(params,reader,callback,scope,options);},buildUrl:function(action,record){record=record||null;var url=(this.api[action])?this.api[action]['url']:this.url;if(!url){throw new Ext.data.Api.Error('invalid-url',action);}
if((this.prettyUrls===true||this.restful===true)&&record instanceof Ext.data.Record&&!record.phantom){url+='/'+record.id;}
return url;},destroy:function(){this.purgeListeners();}});Ext.data.DataProxy.Error=Ext.extend(Ext.Error,{constructor:function(message,arg){this.arg=arg;Ext.Error.call(this,message);},name:'Ext.data.DataProxy'});Ext.apply(Ext.data.DataProxy.Error.prototype,{lang:{'action-undefined':"DataProxy attempted to execute an API-action but found an undefined url / function.  Please review your Proxy url/api-configuration.",'api-invalid':'Recieved an invalid API-configuration.  Please ensure your proxy API-configuration contains only the actions from Ext.data.Api.actions.'}});