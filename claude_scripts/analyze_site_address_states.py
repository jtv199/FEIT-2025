#!/usr/bin/env python3
import json
from collections import Counter
import re

def extract_states_from_site_addresses():
    """Extract and analyze states from siteAddress fields in 2023 contracts."""

    with open('extracted_data/contracts_2023.json', 'r') as f:
        data = json.load(f)

    states = []
    locations = []

    for contract_key, contract in data.items():
        site_address = contract.get('siteAddress')

        if not site_address:
            continue

        # Check different fields for state information
        name = site_address.get('name', '') or ''
        line1 = site_address.get('line1', '') or ''
        town = site_address.get('town', '') or ''

        # Combine all address text
        full_address = f"{name} {line1} {town}".strip()

        if full_address:
            locations.append({
                'contract': contract_key,
                'name': name,
                'line1': line1,
                'town': town,
                'full_address': full_address
            })

            # Extract state abbreviations (NSW, VIC, QLD, etc.)
            state_matches = re.findall(r'\b(NSW|VIC|QLD|SA|WA|TAS|NT|ACT)\b', full_address, re.IGNORECASE)
            if state_matches:
                states.extend([s.upper() for s in state_matches])

    return states, locations

def main():
    print("=== SITE ADDRESS STATE ANALYSIS (2023 Contracts) ===\n")

    states, locations = extract_states_from_site_addresses()

    # Count states
    state_counts = Counter(states)

    print(f"=== STATE DISTRIBUTION ===")
    print(f"{'State':<5} {'Count':<8} {'Percentage':<10} {'Bar Chart'}")
    print("-" * 50)

    total_with_states = sum(state_counts.values())
    max_count = max(state_counts.values()) if state_counts else 0

    for state, count in state_counts.most_common():
        percentage = (count / total_with_states) * 100
        bar_length = int((count / max_count) * 20) if max_count > 0 else 0
        bar = "█" * bar_length

        print(f"{state:<5} {count:<8} {percentage:<10.1f}% {bar}")

    print(f"\nTotal contracts with state info: {total_with_states}")
    print(f"Total contracts analyzed: {len(locations)}")
    print(f"Contracts without state info: {len(locations) - total_with_states}")

    # Show some sample addresses
    print(f"\n=== SAMPLE SITE ADDRESSES ===")

    # Group by state for samples
    state_samples = {}
    for location in locations:
        state_matches = re.findall(r'\b(NSW|VIC|QLD|SA|WA|TAS|NT|ACT)\b', location['full_address'], re.IGNORECASE)
        if state_matches:
            state = state_matches[0].upper()
            if state not in state_samples:
                state_samples[state] = []
            if len(state_samples[state]) < 3:  # Max 3 samples per state
                state_samples[state].append(location)

    for state, samples in sorted(state_samples.items()):
        print(f"\n{state} samples:")
        for sample in samples:
            print(f"  {sample['contract']}: {sample['full_address'][:80]}")

    # Show addresses without state info
    no_state_samples = [loc for loc in locations if not re.search(r'\b(NSW|VIC|QLD|SA|WA|TAS|NT|ACT)\b', loc['full_address'], re.IGNORECASE)]

    print(f"\n=== ADDRESSES WITHOUT STATE INFO (first 10) ===")
    for sample in no_state_samples[:10]:
        print(f"  {sample['contract']}: {sample['full_address'][:80]}")

if __name__ == "__main__":
    main()