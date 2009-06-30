/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.apply(Ext.Element.prototype,function(){var GETDOM=Ext.getDom,GET=Ext.get,DH=Ext.DomHelper;return{insertSibling:function(el,where,returnDom){var me=this,rt;if(Ext.isArray(el)){Ext.each(el,function(e){rt=me.insertSibling(e,where,returnDom);});return rt;}
where=(where||'before').toLowerCase();el=el||{};if(el.nodeType||el.dom){rt=me.dom.parentNode.insertBefore(GETDOM(el),where=='before'?me.dom:me.dom.nextSibling);if(!returnDom){rt=GET(rt);}}else{if(where=='after'&&!me.dom.nextSibling){rt=DH.append(me.dom.parentNode,el,!returnDom);}else{rt=DH[where=='after'?'insertAfter':'insertBefore'](me.dom,el,!returnDom);}}
return rt;}}}());