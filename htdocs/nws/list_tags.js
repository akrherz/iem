// global Ext
Ext.onReady(() => {
    const btn = Ext.get("create-grid1");
    btn.on("click", () => {
        btn.dom.disabled = true;

        // create the grid
        const grid = new Ext.ux.grid.TableGrid("svr", {
            stripeRows: true // stripe alternate rows
        });
        grid.render();
    }, false, {
        single: true
    }); // run once

    const btn2 = Ext.get("create-grid2");
    btn2.on("click", () => {
        btn2.dom.disabled = true;

        // create the grid
        const grid = new Ext.ux.grid.TableGrid("tor", {
            stripeRows: true // stripe alternate rows
        });
        grid.render();
    }, false, {
        single: true
    }); // run once

    const btn3 = Ext.get("create-grid3");
    btn3.on("click", () => {
        btn3.dom.disabled = true;

        // create the grid
        const grid = new Ext.ux.grid.TableGrid("ffw", {
            stripeRows: true // stripe alternate rows
        });
        grid.render();
    }, false, {
        single: true
    }); // run once

    const btn4 = Ext.get("create-grid4");
    btn4.on("click", () => {
        btn4.dom.disabled = true;

        // create the grid
        const grid = new Ext.ux.grid.TableGrid("smw", {
            stripeRows: true // stripe alternate rows
        });
        grid.render();
    }, false, {
        single: true
    }); // run once

});
