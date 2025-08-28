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
     "Spinning up threads...",
    "Priming HTTP sessions...",
    "Arming observability...",
    "Ready to launch 🚀"
]

SPINNER_FRAMES = ["⣾","⣽","⣻","⢿","⡿","⣟","⣯",">

shutdown_flag = threading.Event()

def print_banner():
    print(Fore.MAGENTA + Style.BRIGHT + BANNER)
    # cyberpunk boot animation
    for i, line in enumerate(CYBER_LINES):
        for _ in range(8):
            frame = SPINNER_FRAMES[_ % len(SPIN>
            sys.stdout.write(f"\r{Fore.CYAN}{fr>
            sys.stdout.flush()
            time.sleep(0.05)
        print(f"\r{Fore.GREEN}✔ {line}{' ' * 20>
    print("")

# --------- Worker Logic ---------
class Metrics:
    def __init__(self):
        self.lock = threading.Lock()
        self.latencies: List[float] = []
        self.success = 0
        self.fail = 0
        self.codes: Dict[int, int] = {}

    def record(self, ok: bool, latency: float, >
        with self.lock:
            if ok:
                self.success += 1
                self.latencies.append(latency)
            else:
                
