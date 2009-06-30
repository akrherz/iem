/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.util.Format=function(){var trimRe=/^\s+|\s+$/g;return{ellipsis:function(value,len,word){if(value&&value.length>len){if(word){var vs=value.substr(0,len-2);var index=Math.max(vs.lastIndexOf(' '),vs.lastIndexOf('.'),vs.lastIndexOf('!'),vs.lastIndexOf('?'));if(index==-1||index<(len-15)){return value.substr(0,len-3)+"...";}else{return vs.substr(0,index)+"...";}}else{return value.substr(0,len-3)+"...";}}
return value;},undef:function(value){return value!==undefined?value:"";},defaultValue:function(value,defaultValue){return value!==undefined&&value!==''?value:defaultValue;},htmlEncode:function(value){return!value?value:String(value).replace(/&/g,"&amp;").replace(/>/g,"&gt;").replace(/</g,"&lt;").replace(/"/g,"&quot;");},htmlDecode:function(value){return!value?value:String(value).replace(/&gt;/g,">").replace(/&lt;/g,"<").replace(/&quot;/g,'"').replace(/&amp;/g,"&");},trim:function(value){return String(value).replace(trimRe,"");},substr:function(value,start,length){return String(value).substr(start,length);},lowercase:function(value){return String(value).toLowerCase();},uppercase:function(value){return String(value).toUpperCase();},capitalize:function(value){return!value?value:value.charAt(0).toUpperCase()+value.substr(1).toLowerCase();},call:function(value,fn){if(arguments.length>2){var args=Array.prototype.slice.call(arguments,2);args.unshift(value);return eval(fn).apply(window,args);}else{return eval(fn).call(window,value);}},usMoney:function(v){v=(Math.round((v-0)*100))/100;v=(v==Math.floor(v))?v+".00":((v*10==Math.floor(v*10))?v+"0":v);v=String(v);var ps=v.split('.');var whole=ps[0];var sub=ps[1]?'.'+ps[1]:'.00';var r=/(\d+)(\d{3})/;while(r.test(whole)){whole=whole.replace(r,'$1'+','+'$2');}
v=whole+sub;if(v.charAt(0)=='-'){return'-$'+v.substr(1);}
return"$"+v;},date:function(v,format){if(!v){return"";}
if(!Ext.isDate(v)){v=new Date(Date.parse(v));}
return v.dateFormat(format||"m/d/Y");},dateRenderer:function(format){return function(v){return Ext.util.Format.date(v,format);};},stripTagsRE:/<\/?[^>]+>/gi,stripTags:function(v){return!v?v:String(v).replace(this.stripTagsRE,"");},stripScriptsRe:/(?:<script.*?>)((\n|\r|.)*?)(?:<\/script>)/ig,stripScripts:function(v){return!v?v:String(v).replace(this.stripScriptsRe,"");},fileSize:function(size){if(size<1024){return size+" bytes";}else if(size<1048576){return(Math.round(((size*10)/1024))/10)+" KB";}else{return(Math.round(((size*10)/1048576))/10)+" MB";}},math:function(){var fns={};return function(v,a){if(!fns[a]){fns[a]=new Function('v','return v '+a+';');}
return fns[a](v);}}(),round:function(value,precision){var result=Number(value);if(typeof precision=='number'){precision=Math.pow(10,precision);result=Math.round(value*precision)/precision;}
return result;},number:function(v,format){if(!format){return v;}
v=Ext.num(v,NaN);if(isNaN(v)){return'';}
var comma=',',dec='.',i18n=false,neg=v<0;v=Math.abs(v);if(format.substr(format.length-2)=='/i'){format=format.substr(0,format.length-2);i18n=true;comma='.';dec=',';}
var hasComma=format.indexOf(comma)!=-1,psplit=(i18n?format.replace(/[^\d\,]/g,''):format.replace(/[^\d\.]/g,'')).split(dec);if(1<psplit.length){v=v.toFixed(psplit[1].length);}else if(2<psplit.length){throw('NumberFormatException: invalid format, formats should have no more than 1 period: '+format);}else{v=v.toFixed(0);}
var fnum=v.toString();if(hasComma){psplit=fnum.split('.');var cnum=psplit[0],parr=[],j=cnum.length,m=Math.floor(j/3),n=cnum.length%3||3;for(var i=0;i<j;i+=n){if(i!=0){n=3;}
parr[parr.length]=cnum.substr(i,n);m-=1;}
fnum=parr.join(comma);if(psplit[1]){fnum+=dec+psplit[1];}}
return(neg?'-':'')+format.replace(/[\d,?\.?]+/,fnum);},numberRenderer:function(format){return function(v){return Ext.util.Format.number(v,format);};},plural:function(v,s,p){return v+' '+(v==1?s:(p?p:s+'s'));},nl2br:function(v){return v===undefined||v===null?'':v.replace(/\n/g,'<br/>');}}}();