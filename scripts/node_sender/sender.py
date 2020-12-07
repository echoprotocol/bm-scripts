import time
from datetime import timezone, datetime
from math import ceil
from calendar import timegm

from .base import Base

from ..utils.utils import generate_keys
from ..utils.utils import seconds_to_iso
from ..utils.utils import iso_to_seconds

import logging
import traceback
import random
import json
import os
import threading
import echopy
import sys
from websocket import create_connection

login_req = '{"method": "call", "params": [1, "login", ["", ""]], "id": 0}'
database_req = '{"method": "call", "params": [1, "database", []], "id": 0}'
subscribe_callback_req = (
    '{"method": "set_subscribe_callback", "params": [0, false], "id": 0}'
)
subscribe_dgpo_req = '{"method": "get_objects", "params": [["2.1.0"]], "id": 0}'
tx_count_req = '{{"method": "get_block_tx_number", "params": [{block_id}], "id": 0}}'


class Sender(Base):
    def __init__(self, node_url, port, call_id=0, step=1, sequence_num=0):
        super().__init__(node_url, port)

        self.call_id = call_id

        self.from_id = 6
        self.to_id = 0

        self.account_num = (
            self.get_account_count() - 6
        )  # 6 - Count reserved Account IDs with special meaning
        self.generate_private_keys()

        self.nathan = self.get_account("nathan", self.database_api_identifier)
        self.echo_nathan_id = self.nathan["id"]
        self.INITIAL_BALANCE = 1000000000000000

        self.is_interrupted = False
        self.lock = threading.Lock()
        self.sws = None
        self.t = threading.Thread(target=self.processing_gpo)
        self.t.start()

        self.step = step
        self.index = call_id
        self.sequence_num = sequence_num
        self.set_from_id()
        self.transfer_amount = 0
        self.fee_delta = 0

    def __del__(self):
        self.interrupt_sender()

    def processing_gpo(self):
        try:
            self.sws = create_connection(self.node_url)
            self.sws.send(login_req)
            self.sws.recv()
            self.sws.send(database_req)
            self.sws.recv()
            self.sws.send(subscribe_callback_req)
            self.sws.recv()
            self.sws.send(subscribe_dgpo_req)
            self.sws.recv()
            while not self.is_interrupted:
                msg = self.sws.recv()
                self.lock.acquire()
                response = json.loads(msg)
                self.dynamic_global_chain_data = response["params"][1][0][0]
                self.lock.release()
        except (json.decoder.JSONDecodeError, OSError) as e:
            if not self.is_interrupted:
                print("Caught exception in tps colletor thread:")
                print("-------------------------------------------")
                logging.error(traceback.format_exc())
                print("-------------------------------------------")

    def interrupt_sender(self):
        self.is_interrupted = True
        if self.sws is not None:
            if self.lock.locked() is True:
                self.lock.release()
            self.sws.close()

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
            self.echo_nathan_id,
            nathan_public_key,
            self.INITIAL_BALANCE,
            self.nathan_priv_key,
        )
        collected_operation = self.collect_operations(
            operation, self.database_api_identifier
        )
        self.echo_ops.broadcast(
            self.echo_ops.get_sign_transaction(
                echo=self.echo,
                list_operations=collected_operation,
                chain_id=self.chain_id,
                dynamic_global_chain_data=self.dynamic_global_chain_data,
            ),
            with_response=True,
        )

        print("Import balance - Done\n")

    def balance_distribution(self):
        print("Started balance distribution")

        operations = []

        distributed_balance = int(self.INITIAL_BALANCE / (self.account_num))

        to_id = "1.2.{}"
        for offset in range(self.account_num - 1):
            op = self.echo_ops.get_transfer_operation(
                echo=self.echo,
                from_account_id=self.echo_nathan_id,
                to_account_id=to_id.format(offset + 6),
                amount=distributed_balance,
                signer=self.nathan_priv_key,
            )
            operations.append(self.collect_operations(
                op, self.database_api_identifier))

        self.echo_ops.broadcast(
            self.echo_ops.get_sign_transaction(
                echo=self.echo,
                list_operations=operations,
                chain_id=self.chain_id,
                dynamic_global_chain_data=self.dynamic_global_chain_data,
            ),
            with_response=True,
        )

        print("Balance distribution - Done\n")

    def send_transaction_list(self, transaction_list, with_response=False):
        sign_transaction_list = []

        for tr in transaction_list:
            sign_transaction_list.append(self.echo_ops.get_sign_transaction(
                echo=self.echo,
                list_operations=tr,
                chain_id=self.chain_id,
                dynamic_global_chain_data=self.dynamic_global_chain_data,
            ))

        k = 0
        for tx in sign_transaction_list:
            try:
                self.echo_ops.broadcast(tx, with_response=with_response)
                k = k + 1
            except echopy.echoapi.ws.exceptions.RPCError as rpc_error:
                if "skip_transaction_dupe_check" in str(rpc_error):
                    logging.info("Caught txs dupe")
                elif "is_known_transaction" in str(rpc_error):
                    logging.info("The same transaction exists in chain")
                elif "pending_txs" in str(rpc_error):
                    logging.info("The same transaction exists in pending txs")
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
        transfer_delta = 1

        self.to_id = self.get_next_to_account(self.from_id, self.to_id)
        transaction_list = []
        for _ in range(transaction_count):
            from_ = from_acc.format(self.from_id + 6)
            to_ = to_acc.format(self.to_id + 6)
            self.fee_delta, increase_transfer_value = self.get_next_value(
                self.fee_delta, True
            )

            transfer_operation = self.echo_ops.get_transfer_operation(
                echo=self.echo,
                from_account_id=from_,
                amount=self.transfer_amount + transfer_delta,
                to_account_id=to_,
                signer=self.private_keys[self.from_id],
            )
            collected_operation = self.collect_operations(
                transfer_operation,
                self.database_api_identifier,
                fee_amount=fee_amount + self.fee_delta,
            )
            transaction_list.append(collected_operation)
            self.transfer_amount, increase_next_account = self.get_next_value(
                self.transfer_amount, increase_transfer_value
            )
            self.to_id = self.to_id = self.get_next_to_account(
                self.from_id, self.to_id + 1 * increase_next_account
            )

        return self.send_transaction_list(transaction_list)

    def create_contract(
        self,
        x86_64_contract=True,
        value=0,
        transaction_count=1,
        fee_amount=None,
        with_response=False,
    ):
        code = self.get_byte_code(
            "fib", "code", ethereum_contract=not x86_64_contract)

        transaction_list = []
        transfer_delta = 1

        for _ in range(transaction_count):
            self.fee_delta, increase_transfer_value = self.get_next_value(
                self.fee_delta, True
            )
            operation = self.echo_ops.get_contract_create_operation(
                echo=self.echo,
                registrar="1.2.{}".format(self.from_id + 6),
                bytecode=code,
                value_amount=self.transfer_amount + transfer_delta,
                value_asset_id=self.echo_asset,
                signer=self.private_keys[self.from_id],
            )
            collected_operation = self.collect_operations(
                operation,
                self.database_api_identifier,
                fee_amount=fee_amount + self.fee_delta,
            )
            self.transfer_amount, _ = self.get_next_value(
                self.transfer_amount, increase_transfer_value
            )
            transaction_list.append(collected_operation)

        return self.send_transaction_list(transaction_list, with_response=with_response)

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

        code = self.get_byte_code(
            "fib", "fib(1)", ethereum_contract=not x86_64_contract)

        transaction_list = []
        transfer_delta = 1

        for _ in range(transaction_count):
            self.fee_delta, increase_transfer_value = self.get_next_value(
                self.fee_delta, True
            )
            operation = self.echo_ops.get_contract_call_operation(
                echo=self.echo,
                registrar="1.2.{}".format(self.from_id + 6),
                value_amount=self.transfer_amount + transfer_delta,
                bytecode=code,
                callee=contract_id,
                signer=self.private_keys[self.from_id],
            )
            collected_operation = self.collect_operations(
                operation,
                self.database_api_identifier,
                fee_amount=fee_amount + self.fee_delta,
            )
            self.transfer_amount, _ = self.get_next_value(
                self.transfer_amount, increase_transfer_value
            )
            transaction_list.append(collected_operation)

        return self.send_transaction_list(transaction_list)

    def create_transfer_transaction(self):
        transfer_amount = 1
        to_account_id = "1.2.6"

        transaction_list = []
        transfer_operation = self.echo_ops.get_transfer_operation(
            echo=self.echo,
            from_account_id=self.echo_nathan_id,
            amount=transfer_amount,
            to_account_id=to_account_id,
            signer=self.nathan_priv_key,
        )
        collected_operation = self.collect_operations(
            transfer_operation, self.database_api_identifier
        )
        transaction_list.append(collected_operation)

        sign_transaction_list = []
        time_increment = 300
        for tr in transaction_list:
            now_iso = seconds_to_iso(datetime.now(timezone.utc).timestamp())
            now_seconds = iso_to_seconds(now_iso)
            expiration_time = seconds_to_iso(
                now_seconds + time_increment + self.call_id
            )
            sign_transaction_list.append(
                self.echo_ops.get_sign_transaction(
                    echo=self.echo,
                    list_operations=tr,
                    expiration=expiration_time,
                    chain_id=self.chain_id,
                    dynamic_global_chain_data=self.dynamic_global_chain_data,
                )
            )
            self.call_id += 1

        return sign_transaction_list[0]
