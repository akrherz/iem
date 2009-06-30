/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.apply(Ext.util.Observable.prototype,function(){function getMethodEvent(method){var e=(this.methodEvents=this.methodEvents||{})[method],returnValue,v,cancel,obj=this;if(!e){this.methodEvents[method]=e={};e.originalFn=this[method];e.methodName=method;e.before=[];e.after=[];function makeCall(fn,scope,args){if(!Ext.isEmpty(v=fn.apply(scope||obj,args))){if(Ext.isObject(v)){returnValue=!Ext.isEmpty(v.returnValue)?v.returnValue:v;cancel=!!v.cancel;}
else
if(v===false){cancel=true;}
else{returnValue=v;}}}
this[method]=function(){var args=Ext.toArray(arguments);returnValue=v=undefined;cancel=false;Ext.each(e.before,function(b){makeCall(b.fn,b.scope,args);if(cancel){return returnValue;}});if(!Ext.isEmpty(v=e.originalFn.apply(obj,args))){returnValue=v;}
Ext.each(e.after,function(a){makeCall(a.fn,a.scope,args);if(cancel){return returnValue;}});return returnValue;};}
return e;}
return{beforeMethod:function(method,fn,scope){getMethodEvent.call(this,method).before.push({fn:fn,scope:scope});},afterMethod:function(method,fn,scope){getMethodEvent.call(this,method).after.push({fn:fn,scope:scope});},removeMethodListener:function(method,fn,scope){var e=getMethodEvent.call(this,method),found=false;Ext.each(e.before,function(b){if(b.fn==fn&&b.scope==scope){b.splice(i,1);found=true;return false;}});if(!found){Ext.each(e.after,function(a){if(a.fn==fn&&a.scope==scope){a.splice(i,1);return false;}});}},relayEvents:function(o,events){var me=this;function createHandler(ename){return function(){return me.fireEvent.apply(me,[ename].concat(Ext.toArray(arguments)));};};Ext.each(events,function(ename){me.events[ename]=me.events[ename]||true;o.on(ename,createHandler(ename),me);});},enableBubble:function(events){var me=this;events=Ext.isArray(events)?events:Ext.toArray(arguments);Ext.each(events,function(ename){ename=ename.toLowerCase();var ce=me.events[ename]||true;if(typeof ce=="boolean"){ce=new Ext.util.Event(me,ename);me.events[ename]=ce;}
ce.bubble=true;});}}}());Ext.util.Observable.capture=function(o,fn,scope){o.fireEvent=o.fireEvent.createInterceptor(fn,scope);};Ext.util.Observable.observeClass=function(c){Ext.apply(c,new Ext.util.Observable());c.prototype.fireEvent=function(){return(c.fireEvent.apply(c,arguments)!==false)&&(Ext.util.Observable.prototype.fireEvent.apply(this,arguments)!==false);};};