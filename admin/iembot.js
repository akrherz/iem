Ext.ns('App');
Ext.onReady(function(){
    var ds2;
    var ds = new Ext.data.Store({
        proxy: new Ext.data.HttpProxy({
            url		: 'iembot_channels.php'
        }),
        baseParams	: {'mode': 'avail', 'chatroom': App.roomname},
        reader: new Ext.data.JsonReader({
            root: 'channels',
            totalProperty: 'totalCount',
            id: 'id'
        }, [
            {name: 'id', mapping: 'id'},
            {name: 'text', mapping: 'text'}
        ])
    });


    // Custom rendering Template
    var resultTpl = new Ext.XTemplate(
        '<tpl for="."><div class="search-item">',
            '<span>{text} ({id})</span>',
        '</div></tpl>'
    );
    
    var search = new Ext.form.ComboBox({
        store: ds,
        displayField:'text',
        typeAhead: false,
        loadingText: 'Searching...',
        minChars	: 2,
        width: 280,
        pageSize:10,
        hideTrigger:true,
        applyTo: 'channelsearch',
        itemSelector: 'div.search-item',
        tpl			: resultTpl,
        onSelect: function(record){ // override default onSelect to do redirect
            Ext.Ajax.request({
            	   url: 'iembot_channels.php',
            	   success: function(){
            			ds2.reload({add:false});
            		},
            	   params: { chatroom: App.roomname,
            		   mode: 'add',
            		   channel: record.id}
            	});
        }
    });
    var mytree = new Ext.tree.TreePanel({
    	renderTo	: 'channel_del',
    	height		: 150,
    	width		: 300,
    	autoScroll	: true,
    	collapsed	: false,
    	lines		: false,
    	rootVisible	: false,
    	listeners	: {
    		click	: function(n){
    			 Ext.Ajax.request({
              	   url: 'iembot_channels.php',
              	   success: function(){
              			ds2.reload({add:false});
              		},
              	   params: { chatroom: App.roomname,
              		   mode: 'remove',
              		   channel: n.attributes.channelid}
              	});
    }
    	},
    	root        : new Ext.tree.TreeNode()
    });
    ds2 = new Ext.data.Store({
    	autoLoad: true,
        proxy: new Ext.data.HttpProxy({
            url: 'iembot_channels.php'
        }),
        baseParams: {chatroom: App.roomname,
    		mode: 'subs'},
        listeners: {
    		load : function(st, records, options){
    			mytree.root.removeAll();
    			for(var i=0;i<records.length;i++){
    	              mytree.root.appendChild({
    	                  text 		: records[i].data.text +' ('+ records[i].data.id +')', 
    	                  channelid	: records[i].data.id,
    	                  leaf 		: true
    	               });

    			}
    		}
    	},
        reader: new Ext.data.JsonReader({
            root: 'channels',
            totalProperty: 'totalCount',
            id: 'id'
        }, [
            {name: 'id', mapping: 'id'},
            {name: 'text', mapping: 'text'}
        ])
    });
    






});
