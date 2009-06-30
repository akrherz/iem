/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */

Ext.onReady(function() {
  var btn = Ext.get("create-grid");
  btn.on("click", function(){
    btn.dom.disabled = true;

    // create the grid
    var grid = new Ext.ux.TableGrid("the-table", {
      stripeRows: true // stripe alternate rows
    });
    grid.render();
  }, false, {single:true}); // run once
});
