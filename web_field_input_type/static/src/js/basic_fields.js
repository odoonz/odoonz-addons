odoo.define('web_field_input_type.basic_fields', function (require) {
    "use_strict";

    var fields = require('web.basic_fields');

    fields.FieldChar.include({
        _prepareInput: function ($input) {
            this.$input = this._super.apply(this, arguments);
            if (this.attrs.options && this.attrs.options.hasOwnProperty("input_type")) {
                this.$input.attr({
                    type: this.nodeOptions.isPassword ? 'password' : this.attrs.options.input_type
                });
                return this.$input;
            };
        }
    });

    fields.FieldFloat.include({
        _prepareInput: function ($input) {
            this.$input = this._super.apply(this, arguments);
            this.$input.attr({
                type: this.nodeOptions.isPassword ? 'password' : 'number',
                placeholder: this.attrs.placeholder || "",
                autocomplete: this.nodeOptions.isPassword ?
                    'new-password' :
                    this.attrs.autocomplete,
            });
            return this.$input;
        },
    });

    fields.FieldInteger.include({
        _prepareInput: function ($input) {
            this.$input = this._super.apply(this, arguments);
            this.$input.attr({
                type: this.nodeOptions.isPassword ? 'password' : 'tel',
                placeholder: this.attrs.placeholder || "",
                autocomplete: this.nodeOptions.isPassword ?
                    'new-password' :
                    this.attrs.autocomplete,
            });
            return this.$input;
        },
    });
});
