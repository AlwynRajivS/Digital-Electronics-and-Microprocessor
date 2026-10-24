"""
Synchronous Counter Design Assistant - Automated Verification Test Suite
EC2201 Unit III: Synchronous Sequential Circuits
Includes 10 Normal Test Cases + 5 Edge/Fault Cases.
"""

import json
import os
import sys
import pandas as pd
from counter_engine import SynchronousCounterAssistant

TEST_CASES = [
    # 10 Normal Test Cases
    {
        'id': 'TC_NORM_01',
        'type': 'normal',
        'name': '3-Bit Mod-8 Binary Up Counter (Handwritten Case 1)',
        'sequence': [0, 1, 2, 3, 4, 5, 6, 7],
        'ff_type': 'JK',
        'expected_self_starting': True,
        'description': 'Standard 3-bit binary up counter with JK flip-flops from lecture notes.'
    },
    {
        'id': 'TC_NORM_02',
        'type': 'normal',
        'name': '3-Bit Mod-8 Down Counter (Handwritten Case 2)',
        'sequence': [0, 7, 6, 5, 4, 3, 2, 1],
        'ff_type': 'SR',
        'expected_self_starting': True,
        'description': 'Standard 3-bit binary down counter with SR flip-flops from lecture notes.'
    },
    {
        'id': 'TC_NORM_03',
        'type': 'normal',
        'name': '4-Bit Mod-10 BCD Decade Counter',
        'sequence': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        'ff_type': 'T',
        'expected_self_starting': True,
        'description': 'Decade counter (0 to 9) with T flip-flops, 6 unused states (10-15).'
    },
    {
        'id': 'TC_NORM_04',
        'type': 'normal',
        'name': '3-Bit Mod-6 Up Counter',
        'sequence': [0, 1, 2, 3, 4, 5],
        'ff_type': 'D',
        'expected_self_starting': True,
        'description': 'Modulo-6 counter with D flip-flops, states 6 and 7 unused.'
    },
    {
        'id': 'TC_NORM_05',
        'type': 'normal',
        'name': '2-Bit Mod-4 Up Counter',
        'sequence': [0, 1, 2, 3],
        'ff_type': 'JK',
        'expected_self_starting': True,
        'description': 'Minimal 2-bit counter with 4 states, no unused states.'
    },
    {
        'id': 'TC_NORM_06',
        'type': 'normal',
        'name': '4-Bit Mod-16 Full Binary Counter',
        'sequence': list(range(16)),
        'ff_type': 'T',
        'expected_self_starting': True,
        'description': 'Full 4-bit synchronous binary counter using toggle flip-flops.'
    },
    {
        'id': 'TC_NORM_07',
        'type': 'normal',
        'name': '3-Bit Gray Code Counter',
        'sequence': [0, 1, 3, 2, 6, 7, 5, 4],
        'ff_type': 'D',
        'expected_self_starting': True,
        'description': 'Unit-distance code counter where only 1 bit flips per transition.'
    },
    {
        'id': 'TC_NORM_08',
        'type': 'normal',
        'name': '3-Bit Ring Counter Sequence',
        'sequence': [1, 2, 4],
        'ff_type': 'D',
        'expected_self_starting': False,
        'description': 'Circulating single 1 (001 -> 010 -> 100), 5 unused states.'
    },
    {
        'id': 'TC_NORM_09',
        'type': 'normal',
        'name': '3-Bit Johnson (Twisted Ring) Counter',
        'sequence': [0, 1, 3, 7, 6, 4],
        'ff_type': 'JK',
        'expected_self_starting': True,
        'description': '6-state Johnson counter with 2 unused states (2, 5).'
    },
    {
        'id': 'TC_NORM_10',
        'type': 'normal',
        'name': '3-Bit Prime Number Sequence Counter',
        'sequence': [2, 3, 5, 7],
        'ff_type': 'JK',
        'expected_self_starting': True,
        'description': 'Non-linear arbitrary sequence counter (2 -> 3 -> 5 -> 7).'
    },

    # 5 Edge / Fault Cases
    {
        'id': 'TC_EDGE_01',
        'type': 'edge',
        'name': 'Mod-5 Counter with Lockout Trap Analysis',
        'sequence': [0, 1, 2, 3, 4],
        'ff_type': 'JK',
        'expected_self_starting': None,
        'description': 'Truncated non-power-of-2 counter testing unused states (5, 6, 7) for deadlock.'
    },
    {
        'id': 'TC_EDGE_02',
        'type': 'edge',
        'name': 'Single-Bit Strobe / 2-State Oscillating Loop',
        'sequence': [0, 3],
        'ff_type': 'D',
        'expected_self_starting': None,
        'description': 'Alternates between 00 and 11, testing states 01 and 10 behavior.'
    },
    {
        'id': 'TC_EDGE_03',
        'type': 'edge',
        'name': 'Non-Zero Starting Offset Counter (3 -> 4 -> 5 -> 6)',
        'sequence': [3, 4, 5, 6],
        'ff_type': 'T',
        'expected_self_starting': None,
        'description': 'Counter sequence does not include state 0, testing all-zero initial power-up recovery.'
    },
    {
        'id': 'TC_EDGE_04',
        'type': 'edge',
        'name': '3-Bit Mod-7 Truncated Counter (0 to 6)',
        'sequence': [0, 1, 2, 3, 4, 5, 6],
        'ff_type': 'JK',
        'expected_self_starting': None,
        'description': 'Single unused state 7 (111) test for immediate cycle return.'
    },
    {
        'id': 'TC_EDGE_05',
        'type': 'edge',
        'name': 'Arbitrary Leap Counter (0 -> 4 -> 2 -> 6)',
        'sequence': [0, 4, 2, 6],
        'ff_type': 'D',
        'expected_self_starting': None,
        'description': 'Even-number sub-cycle with 4 odd unused states (1, 3, 5, 7).'
    }
]

