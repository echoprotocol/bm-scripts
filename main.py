#!/usr/bin/python3

import argparse
import traceback
import logging
import psutil
import signal
import sys

from scripts.tps_test import tps_test
from scripts.database_size_test import database_size_test
from scripts.propagation_test import propagation_test
from scripts.node_deployer.deployer import connect_type
from scripts.load_test import load_test

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
    parser.add_argument('-s', '--suite', dest='suite', action='store',
        type=str, help="Name of test suite. Can be the next: tps, database, load, propagation ", required=True)
    parser.add_argument('-txs', '--txs_count', dest='txs_count', action='store',
        type=int, help="Number of transactions", default=10000)
    parser.add_argument('-tt', '--tx_type', dest='tx_type', action='store',
        type=str, help="Transaction type: transfer, create_evm, call_emv, create_x86, call_x86", default = "transfer")
    parser.add_argument('-sc', '--send_cycles', dest='cycles', action='store',
        type=int, help="Count of cycles of send", default=1)
    parser.add_argument('-cl', '--clear', action='store_true', help="Clear containers after test execution")


def get_connection_type(type):
    conn_type = connect_type.all_to_all
    if (type == "serial"):
        conn_type = connect_type.serial
    elif (type == "cyclic"):
        conn_type = connect_type.circular
    return conn_type

def get_transaction_type(type):
    tx_type = 0
    if (type == "create_evm"):
        tx_type = 1
    elif (type == "call_evm"):
        tx_type = 2
    elif (type == "create_x86"):
        tx_type = 3
    elif (type == "call_x86"):
        tx_type = 4
    return tx_type

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

def select_suite(args):
    if args.suite == "tps":
       if args.pumba_bin != "":
            return tps_test(args.node_count, args.echo_bin, args.pumba_bin, args.image,
               args.txs_count, args.time, create_delayed_node_lst(args), get_transaction_type(args.tx_type), get_connection_type(args.conn_type))
       else:
           raise Exception("pumba_bin argmunet should be specified!")
    elif args.suite == "database":
       return database_size_test(args.node_count, args.echo_bin, args.image, args.txs_count, cycles=args.cycles)
    elif args.suite == "propagation":
       if args.pumba_bin != "":
           return propagation_test(args.node_count, args.echo_bin,
               args.image, args.pumba_bin, args.time, create_delayed_node_lst(args))
       else:
           raise Exception("pumba_bin argmunet should be specified!")
    elif args.suite == "load":
        return load_test(args.node_count, args.echo_bin, args.image, args.pumba_bin, args.time,
            get_connection_type(args.conn_type), tx_count=args.txs_count, cycles=args.cycles)

def cleanup_resources(test, clr):
    if test is not None:
        test.d.kill_pumba()
    if clr == True:
        test.d.stop_containers()

def check_pumba():
    for proc in psutil.process_iter():
        if (proc.name() == "pumba"):
            p = psutil.Process(proc.pid)
            p.kill()
            break
def main():
    parser = argparse.ArgumentParser(description="Help for bm-scripts binary")
    set_options(parser)
    args = parser.parse_args()
    test = None
    def signal_handler(sig, frame):
        print("\nCaught SIGINT, waiting closing:")
        if test is not None:
            test.stop_checkers()
        raise SystemExit("Exited from Ctrl-C handler")

    signal.signal(signal.SIGINT, signal_handler)
    try:
        test = select_suite(args)
        test.run_test()
        if args.clear == True:
            test.d.stop_containers()
    except Exception as e:
        print("Caught exception, exit cleanly.")
        print("-------------------------------------------")
        logging.error(traceback.format_exc())
        cleanup_resources(test, args.clear)
        check_pumba()
        print("-------------------------------------------")
        print("Exited")
    except SystemExit as e:
        print(e)
        cleanup_resources(test, args.clear)
        check_pumba()

if __name__ == "__main__":
    main()
