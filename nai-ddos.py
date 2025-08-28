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
                self.fail += 1
            if code is not None:
                self.codes[code] = self.codes.g>

def build_session(timeout, keepalive=True, veri>
    s = requests.Session()
    # robust adapter with connection pool
    retries = Retry(total=0, backoff_factor=0)
    adapter = HTTPAdapter(
        max_retries=retries,
        pool_connections=100,
        pool_maxsize=1000
    )
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    s.headers.update({
        "User-Agent": "NAI-LoadTester/1.0",
        "Connection": "keep-alive" if keepalive>
    })
    s.verify = verify_tls
    s.timeout = timeout
    return s

def worker(idx, args, job_q: queue.Queue, metri>
    session = build_session(timeout=args.timeou>
    rng = random.Random(idx ^ int(time.time()))
    # simple log pulse each second
    last_log = time.time()

    while not shutdown_flag.is_set():
        now = time.time()
        if now < start_ts:
            time.sleep(min(0.01, start_ts - now>
            continue
        if now >= end_ts:
            break
         # rate limiting per thread
        if args.rps > 0:
            # spread requests evenly within sec>
            delay = 1.0 / args.rps
        else:
            delay = 0.0

        try:
            method, url, payload, headers = job>
        except queue.Empty:
            # recycle a default job if queue em>
            method = args.method
            url = args.url
            payload = None
            headers = {}

        t0 = time.perf_counter()
        ok = False
        code = None
        try:
            if method == "GET":
                resp = session.get(url, headers>
            elif method == "POST":
                resp = session.post(url, data=p>
                                    json=None i>
            elif method == "PUT":
                resp = session.put(url, data=pa>
                                   json=None if>
            else:
                resp = session.request(method, >
            code = resp.status_code
            ok = 200 <= resp.status_code < 500 >
        except requests.RequestException:
            ok = False
        latency = (time.perf_counter() - t0) * >
        metrics.record(ok, latency, code)
        # eye-candy pulse
        if time.time() - last_log >= 1.0 and id>
            total = metrics.success + metrics.f>
            sys.stdout.write(
                f"\r{Fore.YELLOW}🚀 Threads {ar>
                f"{sum(v for k,v in metrics.cod>
                f"{sum(v for k,v in metrics.cod>
                f"{sum(v for k,v in metrics.cod>
                f"{sum(v for k,v in metrics.cod>
            )
            sys.stdout.flush()
            last_log = time.time()

        if delay > 0:
            # add tiny jitter so all threads do>
            time.sleep(delay * (0.8 + 0.4 * rng>

# --------- Percentiles / Report ---------
def percentile(values: List[float], p: float) ->
    if not values:
        return float("nan")
    v = sorted(values)
    k = (len(v) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(v) - 1)
    if f == c:
        return v[int(k)]
    return v[f] + (v[c] - v[f]) * (k - f)

    def print_report(args, metrics: Metrics, start_>
    duration = max(0.001, end_ts - start_ts)
    total = metrics.success + metrics.fail
    rps = total / duration
    p50 = percentile(metrics.latencies, 50)
    p95 = percentile(metrics.latencies, 95)
    p99 = percentile(metrics.latencies, 99)
    avg = statistics.mean(metrics.latencies) if>

    print("\n")
    print(Fore.CYAN + Style.BRIGHT + "─" * 64)
    print(Fore.CYAN + Style.BRIGHT + " NAI DDoS>
    print(Fore.CYAN + Style.BRIGHT + "─" * 64)
    print(f"{Fore.MAGENTA}Target    : {args.url>
    print(f"{Fore.MAGENTA}Method    : {args.met>
    print(f"{Fore.MAGENTA}Duration  : {args.dur>
    print(f"{Fore.MAGENTA}Timeline  : {datetime>
    print("")
    print(f"{Fore.GREEN}Total Requests : {total>
    print(f"{Fore.GREEN}Success        : {metri>
    print(f"{Fore.RED}Failures       : {metrics>
    print(f"{Fore.YELLOW}Overall RPS    : {rps:>
    print("")
    print(f"{Fore.CYAN}Latency (ms)   : avg={av>
    print("")
    # status code breakdown
    if metrics.codes:
        print(Fore.WHITE + Style.DIM + "Status >
        for code in sorted(metrics.codes.keys()>
            print(f"  {code}: {metrics.codes[co>
    print(Fore.CYAN + Style.BRIGHT + "─" * 64)
    for code in sorted(metrics.codes.keys()>
            print(f"  {code}: {metrics.codes[co>
    print(Fore.CYAN + Style.BRIGHT + "─" * 64)

# --------- Main ---------
def sigint_handler(signum, frame):
    shutdown_flag.set()
    print(Fore.RED + "\n[!] Ctrl-C received, sh>

def main():
    parser = argparse.ArgumentParser(descriptio>
    parser.add_argument("--url", required=True,>
    parser.add_argument("--method", default="GE>
    parser.add_argument("--threads", type=int, >
    parser.add_argument("--rps", type=float, de>
    parser.add_argument("--duration", type=int,>
    parser.add_argument("--timeout", type=float>
    parser.add_argument("--no-keepalive", actio>
    parser.add_argument("--insecure", action="s>
    parser.add_argument("--payload", help="JSON>
    parser.add_argument("--form", action="store>
    parser.add_argument("--header", action="app>
    args = parser.parse_args()

    print_banner()

    # prepare job queue (optional mixed endpoin>
    job_q = queue.Queue()
    headers = {}
    for h in args.header:
        if ":" in h:
            k, v = h.split(":", 1)
            headers[k.strip()] = v.strip()

    payload = None
    if args.payload:
        # rough parse: try JSON then fall back >
        import json
        try:
            payload = json.loads(args.payload)
        except json.JSONDecodeError:
            payload = args.payload

    # push a few starter jobs so workers don't >
    for _ in range(min(1000, args.threads * 10)>
        job_q.put((args.method, args.url, paylo>

    signal.signal(signal.SIGINT, sigint_handler)

    metrics = Metrics()
    start_ts = time.time() + 1.0  # 1s warmup b>
    end_ts = start_ts + args.duration

    threads = []
    for i in range(args.threads):
        t = threading.Thread(target=worker, arg>
        t.start()
        threads.append(t)

    # countdown with flashy spinner
    print(Fore.YELLOW + Style.BRIGHT + "Arming >
    for s in range(3, 0, -1):
        for frame in SPINNER_FRAMES:
            sys.stdout.write(f"\r{Fore.YELLOW}{>
            sys.stdout.flush()
            time.sleep(0.08)
    print(f"\r{Fore.GREEN}🚀 Launch!{' ' * 20}")

    # wait for completion
    while time.time() < end_ts and not shutdown>
        time.sleep(0.2)
    shutdown_flag.set()

    for t in threads:
        t.join(timeout=1)

    print_report(args, metrics, start_ts, min(t>

if __name__ == "__main__":
    main()
