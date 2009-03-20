Ext.onReady(function(){

var tabPanel;

var addTab = function(tabid, tabname) {
    var a = tabPanel.find("id", tabid);
    if (a.length > 0){ tabPanel.setActiveTab(tabid); return; }

    st = new Ext.data.Store({

                    autoLoad:false,
                    seqnum: 0,
                    proxy: new Ext.data.HttpProxy({
                        url: '/nwsbot-json/channel/'+ tabid +'chat',
                        method: 'GET',
                        params:{seqnum:0}
                    }),
                    reader: new Ext.data.JsonReader({
                        root: 'messages',
                        id:'seqnum'
                        }, [
                            {name: 'seqnum', type: 'int'},
                            {name: 'ts'},
                            {name: 'author'},
                            {name: 'message'}
                    ])
    });
    st.on('load', function(self, records, idx){
        for (i=0;i<records.length;i++){
          if (records[i].get("seqnum") > self.seqnum){ 
             self.seqnum = records[i].get("seqnum");
          }
        }
    });
    task = {
      run: function() {
        st.load({add:true, params:{seqnum: st.seqnum}});
      },
      interval:7000
    };

    gp = new Ext.grid.GridPanel({
        id: tabid,
        title: tabname,
                closable: true,
                store: st,
                columns: [
                  {header:'Timestamp', width: 75, sortable:true,
                   dataIndex: 'ts', type: 'date', dateFormat: 'Y-m-d H:i:s'},
                  {header:'Author', width: 75, sortable:true,
                   dataIndex: 'author'},
                  {header:'Message', sortable:true, width: 500,
                   dataIndex: 'message', id: 'message' }
                ],
                autoExpandColumn: 'message',
                stripeRows: true,
                autoScroll:true
    });
    gp.on('activate', function() {
      Ext.TaskMgr.start(task);
    });
    gp.on('destroy', function() {
      Ext.TaskMgr.stop(task);
    });
    tabPanel.add(gp);
    tabPanel.setActiveTab(tabid);
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
    region:'center',
    plain:true,
    enableTabScroll:true,
    height:.75,
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
            height:50,
            contentEl: 'iem-footer'
         },{
            region:'west',
            width: 200,
            collapsible:true,
            items:[configPanel]
         }, tabPanel
         ]
});

// End of static.js
});
