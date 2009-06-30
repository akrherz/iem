/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.util.DelayedTask=function(fn,scope,args){var me=this,id,call=function(){clearInterval(id);id=null;fn.apply(scope,args||[]);};me.delay=function(delay,newFn,newScope,newArgs){me.cancel();fn=newFn||fn;scope=newScope||scope;args=newArgs||args;id=setInterval(call,delay);};me.cancel=function(){if(id){clearInterval(id);id=null;}};};