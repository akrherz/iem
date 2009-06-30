/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.data.Api=(function(){var validActions={};return{actions:{create:'create',read:'read',update:'update',destroy:'destroy'},restActions:{create:'POST',read:'GET',update:'PUT',destroy:'DELETE'},isAction:function(action){return(Ext.data.Api.actions[action])?true:false;},getVerb:function(name){if(validActions[name]){return validActions[name];}
for(var verb in this.actions){if(this.actions[verb]===name){validActions[name]=verb;break;}}
return(validActions[name]!==undefined)?validActions[name]:null;},isValid:function(api){var invalid=[];var crud=this.actions;for(var action in api){if(!(action in crud)){invalid.push(action);}}
return(!invalid.length)?true:invalid;},hasUniqueUrl:function(proxy,verb){var url=(proxy.api[verb])?proxy.api[verb].url:null;var unique=true;for(var action in proxy.api){if((unique=(action===verb)?true:(proxy.api[action].url!=url)?true:false)===false){break;}}
return unique;},prepare:function(proxy){if(!proxy.api){proxy.api={};}
for(var verb in this.actions){var action=this.actions[verb];proxy.api[action]=proxy.api[action]||proxy.url||proxy.directFn;if(typeof(proxy.api[action])=='string'){proxy.api[action]={url:proxy.api[action]};}}},restify:function(proxy){proxy.restful=true;for(var verb in this.restActions){proxy.api[this.actions[verb]].method=this.restActions[verb];}}};})();Ext.data.Api.Error=Ext.extend(Ext.Error,{constructor:function(message,arg){this.arg=arg;Ext.Error.call(this,message);},name:'Ext.data.Api'});Ext.apply(Ext.data.Api.Error.prototype,{lang:{'action-url-undefined':'No fallback url defined for this action.  When defining a DataProxy api, please be sure to define an url for each CRUD action in Ext.data.Api.actions or define a default url in addition to your api-configuration.','invalid':'received an invalid API-configuration.  Please ensure your proxy API-configuration contains only the actions defined in Ext.data.Api.actions','invalid-url':'Invalid url.  Please review your proxy configuration.','execute':'Attempted to execute an unknown action.  Valid API actions are defined in Ext.data.Api.actions"'}});