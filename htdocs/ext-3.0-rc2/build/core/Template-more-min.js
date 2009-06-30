/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.apply(Ext.Template.prototype,{applyTemplate:function(values){var me=this,useF=me.disableFormats!==true,fm=Ext.util.Format,tpl=me;if(me.compiled){return me.compiled(values);}
function fn(m,name,format,args){if(format&&useF){if(format.substr(0,5)=="this."){return tpl.call(format.substr(5),values[name],values);}else{if(args){var re=/^\s*['"](.*)["']\s*$/;args=args.split(',');for(var i=0,len=args.length;i<len;i++){args[i]=args[i].replace(re,"$1");}
args=[values[name]].concat(args);}else{args=[values[name]];}
return fm[format].apply(fm,args);}}else{return values[name]!==undefined?values[name]:"";}};return me.html.replace(me.re,fn);},disableFormats:false,re:/\{([\w-]+)(?:\:([\w\.]*)(?:\((.*?)?\))?)?\}/g,compile:function(){var me=this,fm=Ext.util.Format,useF=me.disableFormats!==true,sep=Ext.isGecko?"+":",",body;function fn(m,name,format,args){if(format&&useF){args=args?','+args:"";if(format.substr(0,5)!="this."){format="fm."+format+'(';}else{format='this.call("'+format.substr(5)+'", ';args=", values";}}else{args='';format="(values['"+name+"'] == undefined ? '' : ";}
return"'"+sep+format+"values['"+name+"']"+args+")"+sep+"'";}
if(Ext.isGecko){body="this.compiled = function(values){ return '"+
me.html.replace(/\\/g,'\\\\').replace(/(\r\n|\n)/g,'\\n').replace(/'/g,"\\'").replace(this.re,fn)+"';};";}else{body=["this.compiled = function(values){ return ['"];body.push(me.html.replace(/\\/g,'\\\\').replace(/(\r\n|\n)/g,'\\n').replace(/'/g,"\\'").replace(this.re,fn));body.push("'].join('');};");body=body.join('');}
eval(body);return me;},call:function(fnName,value,allValues){return this[fnName](value,allValues);}});Ext.Template.prototype.apply=Ext.Template.prototype.applyTemplate;