====================================
Odoo Webclient Hardening - Queue Job
====================================

This is an **opinionated** bridge module between ``odoo_webclient_hardening``
and ``queue_job``. Its single purpose is to remove the *timing* side-channel
that survives the password-reset hardening in the base module.

.. warning::

   This module is **alpha** and under constant review. Its behaviour may change
   at any time. Pin and test against your own deployment before relying on it.

Like the base module, it is **icing on the cake**: a marginal,
defence-in-depth refinement, not a security boundary and not a replacement for
the standard Odoo security baseline (reverse proxy, ``list_db = False``, strict
``dbfilter``, strong ``admin_passwd``, rate limiting, patching, ...). It is
meant for mature, enterprise-grade deployments with dedicated expert staff,
installed only **after** those fundamentals and the base hardening module are
already in place.

For the canonical, upstream list of the baseline security recommendations that
must come first, see Odoo's official deployment and security documentation:

* https://www.odoo.com/documentation/19.0/administration/on_premise/deploy.html
* https://www.odoo.com/security

It installs automatically (``auto_install``) wherever both
``odoo_webclient_hardening`` and ``queue_job`` are present.

What this module does
=====================

**Purpose:** ``odoo_webclient_hardening`` already makes the public
``/web/reset_password`` flow return the same message whether or not an account
exists. But a *real* account still triggers synchronous token generation and an
email send (``force_send=True``), so the response is measurably slower than the
no-op for an unknown login. That timing difference is enough to re-enable
account enumeration despite the uniform message.

This module overrides ``res.users.reset_password`` so that, **for anonymous web
requests only**, the actual work is handed to a ``queue_job`` and the request
returns immediately. Both existing and non-existing logins now do the same
constant amount of synchronous work (enqueue one job, return), so the response
time no longer reveals whether the account exists.

Authenticated callers (admin-triggered resets, scripts, crons) keep the
**synchronous** path, so they still see mail-server errors directly.

Caveats and guidance
====================

* **Requires a running queue_job runner.** Deferred reset emails are only sent
  if jobs are actually processed. If the runner is down, public password-reset
  emails will silently queue instead of being sent. This is an availability
  trade-off accepted in exchange for closing the timing oracle; monitor the
  ``queue_job`` channels accordingly.
* **Anonymous detection.** Deferral triggers only when there is a bound web
  request with no ``session.uid``. Non-web callers are never deferred, so the
  admin "send password reset" button and any scripting keep their synchronous
  behaviour and error reporting.
* **Timing is reduced, not mathematically constant.** Enqueuing a job is a
  small, roughly constant cost, but no claim is made of perfect constant-time
  behaviour. Combine with rate limiting and (optionally) a configured CAPTCHA
  on the reset route for meaningful protection against automated enumeration.
* **Opinionated.** It assumes you want resets to be fire-and-forget for
  anonymous users. If you require synchronous delivery confirmation on the
  public flow, do not install this module.

Credits
=======

Authors
-------

* Graeme Gellatly

Maintainers
-----------

This module is maintained for an internal, opinionated deployment. Use at your
own risk.
