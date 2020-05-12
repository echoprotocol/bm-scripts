#!/usr/bin/python3

import argparse
from scripts.node_sender.sender import Sender
import time
import traceback
import logging
import signal
import sys
import psutil
import json
import os
import echopy

def kill_sender():
    my_pid = os.getpid()
    for proc in psutil.process_iter():
        if (proc.name() == "start_sender.py" and proc.pid != my_pid):
            print("Killing previous sender process")
            os.kill(proc.pid, signal.SIGTERM)

def main():
    parser = argparse.ArgumentParser(description="Help for bm-scripts binary")
    parser.add_argument('-hi', '--hosts_info', dest='hosts_info', action='store',
        type=str, help="Host info in dictionary format: {\"ip address\" : number of nodes}", default="", required=True)
    parser.add_argument('-txs', '--txs_count', dest='txs_count', action='store',
        type=int, help="Number of transactions", default=1)
    parser.add_argument('-d', '--delay', dest='delay', action='store',
        type=int, help="Delay in seconds between transfers", default=2)
    parser.add_argument('-in', '--import_balance_nathan', dest='nathan_balance', action='store',
        type=bool, help="Flag for import balance to nathan", default=False)
    args = parser.parse_args()

    hosts_info = json.loads(args.hosts_info)

    # if args.start_new == False:
    #     kill_sender()

    start_port=8090
    slist=[]
    info_lst=[]
    prev_num_nodes=0

    def signal_handler(sig, frame):
        print("\nCaught SIGINT:")
        for s in slist:
            s.interrupt_sender()
        raise SystemExit("Exited from Ctrl-C handler")
    signal.signal(signal.SIGINT, signal_handler)

    for addr, count in hosts_info.items():
        for i in range(count):
            try:
                print("Trying connect to",addr,":",start_port+i)
                sys.stdout.flush()
                slist.append(Sender(addr, start_port+i, (i+prev_num_nodes)))
                info_lst.append("Address : {}  Port : {}".format(addr, start_port+i))
                print("Done")
                sys.stdout.flush()
            except ConnectionRefusedError as e:
                logging.error(traceback.format_exc())
                sys.stdout.flush()
                print(e)
                sys.stdout.flush()
        prev_num_nodes=prev_num_nodes+count

    if slist and args.nathan_balance:
        slist[0].import_balance_to_nathan()

    total = 0

    if slist:
        while True:
            i=0
            num=len(slist)
            if num == 0:
                break
            while i < num:
                try:
                    print("Trying sent transactions to:", info_lst[i], flush=True)
                    sent = slist[i].transfer(args.txs_count)
                    total += sent
                    print(sent, "Transactions sent")
                    sys.stdout.flush()
                    time.sleep(args.delay)
                    i=i+1
                except Exception as e:
                    print("Caught exception during transaction sending")
                    print(e)
                    sys.stdout.flush()
                    exit(1)
                    logging.error(traceback.format_exc())
                    sys.stdout.flush()
                    del slist[i]
                    del info_lst[i]
                    num=num-1
                
            if total % 1000 == 0:
                print("Total transfers: ", total)

if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        print(e)
    except Exception as e:
        logging.error(traceback.format_exc())
