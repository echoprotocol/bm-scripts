#!/usr/bin/python3

"""
Sender transactions for Echo node
"""

import collections
import configparser
import argparse
import time
import traceback
import logging
import signal
import sys
import json
import os
from multiprocessing import Process

import psutil
from scripts.node_sender.sender import Sender


def kill_sender():
    """ Kill sender process by ID """
    my_pid = os.getpid()
    for proc in psutil.process_iter():
        if proc.name() == "start_sender.py" and proc.pid != my_pid:
            print("Killing previous sender process")
            os.kill(proc.pid, signal.SIGTERM)


def transfer_operation(sender, txs_count):
    """ Send transaction with txs_count transfer operations """

    return sender.transfer(transaction_count=txs_count, fee_amount=20)


def create_evm_contract_operation(sender, txs_count):
    """ Send transaction with txs_count create evm contract operations """

    return sender.create_contract(
        transaction_count=txs_count, x86_64_contract=False, fee_amount=395
    )


def create_x86_contract_operation(sender, txs_count):
    """ Send transaction with txs_count create x86 contract operations """

    return sender.create_contract(
        transaction_count=txs_count, x86_64_contract=True, fee_amount=201
    )


def call_evm_contract_operation(sender, txs_count):
    """ Send transaction with txs_count call evm contract operations """

    return sender.call_contract(
        contract_id="1.11.0",
        transaction_count=txs_count,
        x86_64_contract=False,
        fee_amount=244,
    )


def call_x86_contract_operation(sender, txs_count):
    """ Send transaction with txs_count call x86 contract operations """

    return sender.call_contract(
        contract_id="1.11.0",
        transaction_count=txs_count,
        x86_64_contract=True,
        fee_amount=201,
    )


def send_tx(sender, tx_type, txs_count):
    """ Send transaction by operation type """

    # map the inputs to the operation type
    operation_types = {
        1: transfer_operation,
        2: create_evm_contract_operation,
        3: create_x86_contract_operation,
        4: call_evm_contract_operation,
        5: call_x86_contract_operation,
    }

    return operation_types[tx_type](sender, txs_count)


def parse_arguments():
    """ Parse arguments for start sender """

    parser = argparse.ArgumentParser(description="Help for bm-scripts binary")
    parser.add_argument(
        "-hi",
        "--hosts_info",
        dest="hosts_info",
        action="store",
        type=str,
        help='Host info in dictionary format: {"ip address" : number of nodes}',
        default="",
    )
    parser.add_argument(
        "-txs",
        "--txs_count",
        dest="txs_count",
        action="store",
        type=int,
        help="Number of transactions",
        default=1,
    )
    parser.add_argument(
        "-d",
        "--delay",
        dest="delay",
        action="store",
        type=int,
        help="Delay in seconds between transfers",
        default=0,
    )
    parser.add_argument(
        "-n",
        "--account_num",
        dest="account_num",
        action="store",
        type=int,
        help="Number of accounts",
        required=True,
    )
    parser.add_argument(
        "-tt",
        "--tx_type",
        dest="tx_type",
        action="store",
        type=int,
        help="Transaction type: 1-transfer, 2-create_evm, 3-create_x86, 4-call_evm, 5-call_x86",
        default=1,
    )
    parser.add_argument(
        "-sn",
        "--sender_number",
        dest="sender_number",
        action="store",
        type=int,
        help="The sequence number of the sender",
        required=True,
    )
    parser.add_argument(
        "-s",
        "--start_new",
        action="store_true",
        help="Start new sender instance without deletion previous",
    )
    parser.add_argument(
        "-t",
        "--tps",
        action="store_true",
        help="Enable adaptive sleep for constant tps",
    )
    parser.add_argument(
        "-ibn",
        "--import_balance_nathan",
        action="store_true",
        help="Enable import balance to nathan",
    )
    parser.add_argument(
        "-mp",
        "--multiprocess",
        action="store_true",
        help="If specified, then sender will work multiprocessing",
    )
    parser.add_argument(
        "-pn",
        "--private_network",
        action="store_true",
        help="Enable sender for private network",
    )

    return parser.parse_args()


