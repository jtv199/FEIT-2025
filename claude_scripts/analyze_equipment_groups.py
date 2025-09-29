#!/usr/bin/env python3
import json
from collections import Counter

def analyze_equipment_groups():
    """Analyze equipmentGroup names from hireContractLines in 2023 contracts."""

    with open('extracted_data/contracts_2023.json', 'r') as f:
        data = json.load(f)

    equipment_groups = []
    samples = []

    for contract_key, contract in data.items():
        hire_lines = contract.get('hireContractLines', [])

        if not hire_lines:
            continue

        for i, line in enumerate(hire_lines):
            category = line.get('category', {})
            if not category:
                continue

            equipment_group = category.get('equipmentGroup')

            if equipment_group and isinstance(equipment_group, dict):
                group_name = equipment_group.get('name')
                if group_name:
                    equipment_groups.append(group_name)

                    # Collect samples
                    if len(samples) < 20:
                        samples.append({
                            'contract': contract_key,
                            'line_index': i,
                            'equipment_group': group_name,
                            'category_name': category.get('name', ''),
                            'description': line.get('description', ''),
                            'stock_no': line.get('stockNo', '')
                        })

    return equipment_groups, samples

def main():
    print("=== EQUIPMENT GROUP ANALYSIS (2023 Contracts) ===\n")

    equipment_groups, samples = analyze_equipment_groups()

    if not equipment_groups:
        print("No equipment groups found in the data.")
        return

    # Count equipment groups
    group_counts = Counter(equipment_groups)

    print(f"=== EQUIPMENT GROUP DISTRIBUTION ===")
    print(f"Total equipment group entries: {len(equipment_groups)}")
    print(f"Unique equipment groups: {len(group_counts)}")
    print()

    print(f"{'Equipment Group':<20} {'Count':<8} {'Percentage'}")
    print("-" * 50)

    total = len(equipment_groups)
    for group, count in group_counts.most_common():
        percentage = (count / total) * 100
        print(f"{group:<20} {count:<8} {percentage:.1f}%")

    # Show samples
    print(f"\n=== SAMPLE EQUIPMENT GROUP ENTRIES ===")
    print(f"{'Contract':<10} {'Group':<15} {'Category':<20} {'Description':<30} {'Stock No'}")
    print("-" * 100)

    for sample in samples:
        description = sample['description'] or ''
        stock_no = sample['stock_no'] or ''
        print(f"{sample['contract']:<10} {sample['equipment_group']:<15} {sample['category_name']:<20} {description[:30]:<30} {stock_no}")

if __name__ == "__main__":
    main()