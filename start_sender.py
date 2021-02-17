#!/usr/bin/python3

"""
Sender transactions for Echo node
"""

import configparser
import argparse
import time
import traceback
import logging
import signal
import sys
import json
import os
import asyncio
import concurrent.futures

import psutil
from scripts.node_sender.sender import create_sender
from scripts.node_sender.base import create_base


def kill_sender():
    """ Kill sender process by ID """

    my_pid = os.getpid()
    for proc in psutil.process_iter():
        if proc.name() == "start_sender.py" and proc.pid != my_pid:
            print("Killing previous sender process")
            os.kill(proc.pid, signal.SIGTERM)


async def shutdown(signal, loop):
    """Cleanup tasks tied to the service's shutdown."""

    logging.info(f"Received exit signal {signal.name}...")
    tasks = [t for t in asyncio.all_tasks() if t is not
             asyncio.current_task()]

    [task.cancel() for task in tasks]

    logging.info(f"Cancelling {len(tasks)} outstanding tasks")
    await asyncio.gather(*tasks)
    logging.info(f"Flushing metrics")
    loop.stop()


def setup_sender_logger(start_index):
    """ To setup for sender logger. Start index in this case file log ID """

    logging.basicConfig(
        filename="send{}.log".format(start_index), filemode="w", level=logging.INFO
    )


async def transfer_operation(sender, txs_count):
    """ Send transaction with txs_count transfer operations """

    return await sender.transfer(transaction_count=txs_count, fee_amount=20)


async def create_evm_contract_operation(sender, txs_count):
    """ Send transaction with txs_count create evm contract operations """

    return await sender.create_contract(
        transaction_count=txs_count, x86_64_contract=False, fee_amount=395
    )


async def create_x86_contract_operation(sender, txs_count):
    """ Send transaction with txs_count create x86 contract operations """

    return await sender.create_contract(
        transaction_count=txs_count, x86_64_contract=True, fee_amount=201
    )


async def call_evm_contract_operation(sender, txs_count):
    """ Send transaction with txs_count call evm contract operations """

    return await sender.call_contract(
        contract_id="1.11.0",
        transaction_count=txs_count,
        x86_64_contract=False,
        fee_amount=244,
    )


async def call_x86_contract_operation(sender, txs_count):
    """ Send transaction with txs_count call x86 contract operations """

    return await sender.call_contract(
        contract_id="1.11.0",
        transaction_count=txs_count,
        x86_64_contract=True,
        fee_amount=201,
    )


async def send_tx(sender, tx_type, txs_count):
    """ Send transaction by operation type """

    # map the inputs to the operation type
    operation_types = {
        1: transfer_operation,
        2: create_evm_contract_operation,
        3: create_x86_contract_operation,
        4: call_evm_contract_operation,
        5: call_x86_contract_operation,
    }

    return await operation_types[tx_type](sender, txs_count)


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
    # parser.add_argument(
    #     "-mp",
    #     "--multiprocess",
    #     dest="multiprocess",
    #     action="store",
    #     type=int,
    #     help="Specify the number of running sender transactions",
    #     default=0,
    # )
    parser.add_argument(
        "-pn",
        "--private_network",
        action="store_true",
        help="Enable sender for private network",
    )

    return parser.parse_args()


def host_config_parse(section):
    """ Parse hosts config for start sender """

    parser = configparser.ConfigParser()

    parser.read("scripts/resources/host_config.ini")

    if not parser.sections():
        raise Exception(
            "Config parse read exception, path to config incorrect")

    return {k: int(v) for k, v in parser.items(section)}


async def validate_count_nodes(hosts_info):
    """ Validation arguments hosts info with number of accounts """

    address = next(iter(hosts_info))

    try:
        base = await create_base(address, 8090)

        number_of_accounts = await base.get_account_count()
        count_nodes = sum(int(hosts_info[host]) for host in hosts_info)
        if count_nodes > number_of_accounts:
            raise Exception(
                "Number of nodes should be less or equal to initial accounts number!"
            )
    except ConnectionRefusedError as err:
        logging.error(traceback.format_exc())
        print(err, flush=True)


