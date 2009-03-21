Ext.onReady(function(){

Ext.override(Ext.Panel, {
    setIconCls: function(i) {
        Ext.fly(this.ownerCt.getTabEl(this)).child('.x-tab-strip-text').replaceClass(this.iconCls, i);
        this.setIconClass(i);
    }
});

var tabPanel;

Ext.override(Date, {
    toUTC : function() {
                        // Convert the date to the UTC date
        return this.add(Date.MINUTE, this.getTimezoneOffset());
    },
    
    fromUTC : function() {
                        // Convert the date from the UTC date
        return this.add(Date.MINUTE, -this.getTimezoneOffset());
    }    
}); 

var LinkInterceptor = {
    render: function(p){
        p.body.on({
            'mousedown': function(e, t){ // try to intercept the easy way
                t.target = '_blank';
            },
            'click': function(e, t){ // if they tab + enter a link, need to do it old fashioned way
                if(String(t.target).toLowerCase() != '_blank'){
                    e.stopEvent();
                    window.open(t.href);
                }
            },
            delegate:'a'
        });
    }
};



function UTCStringToDate(dtStr, format){
    var dt = Date.parseDate(dtStr, format);
    if (dt == undefined) return ''; // or whatever you want to do
    return dt.fromUTC();
} 


var addTab = function(tabid, tabname) {
    var a = tabPanel.find("id", tabid);
    if (a.length > 0){ tabPanel.setActiveTab(tabid); return; }

    st = new Ext.data.Store({
        roomname:tabid,
        baseParams:{seqnum:0},
        seqnum:0,
                    autoLoad:true,
                    proxy: new Ext.data.HttpProxy({
                        url: '/iembot-json/room/'+ tabid ,
                        method: 'GET'
                    }),
                    reader: new Ext.data.JsonReader({
                        root: 'messages',
                        id:'seqnum'
                        }, [
                            {name: 'seqnum', type: 'int'},
                       {name: 'ts', type: 'date', dateFormat: 'Y-m-d h:i:s',
convert: function(v){ return UTCStringToDate(v, "Y-m-d h:i:s");} },
                            {name: 'author'},
                            {name: 'message'}
                    ])
    });
    st.setDefaultSort('ts', 'DESC');
    st.on('beforeload', function(self, options){
        self.baseParams = {'seqnum': self.seqnum};
        Ext.getCmp(self.roomname +"-status").showBusy();
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
        Ext.getCmp(self.roomname +"-status").clearStatus();
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
        listeners: LinkInterceptor,
        iconCls:'tabno',
        tbar:[
          new Ext.Button({
            text:'Clear Room Log',
            listeners: {
              click: function() {
                tabPanel.getActiveTab().getStore().removeAll();
              }  // End of handler
            }
          }),
         new Ext.StatusBar({
           id: tabid+'-status',
           defaultText: ''
         })
        ],
                closable: true,
                store: st,
                columns: [
                  {header:'Timestamp', width: 100, sortable:false,
                   dataIndex: 'ts', renderer: Ext.util.Format.dateRenderer('m/d g:i A')},
                  {header:'Author', width: 100, sortable:false,
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

var roomSelector = new Ext.form.ComboBox({
          store: new Ext.data.SimpleStore({
                    fields: ['roomid', 'roomname'],
                    data : chatdata.rooms
          }),
          valueField:'roomid',
          displayField:'roomname',
  fieldLabel: 'Available Rooms',
  tpl: '<tpl for="."><div class="x-combo-list-item">[{roomid}] {roomname}</div></tpl>',
          typeAhead: true,
          mode: 'local',
          triggerAction: 'all',
          emptyText:'Select a Room...',
          selectOnFocus:true,
          listWidth:180,
          width:180
});
roomSelector.on("select", function(self, record, idx){
  addTab( record.get("roomid"), record.get("roomname") );
});


var configPanel = new Ext.FormPanel({
  frame: true,
  labelAlign:'top',
  items: [ roomSelector ]
});

tabPanel = new Ext.TabPanel({
    id:'tabs',
    region:'center',
    plain:true,
    enableTabScroll:true,
    height:.75,
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
            region:'west',
            width: 200,
            collapsible:true,
            title:'Options',
            items:[configPanel]
         },{
             region:'south',
             height:50,
             contentEl: 'iem-footer'
         }, tabPanel
         ]
});

// End of static.js
});
