import time
from datetime import timezone, datetime
from math import ceil
from calendar import timegm
from random import randrange

from .base import Base
from ..node_deployer.deployer import NATHAN_PRIV
from ..utils.utils import generate_keys
initial_balance = 1000000000000000
import random
import json
import os

from echopy import Echo

class Sender(Base):
    def __init__(self, node_url, port, account_num, call_id = 0):
        super().__init__(node_url, port)
        self.url="ws://{}:{}".format(node_url, port)
        self.call_id = call_id
        self.nathan = self.get_account("nathan", self.database_api_identifier)
        self.echo_nathan_id = self.nathan["id"]
        self.account_count=int(self.echo_nathan_id.split('.')[-1]) - 6 # without nathan
        self.nathan_priv_key = NATHAN_PRIV
        self.echo_acc_2 = "1.2.6"
        self.x86_64_contract = self.get_byte_code("fib", "code", ethereum_contract = False)
        self.ethereum_contract = self.get_byte_code("fib", "code", ethereum_contract = True)
        self.total_num_send = 0
        self.private_keys = generate_keys(account_num)[0]
        self.from_id=6

    @staticmethod
    def seconds_to_iso(sec):
        iso_result = datetime.fromtimestamp(sec, timezone.utc).replace(microsecond=0).isoformat()
        return iso_result[:iso_result.rfind('+')]

    @staticmethod
    def iso_to_seconds(iso):
        timeformat = "%Y-%m-%dT%H:%M:%S%Z"
        return ceil(timegm(time.strptime((iso + "UTC"), timeformat)))

    def import_balance_to_nathan(self):
        print("Started import balance")
        nathan_public_key = self.get_public_key(self.nathan)
        operation = self.echo_ops.get_balance_claim_operation(self.echo, self.echo_nathan_id, nathan_public_key,
                                                                initial_balance, self.nathan_priv_key)
        collected_operation = self.collect_operations(operation, self.database_api_identifier)
        self.echo_ops.broadcast(self.echo_ops.get_sign_transaction(
            echo = self.echo, list_operations = collected_operation, chain_id = self.chain_id, dynamic_global_chain_data = self.dynamic_global_chain_data),
            with_response = True)

        print("Import balance - Done\n")

    def balance_distribution(self):
        print("Started balance distribution")
        id="1.2.{}"
        op_lst=[]
        bal = int(initial_balance / (self.account_count+1))
        for i in range(self.account_count):
            op=self.echo_ops.get_transfer_operation(echo = self.echo, from_account_id = self.echo_nathan_id,
                amount = bal, to_account_id = id.format(i+6), signer = self.nathan_priv_key)
            ops = self.collect_operations(op, self.database_api_identifier)
            op_lst.append(ops[0])
        now_iso = self.seconds_to_iso(datetime.now(timezone.utc).timestamp())
        now_seconds = self.iso_to_seconds(now_iso)
        expiration_time = self.seconds_to_iso(now_seconds + 300 + self.call_id)

        tx = self.echo.create_transaction()
        for operation in op_lst:
            tx.add_operation(name = operation[0], props = operation[1])
            tx.add_signer(operation[2])
        tx.expiration = expiration_time
        self.echo_ops.sign(tx, self.chain_id, self.dynamic_global_chain_data)
        self.echo_ops.broadcast(tx, with_response=True)
        print("Balance distribution - Done\n")

    def send_transaction_list(self, transaction_list, with_response = False):
        sign_transaction_list = []

        time_increment = 900
        divider = random.randint(100, 250)
        for tr in transaction_list:
            now_iso = self.seconds_to_iso(datetime.now(timezone.utc).timestamp())
            now_seconds = self.iso_to_seconds(now_iso)
            expiration_time = self.seconds_to_iso(now_seconds + time_increment + self.call_id)
            sign_transaction_list.append(self.echo_ops.get_sign_transaction(
                echo = self.echo, list_operations = tr, expiration = expiration_time, chain_id = self.chain_id, dynamic_global_chain_data = self.dynamic_global_chain_data))
            self.call_id += 1
            self.total_num_send += 1
            if (self.total_num_send % divider == 0):
                echo = Echo()
                echo.connect(self.url)
                prev_head=self.dynamic_global_chain_data['head_block_number']
                self.dynamic_global_chain_data = echo.api.database.get_objects(['2.1.0'])[0]
                echo.disconnect()
                divider = random.randint(100, 250)
                if prev_head != self.dynamic_global_chain_data['head_block_number']:
                    self.call_id = 0

        k = 0
        for tr in sign_transaction_list:
            k += 1
            self.echo_ops.broadcast(tr, with_response = with_response)
            if (k % 1000 == 0):
                print("Sent ", k, " transactions")

    def transfer(self, transaction_count = 1, amount = 1):
        from_acc = "1.2.{}"
        to_acc = "1.2.{}"

        a=6
        d=self.account_count+6

        transfer_amount = amount
        transaction_list = []

        n = 0
        while n != transaction_count:
            b=self.from_id-1
            c=self.from_id+1
            numbers = list(range(a,b)) + list(range(c,d))
            r = random.choice(numbers)

            from_ = from_acc.format(self.from_id)
            to_ = to_acc.format(r)

            transfer_operation = self.echo_ops.get_transfer_operation(echo = self.echo, from_account_id = from_,
                amount = transfer_amount, to_account_id = to_, signer = self.private_keys[self.from_id-6])

            collected_operation = self.collect_operations(transfer_operation, self.database_api_identifier)
            transaction_list.append(collected_operation)
            n += 1
            if (self.from_id == self.account_count+6):
                self.from_id = 6
            else:
                self.from_id += 1

        self.send_transaction_list(transaction_list)


    def create_contract(self, x86_64_contract = True, value = 0, transaction_count = 1, with_response = False):
        if x86_64_contract is True:
            code = self.x86_64_contract
        else:
            code = self.ethereum_contract

        transaction_list = []

        n = 0
        while n != transaction_count:
            numbers = list(range(6,self.account_count+6))
            r = random.choice(numbers)
            operation = self.echo_ops.get_contract_create_operation(echo = self.echo, registrar = "1.2.{}".format(r), bytecode = code,
                                                                    value_amount = value, value_asset_id = self.echo_asset,
                                                                    signer = self.private_keys[r-6])
            collected_operation = self.collect_operations(operation, self.database_api_identifier)
            transaction_list.append(collected_operation)
            n += 1

        self.send_transaction_list(transaction_list, with_response = with_response)

    def call_contract(self, contract_id = None, x86_64_contract = True, value = 0, transaction_count = 1):
        if contract_id is None:
            contract_id = "1.11.0"

        if x86_64_contract is True:
            code = self.get_byte_code("fib", "fib(1)", ethereum_contract = False)
        else:
            code = self.get_byte_code("fib", "fib(1)", ethereum_contract = True)

        transaction_list = []

        n = 0
        while n != (transaction_count):
            numbers = list(range(6,self.account_count+6))
            r = random.choice(numbers)
            operation = self.echo_ops.get_contract_call_operation(echo = self.echo, registrar = "1.2.{}".format(r),
                                                              bytecode = code, callee = contract_id, signer = self.nathan_priv_key)
            collected_operation = self.collect_operations(operation, self.private_keys[r-6])
            transaction_list.append(collected_operation)
            n += 1

        self.send_transaction_list(transaction_list)

    def create_transfer_transaction(self):
        transfer_amount = 1
        transaction_list = []
        transfer_operation = self.echo_ops.get_transfer_operation(echo = self.echo, from_account_id = self.echo_nathan_id,
            amount = transfer_amount, to_account_id = self.echo_acc_2, signer = self.nathan_priv_key)
        collected_operation = self.collect_operations(transfer_operation, self.database_api_identifier)
        transaction_list.append(collected_operation)

        sign_transaction_list = []
        time_increment = 300
        for tr in transaction_list:
            now_iso = self.seconds_to_iso(datetime.now(timezone.utc).timestamp())
            now_seconds = self.iso_to_seconds(now_iso)
            expiration_time = self.seconds_to_iso(now_seconds + time_increment + self.call_id)
            sign_transaction_list.append(self.echo_ops.get_sign_transaction(
                echo = self.echo, list_operations = tr, expiration = expiration_time, chain_id = self.chain_id, dynamic_global_chain_data = self.dynamic_global_chain_data))
            self.call_id += 1

        return sign_transaction_list[0]
