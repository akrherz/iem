/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.Element.addMethods({swallowEvent:function(eventName,preventDefault){var me=this;function fn(e){e.stopPropagation();if(preventDefault){e.preventDefault();}}
if(Ext.isArray(eventName)){Ext.each(eventName,function(e){me.on(e,fn);});return me;}
me.on(eventName,fn);return me;},relayEvent:function(eventName,observable){this.on(eventName,function(e){observable.fireEvent(eventName,e);});},clean:function(forceReclean){var me=this,n=me.dom.firstChild,ni=-1;if(me.isCleaned&&forceReclean!==true){return me;}
while(n){var nx=n.nextSibling;n.nodeType==3&&!/\S/.test(n.nodeValue)?me.dom.removeChild(n):n.nodeIndex=++ni;n=nx;}
me.isCleaned=true;return me;},load:function(){var um=this.getUpdater();um.update.apply(um,arguments);return this;},getUpdater:function(){return this.updateManager||(this.updateManager=new Ext.Updater(this));},update:function(html,loadScripts,callback){html=html||"";if(loadScripts!==true){this.dom.innerHTML=html;if(Ext.isFunction(callback)){callback();}
return this;}
var id=Ext.id(),dom=this.dom;html+='<span id="'+id+'"></span>';Ext.lib.Event.onAvailable(id,function(){var DOC=document,hd=DOC.getElementsByTagName("head")[0],re=/(?:<script([^>]*)?>)((\n|\r|.)*?)(?:<\/script>)/ig,srcRe=/\ssrc=([\'\"])(.*?)\1/i,typeRe=/\stype=([\'\"])(.*?)\1/i,match,attrs,srcMatch,typeMatch,el,s;while(match=re.exec(html)){attrs=match[1];srcMatch=attrs?attrs.match(srcRe):false;if(srcMatch&&srcMatch[2]){s=DOC.createElement("script");s.src=srcMatch[2];typeMatch=attrs.match(typeRe);if(typeMatch&&typeMatch[2]){s.type=typeMatch[2];}
hd.appendChild(s);}else if(match[2]&&match[2].length>0){if(window.execScript){window.execScript(match[2]);}else{window.eval(match[2]);}}}
el=DOC.getElementById(id);if(el){Ext.removeNode(el);}
if(Ext.isFunction(callback)){callback();}});dom.innerHTML=html.replace(/(?:<script.*?>)((\n|\r|.)*?)(?:<\/script>)/ig,"");return this;},createProxy:function(config,renderTo,matchBox){config=Ext.isObject(config)?config:{tag:"div",cls:config};var me=this,proxy=renderTo?Ext.DomHelper.append(renderTo,config,true):Ext.DomHelper.insertBefore(me.dom,config,true);if(matchBox&&me.setBox&&me.getBox){proxy.setBox(me.getBox());}
return proxy;}});Ext.Element.prototype.getUpdateManager=Ext.Element.prototype.getUpdater;Ext.Element.uncache=function(el){for(var i=0,a=arguments,len=a.length;i<len;i++){if(a[i]){delete Ext.Element.cache[a[i].id||a[i]];}}};