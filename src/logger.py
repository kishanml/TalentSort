import os
import logging

os.makedirs("LOGS", exist_ok=True)

log_format = "%(levelname)s:     [%(asctime)s] - [%(lineno)d, %(name)s] %(message)s"
formatter = logging.Formatter(log_format)

def get_file_handler(level_name, level):
    """File handler"""
    handler = logging.FileHandler(filename=f"LOGS/{level_name.lower()}.log", mode="a+")
    handler.setLevel(level)
    handler.setFormatter(formatter)
    handler.addFilter(lambda record: record.levelno == level)
    return handler

def get_stream_handler(level=logging.ERROR):
    """Stream handler"""
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)
    return stream_handler


info_handler    = get_file_handler("info", logging.INFO)
debug_handler   = get_file_handler("debug", logging.DEBUG)
error_handler   = get_file_handler("error", logging.ERROR)
warning_handler = get_file_handler("warning", logging.WARNING)

# Display only error logs on terminal
stream_handler = get_stream_handler(logging.ERROR)


logging.basicConfig(
    level=os.getenv("LOG_LEVEL"),
    handlers=[
        info_handler,
        debug_handler,
        error_handler,
        warning_handler,
        stream_handler
    ]
)