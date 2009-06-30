/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.Panel=Ext.extend(Ext.Container,{baseCls:'x-panel',collapsedCls:'x-panel-collapsed',maskDisabled:true,animCollapse:Ext.enableFx,headerAsText:true,buttonAlign:'right',collapsed:false,collapseFirst:true,minButtonWidth:75,elements:'body',preventBodyReset:false,toolTarget:'header',collapseEl:'bwrap',slideAnchor:'t',disabledClass:'',deferHeight:true,expandDefaults:{duration:.25},collapseDefaults:{duration:.25},initComponent:function(){Ext.Panel.superclass.initComponent.call(this);this.addEvents('bodyresize','titlechange','iconchange','collapse','expand','beforecollapse','beforeexpand','beforeclose','close','activate','deactivate');if(this.unstyled){this.baseCls='x-plain';}
if(this.tbar){this.elements+=',tbar';if(Ext.isObject(this.tbar)){this.topToolbar=this.tbar;}
delete this.tbar;}
if(this.bbar){this.elements+=',bbar';if(Ext.isObject(this.bbar)){this.bottomToolbar=this.bbar;}
delete this.bbar;}
if(this.header===true){this.elements+=',header';delete this.header;}else if(this.title&&this.header!==false){this.elements+=',header';}
if(this.footer===true){this.elements+=',footer';delete this.footer;}
if(this.buttons){this.elements+=',footer';var btns=this.buttons;this.buttons=[];for(var i=0,len=btns.length;i<len;i++){if(btns[i].render){this.buttons.push(btns[i]);}else if(btns[i].xtype){this.buttons.push(Ext.create(btns[i],'button'));}else{this.addButton(btns[i]);}}}
if(this.fbar){this.elements+=',footer';}
if(this.autoLoad){this.on('render',this.doAutoLoad,this,{delay:10});}},createElement:function(name,pnode){if(this[name]){pnode.appendChild(this[name].dom);return;}
if(name==='bwrap'||this.elements.indexOf(name)!=-1){if(this[name+'Cfg']){this[name]=Ext.fly(pnode).createChild(this[name+'Cfg']);}else{var el=document.createElement('div');el.className=this[name+'Cls'];this[name]=Ext.get(pnode.appendChild(el));}
if(this[name+'CssClass']){this[name].addClass(this[name+'CssClass']);}
if(this[name+'Style']){this[name].applyStyles(this[name+'Style']);}}},onRender:function(ct,position){Ext.Panel.superclass.onRender.call(this,ct,position);this.createClasses();var el=this.el,d=el.dom;el.addClass(this.baseCls);if(d.firstChild){this.header=el.down('.'+this.headerCls);this.bwrap=el.down('.'+this.bwrapCls);var cp=this.bwrap?this.bwrap:el;this.tbar=cp.down('.'+this.tbarCls);this.body=cp.down('.'+this.bodyCls);this.bbar=cp.down('.'+this.bbarCls);this.footer=cp.down('.'+this.footerCls);this.fromMarkup=true;}
if(this.preventBodyReset===true){el.addClass('x-panel-reset');}
if(this.cls){el.addClass(this.cls);}
if(this.buttons){this.elements+=',footer';}
if(this.frame){el.insertHtml('afterBegin',String.format(Ext.Element.boxMarkup,this.baseCls));this.createElement('header',d.firstChild.firstChild.firstChild);this.createElement('bwrap',d);var bw=this.bwrap.dom;var ml=d.childNodes[1],bl=d.childNodes[2];bw.appendChild(ml);bw.appendChild(bl);var mc=bw.firstChild.firstChild.firstChild;this.createElement('tbar',mc);this.createElement('body',mc);this.createElement('bbar',mc);this.createElement('footer',bw.lastChild.firstChild.firstChild);if(!this.footer){this.bwrap.dom.lastChild.className+=' x-panel-nofooter';}}else{this.createElement('header',d);this.createElement('bwrap',d);var bw=this.bwrap.dom;this.createElement('tbar',bw);this.createElement('body',bw);this.createElement('bbar',bw);this.createElement('footer',bw);if(!this.header){this.body.addClass(this.bodyCls+'-noheader');if(this.tbar){this.tbar.addClass(this.tbarCls+'-noheader');}}}
if(this.padding!==undefined){this.body.setStyle('padding',this.body.addUnits(this.padding));}
if(this.border===false){this.el.addClass(this.baseCls+'-noborder');this.body.addClass(this.bodyCls+'-noborder');if(this.header){this.header.addClass(this.headerCls+'-noborder');}
if(this.footer){this.footer.addClass(this.footerCls+'-noborder');}
if(this.tbar){this.tbar.addClass(this.tbarCls+'-noborder');}
if(this.bbar){this.bbar.addClass(this.bbarCls+'-noborder');}}
if(this.bodyBorder===false){this.body.addClass(this.bodyCls+'-noborder');}
this.bwrap.enableDisplayMode('block');if(this.header){this.header.unselectable();if(this.headerAsText){this.header.dom.innerHTML='<span class="'+this.headerTextCls+'">'+this.header.dom.innerHTML+'</span>';if(this.iconCls){this.setIconClass(this.iconCls);}}}
if(this.floating){this.makeFloating(this.floating);}
if(this.collapsible){this.tools=this.tools?this.tools.slice(0):[];if(!this.hideCollapseTool){this.tools[this.collapseFirst?'unshift':'push']({id:'toggle',handler:this.toggleCollapse,scope:this});}
if(this.titleCollapse&&this.header){this.mon(this.header,'click',this.toggleCollapse,this);this.header.setStyle('cursor','pointer');}}
if(this.tools){var ts=this.tools;this.tools={};this.addTool.apply(this,ts);}else{this.tools={};}
if(this.buttons&&this.buttons.length>0){this.fbar=new Ext.Toolbar({items:this.buttons,toolbarCls:'x-panel-fbar'});}
this.toolbars=[];if(this.fbar){this.fbar=Ext.create(this.fbar,'toolbar');this.fbar.enableOverflow=false;if(this.fbar.items){this.fbar.items.each(function(c){c.minWidth=c.minWidth||this.minButtonWidth;},this);}
this.fbar.toolbarCls='x-panel-fbar';var bct=this.footer.createChild({cls:'x-panel-btns x-panel-btns-'+this.buttonAlign});this.fbar.ownerCt=this;this.fbar.render(bct);bct.createChild({cls:'x-clear'});this.toolbars.push(this.fbar);}
if(this.tbar&&this.topToolbar){if(Ext.isArray(this.topToolbar)){this.topToolbar=new Ext.Toolbar(this.topToolbar);}else if(!this.topToolbar.events){this.topToolbar=Ext.create(this.topToolbar,'toolbar');}
this.topToolbar.ownerCt=this;this.topToolbar.render(this.tbar);this.toolbars.push(this.topToolbar);}
if(this.bbar&&this.bottomToolbar){if(Ext.isArray(this.bottomToolbar)){this.bottomToolbar=new Ext.Toolbar(this.bottomToolbar);}else if(!this.bottomToolbar.events){this.bottomToolbar=Ext.create(this.bottomToolbar,'toolbar');}
this.bottomToolbar.ownerCt=this;this.bottomToolbar.render(this.bbar);this.toolbars.push(this.bottomToolbar);}
Ext.each(this.toolbars,function(tb){tb.on({scope:this,afterlayout:this.syncHeight,remove:this.syncHeight})},this);},setIconClass:function(cls){var old=this.iconCls;this.iconCls=cls;if(this.rendered&&this.header){if(this.frame){this.header.addClass('x-panel-icon');this.header.replaceClass(old,this.iconCls);}else{var hd=this.header.dom;var img=hd.firstChild&&String(hd.firstChild.tagName).toLowerCase()=='img'?hd.firstChild:null;if(img){Ext.fly(img).replaceClass(old,this.iconCls);}else{Ext.DomHelper.insertBefore(hd.firstChild,{tag:'img',src:Ext.BLANK_IMAGE_URL,cls:'x-panel-inline-icon '+this.iconCls});}}}
this.fireEvent('iconchange',this,cls,old);},makeFloating:function(cfg){this.floating=true;this.el=new Ext.Layer(Ext.isObject(cfg)?cfg:{shadow:this.shadow!==undefined?this.shadow:'sides',shadowOffset:this.shadowOffset,constrain:false,shim:this.shim===false?false:undefined},this.el);},getTopToolbar:function(){return this.topToolbar;},getBottomToolbar:function(){return this.bottomToolbar;},addButton:function(config,handler,scope){var bc={handler:handler,scope:scope,minWidth:this.minButtonWidth,hideParent:true};if(typeof config=="string"){bc.text=config;}else{Ext.apply(bc,config);}
var btn=new Ext.Button(bc);if(!this.buttons){this.buttons=[];}
this.buttons.push(btn);return btn;},addTool:function(){if(!this[this.toolTarget]){return;}
if(!this.toolTemplate){var tt=new Ext.Template('<div class="x-tool x-tool-{id}">&#160;</div>');tt.disableFormats=true;tt.compile();Ext.Panel.prototype.toolTemplate=tt;}
for(var i=0,a=arguments,len=a.length;i<len;i++){var tc=a[i];if(!this.tools[tc.id]){var overCls='x-tool-'+tc.id+'-over';var t=this.toolTemplate.insertFirst((tc.align!=='left')?this[this.toolTarget]:this[this.toolTarget].child('span'),tc,true);this.tools[tc.id]=t;t.enableDisplayMode('block');this.mon(t,'click',this.createToolHandler(t,tc,overCls,this));if(tc.on){this.mon(t,tc.on);}
if(tc.hidden){t.hide();}
if(tc.qtip){if(Ext.isObject(tc.qtip)){Ext.QuickTips.register(Ext.apply({target:t.id},tc.qtip));}else{t.dom.qtip=tc.qtip;}}
t.addClassOnOver(overCls);}}},onLayout:function(){if(this.toolbars.length>0){this.duringLayout=true;Ext.each(this.toolbars,function(tb){tb.doLayout();});delete this.duringLayout;this.syncHeight();}},syncHeight:function(){if(!this.duringLayout){var last=this.lastSize;if(last&&!Ext.isEmpty(last.height)){var old=last.height,h=this.el.getHeight();if(old!='auto'&&old!=h){h=old-h;var bd=this.body;bd.setHeight(bd.getHeight()+h);var sz=bd.getSize();this.fireEvent('bodyresize',sz.width,sz.height);}}}},onShow:function(){if(this.floating){return this.el.show();}
Ext.Panel.superclass.onShow.call(this);},onHide:function(){if(this.floating){return this.el.hide();}
Ext.Panel.superclass.onHide.call(this);},createToolHandler:function(t,tc,overCls,panel){return function(e){t.removeClass(overCls);if(tc.stopEvent!==false){e.stopEvent();}
if(tc.handler){tc.handler.call(tc.scope||t,e,t,panel,tc);}};},afterRender:function(){if(this.floating&&!this.hidden){this.el.show();}
if(this.title){this.setTitle(this.title);}
this.setAutoScroll();if(this.html){this.body.update(Ext.isObject(this.html)?Ext.DomHelper.markup(this.html):this.html);delete this.html;}
if(this.contentEl){var ce=Ext.getDom(this.contentEl);Ext.fly(ce).removeClass(['x-hidden','x-hide-display']);this.body.dom.appendChild(ce);}
if(this.collapsed){this.collapsed=false;this.collapse(false);}
Ext.Panel.superclass.afterRender.call(this);this.initEvents();},setAutoScroll:function(){if(this.rendered&&this.autoScroll){var el=this.body||this.el;if(el){el.setOverflow('auto');}}},getKeyMap:function(){if(!this.keyMap){this.keyMap=new Ext.KeyMap(this.el,this.keys);}
return this.keyMap;},initEvents:function(){if(this.keys){this.getKeyMap();}
if(this.draggable){this.initDraggable();}},initDraggable:function(){this.dd=new Ext.Panel.DD(this,typeof this.draggable=='boolean'?null:this.draggable);},beforeEffect:function(){if(this.floating){this.el.beforeAction();}
this.el.addClass('x-panel-animated');},afterEffect:function(){this.syncShadow();this.el.removeClass('x-panel-animated');},createEffect:function(a,cb,scope){var o={scope:scope,block:true};if(a===true){o.callback=cb;return o;}else if(!a.callback){o.callback=cb;}else{o.callback=function(){cb.call(scope);Ext.callback(a.callback,a.scope);};}
return Ext.applyIf(o,a);},collapse:function(animate){if(this.collapsed||this.el.hasFxBlock()||this.fireEvent('beforecollapse',this,animate)===false){return;}
var doAnim=animate===true||(animate!==false&&this.animCollapse);if(doAnim){this.beforeEffect();}
this.onCollapse(doAnim,animate);return this;},onCollapse:function(doAnim,animArg){if(doAnim){this[this.collapseEl].slideOut(this.slideAnchor,Ext.apply(this.createEffect(animArg||true,this.afterCollapse,this),this.collapseDefaults));}else{this[this.collapseEl].hide();this.afterCollapse(doAnim);}},afterCollapse:function(doAnim){this.collapsed=true;this.el.addClass(this.collapsedCls);if(doAnim){this.afterEffect();}
this.fireEvent('collapse',this);},expand:function(animate){if(!this.collapsed||this.el.hasFxBlock()||this.fireEvent('beforeexpand',this,animate)===false){return;}
var doAnim=animate===true||(animate!==false&&this.animCollapse);this.el.removeClass(this.collapsedCls);this.beforeEffect();this.onExpand(doAnim,animate);return this;},onExpand:function(doAnim,animArg){if(doAnim){this[this.collapseEl].slideIn(this.slideAnchor,Ext.apply(this.createEffect(animArg||true,this.afterExpand,this),this.expandDefaults));}else{this[this.collapseEl].show();this.afterExpand();}},afterExpand:function(){this.collapsed=false;this.afterEffect();if(this.deferLayout!==undefined){this.doLayout(true);}
this.fireEvent('expand',this);},toggleCollapse:function(animate){this[this.collapsed?'expand':'collapse'](animate);return this;},onDisable:function(){if(this.rendered&&this.maskDisabled){this.el.mask();}
Ext.Panel.superclass.onDisable.call(this);},onEnable:function(){if(this.rendered&&this.maskDisabled){this.el.unmask();}
Ext.Panel.superclass.onEnable.call(this);},onResize:function(w,h){if(w!==undefined||h!==undefined){if(!this.collapsed){if(typeof w=='number'){w=this.adjustBodyWidth(w-this.getFrameWidth());if(this.tbar){this.tbar.setWidth(w);if(this.topToolbar){this.topToolbar.setSize(w);}}
if(this.bbar){this.bbar.setWidth(w);if(this.bottomToolbar){this.bottomToolbar.setSize(w);}}
if(this.fbar){var f=this.fbar,fWidth=1;strict=Ext.isStrict;if(this.buttonAlign=='left'){fWidth=w-f.container.getFrameWidth('lr');}else{if(Ext.isIE||Ext.isWebKit){if(!(this.buttonAlign=='center'&&Ext.isWebKit)&&(!strict||(!Ext.isIE8&&strict))){(function(){f.setWidth(f.getEl().child('.x-toolbar-ct').getWidth());}).defer(1);}else{fWidth='auto';}}else{fWidth='auto';}}
f.setWidth(fWidth);}
this.body.setWidth(w);}else if(w=='auto'){this.body.setWidth(w);}
if(typeof h=='number'){h=this.adjustBodyHeight(h-this.getFrameHeight());this.body.setHeight(h);}else if(h=='auto'){this.body.setHeight(h);}
if(this.disabled&&this.el._mask){this.el._mask.setSize(this.el.dom.clientWidth,this.el.getHeight());}}else{this.queuedBodySize={width:w,height:h};if(!this.queuedExpand&&this.allowQueuedExpand!==false){this.queuedExpand=true;this.on('expand',function(){delete this.queuedExpand;this.onResize(this.queuedBodySize.width,this.queuedBodySize.height);this.doLayout();},this,{single:true});}}
this.fireEvent('bodyresize',this,w,h);}
this.syncShadow();},adjustBodyHeight:function(h){return h;},adjustBodyWidth:function(w){return w;},onPosition:function(){this.syncShadow();},getFrameWidth:function(){var w=this.el.getFrameWidth('lr')+this.bwrap.getFrameWidth('lr');if(this.frame){var l=this.bwrap.dom.firstChild;w+=(Ext.fly(l).getFrameWidth('l')+Ext.fly(l.firstChild).getFrameWidth('r'));var mc=this.bwrap.dom.firstChild.firstChild.firstChild;w+=Ext.fly(mc).getFrameWidth('lr');}
return w;},getFrameHeight:function(){var h=this.el.getFrameWidth('tb')+this.bwrap.getFrameWidth('tb');h+=(this.tbar?this.tbar.getHeight():0)+
(this.bbar?this.bbar.getHeight():0);if(this.frame){var hd=this.el.dom.firstChild;var ft=this.bwrap.dom.lastChild;h+=(hd.offsetHeight+ft.offsetHeight);var mc=this.bwrap.dom.firstChild.firstChild.firstChild;h+=Ext.fly(mc).getFrameWidth('tb');}else{h+=(this.header?this.header.getHeight():0)+
(this.footer?this.footer.getHeight():0);}
return h;},getInnerWidth:function(){return this.getSize().width-this.getFrameWidth();},getInnerHeight:function(){return this.getSize().height-this.getFrameHeight();},syncShadow:function(){if(this.floating){this.el.sync(true);}},getLayoutTarget:function(){return this.body;},setTitle:function(title,iconCls){this.title=title;if(this.header&&this.headerAsText){this.header.child('span').update(title);}
if(iconCls){this.setIconClass(iconCls);}
this.fireEvent('titlechange',this,title);return this;},getUpdater:function(){return this.body.getUpdater();},load:function(){var um=this.body.getUpdater();um.update.apply(um,arguments);return this;},beforeDestroy:function(){if(this.header){this.header.removeAllListeners();if(this.headerAsText){Ext.Element.uncache(this.header.child('span'));}}
Ext.Element.uncache(this.header,this.tbar,this.bbar,this.footer,this.body,this.bwrap);if(this.tools){for(var k in this.tools){Ext.destroy(this.tools[k]);}}
if(this.buttons){for(var b in this.buttons){Ext.destroy(this.buttons[b]);}}
Ext.destroy(this.topToolbar,this.bottomToolbar,this.fbar);Ext.Panel.superclass.beforeDestroy.call(this);},createClasses:function(){this.headerCls=this.baseCls+'-header';this.headerTextCls=this.baseCls+'-header-text';this.bwrapCls=this.baseCls+'-bwrap';this.tbarCls=this.baseCls+'-tbar';this.bodyCls=this.baseCls+'-body';this.bbarCls=this.baseCls+'-bbar';this.footerCls=this.baseCls+'-footer';},createGhost:function(cls,useShim,appendTo){var el=document.createElement('div');el.className='x-panel-ghost '+(cls?cls:'');if(this.header){el.appendChild(this.el.dom.firstChild.cloneNode(true));}
Ext.fly(el.appendChild(document.createElement('ul'))).setHeight(this.bwrap.getHeight());el.style.width=this.el.dom.offsetWidth+'px';;if(!appendTo){this.container.dom.appendChild(el);}else{Ext.getDom(appendTo).appendChild(el);}
if(useShim!==false&&this.el.useShim!==false){var layer=new Ext.Layer({shadow:false,useDisplay:true,constrain:false},el);layer.show();return layer;}else{return new Ext.Element(el);}},doAutoLoad:function(){var u=this.body.getUpdater();if(this.renderer){u.setRenderer(this.renderer);}
u.update(Ext.isObject(this.autoLoad)?this.autoLoad:{url:this.autoLoad});},getTool:function(id){return this.tools[id];}});Ext.reg('panel',Ext.Panel);