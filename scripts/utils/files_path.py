import os.path
import json

RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "../resources")

ETHEREUM_CONTRACTS = json.load(
    open(os.path.join(RESOURCES_DIR, "ethereum_contracts.json"))
)
ECHO_CONTRACTS = json.load(open(os.path.join(RESOURCES_DIR, "echo_contracts.json")))
