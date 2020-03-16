#!/usr/bin/python3

import argparse
from scripts.node_deployer.utilization_checker import utilization_checker
from threading import Event
exit = Event()

def quit(signo, _frame):
    print("Interrupted by %d, shutting down" % signo)
    exit.set()

def main():
    parser = argparse.ArgumentParser(description="Help for bm-scripts binary")
    parser.add_argument('-n', '--node_count', action='store', dest='node_count',
        type=int, help="Node count for measuring", default=2)
    parser.add_argument('-t', '--time', action='store', dest='time',
        type=int, help="Time specify how long utilization checker will work (in seconds)", default=3600)
    args = parser.parse_args()

    addrs = []
    ports = []
    names = []
    start_addr="172.17.0.{}"
    start_name="echonode{}"
    for i in range(args.node_count):
        addrs.append(start_addr.format(i+2))
        ports.append(13375+i)
        names.append(start_name.format(i))

    u = utilization_checker(addrs, ports, names)
    u.run_check()
    exit.wait(args.time) 
    u.stop_check()    
    print("Stopped")

if __name__ == "__main__":
    import signal
    for sig in ('TERM', 'HUP', 'INT'):
        signal.signal(getattr(signal, 'SIG'+sig), quit);
    main()
