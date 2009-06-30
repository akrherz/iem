/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.apply(Ext.DomHelper,function(){var pub,afterbegin="afterbegin",afterend="afterend",beforebegin="beforebegin",beforeend="beforeend";function doInsert(el,o,returnElement,pos,sibling,append){el=Ext.getDom(el);var newNode;if(pub.useDom){newNode=createDom(o,null);if(append){el.appendChild(newNode);}else{(sibling=="firstChild"?el:el.parentNode).insertBefore(newNode,el[sibling]||el);}}else{newNode=Ext.DomHelper.insertHtml(pos,el,Ext.DomHelper.createHtml(o));}
return returnElement?Ext.get(newNode,true):newNode;}
function createDom(o,parentNode){var el,doc=document,useSet,attr,val,cn;if(Ext.isArray(o)){el=doc.createDocumentFragment();Ext.each(o,function(v){createDom(v,el);});}else if(typeof o=="string"){el=doc.createTextNode(o);}else{el=doc.createElement(o.tag||'div');useSet=!!el.setAttribute;for(attr in o){val=o[attr];if(["tag","children","cn","html","style"].indexOf(attr)==-1||!Ext.isFunction(val)){if(attr=="cls"){el.className=val;}else{useSet?el.setAttribute(attr,val):el[attr]=val;}}}
pub.applyStyles(el,o.style);if(cn=o.children||o.cn){createDom(cn,el);}else if(o.html){el.innerHTML=o.html;}}
if(parentNode){parentNode.appendChild(el);}
return el;};pub={createTemplate:function(o){var html=Ext.DomHelper.createHtml(o);return new Ext.Template(html);},useDom:false,applyStyles:function(el,styles){if(styles){var i=0,len,style;el=Ext.fly(el);if(Ext.isFunction(styles)){styles=styles.call();}
if(typeof styles=="string"){styles=styles.trim().split(/\s*(?::|;)\s*/);for(len=styles.length;i<len;){el.setStyle(styles[i++],styles[i++]);}}else if(Ext.isObject(styles)){el.setStyle(styles);}}},insertBefore:function(el,o,returnElement){return doInsert(el,o,returnElement,beforebegin);},insertAfter:function(el,o,returnElement){return doInsert(el,o,returnElement,afterend,"nextSibling");},insertFirst:function(el,o,returnElement){return doInsert(el,o,returnElement,afterbegin,"firstChild");},append:function(el,o,returnElement){return doInsert(el,o,returnElement,beforeend,"",true);},createDom:createDom}
return pub;}());