def run_all_tests():
    print("=" * 80)
    print("EC2201 SYNCHRONOUS COUNTER DESIGN ASSISTANT - TEST SUITE")
    print(f"Total Test Cases: {len(TEST_CASES)} (10 Normal + 5 Edge/Fault)")
    print("=" * 80)

    summary_rows = []
    all_passed = True

    for idx, tc in enumerate(TEST_CASES, 1):
        tc_id = tc['id']
        name = tc['name']
        seq = tc['sequence']
        ff = tc['ff_type']

        try:
            assistant = SynchronousCounterAssistant(sequence=seq, ff_type=ff)
            design = assistant.generate_full_design()
            equations = design['step7_kmaps_and_equations']['equations']
            lockout = design['unused_state_analysis']
            metrics = design['ai_circuit_metrics']

            # Verify cycle reproducibility in simulation
            sim = assistant.simulate_clock_cycles(num_cycles=len(seq) * 2, initial_state=seq[0])
            sim_states = [s['state'] for s in sim]
            
            # Check cycle recurrence
            cycle_ok = False
            for offset in range(1, len(seq) + 1):
                if sim_states[offset:offset + len(seq)] == seq:
                    cycle_ok = True
                    break

            is_self_starting = lockout['is_self_starting']
            unused_count = lockout['unused_count']

            status = "PASS" if cycle_ok else "FAIL"
            if not cycle_ok:
                all_passed = False

            summary_rows.append({
                'Test ID': tc_id,
                'Type': tc['type'].upper(),
                'Name': name,
                'FF Type': ff,
                'States': len(seq),
                'Unused': unused_count,
                'Self-Starting': 'YES' if is_self_starting else 'NO (Lockout)',
                'Gates': metrics['total_combinational_gates'],
                'tpd (ns)': metrics['propagation_delay_ns'],
                'Status': status
            })

            print(f"[{status}] {tc_id} ({tc['type'].upper()}): {name}")
            print(f"       FF: {ff} | Seq: {seq} | Unused: {unused_count} | Self-Start: {is_self_starting}")
            print(f"       Equations: {', '.join([f'{k}={v['sop']}' for k, v in equations.items()])}")
            print("-" * 80)

        except Exception as e:
            all_passed = False
            print(f"[ERROR] {tc_id}: {str(e)}")
            summary_rows.append({
                'Test ID': tc_id,
                'Type': tc['type'].upper(),
                'Name': name,
                'FF Type': ff,
                'States': len(seq),
                'Unused': '-',
                'Self-Starting': 'ERROR',
                'Gates': '-',
                'tpd (ns)': '-',
                'Status': 'ERROR'
            })

    df = pd.DataFrame(summary_rows)
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/test_results_summary.csv', index=False)
    
    # Also save raw json
    with open('data/test_cases.json', 'w') as f:
        json.dump(TEST_CASES, f, indent=2)

    print("\n" + "=" * 80)
    print(df.to_string(index=False))
    print("=" * 80)
    print(f"Overall Verification Result: {'ALL TESTS VERIFIED SUCCESSFULLY' if all_passed else 'SOME TESTS FAILED'}")
    print("Summary saved to: data/test_results_summary.csv")
    print("=" * 80)

    return all_passed

if __name__ == '__main__':
    run_all_tests()
