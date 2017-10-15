odoo.define('web_field_input_type.basic_fields', function (require) {
    "use_strict";

    var fields = require('web.basic_fields');

    fields.InputField.include({
        _prepareInput: function ($input) {
            this.$input = this._super.apply(this, arguments);
            if (this.attrs.options && this.attrs.options.hasOwnProperty("input_type")) {
                this.$input.attr({
                    type: this.attrs.options.input_type
                });
                return this.$input;
            };
        }
    });
});
