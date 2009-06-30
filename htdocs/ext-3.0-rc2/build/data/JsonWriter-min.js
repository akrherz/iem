/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.data.JsonWriter=Ext.extend(Ext.data.DataWriter,{returnJson:true,render:function(action,rs,params,data){Ext.apply(params,data);if(this.returnJson){if(Ext.isArray(rs)&&data[this.meta.idProperty]){params[this.meta.idProperty]=Ext.encode(params[this.meta.idProperty]);}
params[this.meta.root]=Ext.encode(params[this.meta.root]);}},createRecord:function(rec){return this.toHash(rec);},updateRecord:function(rec){return this.toHash(rec);},destroyRecord:function(rec){return rec.id}});