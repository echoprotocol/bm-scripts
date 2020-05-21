#!/usr/bin/python3

import argparse
from scripts.node_sender.sender import Sender


def main():
    parser = argparse.ArgumentParser(description="Help for bm-scripts binary")
    parser.add_argument(
        "-a",
        "--address",
        dest="address",
        action="store",
        type=str,
        help="Specify address for sender",
        default="",
    )
    parser.add_argument(
        "-p",
        "--port",
        dest="port",
        action="store",
        type=int,
        help="Specify port for sender",
        default="",
    )
    args = parser.parse_args()

    s = Sender(args.address, args.port)
    s.balance_distribution()
    s.interrupt_sender()


if __name__ == "__main__":
    main()
