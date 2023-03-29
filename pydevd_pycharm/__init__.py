import logging
import os

HOST = os.environ.get("PYDEVD_PYCHARM_HOST", "host.docker.internal")
PORT = int(os.environ.get("PYDEVD_PYCHARM_PORT", 21000))

logger = logging.getLogger(__name__)


if os.environ.get("ENABLE_PYDEVD_PYCHARM") == "1":
    logger.info("Debugging with pydevd_pycharm enabled")
    try:
        import pydevd_pycharm

        PYDEVD_PYCHARM_INSTALLED = True
    except ModuleNotFoundError:
        PYDEVD_PYCHARM_INSTALLED = False

    if PYDEVD_PYCHARM_INSTALLED:
        version = pydevd_pycharm.__version__
        logger.info(f"Found pydevd_pycharm version {version}")
        logger.info(f"Looking for Python Debug Server at {HOST}:{PORT}...")
        try:
            pydevd_pycharm.settrace(
                HOST,
                port=PORT,
                stdoutToServer=True,
                stderrToServer=True,
                suspend=False,
            )
        except ConnectionError:
            logger.error("Could not connect to Debug Server - is it running?")
        else:
            logger.info("PyDev.Debugger connected")
    else:
        logger.warning("ENABLE_PYDEVD_PYCHARM set but pydevd_pycharm not installed")
