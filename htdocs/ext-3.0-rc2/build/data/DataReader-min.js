/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.data.DataReader=function(meta,recordType){this.meta=meta;this.recordType=Ext.isArray(recordType)?Ext.data.Record.create(recordType):recordType;};Ext.data.DataReader.prototype={realize:function(rs,data){if(Ext.isArray(rs)){for(var i=rs.length-1;i>=0;i--){if(Ext.isArray(data)){this.realize(rs.splice(i,1).shift(),data.splice(i,1).shift());}
else{this.realize(rs.splice(i,1).shift(),data);}}}
else{if(Ext.isArray(data)&&data.length==1){data=data.shift();}
if(!this.isData(data)){rs.commit();throw new Ext.data.DataReader.Error('realize',rs);}
var values=this.extractValues(data,rs.fields.items,rs.fields.items.length);rs.phantom=false;rs._phid=rs.id;rs.id=data[this.meta.idProperty];rs.data=values;rs.commit();}},update:function(rs,data){if(Ext.isArray(rs)){for(var i=rs.length-1;i>=0;i--){if(Ext.isArray(data)){this.update(rs.splice(i,1).shift(),data.splice(i,1).shift());}
else{this.update(rs.splice(i,1).shift(),data);}}}
else{if(Ext.isArray(data)&&data.length==1){data=data.shift();}
if(!this.isData(data)){rs.commit();throw new Ext.data.DataReader.Error('update',rs);}
rs.data=this.extractValues(Ext.apply(rs.data,data),rs.fields.items,rs.fields.items.length);rs.commit();}},isData:function(data){return(data&&typeof(data)=='object'&&!Ext.isEmpty(data[this.meta.idProperty]))?true:false}};Ext.data.DataReader.Error=Ext.extend(Ext.Error,{constructor:function(message,arg){this.arg=arg;Ext.Error.call(this,message);},name:'Ext.data.DataReader'});Ext.apply(Ext.data.DataReader.Error.prototype,{lang:{'update':"#update received invalid data from server.  Please see docs for DataReader#update and review your DataReader configuration.",'realize':"#realize was called with invalid remote-data.  Please see the docs for DataReader#realize and review your DataReader configuration.",'invalid-response':"#readResponse received an invalid response from the server."}});