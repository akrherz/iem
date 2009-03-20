Ext.onReady(function(){

var tabPanel;

var addTab = function(tabid, tabname) {
    var a = tabPanel.find("id", tabid);
    if (a.length > 0){ tabPanel.setActiveTab(tabid); return; }

    st = new Ext.data.Store({
        baseParams:{seqnum:0},
        seqnum:0,
                    autoLoad:true,
                    proxy: new Ext.data.HttpProxy({
                        url: '/nwsbot-json/channel/'+ tabid +'chat',
                        method: 'GET'
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
    st.setDefaultSort('ts', 'DESC');
    st.on('beforeload', function(){
        st.baseParams = {'seqnum': st.seqnum};
    });
    st.on('load', function(self, records, idx){
        for (i=0;i<records.length;i++){
          if (records[i].get("seqnum") > st.seqnum){ 
             st.seqnum = records[i].get("seqnum");
          }
        }
        if (records.length > 0){ 
           self.applySort(); 
           self.fireEvent("datachanged", self);
        }
     });

    gp = new Ext.grid.GridPanel({
        viewConfig:{
            onLoad: Ext.emptyFn,
            listeners: {
                beforerefresh: function(v) {
                    v.scrollTop = v.scroller.dom.scrollTop;
                    v.scrollHeight = v.scroller.dom.scrollHeight;
                },
                refresh: function(v) {
                    v.scroller.dom.scrollTop = v.scrollTop + 
        (v.scrollTop == 0 ? 0 : v.scroller.dom.scrollHeight - v.scrollHeight);
                }
            }
        },
        id: tabid,
        title: tabname,
                closable: true,
                store: st,
                columns: [
                  {header:'Timestamp', width: 75, sortable:false,
                   dataIndex: 'ts', type: 'date', dateFormat: 'Y-m-d H:i:s'},
                  {header:'Author', width: 75, sortable:false,
                   dataIndex: 'author'},
                  {header:'Message', sortable:false, width: 500,
                   dataIndex: 'message', id: 'message' }
                ],
                autoExpandColumn: 'message',
                stripeRows: true,
                autoScroll:true
    });

    tabPanel.add(gp);
    tabPanel.setActiveTab(tabid);
}

var task = {
  run: function(){
    tabPanel.items.each( function(c){ 
      if (c.getId() != "helppanel") { 
       c.getStore().reload({add:true});
      } 
    });
  },
  interval: 7000
}
Ext.TaskMgr.start(task);

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
      {contentEl:'help', title: 'Help', id: 'helppanel'}
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
