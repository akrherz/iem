/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.direct.Provider=Ext.extend(Ext.util.Observable,{priority:1,constructor:function(config){Ext.apply(this,config);this.addEvents('connect','disconnect','data','exception');Ext.direct.Provider.superclass.constructor.call(this,config);},isConnected:function(){return false;},connect:Ext.emptyFn,disconnect:Ext.emptyFn});