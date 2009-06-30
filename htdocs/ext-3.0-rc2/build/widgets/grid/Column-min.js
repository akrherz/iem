/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.grid.Column=function(config){Ext.apply(this,config);if(typeof this.renderer=="string"){this.renderer=Ext.util.Format[this.renderer];}else if(typeof this.renderer=='object'){this.scope=this.renderer.scope;this.renderer=this.renderer.fn;}
this.renderer=this.renderer.createDelegate(this.scope||config);if(typeof this.id=="undefined"){this.id=++Ext.grid.Column.AUTO_ID;}
if(this.editor){if(this.editor.xtype&&!this.editor.events){this.editor=Ext.create(this.editor,'textfield');}}}
Ext.grid.Column.AUTO_ID=0;Ext.grid.Column.prototype={isColumn:true,renderer:function(value){if(typeof value=="string"&&value.length<1){return"&#160;";}
return value;},getEditor:function(rowIndex){return this.editable!==false?this.editor:null;},getCellEditor:function(rowIndex){var editor=this.getEditor(rowIndex);if(editor){if(!editor.startEdit){if(!editor.gridEditor){editor.gridEditor=new Ext.grid.GridEditor(editor);}
return editor.gridEditor;}else if(editor.startEdit){return editor;}}
return null;}};Ext.grid.BooleanColumn=Ext.extend(Ext.grid.Column,{trueText:'true',falseText:'false',undefinedText:'&#160;',constructor:function(cfg){this.supr().constructor.apply(this,arguments);var t=this.trueText,f=this.falseText,u=this.undefinedText;this.renderer=function(v){if(v===undefined){return u;}
if(!v||v==='false'){return f;}
return t;};}});Ext.grid.NumberColumn=Ext.extend(Ext.grid.Column,{format:'0,000.00',constructor:function(cfg){this.supr().constructor.apply(this,arguments);this.renderer=Ext.util.Format.numberRenderer(this.format);}});Ext.grid.DateColumn=Ext.extend(Ext.grid.Column,{format:'m/d/Y',constructor:function(cfg){this.supr().constructor.apply(this,arguments);this.renderer=Ext.util.Format.dateRenderer(this.format);}});Ext.grid.TemplateColumn=Ext.extend(Ext.grid.Column,{constructor:function(cfg){this.supr().constructor.apply(this,arguments);var tpl=typeof this.tpl=='object'?this.tpl:new Ext.XTemplate(this.tpl);this.renderer=function(value,p,r){return tpl.apply(r.data);}
this.tpl=tpl;}});Ext.grid.Column.types={gridcolumn:Ext.grid.Column,booleancolumn:Ext.grid.BooleanColumn,numbercolumn:Ext.grid.NumberColumn,datecolumn:Ext.grid.DateColumn,templatecolumn:Ext.grid.TemplateColumn};