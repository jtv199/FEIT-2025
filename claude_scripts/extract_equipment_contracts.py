#!/usr/bin/env python3
import json

def extract_contracts_by_equipment_group(equipment_group_name, output_filename):
    """Extract contracts that contain specific equipment group."""

    with open('extracted_data/contracts_2023.json', 'r') as f:
        data = json.load(f)

    filtered_contracts = {}

    for contract_key, contract in data.items():
        hire_lines = contract.get('hireContractLines', [])

        if not hire_lines:
            continue

        # Check if any hire line has the specified equipment group
        has_equipment = False
        for line in hire_lines:
            category = line.get('category', {})
            if not category:
                continue

            equipment_group = category.get('equipmentGroup')
            if equipment_group and isinstance(equipment_group, dict):
                group_name = equipment_group.get('name')
                if group_name == equipment_group_name:
                    has_equipment = True
                    break

        if has_equipment:
            filtered_contracts[contract_key] = contract

    # Save filtered contracts
    with open(f'extracted_data/{output_filename}.json', 'w') as f:
        json.dump(filtered_contracts, f, indent=2)

    return len(filtered_contracts)

def main():
    print("=== EXTRACTING EQUIPMENT-SPECIFIC CONTRACTS ===\n")

    # Extract VMS contracts
    print("Extracting VMS contracts...")
    vms_count = extract_contracts_by_equipment_group("VMS", "2023_vms")
    print(f"Found {vms_count} contracts with VMS equipment")

    # Extract Light Towers contracts
    print("\nExtracting Light Towers contracts...")
    light_towers_count = extract_contracts_by_equipment_group("Light Towers", "2023_light_towers")
    print(f"Found {light_towers_count} contracts with Light Towers equipment")

    print(f"\nFiles created:")
    print(f"- extracted_data/2023_vms.json ({vms_count} contracts)")
    print(f"- extracted_data/2023_light_towers.json ({light_towers_count} contracts)")

if __name__ == "__main__":
    main()