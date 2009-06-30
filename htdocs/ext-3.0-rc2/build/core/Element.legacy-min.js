/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.Element.addMethods({autoHeight:function(animate,duration,onComplete,easing){var oldHeight=this.getHeight();this.clip();this.setHeight(1);setTimeout(function(){var height=parseInt(this.dom.scrollHeight,10);if(!animate){this.setHeight(height);this.unclip();if(typeof onComplete=="function"){onComplete();}}else{this.setHeight(oldHeight);this.setHeight(height,animate,duration,function(){this.unclip();if(typeof onComplete=="function")onComplete();}.createDelegate(this),easing);}}.createDelegate(this),0);return this;}});