/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.Element.addMethods(function(){var VISIBILITY="visibility",DISPLAY="display",HIDDEN="hidden",NONE="none",XMASKED="x-masked",XMASKEDRELATIVE="x-masked-relative";return{isVisible:function(deep){var vis=!this.isStyle(VISIBILITY,HIDDEN)&&!this.isStyle(DISPLAY,NONE),p=this.dom.parentNode;if(deep!==true||!vis){return vis;}
while(p&&!/body/i.test(p.tagName)){if(!Ext.fly(p,'_isVisible').isVisible()){return false;}
p=p.parentNode;}
return true;},isDisplayed:function(){return!this.isStyle(DISPLAY,NONE);},enableDisplayMode:function(display){this.setVisibilityMode(Ext.Element.DISPLAY);if(!Ext.isEmpty(display))this.originalDisplay=display;return this;},mask:function(msg,msgCls){var me=this,dom=me.dom,dh=Ext.DomHelper,EXTELMASKMSG="ext-el-mask-msg";if(me.getStyle("position")=="static"){me.addClass(XMASKEDRELATIVE);}
if(me._maskMsg){me._maskMsg.remove();}
if(me._mask){me._mask.remove();}
me._mask=dh.append(dom,{cls:"ext-el-mask"},true);me.addClass(XMASKED);me._mask.setDisplayed(true);if(typeof msg=='string'){me._maskMsg=dh.append(dom,{cls:EXTELMASKMSG,cn:{tag:'div'}},true);var mm=me._maskMsg;mm.dom.className=msgCls?EXTELMASKMSG+" "+msgCls:EXTELMASKMSG;mm.dom.firstChild.innerHTML=msg;mm.setDisplayed(true);mm.center(me);}
if(Ext.isIE&&!(Ext.isIE7&&Ext.isStrict)&&me.getStyle('height')=='auto'){me._mask.setSize(undefined,me.getHeight());}
return me._mask;},unmask:function(){var me=this,mask=me._mask,maskMsg=me._maskMsg;if(mask){if(maskMsg){maskMsg.remove();delete me._maskMsg;}
mask.remove();delete me._mask;}
me.removeClass([XMASKED,XMASKEDRELATIVE]);},isMasked:function(){return this._mask&&this._mask.isVisible();},createShim:function(){var el=document.createElement('iframe'),shim;el.frameBorder='0';el.className='ext-shim';if(Ext.isIE&&Ext.isSecure){el.src=Ext.SSL_SECURE_URL;}
shim=Ext.get(this.dom.parentNode.insertBefore(el,this.dom));shim.autoBoxAdjust=false;return shim;}}}());