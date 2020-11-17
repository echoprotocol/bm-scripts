from datetime import timezone, datetime
from math import ceil
from calendar import timegm
from time import strptime
import asyncio

class tx_ratio:
    transfer = 0.88
    create_contract = 0.04
    call_contract = 0.08


NATHAN_PRIV = "5JjHQ1GqTbqVZLdTB3QRqcUWA6LezqA65iPJbq5craE6MRc4u9K"
NATHAN_PUB = "ECHO5NaRTkq4uBAVGrZkD3jcTEdUxhxxJLU7hvt3p1zJyytc"

from echopy.echobase.account import BrainKey


def generate_keys(account_num):
    name = "init{}"
    private_keys = []
    public_keys = []
    for i in range(account_num - 1):
        key = BrainKey(brain_key=name.format(i))
        private_keys.append(key.get_private_key_base58())
        public_keys.append(key.get_public_key_base58())
    private_keys.append(NATHAN_PRIV)
    public_keys.append(NATHAN_PUB)
    return [private_keys, public_keys]


def seconds_to_iso(sec):
    iso_result = (
        datetime.fromtimestamp(sec, timezone.utc).replace(microsecond=0).isoformat()
    )
    return iso_result[: iso_result.rfind("+")]


def run_async(coro):
        return asyncio.get_event_loop().run_until_complete(coro)
