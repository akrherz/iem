/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.StoreMgr=Ext.apply(new Ext.util.MixedCollection(),{register:function(){for(var i=0,s;s=arguments[i];i++){this.add(s);}},unregister:function(){for(var i=0,s;s=arguments[i];i++){this.remove(this.lookup(s));}},lookup:function(id){if(Ext.isArray(id)){var fields=['field1'],expand=!Ext.isArray(id[0]);if(!expand){for(var i=2,len=id[0].length;i<=len;++i){fields.push('field'+i);}}
return new Ext.data.ArrayStore({fields:fields,data:id,expandData:expand,autoDestroy:true,autoCreated:true});}
return Ext.isObject(id)?(id.events?id:Ext.create(id,'store')):this.get(id);},getKey:function(o){return o.storeId;}});