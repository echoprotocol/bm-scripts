#!/usr/bin/python3

import json

genesis_temp = """
{
  "initial_timestamp": "2019-08-05T00:00:00",
  "max_core_supply": "10000000000000000",
  "initial_parameters": {
    "current_fees": {
      "parameters": [[
          0,{
            "fee": 20
          }
        ],[
          1,{
            "fee": 20
          }
        ],[
          2,{
            "fee": 20
          }
        ],[
          3,{
            "basic_fee": 5000,
            "premium_fee": "2000",
            "price_per_kbyte": 1000
          }
        ],[
          4,{
            "fee": 200,
            "price_per_kbyte": 100
          }
        ],[
          5,{
            "fee": 300000
          }
        ],[
          6,{
            "fee": 200,
            "price_per_kbyte": 100
          }
        ],[
          7,{
            "symbol3": "500000",
            "symbol4": "300000",
            "long_symbol": "5000",
            "price_per_kbyte": 10
          }
        ],[
          8,{
            "fee": "5000",
            "price_per_kbyte": 10
          }
        ],[
          9,{
            "fee": "5000"
          }
        ],[
          10,{
            "fee": "50000"
          }
        ],[
          11,{
            "fee": 2000
          }
        ],[
          12,{
            "fee": 2000
          }
        ],[
          13,{
            "fee": 100
          }
        ],[
          14,{
            "fee": 100
          }
        ],[
          15,{
            "fee": 100
          }
        ],[
          16,{
            "fee": 2000,
            "price_per_kbyte": 10
          }
        ],[
          17,{
            "fee": 2000,
            "price_per_kbyte": 10
          }
        ],[
          18,{
            "fee": 100
          }
        ],[
          19,{
            "fee": "50000"
          }
        ],[
          20,{
            "fee": 200
          }
        ],[
          21,{
            "fee": 10
          }
        ],[
          22,{
            "fee": 0
          }
        ],[
          23,{
            "fee": 0
          }
        ],[
          24,{
            "fee": 20
          }
        ],[
          25,{
            "fee": 20
          }
        ],[
          26,{
            "fee": 100
          }
        ],[
          27,{
            "fee": 100
          }
        ],[
          28,{}
        ],[
          29,{
            "fee": 100
          }
        ],[
          30,{}
        ],[
          31,{
            "fee": 200
          }
        ],[
          32,{
             "fee": 200
          }
        ],[
          33,{
             "fee": 200
          }
        ],[
          34,{}
        ],[
          35,{}
        ],[
          36,{}
        ],[
          37,{
            "fee": 200
          }
        ],[
          38,{
            "fee": 200
          }
        ],[
          39,{
            "fee": 0
          }
        ],[
          40,{
            "fee": 0
          }
        ],[
          41,{
            "fee": 0
          }
        ],[
          42,{
            "fee": 0
          }
        ],[
          43,{
            "fee": 0
          }
        ],[
          44,{
            "fee": 0
          }
        ],[
          45,{
          "fee": 0
          }
        ],[
          46,{
            "fee": 0
          }
        ],[
          47,{
            "fee": 100
          }
        ],[
          48,{}
        ],[
          49,{}
        ],[
          50,{
            "fee": 0
          }
        ],[
          51,{
            "fee": 500000,
            "pool_fee": 500
          }
        ],[
          52,{
            "fee": 0
          }
        ],[
          53,{
            "fee": 0
          }
        ],[
          54,{
            "fee": 0
          }
        ],[
          55,{
            "fee": 0
          }
        ],[
          56,{
            "fee": 0
          }
        ],[
          57,{}
        ],[
          58,{}
        ],[
          59,{
            "fee": 0
          }
        ],[
          60,{
            "fee": 0
          }
        ],[
          61,{
            "fee": 0
          }
        ],[
          62,{
            "fee": 0
          }
        ],[
          63,{
            "fee": 0
          }
        ],[
          64,{
            "fee": 0
          }
        ],[
          65,{
            "fee": 0
          }
        ],[
          66,{
            "fee": 0
          }
        ],[
          67,{
            "fee": 0
          }
        ],[
          68,{
            "fee": 0
          }
        ],[
          69,{}
        ],[
          70,{
            "fee": 0
          }
        ],[
          71,{
            "fee": 0
          }
        ],[
          72,{
            "fee": 0
          }
        ],[
          73,{
            "fee": 0
          }
        ]
      ],
      "scale": 10000
    },
    "maintenance_interval": 86400,
    "maintenance_duration_seconds": 10,
    "balance_unfreezing_time": 7,
    "committee_proposal_review_period": 3600,
    "maximum_transaction_size": 2097152,
    "maximum_block_size": 5242880,
    "maximum_time_until_expiration": 429496729,
    "maximum_proposal_lifetime": 2419200,
    "maximum_asset_whitelist_authorities": 10,
    "maximum_asset_feed_publishers": 10,
    "maximum_authority_membership": 10,
    "max_authority_depth": 2,
    "block_emission_amount": 1000,
    "block_producer_reward_ratio": 5000,
    "committee_frozen_balance_to_activate": 100000000000,
    "committee_maintenance_intervals_to_deposit": 10,
    "committee_balance_unfreeze_duration_seconds": 2592000,
    "x86_64_maximum_contract_size": 200000,
    "frozen_balances_multipliers": [
      [90, 13000],
      [180, 14000],
      [360, 15000]
    ],
    "echorand_config": {
      "_time_generate": 1000,
      "_time_net_1mb": 2000,
      "_time_net_256b": 400,
      "_creator_count": 8,
      "_verifier_count": 18,
      "_ok_threshold": 13,
      "_max_bba_steps": 12,
      "_gc1_delay": 0,
      "_round_attempts": 5
    },
    "sidechain_config": {
      "eth_contract_address": "02b8125e5e2b60f7b92057bd0b719d338658a3b8",
      "eth_committee_update_method": {
        "method": "f1e3eb60",
        "gas": 1000000
      },
      "eth_gen_address_method": {
        "method": "ffcc34fd",
        "gas": 1000000
      },
      "eth_withdraw_method": {
        "method": "e21bd1ce",
        "gas": 1000000
      },
      "eth_update_addr_method": {
        "method": "7ff203ab",
        "gas": 1000000
      },
      "eth_update_contract_address": {
        "method": "3659cfe6",
        "gas": 1000000
      },
      "eth_withdraw_token_method": {
        "method": "1c69c0e2",
        "gas": 1000000
      },
      "eth_collect_tokens_method": {
        "method": "5940a240",
        "gas": 1000000
      },
      "eth_committee_updated_topic": "514bf7702a7d2aca90dcf3d947158aad29563a17c1dbdc76d2eae84c22420142",
      "eth_gen_address_topic": "1855f12530a368418f19b2b15227f19225915b8113c7e17d4c276e2a10225039",
      "eth_deposit_topic": "77227a376c41a7533c952ebde8d7b44ee36c7a6cec0d3448f1a1e4231398356f",
      "eth_withdraw_topic": "481c4276b65cda86cfcd095776a5e290a13932f5bed47d4f786b0ffc4d0d76ae",
      "erc20_deposit_topic": "d6a701782aaded96fbe10d6bd46445ecef12edabc8eb5d3b15fb0e57f6395911",
      "erc20_withdraw_topic": "ec7288d868c54d049bda9254803b6ddaaf0317b76e81601c0af91a480592b272",
      "ETH_asset_id": "1.3.1",
      "BTC_asset_id": "1.3.2",
      "fines": {
        "create_eth_address": -10
      },
      "gas_price": 4000000000,
      "satoshis_per_byte": 12,
      "coefficient_waiting_blocks": 100,
      "btc_deposit_withdrawal_min": 10000,
      "btc_deposit_withdrawal_fee": 1000,
      "eth_withdrawal_fee": 1000000,
      "eth_withdrawal_min": 2000000
    },
    "erc20_config": {
      "create_token_fee": 1000,
      "transfer_topic": "ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
      "check_balance_method": {
        "method": "70a08231",
        "gas": 1000000
      },
      "burn_method": {
        "method": "42966c68",
        "gas": 1000000
      },
      "issue_method": {
        "method": "40c10f19",
        "gas": 1000000
      }
    },
    "stake_sidechain_config" : {
      "contract_address": "db5a91003e87fc49d1cbce62701410c570c59189"
    },
    "gas_price": {
      "price": 1,
      "gas_amount": 1000
    },
    "valid_fee_asset": [
      "1.3.1",
      "1.3.2"
    ],
    "consensus_assets": [
      "1.3.1",
      "1.3.2",
      "1.3.3",
      "1.3.4"
    ],
    "economy_config": {
      "blocks_in_interval": 300,
      "maintenances_in_interval": 1,
      "block_emission_amount": 1000000,
      "block_producer_reward_ratio": 5000,
      "pool_divider": 10
    },
    "extensions": []
  },
  "initial_accounts": [],
  "initial_assets": [{
      "symbol": "EETH",
      "issuer_name": "committee-account",
      "description": "sidechained ethereum asset",
      "precision": 8,
      "max_supply": "10000000000000000",
      "accumulated_fees": 0,
      "is_bitasset": true,
      "collateral_records": [],
      "flags": 8,
      "core_exchange_rate": {
        "base": {
          "amount": 1,
          "asset_id": "1.3.1"
        },
        "quote": {
          "amount": 1,
          "asset_id": "1.3.0"
        }
      }
    },{
      "symbol": "EBTC",
      "issuer_name": "committee-account",
      "description": "sidechained bitcoin asset",
      "precision": 8,
      "max_supply": "2100000000000000",
      "accumulated_fees": 0,
      "is_bitasset": true,
      "collateral_records": [],
      "flags": 8,
      "core_exchange_rate": {
        "base": {
          "amount": 1,
          "asset_id": "1.3.2"
        },
        "quote": {
          "amount": 1,
          "asset_id": "1.3.0"
        }
      }
    }, {
      "symbol": "SETH",
      "issuer_name": "committee-account",
      "description": "stake ethereum asset",
      "precision": 8,
      "max_supply": "10000000000000000",
      "accumulated_fees": 0,
      "is_bitasset": true,
      "collateral_records": [],
      "flags": 24,
      "core_exchange_rate": {
        "base": {
          "amount": 1,
          "asset_id": "1.3.3"
        },
        "quote": {
          "amount": 1,
          "asset_id": "1.3.0"
        }
      }
    },{
      "symbol": "SBTC",
      "issuer_name": "committee-account",
      "description": "stake bitcoin asset",
      "precision": 8,
      "max_supply": "2100000000000000",
      "accumulated_fees": 0,
      "is_bitasset": true,
      "collateral_records": [],
      "flags": 24,
      "core_exchange_rate": {
        "base": {
          "amount": 1,
          "asset_id": "1.3.4"
        },
        "quote": {
          "amount": 1,
          "asset_id": "1.3.0"
        }
      }
    }
  ],
  "initial_balances": [{
      "owner": "ECHO5NaRTkq4uBAVGrZkD3jcTEdUxhxxJLU7hvt3p1zJyytc",
      "asset_symbol": "ECHO",
      "amount": "1000000000000000"
    }
  ],
  "initial_vesting_balances": [],
  "initial_committee_candidates": [
    {
      "owner_name": "init0",
      "eth_address": "f372c3b578534Ac5C1Cf0Cca7049A279d1ca3e79",
      "btc_public_key": "02c16e97132e72738c9c0163656348cd1be03521de17efeb07e496e742ac84512e"
    },
    {
      "owner_name": "init1",
      "eth_address": "Fba802D86f8d9b080eD247e712751DDBF86086A9",
      "btc_public_key": "02c16e97132e72738c9c0163656348cd1be03521de17efeb07e496e742ac84512e"
    },
    {
      "owner_name": "init2",
      "eth_address": "f5Ee319f0641805A3C1Ff3f0ABAacBBC7AB7E303",
      "btc_public_key": "02c16e97132e72738c9c0163656348cd1be03521de17efeb07e496e742ac84512e"
    },
    {
      "owner_name": "init3",
      "eth_address": "7fD9941433fcF0d4CC9A9FC847D01dbB9ed2EBf9",
      "btc_public_key": "02c16e97132e72738c9c0163656348cd1be03521de17efeb07e496e742ac84512e"
    },
    {
      "owner_name": "init4",
      "eth_address": "17B5Cb805fDC853fF6A8f893193Ba6ad29B9Fe86",
      "btc_public_key": "02c16e97132e72738c9c0163656348cd1be03521de17efeb07e496e742ac84512e"
    },
    {
      "owner_name": "init5",
      "eth_address": "DBCD9F4807d30abdDeC6ED3AFe4237fcB946c88B",
      "btc_public_key": "02c16e97132e72738c9c0163656348cd1be03521de17efeb07e496e742ac84512e"
    },
    {
      "owner_name": "init6",
      "eth_address": "DBCD9F4807d30abdDeC6ED3AFe4237fcB946c88B",
      "btc_public_key": "02c16e97132e72738c9c0163656348cd1be03521de17efeb07e496e742ac84512e"
    },
    {
      "owner_name": "init7",
      "eth_address": "DBCD9F4807d30abdDeC6ED3AFe4237fcB946c88B",
      "btc_public_key": "02c16e97132e72738c9c0163656348cd1be03521de17efeb07e496e742ac84512e"
    },
    {
      "owner_name": "init8",
      "eth_address": "DBCD9F4807d30abdDeC6ED3AFe4237fcB946c88B",
      "btc_public_key": "02c16e97132e72738c9c0163656348cd1be03521de17efeb07e496e742ac84512e"
    }
  ],
  "initial_sidechain_asset_config": [
    {
      "code" : "608060405234801561001057600080fd5b50604051610b93380380610b938339818101604052602081101561003357600080fd5b81019080805190602001909291905050506100533361006060201b60201c565b806001819055505061027d565b6100788160006100be60201b6104981790919060201c565b8073ffffffffffffffffffffffffffffffffffffffff167f6ae172837ea30b801fbfcdd4108aa1d5bf8ff775444fd70256b44e6bf3dfc3f660405160405180910390a250565b6100ce828261019f60201b60201c565b15610141576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040180806020018281038252601f8152602001807f526f6c65733a206163636f756e7420616c72656164792068617320726f6c650081525060200191505060405180910390fd5b60018260000160008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060006101000a81548160ff0219169083151502179055505050565b60008073ffffffffffffffffffffffffffffffffffffffff168273ffffffffffffffffffffffffffffffffffffffff161415610226576040517f08c379a0000000000000000000000000000000000000000000000000000000008152600401808060200182810382526022815260200180610b716022913960400191505060405180910390fd5b8260000160008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060009054906101000a900460ff16905092915050565b6108e58061028c6000396000f3fe60806040526004361061004e5760003560e01c806340c10f191461013157806342966c68146101a2578063983b2d56146101dd578063986502751461022e578063aa271e1a146102455761004f565b5b600073ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff1614156100d5576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260218152602001806108366021913960400191505060405180910390fd5b600154261461012f576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260348152602001806108576034913960400191505060405180910390fd5b005b34801561013d57600080fd5b5061018a6004803603604081101561015457600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803590602001909291905050506102ac565b60405180821515815260200191505060405180910390f35b3480156101ae57600080fd5b506101db600480360360208110156101c557600080fd5b8101908080359060200190929190505050610403565b005b3480156101e957600080fd5b5061022c6004803603602081101561020057600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190505050610406565b005b34801561023a57600080fd5b50610243610470565b005b34801561025157600080fd5b506102946004803603602081101561026857600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff16906020019092919050505061047b565b60405180821515815260200191505060405180910390f35b60006102b73361047b565b61030c576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260308152602001806107c36030913960400191505060405180910390fd5b600073ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff1614156103af576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040180806020018281038252601f8152602001807f45524332303a206d696e7420746f20746865207a65726f20616464726573730081525060200191505060405180910390fd5b6001548373ffffffffffffffffffffffffffffffffffffffff166108fc8490811502906040516000604051808303818588882a93505050501580156103f8573d6000803e3d6000fd5b506001905092915050565b50565b61040f3361047b565b610464576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260308152602001806107c36030913960400191505060405180910390fd5b61046d81610573565b50565b610479336105cd565b565b600061049182600061062790919063ffffffff16565b9050919050565b6104a28282610627565b15610515576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040180806020018281038252601f8152602001807f526f6c65733a206163636f756e7420616c72656164792068617320726f6c650081525060200191505060405180910390fd5b60018260000160008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060006101000a81548160ff0219169083151502179055505050565b61058781600061049890919063ffffffff16565b8073ffffffffffffffffffffffffffffffffffffffff167f6ae172837ea30b801fbfcdd4108aa1d5bf8ff775444fd70256b44e6bf3dfc3f660405160405180910390a250565b6105e181600061070590919063ffffffff16565b8073ffffffffffffffffffffffffffffffffffffffff167fe94479a9f7e1952cc78f2d6baab678adc1b772d936c6583def489e524cb6669260405160405180910390a250565b60008073ffffffffffffffffffffffffffffffffffffffff168273ffffffffffffffffffffffffffffffffffffffff1614156106ae576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260228152602001806108146022913960400191505060405180910390fd5b8260000160008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060009054906101000a900460ff16905092915050565b61070f8282610627565b610764576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260218152602001806107f36021913960400191505060405180910390fd5b60008260000160008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060006101000a81548160ff021916908315150217905550505056fe4d696e746572526f6c653a2063616c6c657220646f6573206e6f74206861766520746865204d696e74657220726f6c65526f6c65733a206163636f756e7420646f6573206e6f74206861766520726f6c65526f6c65733a206163636f756e7420697320746865207a65726f206164647265737345524332303a206275726e2066726f6d20746865207a65726f206164647265737345524332303a206d73672e6964617373657420646f73656e2774206d617463682077697468207468697320636f6e737472616374a2646970667358221220739d26b13e143158023483ada5d1d49011300a4ea76320fdb101e3862e2113b364736f6c637827302e372e302d646576656c6f702e323032302e31302e382b636f6d6d69742e36346261386532640058526f6c65733a206163636f756e7420697320746865207a65726f2061646472657373",
      "address" : "bC384aBfDd339BCf2f9e68Ea3858C04563ef012C",
      "name" : "EchoToken",
      "symbol" : "ECHO",
      "decimals" : 8,
      "supported_asset" : "1.3.0"
    },
    {
      "code" : "608060405234801561001057600080fd5b50604051610b93380380610b938339818101604052602081101561003357600080fd5b81019080805190602001909291905050506100533361006060201b60201c565b806001819055505061027d565b6100788160006100be60201b6104981790919060201c565b8073ffffffffffffffffffffffffffffffffffffffff167f6ae172837ea30b801fbfcdd4108aa1d5bf8ff775444fd70256b44e6bf3dfc3f660405160405180910390a250565b6100ce828261019f60201b60201c565b15610141576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040180806020018281038252601f8152602001807f526f6c65733a206163636f756e7420616c72656164792068617320726f6c650081525060200191505060405180910390fd5b60018260000160008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060006101000a81548160ff0219169083151502179055505050565b60008073ffffffffffffffffffffffffffffffffffffffff168273ffffffffffffffffffffffffffffffffffffffff161415610226576040517f08c379a0000000000000000000000000000000000000000000000000000000008152600401808060200182810382526022815260200180610b716022913960400191505060405180910390fd5b8260000160008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060009054906101000a900460ff16905092915050565b6108e58061028c6000396000f3fe60806040526004361061004e5760003560e01c806340c10f191461013157806342966c68146101a2578063983b2d56146101dd578063986502751461022e578063aa271e1a146102455761004f565b5b600073ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff1614156100d5576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260218152602001806108366021913960400191505060405180910390fd5b600154261461012f576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260348152602001806108576034913960400191505060405180910390fd5b005b34801561013d57600080fd5b5061018a6004803603604081101561015457600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803590602001909291905050506102ac565b60405180821515815260200191505060405180910390f35b3480156101ae57600080fd5b506101db600480360360208110156101c557600080fd5b8101908080359060200190929190505050610403565b005b3480156101e957600080fd5b5061022c6004803603602081101561020057600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190505050610406565b005b34801561023a57600080fd5b50610243610470565b005b34801561025157600080fd5b506102946004803603602081101561026857600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff16906020019092919050505061047b565b60405180821515815260200191505060405180910390f35b60006102b73361047b565b61030c576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260308152602001806107c36030913960400191505060405180910390fd5b600073ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff1614156103af576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040180806020018281038252601f8152602001807f45524332303a206d696e7420746f20746865207a65726f20616464726573730081525060200191505060405180910390fd5b6001548373ffffffffffffffffffffffffffffffffffffffff166108fc8490811502906040516000604051808303818588882a93505050501580156103f8573d6000803e3d6000fd5b506001905092915050565b50565b61040f3361047b565b610464576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260308152602001806107c36030913960400191505060405180910390fd5b61046d81610573565b50565b610479336105cd565b565b600061049182600061062790919063ffffffff16565b9050919050565b6104a28282610627565b15610515576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040180806020018281038252601f8152602001807f526f6c65733a206163636f756e7420616c72656164792068617320726f6c650081525060200191505060405180910390fd5b60018260000160008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060006101000a81548160ff0219169083151502179055505050565b61058781600061049890919063ffffffff16565b8073ffffffffffffffffffffffffffffffffffffffff167f6ae172837ea30b801fbfcdd4108aa1d5bf8ff775444fd70256b44e6bf3dfc3f660405160405180910390a250565b6105e181600061070590919063ffffffff16565b8073ffffffffffffffffffffffffffffffffffffffff167fe94479a9f7e1952cc78f2d6baab678adc1b772d936c6583def489e524cb6669260405160405180910390a250565b60008073ffffffffffffffffffffffffffffffffffffffff168273ffffffffffffffffffffffffffffffffffffffff1614156106ae576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260228152602001806108146022913960400191505060405180910390fd5b8260000160008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060009054906101000a900460ff16905092915050565b61070f8282610627565b610764576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260218152602001806107f36021913960400191505060405180910390fd5b60008260000160008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060006101000a81548160ff021916908315150217905550505056fe4d696e746572526f6c653a2063616c6c657220646f6573206e6f74206861766520746865204d696e74657220726f6c65526f6c65733a206163636f756e7420646f6573206e6f74206861766520726f6c65526f6c65733a206163636f756e7420697320746865207a65726f206164647265737345524332303a206275726e2066726f6d20746865207a65726f206164647265737345524332303a206d73672e6964617373657420646f73656e2774206d617463682077697468207468697320636f6e737472616374a2646970667358221220739d26b13e143158023483ada5d1d49011300a4ea76320fdb101e3862e2113b364736f6c637827302e372e302d646576656c6f702e323032302e31302e382b636f6d6d69742e36346261386532640058526f6c65733a206163636f756e7420697320746865207a65726f2061646472657373",
      "address" : "2A365517AB5f70b4079Cd2dC2C3Bc9d111AaE951",
      "name" : "EbtcToken",
      "symbol" : "EBTC",
      "decimals" : 8,
      "supported_asset" : "1.3.2"
    }
  ],
  "initial_chain_id": "aa34045518f1469a28fa4578240d5f039afa9959c0b95ce3b39674efa691fb21"
}"""


def create_init_account(name, active, echorand):
    init_account_template = {"name": "", "active_key": "", "echorand_key": ""}
    init_account_template["name"] = name
    init_account_template["active_key"] = active
    init_account_template["echorand_key"] = echorand
    return init_account_template


def get_genesis_string(accounts):
    g = json.loads(genesis_temp)
    g["initial_accounts"] = accounts
    return json.dumps(g)