async def connect_to_peers(hosts_info, sender_number):
    """ Setting up a connection to nodes """

    senders = []
    info_nodes = []
    start_port = 8090
    sender_id = 0

    for addr, count_nodes in hosts_info.items():
        for index in range(count_nodes):
            try:
                print("Trying connect to", addr, ":",
                      start_port + index, flush=True)

                sender = await create_sender(
                    addr,
                    start_port + index,
                    index=sender_id,
                    step=count_nodes,
                    sequence_num=sender_number
                )
                senders.append(sender)

                info = "Address : {}  Port : {}".format(
                    addr, start_port + index)
                info_nodes.append(info)

                print("Done", flush=True)

                sender_id = sender_id + 1
            except ConnectionRefusedError as err:
                logging.error(err, flush=True)

    return senders, info_nodes


async def send(args, sender, info):
    """ Send transactions with arguments """

    sent = 0

    if not sender.is_interrupted:
        logging.info("Trying sent transactions to: %s", info)
        if args.tps:
            start = time.time()
            sent = await send_tx(sender, args.tx_type, args.txs_count)
            logging.info("%d transactions sent", sent)
            diff = time.time() - start
            if diff < 1.0:
                time.sleep(round((1.0 - diff), 3))
        else:
            sent = await send_tx(sender, args.tx_type, args.txs_count)
            logging.info("%d transactions sent", sent)
            time.sleep(args.delay)
    return sent


async def run_sender(args, senders, info_nodes, sender_ID=0):
    """ Run sender to send transactions """

    print("Run sender{}".format(sender_ID))

    offset = sender_ID  # Starting the sender with an offset
    while senders:
        for index, _ in enumerate(senders, offset):
            try:
                if index == len(senders) - 1:
                    offset = 0
                    break
                await send(args, senders[index], info_nodes[index])
            except asyncio.CancelledError:
                print("Received cancelled error")
                logging.error(traceback.format_exc())

                del senders[index]
                del info_nodes[index]
            except Exception as err:
                print(
                    "Caught exception during transaction sending: {0}".format(err))
                logging.error(traceback.format_exc())

                del senders[index]
                del info_nodes[index]


async def run_sender_in_multiprocessing(args, senders, info_nodes, number_of_subprocesses):
    """ Run some senders to send transactions with multiprocessing """

    print("Start in multiprocessing")

    sender_numbers = range(
        args.sender_number, args.sender_number + number_of_subprocesses
    )  # fix duplicate transactions for senders in multiprocessing mode

    for index in range(number_of_subprocesses):
        setup_sender_logger(sender_numbers[index])

        for sender in senders:
            sender.sequence_num = sender_numbers[index]
            sender.set_from_id()

        # sender_process = Process(
        #     target=run_sender, args=(args, senders, info_nodes, index)
        # )
        # sender_process.start()
        # await asyncio.create_subprocess_exec(
        #     *["./start_sender"] + [args, senders, info_nodes, index],
        #     stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)


async def main():
    """ Main function for start sender """

    args = parse_arguments()

    if not args.hosts_info:
        hosts_info = host_config_parse(
            "private_network" if args.private_network else "echo_servers"
        )
    else:
        hosts_info = json.loads(args.hosts_info)

    if args.start_new:
        kill_sender()

    await validate_count_nodes(hosts_info)

    senders, info_nodes = await connect_to_peers(hosts_info, args.sender_number)

    loop = asyncio.get_event_loop()

    # May want to catch other signals too
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(shutdown(s, loop)))

    if not senders:
        print("\nList senders is empty", flush=True)
        sys.exit(1)

    if args.private_network:
        for sender in senders:
            sender.private_network()

    if args.tx_type == 4 or args.tx_type == 5:
        await send_tx(senders[0], args.tx_type - 2, 1)

    setup_sender_logger(args.sender_number)
    await run_sender(args, senders, info_nodes)
    # TODO: add support multiprocessing
    # await run_sender_in_multiprocessing(args, senders, info_nodes, args.multiprocess)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except SystemExit as err:
        print(err)
    except Exception as err:
        print(err)
        logging.error(traceback.format_exc())
