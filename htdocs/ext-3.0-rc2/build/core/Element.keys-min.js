/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.Element.addMethods({addKeyListener:function(key,fn,scope){var config;if(typeof key!="object"||Ext.isArray(key)){config={key:key,fn:fn,scope:scope};}else{config={key:key.key,shift:key.shift,ctrl:key.ctrl,alt:key.alt,fn:fn,scope:scope};}
return new Ext.KeyMap(this,config);},addKeyMap:function(config){return new Ext.KeyMap(this,config);}});