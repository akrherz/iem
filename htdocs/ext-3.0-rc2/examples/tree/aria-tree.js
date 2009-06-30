/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */

/*
 * Ext JS Library 3.0 Pre-alpha
 * Copyright(c) 2006-2008, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */

var TreeTest = function(){
    // shorthand
    var Tree = Ext.tree;
    
    return {
        init : function(){
            // yui-ext tree
            var tree = new Tree.TreePanel({
                el:'tree',
                animate:true, 
                autoScroll:true,
                loader: new Tree.TreeLoader({dataUrl:'get-nodes.php'}),
                containerScroll: true,
                border: false,
                height: 300,
                width: 300
            });
                            
            // add a tree sorter in folder mode
            new Tree.TreeSorter(tree, {folderSort:true});
            
            // set the root node
            var root = new Tree.AsyncTreeNode({
                text: 'Ext JS', 
                draggable:false, // disable root node dragging
                id:'source'
            });
            tree.setRootNode(root);
            
            // render the tree
            tree.render();            
            root.expand(false, /*no anim*/ false);
            tree.bodyFocus.fi.setFrameEl(tree.el);     
            tree.getSelectionModel().select(tree.getRootNode()); 
            tree.enter.defer(100, tree);           
        }
    };
}();

Ext.EventManager.onDocumentReady(TreeTest.init, TreeTest, true);