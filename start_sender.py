#!/usr/bin/python3

import argparse
from scripts.node_sender.sender import Sender
from scripts.node_deployer.utilization_checker import utillization_checker
import time

def main():
    parser = argparse.ArgumentParser(description="Help for bm-scripts binary")
    parser.add_argument('-n', '--node_count', action='store', dest='node_count',
        type=int, help="Node count for deploying", default=2)
    parser.add_argument('-a', '--addresses', action='store', dest='addresses',
        type=str, help="Address where sender will connect to node", nargs='+')
    args = parser.parse_args()
    print(args.addresses)
    
    name = "echonode{}"
    addr = "172.17.0.{}"
    start_port=8090
    slist=[]
    ulist=[]
    for i in range(args.node_count):
        slist.append(Sender(args.addresses[i], start_port+i, 90*i*10*255))

    #slist[0].import_balance_to_nathan()

    for i in range(args.node_count):
        ulist.append(utillization_checker(addr.format(2+i), name.format(i)))

    for u in ulist:
        u.run_check()

    while True:
        for s in slist:
            s.transfer(10)
        time.sleep(1)
            
if __name__ == "__main__":
    main()
