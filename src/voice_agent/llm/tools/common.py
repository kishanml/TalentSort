from logger import logging
logger = logging.getLogger(__name__)


def knowledge_base(query):
    """
    Knowledge base for voice agent
    """
    pass


def hangup_call():
    """
    End/Hangup the call with a callee.
    """
    logger.info(f"_hangup_call_ called!")
    return "call ended!"