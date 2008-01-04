Ext.onReady(function(){
    // basic tabs 1, built from existing content
    var tabs = new Ext.TabPanel({
        renderTo: 'tabs1',
        width:900,
        frame:true,
        plain:true,
        enableTabScroll:true,
        defaults:{autoHeight: true},
        items:[
            {contentEl:'svs0', title: 'Issuance'},
            {contentEl:'svs1', title: 'Update 1'},
        ],
        activeTab: 1,
    });
});
