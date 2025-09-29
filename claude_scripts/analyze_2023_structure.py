#!/usr/bin/env python3
import json
from collections import defaultdict, Counter
from typing import Any, Dict, List, Tuple, Set

def explore_json_structure(data: Dict[str, Any], prefix: str = "", path: List[str] = None) -> List[Tuple[int, str, str, Any, int]]:
    """
    Recursively explore JSON structure and return field information.
    Returns: List of (field_number, field_path, field_type, sample_value, nesting_depth)
    """
    if path is None:
        path = []

    fields = []
    field_counter = 0

    def _explore(obj: Any, current_prefix: str = "", current_path: List[str] = None, depth: int = 0) -> None:
        nonlocal field_counter, fields

        if current_path is None:
            current_path = []

        if isinstance(obj, dict):
            for key, value in obj.items():
                field_counter += 1
                new_path = current_path + [key]
                new_prefix = f"{current_prefix}.{key}" if current_prefix else key

                # Determine field type and complexity
                field_type = type(value).__name__
                if isinstance(value, dict):
                    field_type = f"dict({len(value)} keys)"
                elif isinstance(value, list):
                    field_type = f"list({len(value)} items)"

                fields.append((field_counter, new_prefix, field_type, value, depth))

                # Recurse into nested structures
                if isinstance(value, (dict, list)):
                    _explore(value, new_prefix, new_path, depth + 1)

        elif isinstance(obj, list) and obj:
            # Analyze first item in list to understand structure
            first_item = obj[0]
            if isinstance(first_item, dict):
                _explore(first_item, f"{current_prefix}[0]", current_path, depth + 1)

    _explore(data, prefix, path)
    return fields

def main():
    print("=== 2023 CONTRACT DATA STRUCTURE ===\n")

    # Load the 2023 JSON file
    try:
        with open('extracted_data/contracts_2023.json', 'r') as f:
            data = json.load(f)
        print(f"✓ Loaded 2023 contracts: {len(data)} contracts")
    except Exception as e:
        print(f"✗ Error loading 2023 contracts: {e}")
        return

    # Take first contract for structure analysis
    first_contract_key = list(data.keys())[0]
    first_contract = data[first_contract_key]

    print(f"✓ Analyzing structure using contract: {first_contract_key}\n")

    # Explore structure
    fields = explore_json_structure(first_contract)

    print(f"=== FIELD INVENTORY ({len(fields)} fields found) ===")
    print(f"{'#':<3} {'Field Path':<40} {'Type':<20} {'Depth':<5} {'Sample'}")
    print("-" * 100)

    for field_num, field_path, field_type, sample_value, depth in fields:
        # Truncate sample for display
        sample_str = str(sample_value)[:50]
        if len(str(sample_value)) > 50:
            sample_str += "..."

        print(f"{field_num:<3} {'  ' * depth}{field_path:<40} {field_type:<20} {depth:<5} {sample_str}")

    # Summary statistics
    print(f"\n=== SUMMARY STATISTICS ===")

    total_fields = len(fields)
    nested_fields = len([f for f in fields if f[4] > 0])
    dict_fields = len([f for f in fields if "dict" in f[2]])
    list_fields = len([f for f in fields if "list" in f[2]])
    max_depth = max([f[4] for f in fields])

    print(f"Total fields: {total_fields}")
    print(f"Nested fields: {nested_fields} ({nested_fields/total_fields*100:.1f}%)")
    print(f"Dictionary fields: {dict_fields}")
    print(f"List/Array fields: {list_fields}")
    print(f"Maximum nesting depth: {max_depth}")

if __name__ == "__main__":
    main()