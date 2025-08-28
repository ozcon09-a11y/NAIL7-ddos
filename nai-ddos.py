import argparse
import threading
import time
import queue
import random
import signal
import sys
import statistics
from datetime import datetime
from typing import List, Dict

try:
    import requests                                                            from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    from colorama import Fore, Style, init as colorama_init
except ImportError:
    print("Missing deps. Install: pip install requests colorama")
    sys.exit(1)

# --------- UI / Banner ---------
colorama_init(autoreset=True)
