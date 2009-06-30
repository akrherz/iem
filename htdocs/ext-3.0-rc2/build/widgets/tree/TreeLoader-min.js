/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.tree.TreeLoader=function(config){this.baseParams={};Ext.apply(this,config);this.addEvents("beforeload","load","loadexception");Ext.tree.TreeLoader.superclass.constructor.call(this);if(typeof this.paramOrder=='string'){this.paramOrder=this.paramOrder.split(/[\s,|]/);}};Ext.extend(Ext.tree.TreeLoader,Ext.util.Observable,{uiProviders:{},clearOnLoad:true,paramOrder:undefined,paramsAsHash:false,directFn:undefined,load:function(node,callback,scope){if(this.clearOnLoad){while(node.firstChild){node.removeChild(node.firstChild);}}
if(this.doPreload(node)){this.runCallback(callback,scope||node);}else if(this.directFn||this.dataUrl||this.url){this.requestData(node,callback,scope||node);}},doPreload:function(node){if(node.attributes.children){if(node.childNodes.length<1){var cs=node.attributes.children;node.beginUpdate();for(var i=0,len=cs.length;i<len;i++){var cn=node.appendChild(this.createNode(cs[i]));if(this.preloadChildren){this.doPreload(cn);}}
node.endUpdate();}
return true;}
return false;},getParams:function(node){var buf=[],bp=this.baseParams;if(this.directFn){buf.push(node.id);if(bp){if(this.paramOrder){for(var i=0,len=this.paramOrder.length;i<len;i++){buf.push(bp[this.paramOrder[i]]);}}else if(this.paramsAsHash){buf.push(bp);}}
return buf;}else{for(var key in bp){if(!Ext.isFunction(bp[key])){buf.push(encodeURIComponent(key),"=",encodeURIComponent(bp[key]),"&");}}
buf.push("node=",encodeURIComponent(node.id));return buf.join("");}},requestData:function(node,callback,scope){if(this.fireEvent("beforeload",this,node,callback)!==false){if(this.directFn){var args=this.getParams(node);args.push(this.processDirectResponse.createDelegate(this,[{callback:callback,node:node,scope:scope}],true));this.directFn.apply(window,args);}else{this.transId=Ext.Ajax.request({method:this.requestMethod,url:this.dataUrl||this.url,success:this.handleResponse,failure:this.handleFailure,scope:this,argument:{callback:callback,node:node,scope:scope},params:this.getParams(node)});}}else{this.runCallback(callback,scope||node);}},processDirectResponse:function(result,response,args){if(response.status){this.processResponse({responseData:Ext.isArray(result)?result:null,responseText:result,argument:args},args.node,args.callback,args.scope);}else{this.handleFailure({argument:args});}},runCallback:function(cb,scope,args){if(Ext.isFunction(cb)){cb.apply(scope,args);}},isLoading:function(){return!!this.transId;},abort:function(){if(this.isLoading()){Ext.Ajax.abort(this.transId);}},createNode:function(attr){if(this.baseAttrs){Ext.applyIf(attr,this.baseAttrs);}
if(this.applyLoader!==false){attr.loader=this;}
if(typeof attr.uiProvider=='string'){attr.uiProvider=this.uiProviders[attr.uiProvider]||eval(attr.uiProvider);}
if(attr.nodeType){return new Ext.tree.TreePanel.nodeTypes[attr.nodeType](attr);}else{return attr.leaf?new Ext.tree.TreeNode(attr):new Ext.tree.AsyncTreeNode(attr);}},processResponse:function(response,node,callback,scope){var json=response.responseText;try{var o=response.responseData||Ext.decode(json);node.beginUpdate();for(var i=0,len=o.length;i<len;i++){var n=this.createNode(o[i]);if(n){node.appendChild(n);}}
node.endUpdate();this.runCallback(callback,scope||node,[node]);}catch(e){this.handleFailure(response);}},handleResponse:function(response){this.transId=false;var a=response.argument;this.processResponse(response,a.node,a.callback,a.scope);this.fireEvent("load",this,a.node,response);},handleFailure:function(response){this.transId=false;var a=response.argument;this.fireEvent("loadexception",this,a.node,response);this.runCallback(a.callback,a.scope||a.node,[a.node]);}});