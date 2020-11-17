#!/usr/bin/python3

"""
TPS checker for Echo node
"""

import argparse
import traceback
import signal
import logging
import time

from datetime import datetime
from sys import maxsize
from scripts.node_deployer.tps_checker import tps_checker


def parse_arguments():
    """ Parse arguments for start tps checker """

    parser = argparse.ArgumentParser(description="Help for bm-scripts binary")
    parser.add_argument(
        "-a",
        "--address",
        dest="address",
        action="store",
        type=str,
        help="Address for connecting",
        default="172.17.0.2",
    )
    parser.add_argument(
        "-p",
        "--port",
        dest="port",
        action="store",
        type=int,
        help="Rpc port for connecting",
        default=8090,
    )
    parser.add_argument(
        "-ti",
        "--time_interval",
        action="store",
        dest="time_interval",
        type=int,
        help="Time interval between tps measures (in seconds)",
        default=60,
    )

    return parser.parse_args()


def main():
    """ Main function for start tps checker """

    args = parse_arguments()

    tps = None

    def signal_handler(sig, frame):
        print("\nCaught signal: {}. Frame: {}".format(sig, frame))
        if tps is not None:
            tps.interrupt_checker()
        raise SystemExit("Exited from Ctrl-C handler")

    signal.signal(signal.SIGINT, signal_handler)

    tps = tps_checker(args.address, args.port, maxsize)
    tps.run_check()

    collect_tps_results = []
    while not tps.is_interrupted:
        tps.collected_tx_number = 0
        time.sleep(args.time_interval)
        tps_result = tps.collected_tx_number / args.time_interval
        print(
            datetime.now().strftime("%H:%M:%S"),
            "current tps:",
            tps_result,
            "block num:",
            tps.block_number,
            flush=True,
        )

        collect_tps_results.append(tps_result)
        print("Average tps: {}".format(
            sum(collect_tps_results) / len(collect_tps_results)))


if __name__ == "__main__":
    try:
        main()
    except SystemExit as err:
        print(err)
    except Exception as err:
        print(err)
        logging.error(traceback.format_exc())
