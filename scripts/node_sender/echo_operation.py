import json
import time

from calendar import timegm
from codecs import decode
from copy import deepcopy
from datetime import datetime, timezone
from math import ceil
from collections import OrderedDict

from echopy.transaction import TransactionType


class Operation:
    def __init__(self, operation_id, props, signer):
        self.operation_id = operation_id
        self.operation_props = props
        self.signer = signer


class EchoOperation:
    def get_balance_claim_operation(
        self,
        echo,
        deposit_to_account,
        balance_owner_public_key,
        value_amount,
        balance_owner_private_key,
        balance_to_claim='1.8.0',
        value_asset_id='1.3.0',
        extensions=[]
    ):
        balance_claim_operation_props = OrderedDict(
            [
                ("deposit_to_account", deposit_to_account),
                ("balance_to_claim", balance_to_claim),
                ("balance_owner_key", balance_owner_public_key),
                ("total_claimed", OrderedDict(
                    [
                        ("amount", value_amount),
                        ("asset_id", value_asset_id)
                    ]
                )
                ),
                ("extensions", extensions)
            ]
        )
        operation_id = echo.config.operation_ids.BALANCE_CLAIM
        return Operation(operation_id, balance_claim_operation_props, balance_owner_private_key)

    def get_transfer_operation(
        self,
        echo,
        account_from,
        account_to,
        # TODO: add support without signer(get private key from account_from)
        signer,
        amount=1,
        amount_asset_id='1.3.0',
        extensions=[]
    ):
        transfer_options = OrderedDict(
            [
                ("from", account_from),
                ("to", account_to),
                ("amount", OrderedDict(
                    [
                        ("amount", amount),
                        ("asset_id", amount_asset_id)
                    ]
                )
                ),
                ("extensions", extensions)
            ]
        )
        operation_id = echo.config.operation_ids.TRANSFER
        return Operation(operation_id, transfer_options, signer)

    def get_contract_create_operation(
        self,
        echo,
        registrar,
        bytecode,
        # TODO: add support without signer(get private key from registrar)
        signer,
        value_amount=0,
        value_asset_id='1.3.0',
        supported_asset_id=None,
        eth_accuracy=False,
        extensions=[]
    ):
        contract_create_props = OrderedDict(
            [
                ("registrar", registrar),
                ("value", OrderedDict(
                    [
                        ("amount", value_amount),
                        ("asset_id", value_asset_id)
                    ]
                )
                ),
                ("code", bytecode),
                ("eth_accuracy", eth_accuracy),
                ("extensions", extensions)
            ]
        )
        operation_id = echo.config.operation_ids.CONTRACT_CREATE
        return Operation(operation_id, contract_create_props, signer)

    def get_contract_call_operation(
        self,
        echo,
        registrar,
        bytecode,
        callee,
        # TODO: add support without signer(get private key from registrar)
        signer,
        value_amount=0,
        value_asset_id='1.3.0',
        extensions=[]
    ):
        contract_call_props = OrderedDict(
            [
                ("registrar", registrar),
                ("value", OrderedDict(
                    [
                        ("amount", value_amount),
                        ("asset_id", value_asset_id)
                    ]
                )
                ),
                ("code", bytecode),
                ("callee", callee),
                ("extensions", extensions)
            ]
        )
        operation_id = echo.config.operation_ids.CONTRACT_CALL
        return Operation(operation_id, contract_call_props, signer)

    def add_fee_to_operation(
        self,
        echo,
        operation,
        fee_amount,
        fee_asset_id='1.3.0'
    ):
        fee = OrderedDict(
            [
                ("amount", fee_amount),
                ("asset_id", fee_asset_id)
            ]
        )
        operation.operation_props.update({'fee': fee})
        operation.operation_props.move_to_end('fee', last=False)

    async def sign_transaction(self, echo, operation_ids, props, signer):
        tx = echo.create_transaction()
        if type(operation_ids) is list:
            assert(len(operation_ids) == len(props))
            for i in range(len(operation_ids)):
                tx = tx.add_operation(name=operation_ids[i], props=props[i])
        else:
            tx = tx.add_operation(name=operation_ids, props=props)
        await tx.sign(signer)
        return tx

    async def broadcast_operation(self, echo, operation_ids, props, signer, callback=None):
        tx = await self.sign_transaction(echo, operation_ids, props, signer)
        return await tx.broadcast(callback=callback)
