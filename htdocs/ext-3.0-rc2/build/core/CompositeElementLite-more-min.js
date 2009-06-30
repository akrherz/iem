/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.apply(Ext.CompositeElementLite.prototype,{addElements:function(els,root){if(!els)return this;if(typeof els=="string"){els=Ext.Element.selectorFunction(els,root);}
var yels=this.elements;Ext.each(els,function(e){yels.push(Ext.get(e));});return this;},fill:function(els){this.elements=[];this.add(els);return this;},first:function(){return this.item(0);},last:function(){return this.item(this.getCount()-1);},contains:function(el){return this.indexOf(el)!=-1;},filter:function(selector){var els=[];this.each(function(el){if(el.is(selector)){els[els.length]=el.dom;}});this.fill(els);return this;},removeElement:function(keys,removeDom){var me=this,els=this.elements,el;Ext.each(keys,function(val){if(el=(els[val]||els[val=me.indexOf(val)])){if(removeDom)
el.dom?el.remove():Ext.removeNode(el);els.splice(val,1);}});return this;}});