from echopy import Echo

from .echo_operation import EchoOperation

from ..utils.files_path import ECHO_CONTRACTS, ETHEREUM_CONTRACTS
from ..utils.utils import run_async

from echopy.echobase import validation


class Base:
    def __init__(self, node_url, port):
        super().__init__()
        self.node_url = "ws://{}:{}".format(node_url, port)
        self.echo = Echo()
        self.connect = run_async(self.connect_to_echopy_lib())
        self.echo_ops = EchoOperation()
        self.database_api = self.echo.api.database

    @staticmethod
    def get_byte_code(contract_name, code_or_method_name, ethereum_contract=False):
        if ethereum_contract:
            return ETHEREUM_CONTRACTS[contract_name][code_or_method_name]
        return ECHO_CONTRACTS[contract_name][code_or_method_name]

    async def connect_to_echopy_lib(self):
        try:
            await self.echo.connect(url=self.node_url)
        except Exception as _:
            raise Exception("Connection to echopy-lib not established")

    def get_required_fee(self, operations, asset_id='1.3.0'):
        return run_async(self.database_api.get_required_fees(operations, asset_id))

    def get_account(self, account_name):
        if validation.is_account_name(account_name):
            return run_async(self.database_api.get_account_by_name(account_name))
        elif validation.is_account_id(account_name):
            return run_async(self.database_api.get_accounts(account_name))

    def get_account_count(self):
        return run_async(self.database_api.get_account_count())

    def get_public_key(self, account):
        return account["active"]["key_auths"][0][0]
