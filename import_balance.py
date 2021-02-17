#!/usr/bin/python3

import argparse
import asyncio
from scripts.node_sender.sender import create_sender


async def main():
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
    parser.add_argument(
        "-pn",
        "--private_network",
        action="store_true",
        help="Enable sender for private network",
    )
    args = parser.parse_args()

    s = await create_sender(args.address, args.port)

    if args.private_network is True:
        s.private_network()

    await s.import_balance_to_nathan()
    del s


if __name__ == "__main__":
    asyncio.run(main())
