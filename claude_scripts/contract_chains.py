#!/usr/bin/env python3
import json
import math
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

def euclidean_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate Euclidean distance between two points in kilometers."""
    lat_diff = (lat2 - lat1) * 111
    lon_diff = (lon2 - lon1) * 85
    return math.sqrt(lat_diff**2 + lon_diff**2)

def build_contract_chains(date_range_allowance: int = 10):
    """
    Build contract chains showing optimal equipment flow from contract to contract.
    Add prev_contract and next_contract fields to each contract.
    """

    with open('extracted_data/2023_vms_victoria.json', 'r') as f:
        data = json.load(f)

    depot_lat, depot_lon = -37.6805, 145.0064

    contracts_list = []

    # Prepare contract data
    for contract_key, contract in data.items():
        site_address = contract.get('siteAddress', {})
        lat = site_address.get('latitude')
        lon = site_address.get('longitude')

        start_date_str = contract.get('startDate')
        end_date_str = contract.get('actualEndDate') or contract.get('plannedEndDate')

        if not all([lat, lon, start_date_str, end_date_str]):
            continue

        try:
            site_lat = float(lat)
            site_lon = float(lon)
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))

            distance_to_depot = euclidean_distance(site_lat, site_lon, depot_lat, depot_lon)

            contracts_list.append({
                'contract_key': contract_key,
                'site_name': site_address.get('name', ''),
                'latitude': site_lat,
                'longitude': site_lon,
                'start_date': start_date,
                'end_date': end_date,
                'distance_to_depot': distance_to_depot,
                'original_data': contract
            })

        except (ValueError, TypeError):
            continue

    # Sort contracts by start date
    contracts_list.sort(key=lambda x: x['start_date'])

    # Find optimal prev_contract for each contract
    for i, current_contract in enumerate(contracts_list):
        current_start = current_contract['start_date']
        current_lat = current_contract['latitude']
        current_lon = current_contract['longitude']
        current_depot_distance = current_contract['distance_to_depot']

        best_prev_contract = None
        best_savings = 0

        # Look for best previous contract
        for j, previous_contract in enumerate(contracts_list):
            if i == j:
                continue

            prev_end = previous_contract['end_date']
            days_difference = (current_start - prev_end).days

            # Check if previous contract ended within allowable range
            if 0 <= days_difference <= date_range_allowance:
                prev_lat = previous_contract['latitude']
                prev_lon = previous_contract['longitude']

                site_to_site_distance = euclidean_distance(
                    prev_lat, prev_lon, current_lat, current_lon
                )

                # Check if site-to-site is closer than depot-to-site
                if site_to_site_distance < current_depot_distance:
                    potential_savings = current_depot_distance - site_to_site_distance

                    if potential_savings > best_savings:
                        best_savings = potential_savings
                        best_prev_contract = {
                            'contract_key': previous_contract['contract_key'],
                            'site_name': previous_contract['site_name'],
                            'end_date': prev_end.strftime('%Y-%m-%d'),
                            'days_gap': days_difference,
                            'site_to_site_km': round(site_to_site_distance, 1),
                            'savings_km': round(potential_savings, 1),
                            'savings_percentage': round((potential_savings / current_depot_distance) * 100, 1)
                        }

        current_contract['prev_contract'] = best_prev_contract

    # Now find next_contract for each (reverse lookup)
    for contract in contracts_list:
        contract['next_contract'] = None

    for contract in contracts_list:
        if contract['prev_contract']:
            prev_key = contract['prev_contract']['contract_key']
            # Find the previous contract and set its next_contract
            for prev_contract in contracts_list:
                if prev_contract['contract_key'] == prev_key:
                    if prev_contract['next_contract'] is None:
                        prev_contract['next_contract'] = {
                            'contract_key': contract['contract_key'],
                            'site_name': contract['site_name'],
                            'start_date': contract['start_date'].strftime('%Y-%m-%d'),
                            'days_gap': contract['prev_contract']['days_gap'],
                            'site_to_site_km': contract['prev_contract']['site_to_site_km'],
                            'savings_km': contract['prev_contract']['savings_km']
                        }
                    break

    return contracts_list

def find_chain_lengths(contracts_list):
    """Find the longest chains of contract-to-contract equipment transfers."""

    # Build adjacency list
    graph = {}
    for contract in contracts_list:
        contract_key = contract['contract_key']
        graph[contract_key] = []

        if contract['next_contract']:
            next_key = contract['next_contract']['contract_key']
            graph[contract_key].append(next_key)

    # Find all chains
    visited = set()
    chains = []

    def dfs(node, current_chain):
        if node in visited:
            return

        visited.add(node)
        current_chain.append(node)

        if node in graph:
            for neighbor in graph[node]:
                if neighbor not in visited:
                    dfs(neighbor, current_chain.copy())

        # If this is a leaf node, save the chain
        if node not in graph or not graph[node]:
            chains.append(current_chain)

    # Start DFS from nodes that are not destinations (no prev_contract)
    start_nodes = []
    for contract in contracts_list:
        if contract['prev_contract'] is None and contract['next_contract'] is not None:
            start_nodes.append(contract['contract_key'])

    for start_node in start_nodes:
        if start_node not in visited:
            dfs(start_node, [])

    # Sort chains by length
    chains.sort(key=len, reverse=True)

    return chains

def create_modified_json(contracts_list):
    """Create modified JSON with prev_contract and next_contract fields."""

    modified_data = {}

    for contract in contracts_list:
        contract_key = contract['contract_key']
        original_data = contract['original_data'].copy()

        # Add chain information
        original_data['prev_contract'] = contract['prev_contract']
        original_data['next_contract'] = contract['next_contract']

        modified_data[contract_key] = original_data

    # Save modified JSON
    with open('extracted_data/2023_vms_victoria_with_chains.json', 'w') as f:
        json.dump(modified_data, f, indent=2)

    return len(modified_data)

def main():
    print("=== CONTRACT CHAIN ANALYSIS ===\n")

    print("1. Building contract chains...")
    contracts_list = build_contract_chains()

    print("2. Creating modified JSON with chain data...")
    modified_count = create_modified_json(contracts_list)
    print(f"   Created modified JSON with {modified_count} contracts")

    print("3. Finding chain lengths...")
    chains = find_chain_lengths(contracts_list)

    print(f"\n=== CHAIN LENGTH ANALYSIS ===")
    print(f"Total chains found: {len(chains)}")

    if chains:
        print(f"\n=== TOP 10 LONGEST CHAINS ===")
        print(f"{'Rank':<5} {'Length':<7} {'Chain (Contract IDs)'}")
        print("-" * 80)

        for i, chain in enumerate(chains[:10], 1):
            chain_str = " → ".join(chain)
            if len(chain_str) > 60:
                chain_str = chain_str[:57] + "..."
            print(f"{i:<5} {len(chain):<7} {chain_str}")

        # Show detailed view of longest chain
        if chains[0]:
            print(f"\n=== DETAILED VIEW: LONGEST CHAIN (Length {len(chains[0])}) ===")
            longest_chain = chains[0]

            for i, contract_key in enumerate(longest_chain):
                # Find contract details
                contract_details = None
                for contract in contracts_list:
                    if contract['contract_key'] == contract_key:
                        contract_details = contract
                        break

                if contract_details:
                    site_name = contract_details['site_name'][:30]
                    start_date = contract_details['start_date'].strftime('%Y-%m-%d')

                    if i < len(longest_chain) - 1:
                        # Show connection to next
                        next_contract = contract_details.get('next_contract')
                        if next_contract:
                            savings = next_contract['savings_km']
                            print(f"{i+1}. {contract_key} ({start_date}) - {site_name}")
                            print(f"    ↓ saves {savings} km")
                        else:
                            print(f"{i+1}. {contract_key} ({start_date}) - {site_name}")
                    else:
                        print(f"{i+1}. {contract_key} ({start_date}) - {site_name}")

        # Chain length distribution
        print(f"\n=== CHAIN LENGTH DISTRIBUTION ===")
        length_counts = defaultdict(int)
        for chain in chains:
            length_counts[len(chain)] += 1

        for length in sorted(length_counts.keys(), reverse=True):
            count = length_counts[length]
            print(f"Length {length}: {count} chains")

        # Calculate total savings from chains
        total_chain_savings = 0
        contracts_in_chains = 0

        for contract in contracts_list:
            if contract['prev_contract']:
                total_chain_savings += contract['prev_contract']['savings_km']
                contracts_in_chains += 1

        print(f"\n=== CHAIN IMPACT ===")
        print(f"Contracts in chains: {contracts_in_chains}")
        print(f"Total chain savings: {total_chain_savings:.1f} km")
        print(f"Average savings per chained contract: {total_chain_savings/contracts_in_chains:.1f} km")

if __name__ == "__main__":
    main()