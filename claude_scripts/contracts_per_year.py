#!/usr/bin/env python3
import json
from collections import Counter
from datetime import datetime

def count_contracts_per_year():
    with open('data/out.json', 'r') as f:
        data = json.load(f)

    year_counts = Counter()

    for contract_key, contract in data.items():
        # Use raisedDate as the contract year
        raised_date = contract.get('raisedDate')
        if raised_date:
            try:
                # Parse ISO datetime format
                year = datetime.fromisoformat(raised_date.replace('Z', '+00:00')).year
                year_counts[year] += 1
            except:
                print(f"Could not parse date for contract {contract_key}: {raised_date}")

    return year_counts

def main():
    year_counts = count_contracts_per_year()

    print("=== CONTRACTS PER YEAR ===")
    print(f"{'Year':<6} {'Count':<8} {'Bar Chart'}")
    print("-" * 40)

    total = sum(year_counts.values())
    max_count = max(year_counts.values()) if year_counts else 0

    for year in sorted(year_counts.keys()):
        count = year_counts[year]
        percentage = (count / total) * 100
        bar_length = int((count / max_count) * 30) if max_count > 0 else 0
        bar = "█" * bar_length

        print(f"{year:<6} {count:<8} {bar} ({percentage:.1f}%)")

    print(f"\nTotal contracts: {total}")
    print(f"Years covered: {min(year_counts.keys())} - {max(year_counts.keys())}")

if __name__ == "__main__":
    main()