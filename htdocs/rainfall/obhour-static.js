Ext.onReady(function(){

Ext.namespace('iemdata');

iemdata.networks = [
 ['IA_ASOS','Iowa ASOS'],
 ['AWOS','Iowa AWOS'],
 ['AR_ASOS','Arkansas ASOS']
];

var network_selector = new Ext.form.ComboBox({
             hiddenName:'network',
             store: new Ext.data.SimpleStore({
                      fields: ['abbr', 'name'],
                      data : iemdata.networks
             }),
             valueField:'abbr',
             displayField:'name',
             hideLabel: true,
             typeAhead: true,
             mode: 'local',
             triggerAction: 'all',
             emptyText:'Select a Network...',
             selectOnFocus:true,
             lazyRender: true,
             value:"IA_ASOS",
             width:190
});


var dateselector = new Ext.form.DateField({
    id: "df",
    hideLabel: true,
    value: new Date()
});

var timeselector = new Ext.form.TimeField({
    hideLabel: true,
    increment:60,
    value: new Date(),
    format:'h A',
    id: "tm"
});

var selectform = new Ext.form.FormPanel({
     frame: true,
     id: 'selectform',
     title: 'Product Selector',
     labelWidth:0,
     buttons: [{
         text:'Load Data',
         handler: function() {
           var sff = Ext.getCmp('selectform').getForm();
           var network = sff.findField('network').getValue();
           var dt = sff.findField('df').getValue();
           var tm = sff.findField('tm').getValue();
           var d = new Date.parseDate(tm, 'h A');
          Ext.getCmp('precipgrid').getStore().load({
            params:'network='+network+'&ts='+dt.format('Ymd')+d.format('Hi')
          });
          } // End of handler
     }],
     items: [network_selector, dateselector, timeselector]
});



var pstore = new Ext.data.Store({
      root:'precip',
      autoLoad:false,
      proxy: new Ext.data.HttpProxy({
            url: 'obhour-json.php',
            method: 'GET'
     }),
     reader:  new Ext.data.JsonReader({
        root: 'precip',
            id: 'id'
         }, [
         {name: 'id'},
         {name: 'name'},
         {name: 'p1'},
         {name: 'p2'},
         {name: 'p3'},
         {name: 'p6'},
         {name: 'p12'},
         {name: 'p24'},
         {name: 'p48'},
         {name: 'p96'}
     ])
});

var timelabel = new Ext.Toolbar.TextItem("Testing");

var gpanel =  new Ext.grid.GridPanel({
        id:'precipgrid',
        isLoaded:false,
        store: pstore,
        region:'center',
        tbar:[timelabel],
        loadMask: {msg:'Loading Data...'},
        viewConfig:{forceFit:false},
        cm: new Ext.grid.ColumnModel([
            {header: "ID",  width: 40, sortable: true, dataIndex: 'id'},
            {header: "Name", id: "sitename", width: 150, sortable: true, dataIndex: 'name'},
            {header: "1 Hour", width: 80, sortable: true, dataIndex: 'p1'},
            {header: "2 Hour", width: 80, sortable: true, dataIndex: 'p2'},
            {header: "3 Hour", width: 80, sortable: true, dataIndex: 'p3'},
            {header: "6 Hour", width: 80, sortable: true, dataIndex: 'p6'},
            {header: "12 Hour", width: 80, sortable: true, dataIndex: 'p12'},
            {header: "24 Hour", width: 80, sortable: true, dataIndex: 'p24'},
            {header: "48 Hour", width: 80, sortable: true, dataIndex: 'p48'},
            {header: "96 Hour", width: 80, sortable: true, dataIndex: 'p96'}
        ]),
        stripeRows: true,
        title:'Accumulated Precipitation by Interval',
        autoScroll:true
    });



var viewport = new Ext.Viewport({
    layout:'border',
    items:[
         new Ext.BoxComponent({ // raw
             region:'north',
             el: 'header',
             height:60
         }),
         new Ext.BoxComponent({ // raw
             region:'south',
             el: 'footer',
             height:32
         }),
          { 
             region:'west',
             width:210,
             collapsible:true,
             title: 'Settings',
             layoutConfig:{
                animate:true
             },
             items:[selectform]
         },
         gpanel
         ]
});


//  Ext.getCmp('text-display').activate($v);

//  Ext.getCmp('lsr-grid').on('activate', function(q){
//      if (! this.getStore().isLoaded){
//        this.getStore().load({
//         params:'${json_params}&sbw=1'
//        });
//        this.getStore().isLoaded=true;
//      }
//  }); 

// End of static.js
});
