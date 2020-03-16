#!/usr/bin/python3

import argparse
from scripts.node_sender.sender import Sender
import time
import traceback
import logging

def main():
    parser = argparse.ArgumentParser(description="Help for bm-scripts binary")
    parser.add_argument('-n', '--node_count', action='store', dest='node_count',
        type=int, help="Node count for sender connecting to them", default=2)
    parser.add_argument('-a', '--addresses', action='store', dest='addresses',
        type=str, help="Address where sender will connect to node", nargs='+')
    parser.add_argument('-txs', '--txs_count', dest='txs_count', action='store',
        type=int, help="Number of transactions", default=1)
    args = parser.parse_args()
    
    start_port=8090
    slist=[]
    info_lst=[]
    for addr in args.addresses:
        for i in range(args.node_count):
            try:
                print("Trying connect to",addr,":",start_port+i)
                slist.append(Sender(addr, start_port+i, i*6000+18000*i))
                info_lst.append("Address : {}  Port : {}".format(addr, start_port+i))
                print("Done")
            except Exception as e:
                logging.error(traceback.format_exc())
                print(e)
    try:
        slist[0].import_balance_to_nathan()
    except Exception as e:
        print(e)

    while True:
        for s,i in zip(slist, info_lst):
            try:
                print("Trying sent transactions to:", i)
                s.transfer(args.txs_count)
                print(args.txs_count, "Transactions sent")
                time.sleep(2)
            except Exception as e:
                print("Caught exception during transaction sending")
                logging.error(traceback.format_exc())

if __name__ == "__main__":
    main()
