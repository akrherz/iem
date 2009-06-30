/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */

(function() {

Ext.a11y.ARIA = Ext.apply(new Ext.util.Observable(), function() {
    return {
        setRole : function(el, role) {
            el = Ext.getDom(el);
            if(el) {
                el.setAttribute('role', role.toString());
            }
        },
        
        setProperty : function(el, key, value) {
            el = Ext.getDom(el);
            if(el) {
                el.setAttribute(key.toString(), value.toString());
            }                
        }
    }
}());

var ARIA = Ext.a11y.ARIA;

Ext.override(Ext.tree.TreeNode, {
    render : function(bulkRender){
        this.ui.render(bulkRender);
        if(!this.rendered){
            // make sure it is registered
            this.getOwnerTree().registerNode(this);
            this.rendered = true;
            this.fireEvent('noderender', this);
            if(this.expanded){
                this.expanded = false;
                this.expand(false, false);
            }
        }
    }
});

Ext.override(Ext.tree.TreePanel, {
    initARIA : function() {
        Ext.tree.TreePanel.superclass.initARIA.call(this);
        this.getSelectionModel().on('selectionchange', this.onNodeSelect, this);
        this.ariaTreeEl = this.body.down('.x-tree-root-ct');
        this.on('collapsenode', this.onNodeCollapse, this);
        this.on('expandnode', this.onNodeExpand, this);
    },
    
    // private
    registerNode : function(node){
        if(this.nodeHash[node.id] === undefined) {
            node.on('noderender', this.onNodeRender, this);
        }
        this.nodeHash[node.id] = node;
    },

    // private
    unregisterNode : function(node){
        node.un('noderender', this.onNodeRender, this);
        delete this.nodeHash[node.id];
    },
    
    onNodeRender : function(node) {
        var a = node.ui.anchor,
            level = this.rootVisible ? 1 : 0,
            pnode = node;
                                
        if(node.isRoot) {
            ARIA.setRole(this.ariaTreeEl, 'tree');
            ARIA.setProperty(this.ariaTreeEl, 'aria-labelledby', Ext.id(node.ui.textNode));
            ARIA.setProperty(this.ariaTreeEl, 'aria-activedescendant', 'false');
            if(!this.rootVisible) {
                return;
            }
        }
        ARIA.setRole(node.ui.wrap, 'treeitem');
        ARIA.setProperty(node.ui.wrap, 'aria-labelledby', Ext.id(node.ui.textNode));            
        ARIA.setProperty(node.ui.wrap, 'aria-expanded', 'false');
        ARIA.setProperty(node.ui.wrap, 'aria-selected', 'false');
        while (pnode.parentNode) {
            level++;
            pnode = pnode.parentNode;
        }
        ARIA.setProperty(node.ui.wrap, 'aria-level', level);   
        if(!node.isLeaf()) {
            ARIA.setRole(node.ui.ctNode, 'group');
            ARIA.setProperty(node.ui.wrap, 'aria-expanded', node.isExpanded());
        }
    },
    
    onNodeSelect : function(sm, node) {
        ARIA.setProperty(this.ariaTreeEl, 'aria-activedescendant', Ext.id(node.ui.wrap));
        ARIA.setProperty(node.ui.wrap, 'aria-selected', 'true');
    },
    
    onNodeCollapse : function(node) {
        ARIA.setProperty(node.ui.wrap, 'aria-expanded', 'false');
    },
    
    onNodeExpand : function(node) {
        ARIA.setProperty(node.ui.wrap, 'aria-expanded', 'true');
    }
});
     
})();
/*
<ul role="tree" aria-label="My Feeds" tabindex="-1" aria-activedescendant="ext-gen87">
    <div role="presentation">
        <li role="treeitem" aria-labelledby="ext-gen23" aria-expanded="true">
            <div role="presentation">
                <span role="presentation"/>
                <img role="presentation"/>
                <img role="presentation"/>
                <a tabindex="1" role="presentation">
                    <span id="ext-gen23" aria-expanded="false" aria-selected="false" aria-level="1">My Feeds</span>
                </a>
            </div>
            <ul role="group">
                <li role="treeitem" aria-labelledby="ext-gen84" id="ext-gen87">
                    <div role="presentation">
                        <span class="x-tree-node-indent" role="presentation">
                        <img class="x-tree-icon" src="http://extjs.com/s.gif"/></span>
                        <img role="presentation"/>
                        <img unselectable="on" class="x-tree-node-icon feed-icon" src="http://extjs.com/s.gif" role="presentation"/>
                        <a tabindex="1" href="" class="x-tree-node-anchor" hidefocus="on" role="presentation">
                            <span unselectable="on" id="ext-gen84" aria-expanded="false" aria-selected="true" aria-level="2">ExtJS.com Blog</span>
                        </a>
                    </div>
                    <ul style="display: none;" class="x-tree-node-ct"/>
                </li>
                <li class="x-tree-node" role="treeitem" aria-labelledby="ext-gen88">
                    <div unselectable="on" class="x-tree-node-el x-tree-node-leaf x-unselectable feed" ext:tree-node-id="http://extjs.com/forum/external.php?type=RSS2" role="presentation"><span class="x-tree-node-indent" role="presentation"><img class="x-tree-icon" src="http://extjs.com/s.gif"/></span><img class="x-tree-ec-icon x-tree-elbow" src="http://extjs.com/s.gif" role="presentation"/><img unselectable="on" class="x-tree-node-icon feed-icon" src="http://extjs.com/s.gif" role="presentation"/><a tabindex="1" href="" class="x-tree-node-anchor" hidefocus="on" role="presentation"><span unselectable="on" id="ext-gen88" aria-expanded="false" aria-selected="false" aria-level="2">ExtJS.com Forums</span></a></div><ul style="display: none;" class="x-tree-node-ct"/></li><li class="x-tree-node" role="treeitem" aria-labelledby="ext-gen89"><div unselectable="on" class="x-tree-node-el x-tree-node-leaf x-unselectable feed" ext:tree-node-id="http://feeds.feedburner.com/ajaxian" role="presentation"><span class="x-tree-node-indent" role="presentation"><img class="x-tree-icon" src="http://extjs.com/s.gif"/></span><img class="x-tree-ec-icon x-tree-elbow-end" src="http://extjs.com/s.gif" role="presentation"/><img unselectable="on" class="x-tree-node-icon feed-icon" src="http://extjs.com/s.gif" role="presentation"/><a tabindex="1" href="" class="x-tree-node-anchor" hidefocus="on" role="presentation"><span unselectable="on" id="ext-gen89" aria-expanded="false" aria-selected="false" aria-level="2">Ajaxian</span></a></div><ul style="display: none;" class="x-tree-node-ct"/></li></ul></li></div></ul>
                    
*/