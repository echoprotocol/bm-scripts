import json

from copy import deepcopy

from .type_validation import TypeValidator
from .operations_ids import OperationIds

from utils.files_path import ECHO_OPERATIONS

class EchoOperation:
    def __init__(self):
        self.operation_ids = OperationIds()
        self.type_validator = TypeValidator()
        self.nnn = 0


    @staticmethod
    def get_operation_json(variable_name):
        return deepcopy(ECHO_OPERATIONS[variable_name][1])

    def get_balance_claim_operation(self, echo, deposit_to_account, balance_owner_public_key, value_amount,
                                    balance_owner_private_key=None, fee_amount=0, fee_asset_id="1.3.0",
                                    balance_to_claim="1.8.0", value_asset_id="1.3.0", extensions=None, signer=None):
        if extensions is None:
            extensions = []
        operation_id = echo.config.operation_ids.BALANCE_CLAIM
        balance_claim_operation_props = self.get_operation_json("balance_claim_operation")
        balance_claim_operation_props["fee"].update({"amount": fee_amount, "asset_id": fee_asset_id})
        balance_claim_operation_props.update(
            {"deposit_to_account": deposit_to_account, "balance_to_claim": balance_to_claim,
             "balance_owner_key": balance_owner_public_key, "extensions": extensions})
        balance_claim_operation_props["total_claimed"].update({"amount": value_amount, "asset_id": value_asset_id})
        if signer is None:
            return [operation_id, balance_claim_operation_props, balance_owner_private_key]
        return [operation_id, balance_claim_operation_props, signer]

    def get_transfer_operation(self, echo, from_account_id, to_account_id, amount=1, fee_amount=0, fee_asset_id="1.3.0",
                               amount_asset_id="1.3.0", extensions=None, signer=None):
        if extensions is None:
            extensions = []
        operation_id = self.operation_ids.TRANSFER
        transfer_props = self.get_operation_json("transfer_operation")
        transfer_props["fee"].update({"amount": fee_amount, "asset_id": fee_asset_id})
        transfer_props.update({"from": from_account_id, "to": to_account_id, "extensions": extensions})
        transfer_props["amount"].update({"amount": amount, "asset_id": amount_asset_id})
        if signer is None:
            return [operation_id, transfer_props, from_account_id]
        return [operation_id, transfer_props, signer]

    def get_contract_create_operation(self, echo, registrar, bytecode, fee_amount = 0, fee_asset_id = "1.3.0",
                                      value_amount = 0, value_asset_id = "1.3.0", supported_asset_id = None,
                                      eth_accuracy = False, extensions = None, signer = None):
        if extensions is None:
            extensions = []
        operation_id = echo.config.operation_ids.CONTRACT_CREATE
        contract_create_props = self.get_operation_json("contract_create_operation")
        contract_create_props["fee"].update({"amount": fee_amount, "asset_id": fee_asset_id})
        contract_create_props.update(
            {"registrar": registrar, "code": bytecode, "eth_accuracy": eth_accuracy, "extensions": extensions})
        if supported_asset_id is not None:
            contract_create_props.update({"supported_asset_id": supported_asset_id})
        else:
            del contract_create_props["supported_asset_id"]
        contract_create_props["value"].update({"amount": value_amount, "asset_id": value_asset_id})
        if signer is None:
            return [operation_id, contract_create_props, registrar]
        return [operation_id, contract_create_props, signer]

    def get_contract_call_operation(self, echo, registrar, bytecode, callee, fee_amount = 0, fee_asset_id = "1.3.0",
                                    value_amount = 0, value_asset_id = "1.3.0", extensions = None, signer = None):
        if extensions is None:
            extensions = []
        operation_id = echo.config.operation_ids.CONTRACT_CALL
        contract_call_props = self.get_operation_json("contract_call_operation")
        contract_call_props["fee"].update({"amount": fee_amount, "asset_id": fee_asset_id})
        contract_call_props.update(
            {"registrar": registrar, "code": bytecode, "callee": callee, "extensions": extensions})
        contract_call_props["value"].update({"amount": value_amount, "asset_id": value_asset_id})
        if signer is None:
            return [operation_id, contract_call_props, registrar]
        return [operation_id, contract_call_props, signer]

    def get_sign_transaction(self, echo, list_operations, expiration = None):
        tx = echo.create_transaction()
        if len(list_operations) > 1:
            list_operations = [item for sublist in list_operations for item in sublist]
        for operation in list_operations:
            tx.add_operation(name = operation[0], props = operation[1])
        for operation in list_operations:
            tx.add_signer(operation[2])
        if expiration:
            tx.expiration = expiration
        tx.sign()
        return tx

    def check(self):
        self.nnn += 1
        print(self.nnn)

    def broadcast(self, tx, with_callback = True):
        if with_callback == True:
            broadcast_result = tx.broadcast("1")
        else:
            broadcast_result = tx.broadcast()
        return broadcast_result