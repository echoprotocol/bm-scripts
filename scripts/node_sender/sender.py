from .base import Base

from ..utils.utils import (generate_keys, get_byte_code, INITIAL_BALANCE)

import logging
import traceback
import random
import json
import os
import threading
import echopy
import sys
from websocket import create_connection

async def create_sender(node_url, port, index=0, step=1, sequence_num=0):
    sender = Sender(node_url, port)
    await sender._init()
    return sender

class Sender(Base):
    def __init__(self, node_url, port, index=0, step=1, sequence_num=0):
        super().__init__(node_url, port)

        self.from_id = 6
        self.to_id = 0

        self.step = step
        self.index = index
        self.sequence_num = sequence_num
        self.transfer_amount = 0
        self.fee_delta = 0
        self.is_interrupted = False

    async def _init(self):
        await super()._init()
        self.account_num = (
            await self.get_account_count() - 6
        )  # 6 - Count reserved Account IDs with special meaning
        self.generate_private_keys()
        self.nathan = await self.get_account('nathan')

    def __del__(self):
        self.interrupt_sender()

    async def _del(self):
        self.interrupt_sender()
        await super(Sender, self)._del()

    def interrupt_sender(self):
        self.is_interrupted = True

    def generate_private_keys(self):
        self.private_keys = generate_keys(self.account_num)[0]
        self.nathan_priv_key = self.private_keys[-1]

    @staticmethod
    def private_keys_parse():
        """ Parse private keys for private network """

        keys = []

        dirname = os.path.dirname(__file__)
        file = dirname + "/../resources/private_keys.json"
        with open(file, "r") as f:
            data = f.read()
        data = json.loads(data)
        for value in data.values():
            keys.append(value)

        return keys

    def private_network(self):
        self.private_keys = self.private_keys_parse()
        self.nathan_priv_key = self.private_keys[-1]

    def set_from_id(self):
        self.from_id = self.index + self.step * self.sequence_num
        if self.from_id >= self.account_num:
            self.from_id = int(self.from_id % self.account_num)

    def import_balance_to_nathan(self):
        print("Started import balance")
        nathan_public_key = self.get_public_key(self.nathan)
        operation = self.echo_ops.get_balance_claim_operation(
            self.echo,
            self.nathan["id"],
            nathan_public_key,
            INITIAL_BALANCE,
            self.nathan_priv_key
        )

        self.echo_ops.broadcast_operation(
            echo=self.echo,
            operation_ids=operation.operation_id,
            props=operation.operation_props,
            signer=operation.signer
        )
        print("Import balance - Done\n")

    def balance_distribution(self):
        print("Started balance distribution")

        ids = []
        props = []
        signer = self.nathan_priv_key

        distributed_balance = int(INITIAL_BALANCE / (self.account_num))

        to_id = "1.2.{}"
        for offset in range(self.account_num - 1):
            op = self.echo_ops.get_transfer_operation(
                echo=self.echo,
                account_from=self.nathan["id"],
                account_to=to_id.format(offset + 6),
                amount=distributed_balance,
                signer=signer
            )
            ids.append(op.operation_id)
            props.append(op.operation_props)

        self.echo_ops.broadcast_operation(
            echo=self.echo,
            operation_ids=ids,
            props=props,
            signer=signer
        )
        print("Balance distribution - Done\n")

    async def send_operations(self, operations, callback=None):
        k = 0
        for op in operations:
            try:
                await self.echo_ops.broadcast_operation(
                    echo=self.echo,
                    operation_ids=op.operation_id,
                    props=op.operation_props,
                    signer=op.signer,
                    callback=callback
                )
                k = k + 1
            except echopy.echoapi.ws.exceptions.RPCError as rpc_error:
                if "skip_transaction_dupe_check" in str(rpc_error):
                    logging.warning("Caught txs dupe")
                elif "is_known_transaction" in str(rpc_error):
                    logging.warning("The same transaction exists in chain")
                elif "pending_txs" in str(rpc_error):
                    logging.warning(
                        "The same transaction exists in pending txs")
                else:
                    logging.error(str(rpc_error))
                k = k - 1
        return k

    def get_next_to_account(self, from_account, to_account):
        to_account = to_account * (
            ((to_account - (self.account_num)) & 0xFFFFFFFF) >> 31
        )
        return to_account + (not (from_account ^ to_account))

    def get_next_value(self, value, increase_it):
        value = value + (self.index + self.step *
                         (self.sequence_num + 1)) * increase_it
        increase_next = ((value - 16383) & 0xFFFFFFFF) >> 31
        value = value * increase_next
        return value, not (increase_next)

    def transfer(self, transaction_count=1, amount=1, fee_amount=None):
        from_acc = "1.2.{}"
        to_acc = "1.2.{}"

        self.to_id = self.get_next_to_account(self.from_id, self.to_id)
        operations = []
        for _ in range(transaction_count):
            from_ = from_acc.format(self.from_id + 6)
            to_ = to_acc.format(self.to_id + 6)
            self.fee_delta, increase_transfer_value = self.get_next_value(
                self.fee_delta, True
            )

            transfer_operation = self.echo_ops.get_transfer_operation(
                echo=self.echo,
                account_from=from_,
                amount=self.transfer_amount + 1,
                account_to=to_,
                signer=self.private_keys[self.from_id],
            )
            self.echo_ops.add_fee_to_operation(
                echo=self.echo,
                operation=transfer_operation,
                fee_amount=fee_amount + self.fee_delta
            )
            operations.append(transfer_operation)
            self.transfer_amount, increase_next_account = self.get_next_value(
                self.transfer_amount, increase_transfer_value
            )
            self.to_id = self.to_id = self.get_next_to_account(
                self.from_id, self.to_id + 1 * increase_next_account
            )

        return self.send_operations(operations)

    async def create_contract(
        self,
        x86_64_contract=True,
        value=0,
        transaction_count=1,
        fee_amount=None,
        callback=None,
    ):
        code = get_byte_code(
            "fib", "code", ethereum_contract=not x86_64_contract)

        operations = []

        for _ in range(transaction_count):
            self.fee_delta, increase_transfer_value = self.get_next_value(
                self.fee_delta, True
            )
            operation = self.echo_ops.get_contract_create_operation(
                echo=self.echo,
                registrar="1.2.{}".format(self.from_id + 6),
                bytecode=code,
                value_amount=self.transfer_amount + 1,
                signer=self.private_keys[self.from_id],
            )
            self.echo_ops.add_fee_to_operation(
                echo=self.echo,
                operation=operation,
                fee_amount=fee_amount + self.fee_delta
            )
            self.transfer_amount, _ = self.get_next_value(
                self.transfer_amount, increase_transfer_value
            )
            operations.append(operation)

        return await self.send_operations(operations, callback)

    def call_contract(
        self,
        contract_id=None,
        x86_64_contract=True,
        value=0,
        transaction_count=1,
        fee_amount=None,
    ):
        if contract_id is None:
            contract_id = "1.11.0"

        code = get_byte_code(
            "fib", "fib(1)", ethereum_contract=not x86_64_contract)

        operations = []

        for _ in range(transaction_count):
            self.fee_delta, increase_transfer_value = self.get_next_value(
                self.fee_delta, True
            )
            operation = self.echo_ops.get_contract_call_operation(
                echo=self.echo,
                registrar="1.2.{}".format(self.from_id + 6),
                value_amount=self.transfer_amount + 1,
                bytecode=code,
                callee=contract_id,
                signer=self.private_keys[self.from_id],
            )
            self.echo_ops.add_fee_to_operation(
                echo=self.echo,
                operation=operation,
                fee_amount=fee_amount + self.fee_delta
            )
            self.transfer_amount, _ = self.get_next_value(
                self.transfer_amount, increase_transfer_value
            )
            operations.append(operation)

        return self.send_operations(operations)

    def create_transfer_transaction(self):
        operations = []
        transfer_operation = self.echo_ops.get_transfer_operation(
            echo=self.echo,
            account_from=self.nathan["id"],
            amount=1,
            account_to="1.2.6",
            signer=self.nathan_priv_key,
        )
        self.echo_ops.add_fee_to_operation(
            echo=self.echo,
            operation=transfer_operation
        )
        operations.append(transfer_operation)

        sign_transactions = []
        for op in operations:
            sign_transactions.append(
                self.echo_ops.sign_transaction(
                    echo=self.echo,
                    operation_ids=op.operation_id,
                    props=op.operation_props,
                    signer=op.signer
                )
            )
        return sign_transactions[0]
