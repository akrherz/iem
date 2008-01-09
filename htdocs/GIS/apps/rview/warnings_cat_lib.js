Ext.onReady(function(){
    var p = new Ext.Panel({
        title: 'Product Overview',
        collapsible:false,
        width:320,
        height:500,
        items: [Ext.get('controller')]
    });
    p.render('controller-side');

    var expander = new Ext.grid.RowExpander({
        tpl : new Ext.Template(
            '<p><b>Remark:</b> {remark}<br>'
        )
    });

    // create the data store
    var store = new Ext.data.SimpleStore({
        fields: [
           {name: 'i', type: 'int'},
           {name: 'Time'},
           {name: 'Type'},
           {name: 'Magnitude'},
           {name: 'City'},
           {name: 'County'},
           {name: 'remark'}
        ]
    });

    var store2 = new Ext.data.SimpleStore({
        fields: [
           {name: 'i', type: 'int'},
           {name: 'Time'},
           {name: 'Type'},
           {name: 'Magnitude'},
           {name: 'City'},
           {name: 'County'},
           {name: 'remark'}
        ]
    });

    var store3 = new Ext.data.SimpleStore({
        fields: [
           {name: 'i', type: 'int'},
           {name: 'ugc'},
           {name: 'name'},
           {name: 'status'},
           {name: 'issue'},
           {name: 'expire'}
        ]
    });


    // create the Grid
    var grid = new Ext.grid.GridPanel({
        id:'grid',
        store: store,
        cm: new Ext.grid.ColumnModel([
            expander,
            {id: 'i', header: "Time", sortable: true, dataIndex: 'Time'},
            {header: "Type", sortable: true, dataIndex: 'Type'},
            {header: "Magnitude", sortable: true, dataIndex: 'Magnitude'},
            {header: "City", sortable: true, dataIndex: 'City'},
            {header: "County", sortable: true, dataIndex: 'County'}
        ]),
        stripeRows: true,
        title:'Storm Reports within Polygon',
        plugins: expander,
        autoScroll:true
    });

    // create the Grid
    var grid2 = new Ext.grid.GridPanel({
        id:'grid2',
        store: store2,
        cm: new Ext.grid.ColumnModel([
            expander,
            {id: 'i', header: "Time", sortable: true, dataIndex: 'Time'},
            {header: "Type", sortable: true, dataIndex: 'Type'},
            {header: "Magnitude", sortable: true, dataIndex: 'Magnitude'},
            {header: "City", sortable: true, dataIndex: 'City'},
            {header: "County", sortable: true, dataIndex: 'County'}
        ]),
        stripeRows: true,
        title:'All Storm Reports within Time Period',
        plugins: expander,
        autoScroll:true
    });


    // create the Grid
    var grid3 = new Ext.grid.GridPanel({
        id:'grid3',
        store: store3,
        cm: new Ext.grid.ColumnModel([
            {id: 'i', header: "UGC", width: 50, sortable: true, dataIndex: 'ugc'},
            {header: "Name", width: 200, sortable: true, dataIndex: 'name'},
            {header: "Status", width: 50, sortable: true, dataIndex: 'status'},
            {header: "Issue", sortable: true, dataIndex: 'issue'},
            {header: "Expire", sortable: true, dataIndex: 'expire'}
        ]),
        stripeRows: true,
        autoScroll:true,
        title:'Geography Included',
        collapsible: false,
        animCollapse: false
    });


    var tabs22 = new Ext.TabPanel({
        renderTo: 'displaytabs',
        width:600,
        height:500,
        plain:true,
        enableTabScroll:true,
        items:[
            {contentEl:'radar', title: 'RADAR'},
            grid,
            grid2,
            grid3
         ],
        activeTab: 0
    });

    var tabs = new Ext.TabPanel({
        applyTo: 'tabs1',
        id:'text-display',
        width:800,
        defaults:{autoHeight: true},
        frame:true,
        plain:true,
        enableTabScroll:true,
        deferredRender:false,
        autoTabs:true,
        resizeTabs:false,
        autoScroll:true
  }); 

});

