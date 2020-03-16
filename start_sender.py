#!/usr/bin/python3

import argparse
from scripts.node_sender.sender import Sender
import time

def main():
    parser = argparse.ArgumentParser(description="Help for bm-scripts binary")
    parser.add_argument('-n', '--node_count', action='store', dest='node_count',
        type=int, help="Node count for sender connecting to them", default=2)
    parser.add_argument('-a', '--addresses', action='store', dest='addresses',
        type=str, help="Address where sender will connect to node", nargs='+')
    parser.add_argument('-txs', '--txs_count', dest='txs_count', action='store',
        type=int, help="Number of transactions", default=1)
    args = parser.parse_args()
    print(args.addresses)
    print(args.txs_count)
    
    start_port=8090
    slist=[]
    for addr in args.addresses:
        for i in range(args.node_count):
            try:
                slist.append(Sender(addr, start_port+i, i*6000+180000*i))
            except Exception as e:
                print(e)
    try:
        slist[0].import_balance_to_nathan()
    except Exception as e:
        print(e)

    while True:
        for s in slist:
            s.transfer(args.txs_count)
        time.sleep(1)

if __name__ == "__main__":
    main()
