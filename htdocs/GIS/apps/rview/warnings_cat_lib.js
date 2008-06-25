Ext.onReady(function(){
Ext.namespace('Ext.ux.plugins');
Ext.ux.plugins.ContainerMask = function(opt) {
    var options = opt||{};

    return {
        init: function(c) {
            Ext.applyIf(c,{
                showMask : function(msg, msgClass, maskClass){
                    var el;
                    if(this.rendered && (el = this[options.el] || Ext.get(options.el) || this.getEl?this.getEl():null)){
                      el.mask.call(el,msg || options.msg, msgClass || options.msgClass, maskClass || options.maskClass);
                    }
                },
                hideMask : function(){
                    var el;
                    if(this.rendered && (el = this[options.el] || Ext.get(options.el) ||  this.getEl?this.getEl():null)){ 
                      el.unmask.call(el);
                    }
                }
            });
            if(options.masked){ 
                c.on('render', c.showMask.createDelegate(c,[null]) ,c, {delay:10, single:true}) ; 
            }
        }
    };
};

   Ext.ux.grid.filter.StringFilter.prototype.icon = 'find.png';

   var filters = new Ext.ux.grid.GridFilters({
        filters:[
               {type: 'string',  
                dataIndex: 'locations'
                }
                ],
        phpMode:false,
        local:true
        });


    var p = new Ext.Panel({
        title: 'Product Overview',
        collapsible:false,
        width:320,
        height:500,
        items: [Ext.get('controller')]
    });
    p.render('controller-side');


    var expander = new Ext.grid.RowExpander({
        id: 'testexp',
        width: 30,
        tpl : new Ext.Template(
            '<p><b>Remark:</b> {remark}<br>'
        )
    });
    var expander2 = new Ext.grid.RowExpander({
        id: 'testexp2',
        width: 30,
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
          autoLoad:false,
          proxy: new Ext.data.HttpProxy({
                url: 'json-lsrs.php',
                method: 'GET'
          }),
          reader:  new Ext.data.JsonReader({
            root: 'lsrs',
            id: 'id'
           }, [
           {name: 'id'},
           {name: 'valid'},
           {name: 'type'},
           {name: 'event'},
           {name: 'magnitude'},
           {name: 'city'},
           {name: 'county'},
           {name: 'remark'}
          ])
        });

    var pstore = new Ext.data.Store({
          root:'products',
          autoLoad:false,
          proxy: new Ext.data.HttpProxy({
                url: 'json-list.php',
                method: 'GET'
          }),
          reader:  new Ext.data.JsonReader({
            root: 'products',
            id: 'id'
           }, [
           {name: 'id'},
           {name: 'locations'},
           {name: 'wfo'},
           {name: 'year'},
           {name: 'area', type: 'float'},
           {name: 'significance'},
           {name: 'phenomena'},
           {name: 'eventid'},
           {name: 'issued'},
           {name: 'expired'}
          ])
        });

    var jstore2 = new Ext.data.Store({
          autoLoad:false,
          proxy: new Ext.data.HttpProxy({
                url: 'json-lsrs.php',
                method: 'GET'
          }),
          reader:  new Ext.data.JsonReader({
            root: 'lsrs',
            id: 'id'
           }, [
           {name: 'id'},
           {name: 'valid'},
           {name: 'type'},
           {name: 'event'},
           {name: 'magnitude'},
           {name: 'city'},
           {name: 'county'},
           {name: 'remark'}
          ])
        });



    // create the Grid
    var grid = new Ext.grid.GridPanel({
        id:'lsr-grid',
        isLoaded:false,
        store: jstore,
        loadMask: {msg:'Loading Data...'},
        cm: new Ext.grid.ColumnModel([
            expander,
            {header: "Time", sortable: true, dataIndex: 'valid'},
            {header: "Event", width: 100, sortable: true, dataIndex: 'event'},
            {header: "Magnitude", sortable: true, dataIndex: 'magnitude'},
            {header: "City", width: 200, sortable: true, dataIndex: 'city'},
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
        isLoaded:false,
        store: jstore2,
        loadMask: {msg:'Loading Data...'},
        cm: new Ext.grid.ColumnModel([
            expander2,
            {header: "Time (UTC)", sortable: true, dataIndex: 'valid'},
            {header: "Event", width: 100, sortable: true, dataIndex: 'event'},
            {header: "Magnitude", sortable: true, dataIndex: 'magnitude'},
            {header: "City", width: 200, sortable: true, dataIndex: 'city'},
            {header: "County", sortable: true, dataIndex: 'county'}
        ]),
        stripeRows: true,
        title:'All Storm Reports within Time Period',
        plugins: expander2,
        autoScroll:true
    });


    // create the Grid
    var grid3 = new Ext.grid.GridPanel({
        id:'ugc-grid',
        store: ustore,
        loadMask: {msg:'Loading Data...'},
        cm: new Ext.grid.ColumnModel([
            {header: "UGC", width: 50, sortable: true, dataIndex: 'ugc'},
            {header: "Name", width: 200, sortable: true, dataIndex: 'name'},
            {header: "Status", width: 50, sortable: true, dataIndex: 'status'},
            {header: "Issue (UTC)", sortable: true, dataIndex: 'issue'},
            {header: "Expire (UTC)", sortable: true, dataIndex: 'expire'}
        ]),
        stripeRows: true,
        autoScroll:true,
        title:'Geography Included',
        collapsible: false,
        animCollapse: false
    });

    function myEventID(val, p, record){
        return "<span><a href=\"warnings_cat.phtml?year="+ record.get('year') +"&wfo="+ record.get('wfo') +"&phenomena="+ record.get('phenomena') +"&significance="+ record.get('significance') +"&eventid="+ val +"\">" + val + "</a></span>";
    }

function mySplitter(val) {
    var tokens = val.split(",");
    var s = "";
    for(i=0; i < tokens.length; i++) {
      s += tokens[i] +",";
      if ((i % 3) == 0 && i > 0) s += "<br />";
    }
    return '<span>' + s + '</span>';
}

    // create the Grid
    var grid4 = new Ext.grid.GridPanel({
        id:'products-grid',
        store: pstore,
        width:640,
        loadMask: {msg:'Loading Data...'},
        cm: new Ext.grid.ColumnModel([
          {header: "Event", renderer: myEventID, width: 40, sortable: true, dataIndex: 'eventid'},
          {header: "Issued (UTC)", width: 140, sortable: true, dataIndex: 'issued'},
          {header: "Expired (UTC)", width: 140, sortable: true, dataIndex: 'expired'},
          {header: "Area km**2", width: 70, sortable: true, dataIndex: 'area'},
          {header: "Locations", id:"locations", width: 250, sortable: true, dataIndex: 'locations'}
        ]),
        plugins: filters,
        stripeRows: true,
        autoScroll:true,
        title:'Other Events',
        collapsible: false,
        animCollapse: false
    });


    var tabs22 = new Ext.TabPanel({
        renderTo: 'displaytabs',
        id: 'top-display',
        width:660,
        height:560,
        plain:true,
        enableTabScroll:true,
        items:[
            grid,
            grid2,
            grid3,
            grid4
         ],
        activeTab: 0
    });

  var tabs = new Ext.TabPanel({
        applyTo: 'tabs1',
        id: 'text-display',
        width:660,
        height:560,
        plain:true,
        frame:true,
        enableTabScroll:true,
        tbar:[{
         id:'print',
         text: 'View Text in New Window & Print',
         handler: function(e, target){
              var a = tabs.getActiveTab();
              var myForm = new Ext.form.BasicForm("my-form-id", {
                standardSubmit:true
              });
              myForm.getEl().createChild({
                 tag: 'input',
                 type: 'hidden',
                 name: 'data',
                 id:'data',
                 value: a.getEl().dom.childNodes[0].childNodes[0].innerHTML
              });
              myForm.submit();
            }
        }],
        autoTabs:true,
        deferredRender:false
    });


});
