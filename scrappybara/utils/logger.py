import logging.handlers

import scrappybara.config as cfg

# Log file
_LOG_FILE_PATH = cfg.HOME_DIR / 'scrappybara.log'

# File handler
_FILE_SIZE = 1024 * 1024 * 100  # 100Mb
_FILE_FORMATTER = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')
_FILE_HANDLER = logging.handlers.RotatingFileHandler(_LOG_FILE_PATH, maxBytes=_FILE_SIZE, backupCount=10)
_FILE_HANDLER.setFormatter(_FILE_FORMATTER)

# Stream handler
_STREAM_FORMATTER = logging.Formatter('[%(levelname)s|%(filename)s] %(message)s')
_STREAM_HANDLER = logging.StreamHandler()
_STREAM_HANDLER.setFormatter(_STREAM_FORMATTER)

# Logger instance
Logger = logging.getLogger()
Logger.addHandler(_FILE_HANDLER)
Logger.addHandler(_STREAM_HANDLER)
Logger.setLevel(logging.INFO)
