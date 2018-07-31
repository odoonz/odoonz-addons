odoo.define('qweb_txt_report.report', function (require) {
'use strict';

var ActionManager = require('web.ActionManager');
var crash_manager = require('web.crash_manager');
var framework = require('web.framework');

ActionManager.include({
    ir_actions_report: function (action, options){
        var self = this;
        if (action.report_type === 'qweb-text') {
            framework.blockUI();
            var report_txt_url = 'report/text/' + action.report_name;
            if(action.context.active_ids){
                report_txt_url += '/' + action.context.active_ids.join(',');
            } else {
                report_txt_url += '?options=' + encodeURIComponent(JSON.stringify(action.data));
                report_txt_url += '&context=' + encodeURIComponent(JSON.stringify(action.context));
            }
            self.getSession().get_file({
                url: report_txt_url,
                data: {data: JSON.stringify([
                    report_txt_url,
                    action.report_type,
                ])},
                error: crash_manager.rpc_error.bind(crash_manager),
                success: function (){
                    if(action && options && !action.dialog){
                        options.on_close();
                    }
                },
            });
            framework.unblockUI();
            return;
        }
        return self._super(action, options);
    }
});
});
