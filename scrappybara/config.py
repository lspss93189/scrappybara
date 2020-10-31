import multiprocessing
import pathlib

# ###############################################################################
# VERSIONING
# ###############################################################################

APP_VERSION = '0.1.6'
DATA_VERSION = '0.3.0'

# ###############################################################################
# MULTITHREADING
# ###############################################################################

NB_PROCESSES = multiprocessing.cpu_count()

# ###############################################################################
# FILES
# ###############################################################################

ENCODING = 'utf-8'
HOME_DIR = pathlib.Path(__file__).parent
REPORTS_DIR = HOME_DIR / 'reports'
DATA_DIR = HOME_DIR / 'data'

# ###############################################################################
# MACHINE LEARNING
# ###############################################################################

MAX_WORD_LENGTH = 20
MAX_SENT_LENGTH = 50
WORD_VECTOR_SIZE = 100

PADDED_SENT_LENGTH = MAX_SENT_LENGTH + 2
PADDED_WORD_LENGTH = MAX_WORD_LENGTH + 2
