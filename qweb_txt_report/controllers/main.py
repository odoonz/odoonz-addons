from odoo.addons.web.controllers import main as report
from odoo.http import route, request
from odoo.tools import safe_eval

import json
import time


class ReportController(report.ReportController):
    @route()
    def report_routes(self, reportname, docids=None, converter=None, **data):
        if converter == 'text':
            report = request.env['ir.actions.report']._get_report_from_name(
                reportname)
            context = dict(request.env.context)

            if docids:
                docids = [int(i) for i in docids.split(',')]
            if data.get('options'):
                data.update(json.loads(data.pop('options')))
            if data.get('context'):
                # Ignore 'lang' here, because the context in data is the
                # one from the webclient *but* if the user explicitly wants to
                # change the lang, this mechanism overwrites it.
                data['context'] = json.loads(data['context'])
                if data['context'].get('lang'):
                    del data['context']['lang']
                context.update(data['context'])

            attachment_name = reportname
            if report.print_report_name:
                if docids and len(docids) == 1 and report.model:
                    record = request.env[report.model].browse(docids)[0]
                    attachment_name = safe_eval(
                        report.print_report_name,
                        {'object': record, 'time': time})
                elif (report.print_report_name and
                        'object' not in report.print_report_name):
                    attachment_name = safe_eval(
                        report.print_report_name, {'time': time})

            text = report.with_context(context).render_qweb_text(
                docids, data=data)[0]
            response = request.make_response(text)
            response.data = response.data.strip()
            response.headers.set("Content-Type", "text/plain")
            response.headers.set('Content-length', len(response.data))
            response.headers.set(
                'Content-Disposition',
                'attachment; filename="'+attachment_name)
            return response
        return super().report_routes(
            reportname, docids=docids, converter=converter, **data)
