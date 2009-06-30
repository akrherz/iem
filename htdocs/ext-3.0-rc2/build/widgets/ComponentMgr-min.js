/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.ComponentMgr=function(){var all=new Ext.util.MixedCollection();var types={};var ptypes={};return{register:function(c){all.add(c);},unregister:function(c){all.remove(c);},get:function(id){return all.get(id);},onAvailable:function(id,fn,scope){all.on("add",function(index,o){if(o.id==id){fn.call(scope||o,o);all.un("add",fn,scope);}});},all:all,registerType:function(xtype,cls){types[xtype]=cls;cls.xtype=xtype;},create:function(config,defaultType){return config.render?config:new types[config.xtype||defaultType](config);},registerPlugin:function(ptype,cls){ptypes[ptype]=cls;cls.ptype=ptype;},createPlugin:function(config,defaultType){return new ptypes[config.ptype||defaultType](config);}};}();Ext.reg=Ext.ComponentMgr.registerType;Ext.preg=Ext.ComponentMgr.registerPlugin;Ext.create=Ext.ComponentMgr.create;