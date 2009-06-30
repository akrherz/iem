/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.Element.addMethods({getAnchorXY:function(anchor,local,s){anchor=(anchor||"tl").toLowerCase();s=s||{};var me=this,vp=me.dom==document.body||me.dom==document,w=s.width||vp?Ext.lib.Dom.getViewWidth():me.getWidth(),h=s.height||vp?Ext.lib.Dom.getViewHeight():me.getHeight(),xy,r=Math.round,o=me.getXY(),scroll=me.getScroll(),extraX=vp?scroll.left:!local?o[0]:0,extraY=vp?scroll.top:!local?o[1]:0,hash={c:[r(w*.5),r(h*.5)],t:[r(w*.5),0],l:[0,r(h*.5)],r:[w,r(h*.5)],b:[r(w*.5),h],tl:[0,0],bl:[0,h],br:[w,h],tr:[w,0]};xy=hash[anchor];return[xy[0]+extraX,xy[1]+extraY];},anchorTo:function(el,alignment,offsets,animate,monitorScroll,callback){var me=this;function action(){this.alignTo(el,alignment,offsets,animate);Ext.callback(callback,this);};Ext.EventManager.onWindowResize(action,me);if(!Ext.isEmpty(monitorScroll)){Ext.EventManager.on(window,'scroll',action,me,{buffer:!isNaN(monitorScroll)?monitorScroll:50});}
action.call(me);return me;},getAlignToXY:function(el,p,o){el=Ext.get(el);if(!el||!el.dom){throw"Element.alignToXY with an element that doesn't exist";}
o=o||[0,0];p=(p=="?"?"tl-bl?":(!/-/.test(p)&&p!=""?"tl-"+p:p||"tl-bl")).toLowerCase();;var me=this,d=me.dom,a1,a2,x,y,w,h,r,dw=Ext.lib.Dom.getViewWidth()-10,dh=Ext.lib.Dom.getViewHeight()-10,p1y,p1x,p2y,p2x,swapY,swapX,doc=document,docElement=doc.documentElement,docBody=doc.body,scrollX=(docElement.scrollLeft||docBody.scrollLeft||0)+5,scrollY=(docElement.scrollTop||docBody.scrollTop||0)+5,c=false,p1="",p2="",m=p.match(/^([a-z]+)-([a-z]+)(\?)?$/)
if(!m){throw"Element.alignTo with an invalid alignment "+p;}
p1=m[1];p2=m[2];c=!!m[3];a1=me.getAnchorXY(p1,true);a2=el.getAnchorXY(p2,false);x=a2[0]-a1[0]+o[0];y=a2[1]-a1[1]+o[1];if(c){w=me.getWidth();h=me.getHeight();r=el.getRegion();p1y=p1.charAt(0);p1x=p1.charAt(p1.length-1);p2y=p2.charAt(0);p2x=p2.charAt(p2.length-1);swapY=((p1y=="t"&&p2y=="b")||(p1y=="b"&&p2y=="t"));swapX=((p1x=="r"&&p2x=="l")||(p1x=="l"&&p2x=="r"));if(x+w>dw+scrollX){x=swapX?r.left-w:dw+scrollX-w;}
if(x<scrollX){x=swapX?r.right:scrollX;}
if(y+h>dh+scrollY){y=swapY?r.top-h:dh+scrollY-h;}
if(y<scrollY){y=swapY?r.bottom:scrollY;}}
return[x,y];},alignTo:function(element,position,offsets,animate){var me=this;return me.setXY(me.getAlignToXY(element,position,offsets),me.preanim&&!!animate?me.preanim(arguments,3):false);},adjustForConstraints:function(xy,parent,offsets){return this.getConstrainToXY(parent||document,false,offsets,xy)||xy;},getConstrainToXY:function(el,local,offsets,proposedXY){var os={top:0,left:0,bottom:0,right:0};return function(el,local,offsets,proposedXY){el=Ext.get(el);offsets=offsets?Ext.applyIf(offsets,os):os;var vw,vh,vx=0,vy=0;if(el.dom==document.body||el.dom==document){vw=Ext.lib.Dom.getViewWidth();vh=Ext.lib.Dom.getViewHeight();}else{vw=el.dom.clientWidth;vh=el.dom.clientHeight;if(!local){var vxy=el.getXY();vx=vxy[0];vy=vxy[1];}}
var s=el.getScroll();vx+=offsets.left+s.left;vy+=offsets.top+s.top;vw-=offsets.right;vh-=offsets.bottom;var vr=vx+vw;var vb=vy+vh;var xy=proposedXY||(!local?this.getXY():[this.getLeft(true),this.getTop(true)]);var x=xy[0],y=xy[1];var w=this.dom.offsetWidth,h=this.dom.offsetHeight;var moved=false;if((x+w)>vr){x=vr-w;moved=true;}
if((y+h)>vb){y=vb-h;moved=true;}
if(x<vx){x=vx;moved=true;}
if(y<vy){y=vy;moved=true;}
return moved?[x,y]:false;};}(),getCenterXY:function(){return this.getAlignToXY(document,'c-c');},center:function(centerIn){return this.alignTo(centerIn||document,'c-c');}});