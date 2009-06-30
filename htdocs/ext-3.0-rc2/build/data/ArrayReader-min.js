/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.data.ArrayReader=Ext.extend(Ext.data.JsonReader,{readRecords:function(o){this.arrayData=o;var s=this.meta;var sid=s?Ext.num(s.idIndex,s.id):null;var recordType=this.recordType,fields=recordType.prototype.fields;var records=[];if(!this.getRoot){this.getRoot=s.root?this.getJsonAccessor(s.root):function(p){return p;};if(s.totalProperty){this.getTotal=this.getJsonAccessor(s.totalProperty);}}
var root=this.getRoot(o);for(var i=0;i<root.length;i++){var n=root[i];var values={};var id=((sid||sid===0)&&n[sid]!==undefined&&n[sid]!==""?n[sid]:null);for(var j=0,jlen=fields.length;j<jlen;j++){var f=fields.items[j];var k=f.mapping!==undefined&&f.mapping!==null?f.mapping:j;var v=n[k]!==undefined?n[k]:f.defaultValue;v=f.convert(v,n);values[f.name]=v;}
var record=new recordType(values,id);record.json=n;records[records.length]=record;}
var totalRecords=records.length;if(s.totalProperty){var v=parseInt(this.getTotal(o),10);if(!isNaN(v)){totalRecords=v;}}
return{records:records,totalRecords:totalRecords};}});