/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.direct.PollingProvider=Ext.extend(Ext.direct.JsonProvider,{priority:3,interval:3000,constructor:function(config){Ext.direct.PollingProvider.superclass.constructor.call(this,config);this.addEvents('beforepoll','poll');},isConnected:function(){return!!this.pollTask;},connect:function(){if(this.url&&!this.pollTask){this.pollTask=Ext.TaskMgr.start({run:function(){if(this.fireEvent('beforepoll',this)!==false){if(typeof this.url=='function'){this.url(this.baseParams);}else{Ext.Ajax.request({url:this.url,callback:this.onData,scope:this,params:this.baseParams});}}},interval:this.interval,scope:this});this.fireEvent('connect',this);}else if(!this.url){throw'Error initializing PollingProvider, no url configured.';}},disconnect:function(){if(this.pollTask){Ext.TaskMgr.stop(this.pollTask);delete this.pollTask;this.fireEvent('disconnect',this);}},onData:function(opt,success,xhr){if(success){var events=this.getEvents(xhr);for(var i=0,len=events.length;i<len;i++){var e=events[i];this.fireEvent('data',this,e);}}else{var e=new Ext.Direct.ExceptionEvent({data:e,code:Ext.Direct.exceptions.TRANSPORT,message:'Unable to connect to the server.',xhr:xhr});this.fireEvent('data',this,e);}}});Ext.Direct.PROVIDERS['polling']=Ext.direct.PollingProvider;