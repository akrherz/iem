/*
 * Ext JS Library 3.0 RC2
 * Copyright(c) 2006-2009, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */


Ext.ux.ProgressBarPager  = Ext.extend(Object, {
	progBarWidth   : 225,
	defaultText    : 'Loading...',
	defaultAnimCfg : {
		duration   : 1,
		easing     : 'bounceOut'	
	},												  
	constructor : function(config) {
		if (config) {
			Ext.apply(this, config);
		}
	},
	//public
	init : function (parent) {
		
		if(parent.displayInfo){
			this.parent = parent;
			var ind  = parent.items.indexOf(parent.displayItem);
			parent.remove(parent.displayItem, true);
			this.progressBar = new Ext.ProgressBar({
				text    : this.defaultText,
				width   : this.progBarWidth,
				animate :  this.defaultAnimCfg
			});					
		   
			parent.displayItem = this.progressBar;
			
			parent.add(parent.displayItem);	
			parent.doLayout();
			Ext.apply(parent, this.parentOverrides);		
			
			this.progressBar.on('render', function(pb) {
				pb.el.applyStyles('cursor:pointer');

				pb.el.on('click', this.handleProgressBarClick, this);
			}, this);
			
		
			// Remove the click handler from the 
			this.progressBar.on({
				scope         : this,
				beforeDestroy : function() {
					this.progressBar.el.un('click', this.handleProgressBarClick, this);	
				}
			});	
						
		}
		  
	},
	//private
	// This method handles the click for the progress bar
	handleProgressBarClick : function(e){
		var parent = this.parent;
		var displayItem = parent.displayItem;
		
		var box = this.progressBar.getBox();
		var xy = e.getXY();
		var position = xy[0]-box.x;
		var pages = Math.ceil(parent.store.getTotalCount()/parent.pageSize);
		
		var newpage = Math.ceil(position/(displayItem.width/pages));
		parent.changePage(newpage);
	},
	
	//overrides, private
	parentOverrides  : {
		//Private
		// This method updates the information via the progress bar.
		updateInfo : function(){
			if(this.displayItem){
				var count   = this.store.getCount();
				var pgData  = this.getPageData();
				var pageNum = this.readPage(pgData);
				
				var msg    = count == 0 ?
					this.emptyMsg :
					String.format(
						this.displayMsg,
						this.cursor+1, this.cursor+count, this.store.getTotalCount()
					);
					
				pageNum = pgData.activePage; ;	
				
				var pct	= pageNum / pgData.pages;	
				
				this.displayItem.updateProgress(pct, msg, this.animate || this.defaultAnimConfig);
			}
		}
	}
});