def config_parse(section):
    """ Parse hosts config for start sender """

    parser = configparser.ConfigParser()

    parser.read("scripts/resources/host_config.ini")

    if not parser.sections():
        raise Exception("Config parse read exception, path to config incorrect")

    hosts_info = parser._sections[section]

    return {k: int(v) for k, v in hosts_info.items()}


def connect_to_peers(hosts_info, number_of_accounts):
    """ Setting up a connection to nodes """

    senders = []
    info_nodes = []
    start_port = 8090
    sender_id = 0

    for addr, count_nodes in hosts_info.items():
        for index in range(count_nodes):
            try:
                print("Trying connect to", addr, ":", start_port + index, flush=True)

                sender = Sender(
                    addr,
                    start_port + index,
                    number_of_accounts,
                    call_id=sender_id,
                    step=count_nodes,
                )
                senders.append(sender)

                info = "Address : {}  Port : {}".format(addr, start_port + index)
                info_nodes.append(info)

                print("Done", flush=True)

                sender_id = sender_id + 1
            except ConnectionRefusedError as err:
                logging.error(traceback.format_exc())
                print(err, flush=True)

    return senders, info_nodes


def send(args, sender, info):
    """ Send transactions with arguments """

    while sender.is_interrupted is False:
        print("Trying sent transactions to:", info, flush=True)
        if args.tps is True:
            start = time.time()
            sent = send_tx(sender, args.tx_type, args.txs_count)
            print(sent, "Transactions sent", flush=True)
            diff = time.time() - start
            if diff < 1.0:
                time.sleep(round((1.0 - diff), 3))
        else:
            sent = send_tx(sender, args.tx_type, args.txs_count)
            print(sent, "Transactions sent", flush=True)
            time.sleep(args.delay)


def run_sender(args, senders, info_nodes):
    """ Run sender to send transactions """

    print("Run sender")

    while senders:
        for index, _ in enumerate(senders):
            try:
                send(args, senders[index], info_nodes[index])
            except Exception as err:
                print(
                    "Caught exception during transaction sending: {0}".format(err),
                    flush=True,
                )
                logging.error(traceback.format_exc())

                del senders[index]
                del info_nodes[index]


def run_sender_with_subprocess(args, senders, info_nodes, number_of_subprocesses):
    """ Run some senders to send transactions with multiprocessing """

    print("Start in multiprocessing")

    processes = []
    for _ in range(number_of_subprocesses):
        sender_process = Process(target=run_sender, args=(args, senders, info_nodes))
        processes.append(sender_process)
        sender_process.start()


def main():
    """ Main function for start sender """

    args = parse_arguments()

    if not args.hosts_info:
        hosts_info = config_parse(
            "private_network" if args.private_network else "echo_servers"
        )
    else:
        hosts_info = json.loads(args.hosts_info)

    if args.start_new is False:
        kill_sender()

    def signal_handler(sig, frame):
        print("\nCaught signal: ", sig, ":", frame)
        for sender in senders:
            sender.interrupt_sender()
        raise SystemExit("Exited from Ctrl-C handler")

    signal.signal(signal.SIGINT, signal_handler)

    count_nodes = sum(int(hosts_info[host]) for host in hosts_info)
    if count_nodes > args.account_num:
        raise Exception(
            "Number of nodes should be less or equal to initial accounts number!"
        )

    senders, info_nodes = connect_to_peers(hosts_info, args.account_num)

    if not senders:
        print("\nList senders is empty", flush=True)
        sys.exit(1)

    if args.import_balance_nathan is True:
        senders[0].import_balance_to_nathan()

    if args.tx_type == 4 or args.tx_type == 5:
        send_tx(senders[0], args.tx_type, 1)

    if args.multiprocess is False:
        run_sender(args, senders, info_nodes)
    else:
        run_sender_with_subprocess(args, senders, info_nodes, 3)


if __name__ == "__main__":
    try:
        main()
    except SystemExit as err:
        print(err)
    except Exception as err:
        print(err)
        logging.error(traceback.format_exc())
