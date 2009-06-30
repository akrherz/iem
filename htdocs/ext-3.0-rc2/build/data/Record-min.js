/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.data.Record=function(data,id){this.id=(id||id===0)?id:Ext.data.Record.id(this);this.data=data||{};};Ext.data.Record.create=function(o){var f=Ext.extend(Ext.data.Record,{});var p=f.prototype;p.fields=new Ext.util.MixedCollection(false,function(field){return field.name;});for(var i=0,len=o.length;i<len;i++){p.fields.add(new Ext.data.Field(o[i]));}
f.getField=function(name){return p.fields.get(name);};return f;};Ext.data.Record.PREFIX='ext-record';Ext.data.Record.AUTO_ID=1;Ext.data.Record.EDIT='edit';Ext.data.Record.REJECT='reject';Ext.data.Record.COMMIT='commit';Ext.data.Record.id=function(rec){rec.phantom=true;return[Ext.data.Record.PREFIX,'-',Ext.data.Record.AUTO_ID++].join('');}
Ext.data.Record.prototype={dirty:false,editing:false,error:null,modified:null,phantom:false,join:function(store){this.store=store;},set:function(name,value){if(String(this.data[name])==String(value)){return;}
this.dirty=true;if(!this.modified){this.modified={};}
if(typeof this.modified[name]=='undefined'){this.modified[name]=this.data[name];}
this.data[name]=value;if(!this.editing){this.afterEdit();}},afterEdit:function(){if(this.store){this.store.afterEdit(this);}},afterReject:function(){if(this.store){this.store.afterReject(this);}},afterCommit:function(){if(this.store){this.store.afterCommit(this);}},get:function(name){return this.data[name];},beginEdit:function(){this.editing=true;this.modified=this.modified||{};},cancelEdit:function(){this.editing=false;delete this.modified;},endEdit:function(){this.editing=false;if(this.dirty){this.afterEdit();}},reject:function(silent){var m=this.modified;for(var n in m){if(typeof m[n]!="function"){this.data[n]=m[n];}}
this.dirty=false;delete this.modified;this.editing=false;if(silent!==true){this.afterReject();}},commit:function(silent){this.dirty=false;delete this.modified;this.editing=false;if(silent!==true){this.afterCommit();}},getChanges:function(){var m=this.modified,cs={};for(var n in m){if(m.hasOwnProperty(n)){cs[n]=this.data[n];}}
return cs;},hasError:function(){return this.error!=null;},clearError:function(){this.error=null;},copy:function(newId){return new this.constructor(Ext.apply({},this.data),newId||this.id);},isModified:function(fieldName){return!!(this.modified&&this.modified.hasOwnProperty(fieldName));},isValid:function(){return this.fields.find(function(f){return(f.allowBlank==false&&Ext.isEmpty(this.data[f.name]))?true:false;},this)?false:true;},markDirty:function(){this.dirty=true;if(!this.modified){this.modified={};}
this.fields.each(function(f){this.modified[f.name]=this.data[f.name];},this);}};