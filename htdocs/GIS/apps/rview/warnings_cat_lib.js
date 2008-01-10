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


    var ustore = new Ext.data.Store({
          root:'ugcs',
          autoLoad:false,
          proxy: new Ext.data.HttpProxy({
                url: 'json-ugc.php',
                method: 'GET'
          }),
          reader:  new Ext.data.JsonReader({
            root: 'ugcs',
            id: 'id'
           }, [
           {name: 'id'},
           {name: 'ugc'},
           {name: 'name'},
           {name: 'status'},
           {name: 'issue'},
           {name: 'expire'}
          ])
        });


    var jstore = new Ext.data.Store({
          root:'lsrs',
          autoLoad:false,
          proxy: new Ext.data.HttpProxy({
                url: 'json-sbw-lsrs.php',
                method: 'GET'
          }),
          reader:  new Ext.data.JsonReader({
            root: 'lsrs',
            id: 'id'
           }, [
           {name: 'id'},
           {name: 'valid'},
           {name: 'type'},
           {name: 'magnitude'},
           {name: 'city'},
           {name: 'county'},
           {name: 'remark'}
          ])
        });

    var jstore2 = new Ext.data.Store({
          root:'lsrs',
          autoLoad:false,
          proxy: new Ext.data.HttpProxy({
                url: 'json-sbw-lsrs.php',
                method: 'GET'
          }),
          reader:  new Ext.data.JsonReader({
            root: 'lsrs',
            id: 'id'
           }, [
           {name: 'id'},
           {name: 'valid'},
           {name: 'type'},
           {name: 'magnitude'},
           {name: 'city'},
           {name: 'county'},
           {name: 'remark'}
          ])
        });



    // create the Grid
    var grid = new Ext.grid.GridPanel({
        id:'lsr-grid',
        store: jstore,
        cm: new Ext.grid.ColumnModel([
            expander,
            {header: "Time", sortable: true, dataIndex: 'valid'},
            {header: "Type", sortable: true, dataIndex: 'type'},
            {header: "Magnitude", sortable: true, dataIndex: 'magnitude'},
            {header: "City", sortable: true, dataIndex: 'city'},
            {header: "County", sortable: true, dataIndex: 'county'}
        ]),
        stripeRows: true,
        title:'Storm Reports within Polygon',
        plugins: expander,
        autoScroll:true
    });

    // create the Grid
    var grid2 = new Ext.grid.GridPanel({
        id:'all-lsr-grid',
        store: jstore2,
        cm: new Ext.grid.ColumnModel([
            expander,
            {header: "Time", sortable: true, dataIndex: 'valid'},
            {header: "Type", sortable: true, dataIndex: 'type'},
            {header: "Magnitude", sortable: true, dataIndex: 'magnitude'},
            {header: "City", sortable: true, dataIndex: 'city'},
            {header: "County", sortable: true, dataIndex: 'county'}
        ]),
        stripeRows: true,
        title:'All Storm Reports within Time Period',
        plugins: expander,
        autoScroll:true
    });


    // create the Grid
    var grid3 = new Ext.grid.GridPanel({
        id:'ugc-grid',
        store: ustore,
        cm: new Ext.grid.ColumnModel([
            {header: "UGC", width: 50, sortable: true, dataIndex: 'ugc'},
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
        width:660,
        height:520,
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

