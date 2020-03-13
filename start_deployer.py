#!/usr/bin/python3

import argparse
from scripts.node_deployer.deployer import deployer
import json

def set_options(parser):
    parser.add_argument('-e', '--echo_bin', action='store', dest='echo_bin',
        type=str, help="Path to echo_node binary, should be statically compiled!", required=True)
    parser.add_argument('-p', '--pumba_bin', action='store', dest='pumba_bin',
        type=str, help="Path to pumba binary", default="")
    parser.add_argument('-i', '--image', action='store', dest='image',
        type=str, help="Name of image for docker containers", default="", required=True)
    parser.add_argument('-n', '--node_count', action='store', dest='node_count',
        type=int, help="Node count for deploying", default=2)
    parser.add_argument('-ct', '--conn_type', action='store', dest='conn_type',
        type=str, help="Network configurations. Can be the next: all_to_all, cyclic, serial", default="all_to_all")
    parser.add_argument('-dn', '--delayed_node', dest='delayed_node', nargs='+',
        type=int, help="Number on nodes which will be run under the network delay", default=[])
    parser.add_argument('-idn', '--inverse_delayed_node', dest='inverse_delayed_node', nargs='+',
        type=int, help="Number on nodes which will not be run under the network delay, all other nodes will be", default=[])
    parser.add_argument('-t', '--time', dest='time', action='store', 
        type=int, help="Delay on network interface in ms", default=0)
    parser.add_argument('-txs', '--txs_count', dest='txs_count', action='store',
        type=int, help="Number of transactions", default=10000)
    parser.add_argument('-tt', '--tx_type', dest='tx_type', action='store',
        type=str, help="Transaction type: transfer, create_evm, call_emv, create_x86, call_x86", default = "transfer")
    parser.add_argument('-sc', '--send_cycles', dest='cycles', action='store',
        type=int, help="Count of cycles of send", default=1)
    parser.add_argument('-sn', '--server_num', dest='server_num', action='store',
        type=int, help="Number of server on which deployer will be started", required=True)
    parser.add_argument('-hi', '--hosts_info', dest='hosts_info', action='store',
        type=str, help="Host info in dictionary formar: {\"ip address\" : number of nodes}", default="", required=True)
    parser.add_argument('-cl', '--clear', action='store_true', help="Clear containers after test execution")

from scripts.node_deployer.deployer import test

def main():
    parser = argparse.ArgumentParser(description="Help for bm-scripts binary")
    set_options(parser)
    args = parser.parse_args()
    hosts_info=json.loads(args.hosts_info)
    print(hosts_info)
    d = deployer(node_count=args.node_count, echo_bin=args.echo_bin, pumba_bin=args.pumba_bin,
                image=args.image, start_node=args.server_num, host_addresses=hosts_info, remote=True)

if __name__ == "__main__":
    main()
