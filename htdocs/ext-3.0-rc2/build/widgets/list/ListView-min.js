/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.ListView=Ext.extend(Ext.DataView,{itemSelector:'dl',selectedClass:'x-list-selected',overClass:'x-list-over',scrollOffset:19,columnResize:true,columnSort:true,initComponent:function(){if(this.columnResize){this.colResizer=new Ext.ListView.ColumnResizer(this.colResizer);this.colResizer.init(this);}
if(this.columnSort){this.colSorter=new Ext.ListView.Sorter(this.columnSort);this.colSorter.init(this);}
if(!this.internalTpl){this.internalTpl=new Ext.XTemplate('<div class="x-list-header"><div class="x-list-header-inner">','<tpl for="columns">','<div style="width:{width}%;text-align:{align};"><em unselectable="on" id="',this.id,'-xlhd-{#}">','{header}','</em></div>','</tpl>','<div class="x-clear"></div>','</div></div>','<div class="x-list-body"><div class="x-list-body-inner">','</div></div>');}
if(!this.tpl){this.tpl=new Ext.XTemplate('<tpl for="rows">','<dl>','<tpl for="parent.columns">','<dt style="width:{width}%;text-align:{align};"><em unselectable="on">','{[values.tpl.apply(parent)]}','</em></dt>','</tpl>','<div class="x-clear"></div>','</dl>','</tpl>');};var cs=this.columns,allocatedWidth=0,colsWithWidth=0,len=cs.length;for(var i=0;i<len;i++){var c=cs[i];if(!c.tpl){c.tpl=new Ext.XTemplate('{'+c.dataIndex+'}');}else if(typeof c.tpl=='string'){c.tpl=new Ext.XTemplate(c.tpl);}
c.align=c.align||'left';if(typeof c.width=='number'){c.width*=100;allocatedWidth+=c.width;colsWithWidth++;}}
if(colsWithWidth<len){var remaining=len-colsWithWidth;if(allocatedWidth<100){var perCol=((100-allocatedWidth)/remaining);for(var j=0;j<len;j++){var c=cs[j];if(typeof c.width!='number'){c.width=perCol;}}}}
Ext.ListView.superclass.initComponent.call(this);},onRender:function(){Ext.ListView.superclass.onRender.apply(this,arguments);this.internalTpl.overwrite(this.el,{columns:this.columns});this.innerBody=Ext.get(this.el.dom.childNodes[1].firstChild);this.innerHd=Ext.get(this.el.dom.firstChild.firstChild);if(this.hideHeaders){this.el.dom.firstChild.style.display='none';}},getTemplateTarget:function(){return this.innerBody;},collectData:function(){var rs=Ext.ListView.superclass.collectData.apply(this,arguments);return{columns:this.columns,rows:rs}},verifyInternalSize:function(){if(this.lastSize){this.onResize(this.lastSize.width,this.lastSize.height);}},onResize:function(w,h){var bd=this.innerBody.dom;var hd=this.innerHd.dom
if(!bd){return;}
var bdp=bd.parentNode;if(typeof w=='number'){var sw=w-this.scrollOffset;if(this.reserveScrollOffset||((bdp.offsetWidth-bdp.clientWidth)>10)){bd.style.width=sw+'px';hd.style.width=sw+'px';}else{bd.style.width=w+'px';hd.style.width=w+'px';setTimeout(function(){if((bdp.offsetWidth-bdp.clientWidth)>10){bd.style.width=sw+'px';hd.style.width=sw+'px';}},10);}}
if(typeof h=='number'){bdp.style.height=(h-hd.parentNode.offsetHeight)+'px';}},updateIndexes:function(){Ext.ListView.superclass.updateIndexes.apply(this,arguments);this.verifyInternalSize();},findHeaderIndex:function(hd){hd=hd.dom||hd;var pn=hd.parentNode,cs=pn.parentNode.childNodes;for(var i=0,c;c=cs[i];i++){if(c==pn){return i;}}
return-1;},setHdWidths:function(){var els=this.innerHd.dom.getElementsByTagName('div');for(var i=0,cs=this.columns,len=cs.length;i<len;i++){els[i].style.width=cs[i].width+'%';}}});Ext.reg('listview',Ext.ListView);