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
import threading
import logging


def kill_sender():
    my_pid = os.getpid()
    for proc in psutil.process_iter():
        if proc.name() == "start_sender.py" and proc.pid != my_pid:
            print("Killing previous sender process")
            os.kill(proc.pid, signal.SIGTERM)


sending = True


def send(sender, args, info):
    try:
        while sending:
            print("Trying sent transactions to:", info, flush=True)
            if args.tps == True:
                start = time.time()
                sent = send_tx(sender, args)
                print(sent, "Transactions sent", flush=True)
                diff = time.time() - start
                if diff < 1.0:
                    time.sleep(round((1.0 - diff), 3))
            else:
                sent = send_tx(sender, args)
                print(sent, "Transactions sent", flush=True)
                time.sleep(args.delay)
    except Exception as e:
        print("Caught exception during transaction sending", flush=True)
        logging.error(traceback.format_exc())


def send_tx(sender, args):
    if args.tx_type == 1:
        return sender.transfer(args.txs_count, fee_amount=20)
    elif args.tx_type == 2:
        return sender.create_contract(
            transaction_count=args.txs_count, x86_64_contract=False, fee_amount=395
        )
    elif args.tx_type == 3:
        return sender.create_contract(
            transaction_count=args.txs_count, x86_64_contract=True, fee_amount=201
        )
    elif args.tx_type == 4:
        return sender.call_contract(
            contract_id="1.11.0",
            transaction_count=args.txs_count,
            x86_64_contract=False,
            fee_amount=244,
        )
    elif args.tx_type == 5:
        return sender.call_contract(
            contract_id="1.11.0",
            transaction_count=args.txs_count,
            x86_64_contract=True,
            fee_amount=201,
        )


slist = []
tlist = []


def main():
    parser = argparse.ArgumentParser(description="Help for bm-scripts binary")
    parser.add_argument(
        "-hi",
        "--hosts_info",
        dest="hosts_info",
        action="store",
        type=str,
        help='Host info in dictionary formar: {"ip address" : number of nodes}',
        default="",
        required=True,
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
        default=2,
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
        help="Transaction type: 1 - transfer, 2 - create_evm, 3 - create_x86, 4 - call_evm, 5 - call_x86",
        default=1,
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
        "-p",
        "--parallel",
        action="store_true",
        help="If specified, then sender will work concurrently",
    )
    args = parser.parse_args()
    hosts_info = json.loads(args.hosts_info)

    if args.start_new == False:
        kill_sender()

    start_port = 8090
    info_lst = []
    prev_num_nodes = 0

    def signal_handler(sig, frame):
        print("\nCaught SIGINT:")
        sending = False
        for s in slist:
            s.interrupt_sender()
        raise SystemExit("Exited from Ctrl-C handler")

    signal.signal(signal.SIGINT, signal_handler)

    step = 0
    for addr, count in hosts_info.items():
        step = step + count

    if step > args.account_num:
        raise Exception(
            "Number of nodes should be less or equal to initial accounts number!"
        )

    j = 0
    for addr, count in hosts_info.items():
        for i in range(count):
            try:
                print("Trying connect to", addr, ":", start_port + i)
                sys.stdout.flush()
                s = Sender(addr, start_port + i, args.account_num, call_id=j, step=step)
                info = "Address : {}  Port : {}".format(addr, start_port + i)
                slist.append(s)
                info_lst.append(info)
                t = threading.Thread(target=send, args=(slist[j], args, info,))
                tlist.append(t)
                print("Done")
                sys.stdout.flush()
                j = j + 1
            except ConnectionRefusedError as e:
                logging.error(traceback.format_exc())
                sys.stdout.flush()
                print(e)
                sys.stdout.flush()
        prev_num_nodes = prev_num_nodes + count

    if slist:
        if args.tx_type == 4:
            slist[0].create_contract(x86_64_contract=False, with_response=True)
        elif args.tx_type == 5:
            slist[0].create_contract(x86_64_contract=True, with_response=True)

        if args.parallel == False:
            while True:
                i = 0
                num = len(slist)
                if num == 0:
                    break
                while i < num:
                    try:
                        print("Trying sent transactions to:", info_lst[i], flush=True)
                        if args.tps == True:
                            start = time.time()
                            sent = send_tx(slist[i], args)
                            print(sent, "Transactions sent", flush=True)
                            diff = time.time() - start
                            if diff < 1.0:
                                time.sleep(round((1.0 - diff), 3))
                        else:
                            sent = send_tx(slist[i], args)
                            print(sent, "Transactions sent")
                            sys.stdout.flush()
                            time.sleep(args.delay)
                        i = i + 1
                    except Exception as e:
                        print("Caught exception during transaction sending")
                        sys.stdout.flush()
                        logging.error(traceback.format_exc())
                        sys.stdout.flush()
                        del slist[i]
                        del info_lst[i]
                        num = num - 1
        else:
            for t in tlist:
                t.daemon = True
                t.start()
            for t in tlist:
                t.join()


if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        print(e)
    except Exception as e:
        logging.error(traceback.format_exc())
