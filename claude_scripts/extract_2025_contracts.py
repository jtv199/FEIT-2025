#!/usr/bin/env python3
import json
from datetime import datetime

def extract_2025_contracts():
    """Extract all contracts from 2025 based on raisedDate."""

    with open('data/out.json', 'r') as f:
        data = json.load(f)

    contracts_2025 = {}

    for contract_key, contract in data.items():
        raised_date = contract.get('raisedDate')
        if raised_date:
            try:
                # Parse ISO datetime format
                year = datetime.fromisoformat(raised_date.replace('Z', '+00:00')).year
                if year == 2025:
                    contracts_2025[contract_key] = contract
            except Exception as e:
                print(f"Could not parse date for contract {contract_key}: {raised_date} - {e}")

    return contracts_2025

def main():
    print("Extracting 2025 contracts...")

    contracts_2025 = extract_2025_contracts()

    print(f"Found {len(contracts_2025)} contracts from 2025")

    # Save to extracted_data folder
    output_file = 'extracted_data/contracts_2025.json'
    with open(output_file, 'w') as f:
        json.dump(contracts_2025, f, indent=2)

    print(f"Saved 2025 contracts to {output_file}")

    # Show some stats
    print(f"\nFirst few contract IDs: {list(contracts_2025.keys())[:5]}")
    print(f"File size: {len(json.dumps(contracts_2025)) / 1024 / 1024:.1f} MB")

if __name__ == "__main__":
    main()