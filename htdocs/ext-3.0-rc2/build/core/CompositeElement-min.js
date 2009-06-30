/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.CompositeElement=function(els,root){this.elements=[];this.add(els,root);};Ext.extend(Ext.CompositeElement,Ext.CompositeElementLite,{invoke:function(fn,args){Ext.each(this.elements,function(e){Ext.Element.prototype[fn].apply(e,args);});return this;},add:function(els,root){if(!els)return this;if(typeof els=="string"){els=Ext.Element.selectorFunction(els,root);}
var yels=this.elements;Ext.each(els,function(e){yels.push(Ext.get(e));});return this;},item:function(index){return this.elements[index]||null;},indexOf:function(el){return this.elements.indexOf(Ext.get(el));},filter:function(selector){var me=this,out=[];Ext.each(me.elements,function(el){if(el.is(selector)){out.push(Ext.get(el));}})
me.elements=out;return me;},each:function(fn,scope){Ext.each(this.elements,function(e,i){return fn.call(scope||e,e,this,i)},this);return this;}});Ext.Element.select=function(selector,unique,root){var els;if(typeof selector=="string"){els=Ext.Element.selectorFunction(selector,root);}else if(selector.length!==undefined){els=selector;}else{throw"Invalid selector";}
return(unique===true)?new Ext.CompositeElement(els):new Ext.CompositeElementLite(els);};Ext.select=Ext.Element.select;