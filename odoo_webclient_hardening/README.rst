========================
Odoo Webclient Hardening
========================

This module applies a set of **opinionated** hardening measures to public,
unauthenticated Odoo web endpoints, to reduce information disclosure and shave
off attack surface.

.. warning::

   This module is **alpha** and under constant review. Its behaviour and the
   set of fixes it applies may change at any time. Pin and test against your
   own deployment before relying on it.

It is deliberately **icing on the cake**. It is *not* a substitute for defense
in depth and it will *not* make an otherwise-insecure deployment secure. It is
intended for mature, enterprise-grade deployments that already run dedicated,
expert operations / security staff, and that have already completed every
standard Odoo security recommendation first, for example:

* a properly configured reverse proxy terminating TLS;
* ``list_db = False`` and a strict, host-specific ``dbfilter``;
* a strong, rotated ``admin_passwd`` (or the database manager fully closed);
* workers not exposed directly to the internet;
* rate limiting / WAF / fail2ban in front of the login and RPC surfaces;
* network segmentation between Odoo, PostgreSQL and the outside world;
* timely patching of Odoo and its dependencies.

For the canonical, upstream list of these recommendations, see Odoo's official
deployment and security documentation:

* https://www.odoo.com/documentation/19.0/administration/on_premise/deploy.html
* https://www.odoo.com/security

Apply this module only **after** those fundamentals are in place. Every change
here is a small, surgical reduction of what an anonymous caller can learn or
do. None of them is a security boundary on its own; treat the whole module as
marginal attack-surface reduction, not as a control you can rely on.

Read this first
===============

* **It is opinionated.** It encodes *our* choices for *our* deployment, most
  notably that the external RPC endpoints are unused. If you have integrations
  that call XML-RPC or JSON-RPC, this module will break them until you
  re-enable JSON-RPC (see `Configuration`_). Read the per-fix notes below
  before installing.
* **It must be a server-wide module.** Several fixes target ``auth="none"``
  routes that are served from the "nodb" routing map (when no database is
  selected). Controller overrides only apply there if the module is listed in
  ``server_wide_modules``. See `Configuration`_.
* **It monkeypatches** ``odoo.http.serialize_exception`` at load time (via the
  manifest ``post_load`` hook). That is inherently version-sensitive: re-verify
  the behaviour after every Odoo upgrade.
* **Test on staging first.** These changes alter the responses of core public
  routes. Validate login, password reset and any RPC integrations on a staging
  copy before promoting to production.

What this module does
=====================

Each fix is independent and explained below, including *why* it exists and what
it costs.

Translation module enumeration
------------------------------

**Purpose:** ``/web/webclient/translations`` is reachable pre-login and, in
stock Odoo, returns the list of every installed module (so the web client can
fetch their JS translations). That list fingerprints exactly which apps and
custom modules a tenant runs. We filter the response down to modules that
actually ship web translations, so the endpoint stops doubling as a module
inventory while the web client keeps the translations it needs.

RPC endpoints (XML-RPC and JSON-RPC)
------------------------------------

**Purpose:** the external RPC entry points are a large, powerful and
historically CVE-prone surface that the web client never uses (it calls
``/web/dataset/call_kw``). XML-RPC (``/xmlrpc`` and ``/xmlrpc/2``) is always
disabled and returns 404. JSON-RPC (``/jsonrpc``) is disabled by default and
also returns 404; it can be re-enabled with a config parameter for the rare
case an integration needs it (see `Configuration`_). Returning 404 (rather than
403) makes the routes look absent rather than merely forbidden.

In our opinion JSON-RPC integrations should be unnecessary in nearly all cases.
Programmatic integrations are better expressed as a purpose-built framework such
as a FastAPI application that explicitly controls what can be done (a narrow,
audited surface) rather than exposing the entire ORM over generic RPC. Ad-hoc
queries are better run over SSH in a controlled Odoo CLI / shell environment.
Reach for re-enabling JSON-RPC only when neither of those is viable.

Database manager endpoints
--------------------------

