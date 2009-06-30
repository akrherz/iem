/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.Element.addMethods({setBox:function(box,adjust,animate){var me=this,w=box.width,h=box.height;if((adjust&&!me.autoBoxAdjust)&&!me.isBorderBox()){w-=(me.getBorderWidth("lr")+me.getPadding("lr"));h-=(me.getBorderWidth("tb")+me.getPadding("tb"));}
me.setBounds(box.x,box.y,w,h,me.animTest.call(me,arguments,animate,2));return me;},getBox:function(contentBox,local){var me=this,xy,left,top,getBorderWidth=me.getBorderWidth,getPadding=me.getPadding,l,r,t,b;if(!local){xy=me.getXY();}else{left=parseInt(me.getStyle("left"),10)||0;top=parseInt(me.getStyle("top"),10)||0;xy=[left,top];}
var el=me.dom,w=el.offsetWidth,h=el.offsetHeight,bx;if(!contentBox){bx={x:xy[0],y:xy[1],0:xy[0],1:xy[1],width:w,height:h};}else{l=getBorderWidth.call(me,"l")+getPadding.call(me,"l");r=getBorderWidth.call(me,"r")+getPadding.call(me,"r");t=getBorderWidth.call(me,"t")+getPadding.call(me,"t");b=getBorderWidth.call(me,"b")+getPadding.call(me,"b");bx={x:xy[0]+l,y:xy[1]+t,0:xy[0]+l,1:xy[1]+t,width:w-(l+r),height:h-(t+b)};}
bx.right=bx.x+bx.width;bx.bottom=bx.y+bx.height;return bx;},move:function(direction,distance,animate){var me=this,xy=me.getXY(),x=xy[0],y=xy[1],left=[x-distance,y],right=[x+distance,y],top=[x,y-distance],bottom=[x,y+distance],hash={l:left,left:left,r:right,right:right,t:top,top:top,up:top,b:bottom,bottom:bottom,down:bottom};direction=direction.toLowerCase();me.moveTo(hash[direction][0],hash[direction][1],me.animTest.call(me,arguments,animate,2));},setLeftTop:function(left,top){var me=this,style=me.dom.style;style.left=me.addUnits(left);style.top=me.addUnits(top);return me;},getRegion:function(){return Ext.lib.Dom.getRegion(this.dom);},setBounds:function(x,y,width,height,animate){var me=this;if(!animate||!me.anim){me.setSize(width,height);me.setLocation(x,y);}else{me.anim({points:{to:[x,y]},width:{to:me.adjustWidth(width)},height:{to:me.adjustHeight(height)}},me.preanim(arguments,4),'motion');}
return me;},setRegion:function(region,animate){return this.setBounds(region.left,region.top,region.right-region.left,region.bottom-region.top,this.animTest.call(this,arguments,animate,1));}});