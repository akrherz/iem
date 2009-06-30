/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.layout.AbsoluteLayout=Ext.extend(Ext.layout.AnchorLayout,{extraCls:'x-abs-layout-item',onLayout:function(ct,target){target.position();this.paddingLeft=target.getPadding('l');this.paddingTop=target.getPadding('t');Ext.layout.AbsoluteLayout.superclass.onLayout.call(this,ct,target);},adjustWidthAnchor:function(value,comp){return value?value-comp.getPosition(true)[0]+this.paddingLeft:value;},adjustHeightAnchor:function(value,comp){return value?value-comp.getPosition(true)[1]+this.paddingTop:value;}});Ext.Container.LAYOUTS['absolute']=Ext.layout.AbsoluteLayout;