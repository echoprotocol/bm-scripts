#!/usr/bin/python3

import argparse
from scripts.node_deployer.tps_checker import tps_checker
from threading import Event
exit = Event()


def main():
    parser = argparse.ArgumentParser(description="Help for bm-scripts binary")
    parser.add_argument('-txs', '--txs_count', dest='txs_count', action='store',
        type=int, help="Number of transactions", default=1000)
    parser.add_argument('-a', '--address', dest='address', action='store',
        type=str, help="Address for connecting", default="172.17.0.2")
    parser.add_argument('-p', '--port', dest='port', action='store',
        type=int, help="Rpc port for connecting", default=8090)
    args = parser.parse_args()

    def quit(signo, _frame):
        print("Interrupted by %d, shutting down" % signo)
        exit.set()

    t = tps_checker(args.address, args.port, args.txs_count)

    import signal
    def signal_handler(sig, frame):
        print("\nCaught SIGINT, waiting closing:")
        t.interrupt_checker()

    signal.signal(signal.SIGINT, signal_handler)

    t.run_check()
    t.wait_check()
    print("Stopped")

if __name__ == "__main__":
    main()
