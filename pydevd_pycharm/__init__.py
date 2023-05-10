import logging
import os
import time

HOST = os.environ.get("PYDEVD_PYCHARM_HOST", "host.docker.internal")
PORT = int(os.environ.get("PYDEVD_PYCHARM_PORT", 21000))
RETRY_SECONDS = int(os.environ.get("PYDEVD_PYCHARM_RETRY_SECONDS", 3))
RETRY_ATTEMPTS = int(os.environ.get("PYDEVD_PYCHARM_RETRY_ATTEMPTS", 10))

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
        attempts_left = RETRY_ATTEMPTS + 1
        while attempts_left:
            try:
                pydevd_pycharm.settrace(
                    HOST,
                    port=PORT,
                    stdoutToServer=True,
                    stderrToServer=True,
                    suspend=False,
                )
            except ConnectionError:
                attempts_left -= 1
                if attempts_left == 0:
                    logger.error("Could not connect to Debug Server - is it running?")
                else:
                    logger.warning(f"No answer... will try again in {RETRY_SECONDS} seconds ({attempts_left} attempts left)")
                    time.sleep(RETRY_SECONDS)
            else:
                logger.info("PyDev.Debugger connected")
                attempts_left = 0

    else:
        logger.warning("ENABLE_PYDEVD_PYCHARM set but pydevd_pycharm not installed")
