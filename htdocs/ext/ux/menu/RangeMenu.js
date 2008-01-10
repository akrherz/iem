Ext.namespace("Ext.ux.menu");
Ext.ux.menu.RangeMenu = function(){
	Ext.ux.menu.RangeMenu.superclass.constructor.apply(this, arguments);
	this.updateTask = new Ext.util.DelayedTask(this.fireUpdate, this);

	var cfg = this.fieldCfg;
	var cls = this.fieldCls;
	var fields = this.fields = Ext.applyIf(this.fields || {}, {
		'gt': new Ext.ux.menu.EditableItem({
			icon:  this.icons.gt,
			editor: new cls(typeof cfg == "object" ? cfg.gt || '' : cfg)}),
		'lt': new Ext.ux.menu.EditableItem({
			icon:  this.icons.lt,
			editor: new cls(typeof cfg == "object" ? cfg.lt || '' : cfg)}),
		'eq': new Ext.ux.menu.EditableItem({
			icon:   this.icons.eq, 
			editor: new cls(typeof cfg == "object" ? cfg.gt || '' : cfg)})
	});
	this.add(fields.gt, fields.lt, '-', fields.eq);
	
	for(var key in fields)
		fields[key].on('keyup', function(event, input, notSure, field){
			if(event.getKey() == event.ENTER && field.isValid()){
				this.hide(true);
				return;
			}
			
			if(field == fields.eq){
				fields.gt.setValue(null);
				fields.lt.setValue(null);
			} else {
				fields.eq.setValue(null);
			}
			
			this.updateTask.delay(this.updateBuffer);
		}.createDelegate(this, [fields[key]], true));

	this.addEvents({'update': true});
};
Ext.extend(Ext.ux.menu.RangeMenu, Ext.menu.Menu, {
	fieldCls:     Ext.form.NumberField,
	fieldCfg:     '',
	updateBuffer: 500,
	icons: {
		gt: '/img/small_icons/greater_then.png', 
		lt: '/img/small_icons/less_then.png',
		eq: '/img/small_icons/equals.png'},
		
	fireUpdate: function(){
		this.fireEvent("update", this);
	},
	
	setValue: function(data){
		for(var key in this.fields)
			this.fields[key].setValue(data[key] !== undefined ? data[key] : '');
		
		this.fireEvent("update", this);
	},
	
	getValue: function(){
		var result = {};
		for(var key in this.fields){
			var field = this.fields[key];
			if(field.isValid() && String(field.getValue()).length > 0)
				result[key] = field.getValue();
		}
		
		return result;
	}
});