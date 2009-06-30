/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.SplitButton=Ext.extend(Ext.Button,{arrowSelector:'em',split:true,initComponent:function(){Ext.SplitButton.superclass.initComponent.call(this);this.addEvents("arrowclick");},onRender:function(){Ext.SplitButton.superclass.onRender.apply(this,arguments);if(this.arrowTooltip){btn.child(this.arrowSelector).dom[this.tooltipType]=this.arrowTooltip;}},setArrowHandler:function(handler,scope){this.arrowHandler=handler;this.scope=scope;},getMenuClass:function(){return this.menu&&this.arrowAlign!='bottom'?'x-btn-split':'x-btn-split-bottom';},isClickOnArrow:function(e){return this.arrowAlign!='bottom'?e.getPageX()>this.el.child(this.buttonSelector).getRegion().right:e.getPageY()>this.el.child(this.buttonSelector).getRegion().bottom;},onClick:function(e,t){e.preventDefault();if(!this.disabled){if(this.isClickOnArrow(e)){if(this.menu&&!this.menu.isVisible()&&!this.ignoreNextClick){this.showMenu();}
this.fireEvent("arrowclick",this,e);if(this.arrowHandler){this.arrowHandler.call(this.scope||this,this,e);}}else{if(this.enableToggle){this.toggle();}
this.fireEvent("click",this,e);if(this.handler){this.handler.call(this.scope||this,this,e);}}}},isMenuTriggerOver:function(e){return this.menu&&e.target.tagName=='em';},isMenuTriggerOut:function(e,internal){return this.menu&&e.target.tagName!='em';}});Ext.reg('splitbutton',Ext.SplitButton);