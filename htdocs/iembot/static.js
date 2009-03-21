Ext.onReady(function(){

Ext.override(Ext.Panel, {
    setIconCls: function(i) {
        Ext.fly(this.ownerCt.getTabEl(this)).child('.x-tab-strip-text').replaceClass(this.iconCls, i);
        this.setIconClass(i);
    }
});

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
    st.on('beforeload', function(self, options){
        self.baseParams = {'seqnum': self.seqnum};
    });
    st.on('load', function(self, records, idx){
        for (i=0;i<records.length;i++){
          if (records[i].get("seqnum") > self.seqnum){ 
             self.seqnum = records[i].get("seqnum");
          }
        }
        if (records.length > 0){ 
           self.applySort(); 
           self.fireEvent("datachanged", self);
           if (tabPanel.getActiveTab() != Ext.getCmp(tabid)){
               Ext.getCmp(tabid).setIconCls('new-tab');
           }
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
        iconCls:'tabno',
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
    gp.on('activate', function(self){
        self.setIconCls('tabno');
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
          store: new Ext.data.SimpleStore({
                    fields: ['channelid', 'channelname'],
                    data : iemdata.channels
          }),
          valueField:'channelid',
          displayField:'channelname',
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
  addTab( record.get("channelid"), record.get("channelname") );
});


var configPanel = new Ext.FormPanel({
  frame: true,
  title: 'Configuration',
  items: [ channelSelector ]
});

tabPanel = new Ext.TabPanel({
    id:'tabs',
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
