#!/usr/bin/env python3
import json

def get_depot_address_samples():
    with open('data/out.json', 'r') as f:
        data = json.load(f)

    depot_addresses = []
    contract_keys = []

    # Get first 3 contracts that have depot addresses
    for contract_key, contract in data.items():
        if 'depot' in contract and contract['depot'] and 'address' in contract['depot']:
            depot_addresses.append(contract['depot']['address'])
            contract_keys.append(contract_key)
            if len(depot_addresses) >= 3:
                break

    return depot_addresses, contract_keys

def main():
    depot_addresses, contract_keys = get_depot_address_samples()

    for i, (address, contract_key) in enumerate(zip(depot_addresses, contract_keys), 1):
        print(f"=== DEPOT ADDRESS SAMPLE {i} (from contract {contract_key}) ===")
        print(json.dumps(address, indent=2))
        print()

if __name__ == "__main__":
    main()