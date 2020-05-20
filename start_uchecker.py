#!/usr/bin/python3

import argparse
from scripts.node_deployer.utilization_checker import utilization_checker
import signal


def main():
    u = None

    def signal_handler(sig, frame):
        print("\nCaught SIGINT:")
        if u is not None:
            u.is_running = False

    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description="Help for bm-scripts binary")
    parser.add_argument(
        "-n",
        "--node_count",
        action="store",
        dest="node_count",
        type=int,
        help="Node count for measuring",
        default=2,
    )
    parser.add_argument(
        "-v",
        "--volume_dir",
        dest="volume_dir",
        action="store",
        type=str,
        help="Volume dir shared between host and containers",
        default="",
    )
    args = parser.parse_args()

    addrs = []
    ports = []
    names = []
    start_addr = "172.17.0.{}"
    start_name = "echonode{}"
    for i in range(args.node_count):
        addrs.append(start_addr.format(i + 2))
        ports.append(13375 + i)
        names.append(start_name.format(i))

    volume_dir = args.volume_dir
    if args.volume_dir[-1] == "/":
        volume_dir = volume_dir[:-1]
    u = utilization_checker(addrs, ports, names, volume_dir=volume_dir)
    u.collect_stats()
    print("Stopped")


if __name__ == "__main__":
    main()
