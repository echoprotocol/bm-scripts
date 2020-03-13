import json
import os.path

from echopy import Echo

from .echo_operation import EchoOperation
from .receiver import Receiver
from .type_validation import TypeValidator
from websocket import create_connection

from ..utils.files_path import ECHO_CONTRACTS, ETHEREUM_CONTRACTS

DEBUG = False

class Base:
    def __init__(self, node_url, port):
        super().__init__()
        self.node_url = "ws://{}:{}".format(node_url, port)
        self.echo = Echo()
        self.echo_ops = EchoOperation()
        self.ws = self.create_connection_to_echo()
        self.database_api_identifier = self.get_identifier("database")
        self.connect_to_echopy_lib()
        self.__call_id = 0
        self.echo_asset = "1.3.0"
        self.receiver = Receiver(web_socket=self.ws)
        self.type_validator = TypeValidator()
        self.chain_id = None
        self.dynamic_global_chain_data = None
        self.set_chain_params()

    @staticmethod
    def get_call_template():
        return {"id": 0, "method": "call", "params": []}

    @staticmethod
    def get_byte_code(contract_name, code_or_method_name, ethereum_contract = False):
        if ethereum_contract:
            return ETHEREUM_CONTRACTS[contract_name][code_or_method_name]
        return ECHO_CONTRACTS[contract_name][code_or_method_name]

    @staticmethod
    def get_operation_results_ids(response):
        operations_count = len(response.get("trx").get("operations"))
        if operations_count == 1:
            operation_result = response.get("trx").get("operation_results")[0]
            if operation_result[0] != 1:
                raise Exception("Wrong format of operation result")
            return operation_result[1]
        operation_results = []
        for i in range(operations_count):
            operation_results.append(response.get("trx").get("operation_results")[i])
            if operation_results[i][0] != 1:
                raise Exception("Wrong format of operation results")
        return operation_results

    def set_chain_params(self):
        tx = self.echo.create_transaction()
        self.chain_id = tx._get_chain_id()
        self.dynamic_global_chain_data = tx._get_dynamic_global_chain_data(dynamic_global_object_id='2.1.0')[0]

    def create_connection_to_echo(self):
        return create_connection(url = self.node_url)

    def connect_to_echopy_lib(self):
        self.echo.connect(url = self.node_url, debug = DEBUG)
        if self.echo.api.ws.connection is None:
            raise Exception("Connection to echopy-lib not established")

    def get_object_type(self, object_types):
        return "{}.{}.".format(self.echo.config.reserved_spaces.PROTOCOL_IDS, object_types)

    def send_request(self, request, api_identifier = None):
        if api_identifier is None:
            method = self.__call_method(request)
            self.ws.send(json.dumps(method))
            return method["id"]
        method = self.__call_method(request, api_identifier)
        self.ws.send(json.dumps(method))
        return method["id"]

    def get_request(self, method_name, params=None):
        request = [1, method_name]
        if params is None:
            request.append([])
            return request
        request.extend([params])
        return request

    def get_response(self, id_response, negative = False, log_response = False):
        try:
            return self.receiver.get_response(id_response, negative, log_response)
        except KeyError as key:
            print("Response: That key does not exist: '{}'".format(key))
        except IndexError as index:
            print("Response: This index does not exist: '{}'".format(index))

    def get_required_fee(self, operation, database_api_identifier, asset = "1.3.0"):
        response_id = self.send_request(self.get_request("get_required_fees", [[operation], asset]),
                                        database_api_identifier)
        response = self.get_response(response_id)
        if response.get("result")[0].get("fee"):
            return response.get("result")[0].get("fee")
        return response.get("result")[0]

    def add_fee_to_operation(self, operation, database_api_identifier, fee_amount = None, fee_asset_id = "1.3.0"):
        try:
            if fee_amount is None:
                fee = self.get_required_fee(
                    operation,
                    database_api_identifier,
                    asset=fee_asset_id)
                operation[1].update({"fee": fee})
                return fee
            operation[1]["fee"].update({"amount": fee_amount, "asset_id": fee_asset_id})
            return fee_amount
        except KeyError as key:
            print("Add fee: That key does not exist: '{}'".format(key))
        except IndexError as index:
            print("Add fee: This index does not exist: '{}'".format(index))

    def collect_operations(self, list_operations, database_api_identifier, fee_amount = None, fee_asset_id = "1.3.0"):
        if type(list_operations) is list:
            list_operations = [list_operations.copy()]
        for operation in list_operations:
            self.add_fee_to_operation(operation, database_api_identifier, fee_amount, fee_asset_id)
        return list_operations

    def get_identifier(self, api):
        call_template = self.get_call_template()
        call_template["params"] = [1, api, []]
        self.ws.send(json.dumps(call_template))
        response = json.loads(self.ws.recv())
        api_identifier = response["result"]
        return api_identifier

    def __call_method(self, method, api_identifier = None):
        self.__call_id += 1
        call_template = self.get_call_template()
        try:
            if api_identifier is None:
                call_template["id"] = self.__call_id
                call_template["params"] = method
                return call_template
            call_template["id"] = self.__call_id
            call_template["params"].append(api_identifier)
            for i in range(1, len(method)):
                call_template["params"].append(method[i])
            return call_template
        except KeyError as key:
            print("Call method: That key does not exist: '{}'".format(key))
        except IndexError as index:
            print("Call method: This index does not exist: '{}'".format(index))

    def get_trx_completed_response(self, id_response, mode='evm'):
        response = self.get_response(id_response)
        if mode == "evm":
            transaction_excepted = response.get("result")[1].get("exec_res").get("excepted")
        if mode == "x86":
            return response
        if transaction_excepted != "None":
            raise Exception("Transaction not completed")
        return response

    def get_contract_result(self, broadcast_result, database_api_identifier, mode = "evm"):
        contract_result = self.get_operation_results_ids(broadcast_result)
        if len([contract_result]) != 1:
            raise Exception("Need one contract id")
        if self.type_validator.is_erc20_object_id(contract_result):
            return contract_result
        if not self.type_validator.is_contract_result_id(contract_result):
            raise Exception("Wrong format of contract result id")
        response_id = self.send_request(self.get_request("get_contract_result", [contract_result]),
                                        database_api_identifier)
        return self.get_trx_completed_response(response_id, mode)

    def get_contract_id(self, response, contract_call_result = False, address_format = None):
        if address_format:
            contract_identifier_hex = response
        elif not contract_call_result:
            contract_identifier_hex = response["result"][1]["exec_res"]["new_address"]
        else:
            contract_identifier_hex = response["result"][1]["tr_receipt"]["log"][0]["address"]
        if not self.type_validator.is_hex(contract_identifier_hex):
            raise Exception("Wrong format of address")
        contract_id = "{}{}".format(self.get_object_type(self.echo.config.object_types.CONTRACT),
                                    int(str(contract_identifier_hex)[2:], 16))
        if not self.type_validator.is_contract_id(contract_id):
            raise Exception("Wrong format of contract id")
        return contract_id

    def get_account(self, account_name, database_api):
        if self.type_validator.is_account_name(account_name):
            response_id = self.send_request(self.get_request("get_account_by_name", [account_name]),
                                                database_api)
            result = self.get_response(response_id)["result"]
        elif self.type_validator.is_account_id(account_name):
            response_id = self.send_request(self.get_request("get_accounts", [[account_name]]),
                                                database_api)
            result = self.get_response(response_id)["result"][0]
        return result

    def get_public_key(self, account):
        return account["active"]["key_auths"][0][0]
