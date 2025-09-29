#!/usr/bin/env python3
import json
from collections import Counter
import re

def analyze_postcodes():
    """Analyze postcode field in siteAddress from 2023 contracts."""

    with open('extracted_data/contracts_2023.json', 'r') as f:
        data = json.load(f)

    postcode_stats = {
        'has_postcode': 0,
        'no_postcode': 0,
        'null_postcode': 0,
        'empty_postcode': 0,
        'postcodes': [],
        'samples_with_postcode': [],
        'samples_without_postcode': []
    }

    for contract_key, contract in data.items():
        site_address = contract.get('siteAddress')

        if not site_address:
            postcode_stats['no_postcode'] += 1
            continue

        postcode = site_address.get('postcode')

        if postcode is None:
            postcode_stats['null_postcode'] += 1
            if len(postcode_stats['samples_without_postcode']) < 5:
                postcode_stats['samples_without_postcode'].append({
                    'contract': contract_key,
                    'name': site_address.get('name', ''),
                    'line1': site_address.get('line1', ''),
                    'postcode': postcode
                })
        elif postcode == '':
            postcode_stats['empty_postcode'] += 1
        else:
            postcode_stats['has_postcode'] += 1
            postcode_stats['postcodes'].append(postcode)
            if len(postcode_stats['samples_with_postcode']) < 10:
                postcode_stats['samples_with_postcode'].append({
                    'contract': contract_key,
                    'name': site_address.get('name', ''),
                    'line1': site_address.get('line1', ''),
                    'postcode': postcode
                })

    return postcode_stats

def main():
    print("=== POSTCODE ANALYSIS (2023 Contracts) ===\n")

    stats = analyze_postcodes()

    total_contracts = 5877
    has_postcode = stats['has_postcode']
    null_postcode = stats['null_postcode']
    empty_postcode = stats['empty_postcode']
    no_site_address = total_contracts - has_postcode - null_postcode - empty_postcode

    print(f"=== POSTCODE STATISTICS ===")
    print(f"Total contracts: {total_contracts}")
    print(f"Has postcode: {has_postcode} ({has_postcode/total_contracts*100:.1f}%)")
    print(f"Null postcode: {null_postcode} ({null_postcode/total_contracts*100:.1f}%)")
    print(f"Empty postcode: {empty_postcode} ({empty_postcode/total_contracts*100:.1f}%)")
    print(f"No site address: {no_site_address} ({no_site_address/total_contracts*100:.1f}%)")

    if stats['postcodes']:
        # Analyze postcode patterns
        postcode_counts = Counter(stats['postcodes'])

        print(f"\n=== POSTCODE DISTRIBUTION (Top 10) ===")
        for postcode, count in postcode_counts.most_common(10):
            print(f"{postcode}: {count} contracts")

        # Show samples with postcodes
        print(f"\n=== SAMPLE ADDRESSES WITH POSTCODES ===")
        for sample in stats['samples_with_postcode']:
            address = f"{sample['name']} {sample['line1']}".strip()
            print(f"{sample['contract']}: {address} - {sample['postcode']}")

    # Show samples without postcodes
    print(f"\n=== SAMPLE ADDRESSES WITHOUT POSTCODES ===")
    for sample in stats['samples_without_postcode']:
        address = f"{sample['name']} {sample['line1']}".strip()
        print(f"{sample['contract']}: {address} - postcode: {sample['postcode']}")

if __name__ == "__main__":
    main()