/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.handleError=function(e){throw e;};Ext.Error=function(message){this.message=(this.lang[message])?this.lang[message]:message;}
Ext.Error.prototype=new Error();Ext.apply(Ext.Error.prototype,{lang:{},name:'Ext.Error',getName:function(){return this.name;},getMessage:function(){return this.message;},toJson:function(){return Ext.encode(this);}});