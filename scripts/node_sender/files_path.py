import os.path
import json

RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "../resources")
ECHO_OPERATIONS = json.load(open(os.path.join(RESOURCES_DIR, "echo_operations.json")))

ETHEREUM_CONTRACTS = json.load(open(os.path.join(RESOURCES_DIR, "ethereum_contracts.json")))
ECHO_CONTRACTS = json.load(open(os.path.join(RESOURCES_DIR, "echo_contracts.json")))

NATHAN_PK = json.load(open(os.path.join(RESOURCES_DIR, "private_keys.json")))["NATHAN_PK"]