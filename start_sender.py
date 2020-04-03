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
    kill_sender()

    def signal_handler(sig, frame):
        print("\nCaught SIGINT:")
        raise SystemExit("Exited from Ctrl-C handler")
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description="Help for bm-scripts binary")
    parser.add_argument('-hi', '--hosts_info', dest='hosts_info', action='store',
        type=str, help="Host info in dictionary formar: {\"ip address\" : number of nodes}", default="", required=True)
    parser.add_argument('-txs', '--txs_count', dest='txs_count', action='store',
        type=int, help="Number of transactions", default=1)
    parser.add_argument('-d', '--delay', dest='delay', action='store',
        type=int, help="Delay in seconds between transfers", default=2)
    args = parser.parse_args()
    
    start_port=8090
    slist=[]
    info_lst=[]
    hosts_info=json.loads(args.hosts_info)
    prev_num_nodes=0
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

    if slist:
        while True:
            i=0
            num=len(slist)
            if num == 0:
                break
            while i < num:
                try:
                    print("Trying sent transactions to:", info_lst[i])
                    sys.stdout.flush()
                    slist[i].transfer(args.txs_count)
                    print(args.txs_count, "Transactions sent")
                    sys.stdout.flush()
                    time.sleep(args.delay)
                    i=i+1
                except echopy.echoapi.ws.exceptions.RPCError as rpc_error: # we should catch txs dupes, it is cost of decreasing transaction expiration time
                    if "skip_transaction_dupe_check" in str(rpc_error):    # there will little part of all transactions
                        print("Caught txs dupe")
                        pass
                    else:
                        raise Exception(str(rpc_error))
                except Exception as e:
                    print("Caught exception during transaction sending")
                    sys.stdout.flush()
                    logging.error(traceback.format_exc())
                    sys.stdout.flush()
                    del slist[i]
                    del info_lst[i]
                    num=num-1

if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        print(e)
    except Exception as e:
        logging.error(traceback.format_exc())
