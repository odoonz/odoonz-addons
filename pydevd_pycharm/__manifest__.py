{
    "name": "PyDev.Debugger for PyCharm",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "category": "Other",
    "author": "Danny W. Adair - O4SB",
    "website": "https://o4sb.com",
    "description": """
    Start PyDev debugging for PyCharm

    1. Install pydevd-pycharm in your Odoo environment.
       The version needs to match your PyCharm version.

       For exameple, in PyCharm:
       "Help -> About" shows
       "Build #PY-223.8617.48, built on January 25, 2023"
       In this case,

       `pip3 install pydevd-pycharm~=223.8617.48`

       (for our projects, we do this in a docker entrypoint,
       looking up the version number from .env where each
       developer can set their own)

    2. Set environment variable ENABLE_PYDEVD_PYCHARM to "1" in
       your Odoo environment to enable debugging.

    3. You need to set WORKERS=0 in odoo.conf for
       your Odoo environment (it currently only works for
       multi-threading, not multi-processing).

    4. Start a "Python Debug Server" in PyCharm (with
       path mappings to your source) on port 21000.

    5. When the addon is loaded, it will connect to the
       Debug server and stop at your breakpoints. Enjoy!

    You can override the defaults of where to find the
    PyCharm Debug Server with environment variables:

    * PYDEVD_PYCHARM_HOST (default: "host.docker.internal")
    * PYDEVD_PYCHARM_PORT (default: "21000")

    If you're running Odoo with docker compose, you'll need
    to add

    extra_hosts:
      - "host.docker.internal:host-gateway"

    to the Odoo service for "host.docker.internal" to resolve.

    If you're not running Odoo in docker at all, then
    PYDEVD_PYCHARM_HOST should probably just be "localhost".

    It's annoying to start Odoo with debugging enabled, only to
    realise that you didn't start the Debug Server first...
    If the addon cannot connect to the Debug Server, it will
    retry 10 times every 3 seconds.
    You can adjust these figures with environment variables:

    * PYDEVD_PYCHARM_RETRY_SECONDS (default: "3")
    * PYDEVD_PYCHARM_RETRY_ATTEMPTS (default: "10")
    """,
    "depends": ["base"],
    "auto_install": True,
    "installable": True,
}

