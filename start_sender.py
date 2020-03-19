#!/usr/bin/python3

import argparse
from scripts.node_sender.sender import Sender
import time
import traceback
import logging
import signal
import sys

def main():
    def signal_handler(sig, frame):
        print("\nCaught SIGINT:")
        raise SystemExit("Exited from Ctrl-C handler")
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description="Help for bm-scripts binary")
    parser.add_argument('-n', '--node_count', action='store', dest='node_count',
        type=int, help="Node count for sender connecting to them", default=2)
    parser.add_argument('-a', '--addresses', action='store', dest='addresses',
        type=str, help="Address where sender will connect to node", nargs='+')
    parser.add_argument('-txs', '--txs_count', dest='txs_count', action='store',
        type=int, help="Number of transactions", default=1)
    parser.add_argument('-d', '--delay', dest='delay', action='store',
        type=int, help="Delay in seconds between transfers", default=2)
    args = parser.parse_args()
    
    start_port=8090
    slist=[]
    info_lst=[]
    for addr,j in zip(args.addresses,range(len(args.addresses))):
        for i in range(args.node_count):
            try:
                print("Trying connect to",addr,":",start_port+i)
                sys.stdout.flush()
                slist.append(Sender(addr, start_port+i, (i+j*args.node_count)*900000))
                info_lst.append("Address : {}  Port : {}".format(addr, start_port+i))
                print("Done")
                sys.stdout.flush()
            except ConnectionRefusedError as e:
                logging.error(traceback.format_exc())
                sys.stdout.flush()
                print(e)
                sys.stdout.flush()

    if slist:
        while True:
            for s,i in zip(slist, info_lst):
                try:
                    print("Trying sent transactions to:", i)
                    sys.stdout.flush()
                    s.transfer(args.txs_count)
                    print(args.txs_count, "Transactions sent")
                    sys.stdout.flush()
                    time.sleep(args.delay)
                except Exception as e:
                    print("Caught exception during transaction sending")
                    sys.stdout.flush()
                    logging.error(traceback.format_exc())
                    sys.stdout.flush()

if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        print(e)
    except Exception as e:
        logging.error(traceback.format_exc())
