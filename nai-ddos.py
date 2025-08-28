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
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    from colorama import Fore, Style, init as c>
except ImportError:
    print("Missing deps. Install: pip install r>
    sys.exit(1)

# --------- UI / Banner ---------
colorama_init(autoreset=True)

BANNER = r"""
===============================================>
=  =======  ====  ====    =====       ==       >
=   ======  ===    ====  ======  ====  =  ==== >
=    =====  ==  ==  ===  ======  ====  =  ==== >
=  ==  ===  =  ====  ==  ======  ====  =  ==== >
=  ===  ==  =  ====  ==  ======  ====  =  ==== >
=  ====  =  =        ==  ======  ====  =  ==== >
=  =====    =  ====  ==  ======  ====  =  ==== >
=  ======   =  ====  ==  ======  ====  =  ==== >
=  =======  =  ====  =    =====       ==       >
===============================================>
"""

CYBER_LINES = [
    "Booting NAI engine...",
