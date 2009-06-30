/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.menu.BaseItem=function(config){Ext.menu.BaseItem.superclass.constructor.call(this,config);this.addEvents('click','activate','deactivate');if(this.handler){this.on("click",this.handler,this.scope);}};Ext.extend(Ext.menu.BaseItem,Ext.Component,{canActivate:false,activeClass:"x-menu-item-active",hideOnClick:true,clickHideDelay:1,ctype:"Ext.menu.BaseItem",actionMode:"container",onRender:function(container,position){Ext.menu.BaseItem.superclass.onRender.apply(this,arguments);if(this.ownerCt&&this.ownerCt instanceof Ext.menu.Menu){this.parentMenu=this.ownerCt;}else{this.container.addClass('x-menu-list-item');this.mon(this.el,'click',this.onClick,this);this.mon(this.el,'mouseenter',this.activate,this);this.mon(this.el,'mouseleave',this.deactivate,this);}},setHandler:function(handler,scope){if(this.handler){this.un("click",this.handler,this.scope);}
this.on("click",this.handler=handler,this.scope=scope);},onClick:function(e){if(!this.disabled&&this.fireEvent("click",this,e)!==false&&(this.parentMenu&&this.parentMenu.fireEvent("itemclick",this,e)!==false)){this.handleClick(e);}else{e.stopEvent();}},activate:function(){if(this.disabled){return false;}
var li=this.container;li.addClass(this.activeClass);this.region=li.getRegion().adjust(2,2,-2,-2);this.fireEvent("activate",this);return true;},deactivate:function(){this.container.removeClass(this.activeClass);this.fireEvent("deactivate",this);},shouldDeactivate:function(e){return!this.region||!this.region.contains(e.getPoint());},handleClick:function(e){if(this.hideOnClick){this.parentMenu.hide.defer(this.clickHideDelay,this.parentMenu,[true]);}},expandMenu:Ext.emptyFn,hideMenu:Ext.emptyFn});Ext.reg('menubaseitem',Ext.menu.BaseItem);