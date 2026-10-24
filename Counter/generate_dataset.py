"""
Generate Reproducible Synthetic Test Dataset for EC2201 Synchronous Counter Design Assistant
Generates comprehensive transitions, state assignments, excitation vectors, and synthesized equations.
"""

import json
import os
import pandas as pd
from counter_engine import SynchronousCounterAssistant, int_to_bin_list
from test_runner import TEST_CASES

def generate_synthetic_dataset():
    os.makedirs('data', exist_ok=True)
    records = []

    for tc in TEST_CASES:
        tc_id = tc['id']
        name = tc['name']
        seq = tc['sequence']
        ff = tc['ff_type']

        assistant = SynchronousCounterAssistant(sequence=seq, ff_type=ff)
        design = assistant.generate_full_design()
        num_bits = design['step1_problem']['num_bits']
        equations = design['step7_kmaps_and_equations']['equations']
        lockout = design['unused_state_analysis']
        metrics = design['ai_circuit_metrics']

        # Flatten transitions and excitation inputs
        for row in design['step6_excitation_table']['rows']:
            state_dec = row['state']
            ps_bin = row['ps_bin']
            ns_bin = row['ns_bin']
            is_used = row['is_used']
            hw_next = lockout['hardware_next_states'][state_dec]
            hw_next_bin = "".join(map(str, int_to_bin_list(hw_next, num_bits)))

            record = {
                'test_case_id': tc_id,
                'counter_name': name,
                'flip_flop_type': ff,
                'bit_width': num_bits,
                'sequence_length': len(seq),
                'state_decimal': state_dec,
                'present_state_bin': ps_bin,
                'specified_next_state_bin': ns_bin,
                'is_in_valid_cycle': is_used,
                'hardware_actual_next_state_dec': hw_next,
                'hardware_actual_next_state_bin': hw_next_bin,
                'is_counter_self_starting': lockout['is_self_starting'],
                'combinational_gate_count': metrics['total_combinational_gates'],
                'propagation_delay_ns': metrics['propagation_delay_ns']
            }

            # Add all excitation inputs
            for inp_label, val in row['inputs'].items():
                record[f"input_{inp_label}"] = val

            records.append(record)

    df = pd.DataFrame(records)
    csv_path = 'data/synthetic_counter_dataset.csv'
    df.to_csv(csv_path, index=False)
    
    json_path = 'data/synthetic_counter_dataset.json'
    df.to_json(json_path, orient='records', indent=2)

    print(f"Generated synthetic dataset: {csv_path} ({len(df)} records)")
    print(f"Generated synthetic JSON: {json_path}")

if __name__ == '__main__':
    generate_synthetic_dataset()
