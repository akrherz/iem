Ext.onReady(function(){
    const btn = Ext.get("create-grid");
    btn.on("click", () =>{
        btn.dom.disabled = true;
        
        // create the grid
        var grid = new Ext.ux.grid.TableGrid("datagrid", {
            stripeRows: true // stripe alternate rows
        });
        grid.render();
    }, false, {
        single: true
    }); // run once

});