from echopy import Echo
from .files_path import (ECHO_CONTRACTS, ETHEREUM_CONTRACTS)
from echopy.echobase.account import BrainKey

class tx_ratio:
    transfer = 0.88
    create_contract = 0.04
    call_contract = 0.08


NATHAN_PRIV = "5JjHQ1GqTbqVZLdTB3QRqcUWA6LezqA65iPJbq5craE6MRc4u9K"
NATHAN_PUB = "ECHO5NaRTkq4uBAVGrZkD3jcTEdUxhxxJLU7hvt3p1zJyytc"
INITIAL_BALANCE = 1000000000000000

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

def get_byte_code(contract_name, code_or_method_name, ethereum_contract=False):
    if ethereum_contract:
        return ETHEREUM_CONTRACTS[contract_name][code_or_method_name]
    return ECHO_CONTRACTS[contract_name][code_or_method_name]

async def connect_echo(url):
    echo = Echo()
    await echo.connect(url)
    return echo

async def disconnect_echo(echo):
    await echo.disconnect()
