from logger import logging
logger = logging.getLogger(__name__)

def hangup_call():
    """
    End/Hangup the call with a callee.
    """
    logger.info(f"_hangup_call_ called!")
    return "call ended!"