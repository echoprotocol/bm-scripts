from .echo_operation import EchoOperation
from echopy.echobase import validation
from ..utils.utils import (connect_echo, disconnect_echo)

async def create_base(node_url, port):
    base = Base(node_url, port)
    await base._init()
    return base

class Base(object):
    def __init__(self, node_url, port):
        self.node_url = "ws://{}:{}".format(node_url, port)
        self.echo_ops = EchoOperation()

    async def _init(self):
        self.echo = await connect_echo(self.node_url)
        self.database_api = self.echo.api.database

    async def _del(self):
        await disconnect_echo(self.echo)

    async def connect_to_echopy_lib(self):
        try:
            await self.echo.connect(url=self.node_url)
        except Exception as _:
            raise Exception("Connection to echopy-lib not established")

    async def get_required_fee(self, operations, asset_id='1.3.0'):
        return await self.echo.database_api.get_required_fees(operations, asset_id)

    async def get_account(self, account_name):
        if validation.is_account_name(account_name):
            return await self.database_api.get_account_by_name(account_name)
        elif validation.is_account_id(account_name):
            return await self.database_api.get_accounts(account_name)

    async def get_account_count(self):
        return await self.database_api.get_account_count()

    def get_public_key(self, account):
        return account["active"]["key_auths"][0][0]
