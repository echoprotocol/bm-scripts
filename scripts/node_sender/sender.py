import time
from datetime import timezone, datetime
from math import ceil
from calendar import timegm

from random import randrange

from .base import Base

from node_deployer.deployer import NATHAN_PRIV

initial_balance = 1000000000000000

class Sender(Base):
    def __init__(self, node_url):
        super().__init__(node_url)
        self.echo_nathan = "nathan"
        self.echo_nathan_id = "1.2.25"
        self.nathan_priv_key = NATHAN_PRIV
        self.echo_acc_2 = "1.2.6"
        self.x86_64_contract = self.get_byte_code("piggy", "code", ethereum_contract = False)
        self.ethereum_contract = self.get_byte_code("erc20", "code", ethereum_contract = True)

    @staticmethod
    def seconds_to_iso(sec):
        iso_result = datetime.fromtimestamp(sec, timezone.utc).replace(microsecond=0).isoformat()
        return iso_result[:iso_result.rfind('+')]

    @staticmethod
    def iso_to_seconds(iso):
        timeformat = "%Y-%m-%dT%H:%M:%S%Z"
        return ceil(timegm(time.strptime((iso + "UTC"), timeformat)))

    def import_balance_to_nathan(self):
        nathan = self.get_account(self.echo_nathan, self.database_api_identifier)
        nathan_public_key = self.get_public_key(nathan)
        operation = self.echo_ops.get_balance_claim_operation(self.echo, self.echo_nathan_id, nathan_public_key,
                                                                initial_balance, self.nathan_priv_key)
        collected_operation = self.collect_operations(operation, self.database_api_identifier)
        self.echo_ops.broadcast(self.echo_ops.get_sign_transaction(
            echo = self.echo, list_operations = collected_operation, chain_id = self.chain_id, dynamic_global_chain_data = self.dynamic_global_chain_data),
            with_callback = False)

        print("Import balance - Done")

    def send_transaction_list(self, transaction_list):
        sign_transaction_list = []

        time_increment = 300
        for tr in transaction_list:
            now_iso = self.seconds_to_iso(datetime.now(timezone.utc).timestamp())
            now_seconds = self.iso_to_seconds(now_iso)
            expiration_time = self.seconds_to_iso(now_seconds + time_increment)
            sign_transaction_list.append(self.echo_ops.get_sign_transaction(
                echo = self.echo, list_operations = tr, expiration = expiration_time, chain_id = self.chain_id, dynamic_global_chain_data = self.dynamic_global_chain_data))
            time_increment += 1

        k = 0
        for tr in sign_transaction_list:
            k += 1
            self.echo_ops.broadcast(tr)
            if (k % 1000 == 0):
                print("Sent ", k, " transactions")

    def transfer(self, transaction_count = 1):
        transfer_amount = 1

        transaction_list = []

        n = 0
        while n != transaction_count:
            transfer_operation = self.echo_ops.get_transfer_operation(echo = self.echo, from_account_id = self.echo_nathan_id,
                                                                    amount = transfer_amount, to_account_id = self.echo_acc_2, signer = self.nathan_priv_key)

            collected_operation = self.collect_operations(transfer_operation, self.database_api_identifier)
            transaction_list.append(collected_operation)
            n += 1

        self.send_transaction_list(transaction_list)


    def create_contract(self, code = None, value = 0, transaction_count = 1):
        if code is None:
            code = self.x86_64_contract

        transaction_list = []

        n = 0
        while n != transaction_count:
            operation = self.echo_ops.get_contract_create_operation(echo = self.echo, registrar = self.echo_nathan_id, bytecode = code,
                                                                    value_amount = value, value_asset_id = self.echo_asset,
                                                                    signer = self.nathan_priv_key)
            collected_operation = self.collect_operations(operation, self.database_api_identifier)
            transaction_list.append(collected_operation)
            n += 1

        self.send_transaction_list(transaction_list)

    def call_contract(self, code = None, value = 0, contract_id = None, contract_code = None, transaction_count = 1):
        transaction_list = []

        if contract_id is None:
            if contract_code is None:
                contract_code = self.x86_64_contract
            operation = self.echo_ops.get_contract_create_operation(echo = self.echo, registrar = self.echo_nathan_id,
                                                                    bytecode = contract_code, value_amount = value,
                                                                    value_asset_id = self.echo_asset, signer = self.nathan_priv_key)
            collected_operation = self.collect_operations(operation, self.database_api_identifier)
            transaction_list.append(collected_operation)

            contract_id = "1.11.0"

        if code is None:
            code = self.get_byte_code("piggy", "greet()")

        n = 0
        while n != (transaction_count - 1):
            operation = self.echo_ops.get_contract_call_operation(echo = self.echo, registrar = self.echo_nathan_id,
                                                              bytecode = code, callee = contract_id, signer = self.nathan_priv_key)
            collected_operation = self.collect_operations(operation, self.database_api_identifier)
            transaction_list.append(collected_operation)
            n += 1

        self.send_transaction_list(transaction_list)
