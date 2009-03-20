Ext.onReady(function(){

var tabPanel;

var addTab = function(tabid, tabname) {
    var a = tabPanel.find("id", tabid);
    if (a.length > 0){ tabPanel.setActiveTab(tabid); return; }

    tabPanel.add({
        id: tabid,
        title: tabname,
        closable: true,
        autoscroll: true,
        items: [
            new Ext.grid.GridPanel({
                store: new Ext.data.Store({
                    root:'messages',
                    autoLoad:true,
                    proxy: new Ext.data.HttpProxy({
                        url: '/iembot-json',
                        method: 'GET'
                    }),
                    reader: new Ext.data.JsonReader({
                        root: 'messages',
                        id:'ts'
                        }, [
                            {name: 'ts'},
                            {name: 'author'},
                            {name: 'message'}
                    ])
                }),
                columns: [
                  {id:'ts', header:'Timestamp', width: 75, sortable:true,
                   dataIndex: 'ts'},
                  {header:'Author', width: 75, sortable:true,
                   dataIndex: 'author'},
                  {header:'Message', width:'auto', sortable:true,
                   dataIndex: 'message'}
                ],
                stripeRows: true,
                height: 'auto',
                width: 'auto'
            })
        ]
    });

}

var channelSelector = new Ext.form.ComboBox({
          hiddenName:'wfo',
          store: new Ext.data.SimpleStore({
                    fields: ['abbr', 'wfo'],
                    data : iemdata.wfos 
          }),
          valueField:'abbr',
          displayField:'wfo',
          typeAhead: true,
          mode: 'local',
          triggerAction: 'all',
          emptyText:'Select a Channel...',
          hideLabel:true,
          selectOnFocus:true,
          listWidth:180,
          width:180
});
channelSelector.on("select", function(self, record, idx){
  addTab( record.get("abbr"), record.get("wfo") );
});


var configPanel = new Ext.FormPanel({
  frame: true,
  title: 'Configuration',
  items: [ channelSelector ]
});

tabPanel = new Ext.TabPanel({
    plain:true,
    enableTabScroll:true,
    defaults:{bodyStyle:'padding:5px'},
    items:[
      {contentEl:'help', title: 'Help', saveme:true}
    ],
    activeTab:0
});


var viewport = new Ext.Viewport({
    layout:'border',
    items:[{ 
             region:'north',
             height:130,
             contentEl: 'iem-header'
         },{
            region:'south',
            width:130,
            contentEl: 'iem-footer'
         },{
            region:'center',
            items:[tabPanel]
         },{
            region:'west',
            width: 200,
            items:[configPanel]
         }
         ]
});

// End of static.js
});
