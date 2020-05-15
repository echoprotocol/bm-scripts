import re

NAME_MIN_LENGTH = 1
NAME_MAX_LENGTH = 63


class TypeValidator(object):
    id_regex = re.compile(r"^(0|([1-9]\d*\.)){2}(0|([1-9]\d*))$")
    account_id_regex = re.compile(r"^1\.2\.(0|[1-9]\d*)$")
    asset_id_regex = re.compile(r"^1\.3\.(0|[1-9]\d*)$")
    eth_asset_id_regex = re.compile(r"^1.3.1$")
    btc_asset_id_regex = re.compile(r"^1.3.2$")
    committee_member_id_regex = re.compile(r"^1\.4\.(0|[1-9]\d*)$")
    proposal_id_regex = re.compile(r"^1\.5\.(0|[1-9]\d*)$")
    operation_history_id_regex = re.compile(r"^1\.6\.(0|[1-9]\d*)$")
    vesting_balance_id_regex = re.compile(r"^1\.7\.(0|[1-9]\d*)$")
    balance_id_regex = re.compile(r"^1\.8\.(0|[1-9]\d*)$")
    frozen_balance_id_regex = re.compile(r"^1\.9\.(0|[1-9]\d*)$")
    committee_frozen_balance_id_regex = re.compile(r"^1\.10\.(0|[1-9]\d*)$")
    contract_id_regex = re.compile(r"^1\.11\.(0|[1-9]\d*)$")
    contract_result_id_regex = re.compile(r"^1\.12\.(0|[1-9]\d*)$")
    block_id_regex = re.compile(r"^1\.13\.(0|[1-9]\d*)$")
    eth_address_id_regex = re.compile(r"^1\.13\.(0|[1-9]\d*)$")
    deposit_eth_id_regex = re.compile(r"^1\.14\.(0|[1-9]\d*)$")
    withdraw_eth_id_regex = re.compile(r"^1\.15\.(0|[1-9]\d*)$")
    erc20_object_id_regex = re.compile(r"^1\.16\.(0|[1-9]\d*)$")
    deposit_erc20_id_regex = re.compile(r"^1\.17\.(0|[1-9]\d*)$")
    withdraw_erc20_id_regex = re.compile(r"^1\.18\.(0|[1-9]\d*)$")
    btc_address_id_regex = re.compile(r"^1\.19\.(0|[1-9]\d*)$")
    btc_intermediate_deposit_id_regex = re.compile(r"^1\.20\.(0|[1-9]\d*)$")
    btc_deposit_id_regex = re.compile(r"^1\.21\.(0|[1-9]\d*)$")
    btc_withdraw_id_regex = re.compile(r"^1\.22\.(0|[1-9]\d*)$")
    btc_aggregating_id_regex = re.compile(r"^1\.23\.(0|[1-9]\d*)$")
    evm_address_id_regex = re.compile(r"^1\.24\.(0|[1-9]\d*)$")
    global_object_id_regex = re.compile(r"^2.0.0$")
    dynamic_global_object_id_regex = re.compile(r"^2.1.0$")
    dynamic_asset_data_id_regex = re.compile(r"^2\.2\.(0|[1-9]\d*)$")
    bitasset_id_regex = re.compile(r"^2\.3\.(0|[1-9]\d*)$")
    account_balance_id_regex = re.compile(r"^2\.4\.(0|[1-9]\d*)$")
    account_statistics_id_regex = re.compile(r"^2\.5\.(0|[1-9]\d*)$")
    transaction_id_regex = re.compile(r"^2\.6\.(0|[1-9]\d*)$")
    block_summary_id_regex = re.compile(r"^2\.7\.(0|[1-9]\d*)$")
    account_transaction_history_id_regex = re.compile(r"^2\.8\.(0|[1-9]\d*)$")
    chain_property_object_id_regex = re.compile(r"^2.9.0$")
    special_authority_id_regex = re.compile(r"^2\.10\.(0|[1-9]\d*)$")
    contract_balance_id_regex = re.compile(r"^2\.11\.(0|[1-9]\d*)$")
    contract_history_id_regex = re.compile(r"^2\.12\.(0|[1-9]\d*)$")
    contract_statistics_id_regex = re.compile(r"^2\.13\.(0|[1-9]\d*)$")
    account_address_id_regex = re.compile(r"^2\.14\.(0|[1-9]\d*)$")
    contract_pool_id_regex = re.compile(r"^2\.15\.(0|[1-9]\d*)$")
    malicious_committeemen_id_regex = re.compile(r"^2\.16\.(0|[1-9]\d*)$")
    hex_regex = re.compile("^[0-9a-fA-F]+")
    bytecode_regex = re.compile(r"^[\da-fA-F]{8}([\da-fA-F]{64})*$")
    vote_id_type_regex = re.compile(r"^[0-3]:[0-9]+")
    iso8601_regex = re.compile(
        r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01]"
        r"[0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$"
    )
    base58_regex = re.compile(r"^[1-9A-HJ-NP-Za-km-z]+$")
    wif_regex = re.compile(r"^5[HJK][1-9A-Za-z][^OIl]{48}$")

    def __init__(self):
        super().__init__()

    @staticmethod
    def is_string(value):
        if not isinstance(value, str):
            return False
        return True

    def is_hex(self, value):
        if self.is_string(value):
            return bool(self.hex_regex.match(value))

    def is_erc20_object_id(self, value):
        if self.is_string(value):
            return bool(self.erc20_object_id_regex.match(value))

    def is_account_id(self, value):
        if self.is_string(value):
            return bool(self.account_id_regex.match(value))

    def is_contract_id(self, value):
        if self.is_string(value):
            return bool(self.contract_id_regex.match(value))

    def is_contract_result_id(self, value):
        if self.is_string(value):
            return bool(self.contract_result_id_regex.match(value))

    def is_account_name(self, value):
        if not self.is_string(value):
            return False
        if value is None:
            return False
        if len(value) < NAME_MIN_LENGTH or len(value) > NAME_MAX_LENGTH:
            return False

        ref = value.split(".")

        for label in ref:
            if not bool(re.match(r"^[a-z][a-z0-9-]*[a-z\d]$", label)) or bool(
                re.match(r".*--.*", label)
            ):
                return False
        return True
