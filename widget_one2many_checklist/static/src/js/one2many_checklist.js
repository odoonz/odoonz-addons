
odoo.define('widget.CheckListRenderer', function (require) {
"use strict";

var BasicModel = require('web.BasicModel');
var BasicRenderer = require('web.BasicRenderer');
var core = require('web.core');
var view_dialogs = require('web.view_dialogs');
var _t = core._t;
var Qweb = core.qweb;


var CheckListRenderer = BasicRenderer.extend({
	template: "one2many_checklist",
	template_item: "one2many_checklist_item",
	events: {
        // 'click .add_new_item': '_onAddRecord',
        'click .item_delete': '_onDeleteRecord',
        'change .o_input': '_onChangeRecord',
        // 'focusout .o_input': '_onChangeRecord',
    },
	init: function (parent, state, params) {
        this._super.apply(this, arguments);
        
        this.editable = params.editable;
        this.project_id = this.__parentedParent.record.data.project_id;
        
        var attrs = this.arch.attrs;
        this.namefield = (attrs.namefield !== undefined && this.state.fields[attrs.namefield] !== undefined) ? attrs.namefield : false;
        this.summaryfield = (attrs.summaryfield !== undefined && this.state.fields[attrs.summaryfield] !== undefined) ? attrs.summaryfield : false;
        var self = this;
        // this.many2onefield = 't_line';
        
        if(!this.namefield || !this.summaryfield){
        	throw new Error(_t("'namefield' & 'summaryfield' are required for render checklist"));
        }
    },
    start: function () {
        if (this.editable) {
            // core.bus.on('click', this, this._onWindowClicked.bind(this));
        }
        return this._super();
    },
    
    _renderView: function () {
        var self = this;
        
        
        this.$(".items_list").html(Qweb.render(this.template_item, this));
        if(this.editable){
            var summaryfield = false;
        _.each(this.arch.children,function(a){
            if(a.attrs.name == self.summaryfield){
                summaryfield =  a.attrs;
            }
        });
        if(summaryfield.readonly != undefined && summaryfield.readonly){
            this.$('textarea').hide();

        }
        }
        
    	return this._super();
    },
    // _onAddRecord: function (event) {
    //     event.preventDefault();
    //     event.stopPropagation();
        
    //     // Trigger for Add
    //     this.trigger_up('add_record');
    // },
    _onChangeRecord: function(event){
    	event.preventDefault();
        event.stopPropagation();
    	
        var $ele = $(event.currentTarget);
    	var id = $ele.closest(".checklist_item").attr("id");
    	if(id){
	    	var changes = {};
            changes[$ele.attr("name")] = $ele.val();
            // changes[this.many2onefield] = parseInt($ele.closest('.checklist_item').find('[name="'+this.many2onefield+'"]').val());
	    	this.trigger_up('field_changed', {
	            dataPointID: id,
	            changes: changes,
	        });
    	}
    },
    _onDeleteRecord: function(event){
    	event.preventDefault();
        event.stopPropagation();
    	
    	var id = $(event.currentTarget).closest(".checklist_item").attr("id");
    	if(id){ // Trigger for remove
    		this.trigger_up('list_record_delete', {id: id});
    	}
    },
    getEditableRecordID: function () {
        return null;
    },
    confirmUpdate: function (state, id, fields, ev) {
    	return $.when();
    },
    editRecord: function (recordID) {
    	return false;
    },
   
});
return CheckListRenderer;

});


odoo.define('widget.one2many_checklist', function (require) {
'use strict';

var core = require('web.core');
var registry = require('web.field_registry');
var relational_fields = require("web.relational_fields");
var CheckListRenderer = require('widget.CheckListRenderer');
var _t = core._t;
var Qweb = core.qweb;


var one2many_checklist = relational_fields.FieldOne2Many.extend({
	init: function () {
        this._super.apply(this, arguments);
        
        if(this.field.type != "one2many"){
        	throw new Error(_t("Widget 'one2many_checklist' only allow for 'one2many' field"));
        }
    },
    _render: function () {
        if (!this.view) {
            return this._super();
        }
        if (this.renderer) {
            this.currentColInvisibleFields = this._evalColumnInvisibleFields();
            this.renderer.updateState(this.value, {'columnInvisibleFields': this.currentColInvisibleFields});
            this.pager.updateState({ size: this.value.count });
            return $.when();
        }
        var arch = this.view.arch;
        var viewType;
        if (arch.tag === 'tree') {
            viewType = 'list';
            this.currentColInvisibleFields = this._evalColumnInvisibleFields();
            this.renderer = new CheckListRenderer(this, this.value, {
                arch: arch,
                editable: this.mode === 'edit' && arch.attrs.editable,
                viewType: viewType,
                columnInvisibleFields: this.currentColInvisibleFields,
            });
        }
        
        this.$el.addClass('o_field_x2many o_field_x2many_' + viewType);
        return this.renderer ? this.renderer.appendTo(this.$el) : this._super();
    },
    
});



// Register
registry.add("one2many_checklist", one2many_checklist);

});
