/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.data.JsonReader=function(meta,recordType){meta=meta||{};Ext.applyIf(meta,{idProperty:'id',successProperty:'success',totalProperty:'total'});Ext.data.JsonReader.superclass.constructor.call(this,meta,recordType||meta.fields);};Ext.extend(Ext.data.JsonReader,Ext.data.DataReader,{read:function(response){var json=response.responseText;var o=Ext.decode(json);if(!o){throw{message:"JsonReader.read: Json object not found"};}
return this.readRecords(o);},onMetaChange:function(meta,recordType,o){},simpleAccess:function(obj,subsc){return obj[subsc];},getJsonAccessor:function(){var re=/[\[\.]/;return function(expr){try{return(re.test(expr))?new Function("obj","return obj."+expr):function(obj){return obj[expr];};}catch(e){}
return Ext.emptyFn;};}(),readRecords:function(o){this.jsonData=o;if(o.metaData){delete this.ef;this.meta=o.metaData;this.recordType=Ext.data.Record.create(o.metaData.fields);this.onMetaChange(this.meta,this.recordType,o);}
var s=this.meta,Record=this.recordType,f=Record.prototype.fields,fi=f.items,fl=f.length;if(!this.ef){this.ef=this.buildExtractors();}
var root=this.getRoot(o),c=root.length,totalRecords=c,success=true;if(s.totalProperty){var v=parseInt(this.getTotal(o),10);if(!isNaN(v)){totalRecords=v;}}
if(s.successProperty){var v=this.getSuccess(o);if(v===false||v==='false'){success=false;}}
var records=[];for(var i=0;i<c;i++){var n=root[i];var record=new Record(this.extractValues(n,fi,fl),this.getId(n));record.json=n;records[i]=record;}
return{success:success,records:records,totalRecords:totalRecords};},buildExtractors:function(){var s=this.meta,Record=this.recordType,f=Record.prototype.fields,fi=f.items,fl=f.length;if(s.totalProperty){this.getTotal=this.getJsonAccessor(s.totalProperty);}
if(s.successProperty){this.getSuccess=this.getJsonAccessor(s.successProperty);}
this.getRoot=s.root?this.getJsonAccessor(s.root):function(p){return p;};if(s.id||s.idProperty){var g=this.getJsonAccessor(s.id||s.idProperty);this.getId=function(rec){var r=g(rec);return(r===undefined||r==="")?null:r;};}else{this.getId=function(){return null;};}
var ef=[];for(var i=0;i<fl;i++){f=fi[i];var map=(f.mapping!==undefined&&f.mapping!==null)?f.mapping:f.name;ef.push(this.getJsonAccessor(map));}
return ef;},extractValues:function(data,items,len){var f,values={};for(var j=0;j<len;j++){f=items[j];var v=this.ef[j](data);values[f.name]=f.convert((v!==undefined)?v:f.defaultValue,data);}
return values;},readResponse:function(action,response){var o=(typeof(response.responseText)!=undefined)?Ext.decode(response.responseText):response;if(!o){throw new Ext.data.JsonReader.Error('response');}
if(Ext.isEmpty(o[this.meta.successProperty])){throw new Ext.data.JsonReader.Error('successProperty-response',this.meta.successProperty);}
if((action===Ext.data.Api.actions.create||action===Ext.data.Api.actions.update)){if(Ext.isEmpty(o[this.meta.root])){throw new Ext.data.JsonReader.Error('root-emtpy',this.meta.root);}
else if(typeof(o[this.meta.root])===undefined){throw new Ext.data.JsonReader.Error('root-undefined-response',this.meta.root);}}
if(!this.ef){this.ef=this.buildExtractors();}
return o;}});Ext.data.JsonReader.Error=Ext.extend(Ext.Error,{constructor:function(message,arg){this.arg=arg;Ext.Error.call(this,message);},name:'Ext.data.JsonReader'});Ext.apply(Ext.data.JsonReader.Error.prototype,{lang:{'response':"An error occurred while json-decoding your server response",'successProperty-response':'Could not locate your "successProperty" in your server response.  Please review your JsonReader config to ensure the config-property "successProperty" matches the property in your server-response.  See the JsonReader docs.','root-undefined-response':'Could not locate your "root" property in your server response.  Please review your JsonReader config to ensure the config-property "root" matches the property your server-response.  See the JsonReader docs.','root-undefined-config':'Your JsonReader was configured without a "root" property.  Please review your JsonReader config and make sure to define the root property.  See the JsonReader docs.','idProperty-undefined':'Your JsonReader was configured without an "idProperty"  Please review your JsonReader configuration and ensure the "idProperty" is set (eg: "id").  See the JsonReader docs.','root-emtpy':'Data was expected to be returned by the server in the "root" property of the response.  Please review your JsonReader configuration to ensure the "root" property matches that returned in the server-response.  See JsonReader docs.'}});