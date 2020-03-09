#!/usr/bin/python3

import argparse

from scripts.simple_test import simple_test
from scripts.database_size_test import database_size_test
from scripts.propagation_test import propagation_test

def set_options(parser):
    parser.add_argument('-e', '--echo_bin', action='store', dest='echo_bin',
        type=str, help="Path to echo_node binary, should be statically compiled!", required=True)
    parser.add_argument('-p', '--pumba_bin', action='store', dest='pumba_bin',
        type=str, help="Path to pumba binary", default="")
    parser.add_argument('-i', '--image', action='store', dest='image',
        type=str, help="Name of image for docker containers", default="", required=True)
    parser.add_argument('-n', '--node_count', action='store', dest='node_count',
        type=int, help="Node count for deploying", default=2)
    parser.add_argument('-dn', '--delayed_node', dest='delayed_node', nargs='+',
        type=int, help="Number on nodes which will be run under the network delay", default=[])
    parser.add_argument('-idn', '--inverse_delayed_node', dest='inverse_delayed_node', nargs='+',
        type=int, help="Number on nodes which will not be run under the network delay, all other nodes will be", default=[])
    parser.add_argument('-t', '--time', dest='time', action='store', 
        type=int, help="Delay on network interface in ms", default=20)
    parser.add_argument('-s', '--suite', dest='suite', action='store',
        type=str, help="Name of test suite. Can be the next: simple, database[will be added]... ", required=True)
    parser.add_argument('-txs', '--txs_count', dest='txs_count', action='store',
        type=int, help="Number of transactions", default=10000)

def create_delayed_node_lst(args):
    lst = []
    if len(args.delayed_node) and not args.inverse_delayed_node:
        for i in args.delayed_node:
            lst.append("echonode{}".format(i))
        return lst
    elif len(args.inverse_delayed_node) and not args.delayed_node:
        for i in range(args.node_count):
            if i not in args.inverse_delayed_node:
                lst.append("echonode{}".format(i))
        return lst
    else:
        return lst

def run_suite(args):
    if args.suite == "simple":
       st = simple_test(args.node_count, args.echo_bin, args.image, args.txs_count)
       st.run_test()
    elif args.suite == "database":
       dst = database_size_test(args.node_count, args.echo_bin, args.image, args.txs_count)
       dst.run_test()
    elif args.suite == "propagation":
       if args.pumba_bin != "":
           pt = propagation_test(args.node_count, args.echo_bin,
               args.image, args.pumba_bin, args.time, create_delayed_node_lst(args))
           pt.run_test()
       else:
           print("pumba_bin argmunet should be specified!")

def main():
    parser = argparse.ArgumentParser(description="Help for bm-scripts binary")
    set_options(parser)
    args = parser.parse_args()
    run_suite(args)
    
if __name__ == "__main__":
    main()