**Purpose:** the ``/web/database/*`` management routes are ``auth="none"`` and
gated only by the master password. ``create``, ``duplicate``, ``drop``,
``backup``, ``restore``, ``change_password`` and the ``manager`` UI are an
anonymously reachable management / destruction surface, so we disable them
(404). The read-only ``selector`` and ``list`` routes are left intact so
multi-database login still works; restrict *which* databases are visible with
``dbfilter`` / ``list_db`` at the config level.

In an enterprise deployment no administrator would ever use these web
endpoints anyway: database creation, duplication, backups, restores and drops
are handled by dedicated tooling outside of Odoo (orchestration, managed
PostgreSQL, scheduled ``pg_dump`` / WAL archiving, etc.). Disabling the web
routes therefore removes pure attack surface with no loss of operational
capability.

Version fingerprinting
----------------------

**Purpose:** ``/web/webclient/version_info`` is ``auth="none"`` and returns the
exact Odoo version, version tuple and serie (including the ``+e`` Enterprise
marker), which is prime CVE-targeting data. The web client only uses this route
as a connectivity ping and reads the real version from ``session_info``, so we
return a minimal ``{"protocol_version": 1}`` payload and drop the fingerprint.

Exception detail leakage
------------------------

**Purpose:** Odoo serialises every exception raised inside a JSON request into
the response body, including the full traceback, which can disclose file paths,
SQL and PostgreSQL connection details to anyone able to reach a public
endpoint. We keep the rich payload for authenticated sessions (the web client
relies on it) but, for anonymous callers, strip the traceback / context and
genericise non-user-facing errors to ``Internal Server Error``. Genuine
user-facing messages (``UserError``, HTTP 4xx, session-expired, access-denied)
are still surfaced.

Password-reset user enumeration
-------------------------------

**Purpose:** the ``auth_signup`` reset-password flow leaks whether an account
exists. A known login returns "instructions sent" while an unknown one returns
"No account found", and the ``?signup_email=`` probe redirects existing users
to the login page (revealing their login). We make ``reset_password`` a silent
no-op for unknown logins (uniform message) and make the ``signup_email`` probe
always redirect to login, echoing the value supplied, regardless of whether the
account exists. A residual *timing* oracle remains (a real account triggers an
email send); install ``odoo_webclient_hardening_queue_job`` to neutralise it.

Caveats and guidance
====================

* **Breaking change for RPC clients.** XML-RPC is gone and JSON-RPC is off by
  default. Inventory your integrations before deploying.
* **404 vs 403.** Disabled routes intentionally return 404. Monitoring that
  asserts on specific status codes for these paths must be updated.
* **No UI, no data.** The module ships only code. There is nothing to
  configure in the Odoo UI beyond the optional config parameter below.
* **Defense in depth.** Re-state of the headline: this is the *last* layer, not
  the first. Do not let its presence justify relaxing the proxy, ``list_db``,
  ``admin_passwd`` or patching discipline.

Configuration
=============

Server-wide loading (required)
------------------------------

Add the module to ``server_wide_modules`` so its overrides also apply to the
nodb routing map::

    server_wide_modules = base,web,queue_job,...,odoo_webclient_hardening

Re-enabling JSON-RPC (optional)
-------------------------------

JSON-RPC is disabled by default. To re-enable it for a specific integration,
set the system parameter ``odoo_webclient_hardening.jsonrpc_enabled`` to a
truthy value (``1`` / ``True``). XML-RPC cannot be re-enabled by configuration.

If you do re-enable JSON-RPC, the config parameter only flips the endpoint back
on for *everyone* who can reach it. You will want to add access layers at the
reverse-proxy and/or firewall level to limit who can actually call it, for
example an IP allowlist / source-range restriction on the ``/jsonrpc`` path
scoped to the specific integration hosts, ideally combined with network
segmentation so the endpoint is not reachable from the public internet at all.
Treat the parameter as the "on switch" and the proxy / firewall rules as the
actual access control.

Credits
=======

Authors
-------

* Graeme Gellatly

Maintainers
-----------

This module is maintained for an internal, opinionated deployment. Use at your
own risk.
