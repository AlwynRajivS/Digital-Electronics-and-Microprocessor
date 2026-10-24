"""
Synchronous Counter Design Assistant - Core Digital Logic Engine
EC2201 Unit III: Synchronous Sequential Circuits
Author: Sabariayyan P (Section B)
"""

import math
from itertools import combinations
from typing import List, Dict, Tuple, Any, Optional

# --- Flip-Flop Excitation Models ---
# Mapping: (Qn, Qn_plus_1) -> dict of input values ('0', '1', 'X')
FF_EXCITATION = {
    'JK': {
        (0, 0): {'J': '0', 'K': 'X'},
        (0, 1): {'J': '1', 'K': 'X'},
        (1, 0): {'J': 'X', 'K': '1'},
        (1, 1): {'J': 'X', 'K': '0'}
    },
    'SR': {
        (0, 0): {'S': '0', 'R': 'X'},
        (0, 1): {'S': '1', 'R': '0'},
        (1, 0): {'S': '0', 'R': '1'},
        (1, 1): {'S': 'X', 'R': '0'}
    },
    'D': {
        (0, 0): {'D': '0'},
        (0, 1): {'D': '1'},
        (1, 0): {'D': '0'},
        (1, 1): {'D': '1'}
    },
    'T': {
        (0, 0): {'T': '0'},
        (0, 1): {'T': '1'},
        (1, 0): {'T': '1'},
        (1, 1): {'T': '0'}
    }
}

# Next state characteristic functions for simulation & lockout analysis
def eval_next_state_bit(ff_type: str, q_curr: int, inputs: Dict[str, int]) -> int:
    """Calculates Q(t+1) given Q(t) and resolved binary inputs (0 or 1)."""
    if ff_type == 'JK':
        j = inputs.get('J', 0)
        k = inputs.get('K', 0)
        # Q+ = J*Q' + K'*Q
        return (j and (not q_curr)) or ((not k) and q_curr)
    elif ff_type == 'SR':
        s = inputs.get('S', 0)
        r = inputs.get('R', 0)
        # Q+ = S + R'*Q (assuming S and R are not both 1)
        if s and r:
            return 0  # Invalid/forbidden condition in hardware, defaults to 0
        return s or ((not r) and q_curr)
    elif ff_type == 'D':
        return inputs.get('D', 0)
    elif ff_type == 'T':
        t = inputs.get('T', 0)
        return (t ^ q_curr)
    return q_curr


# --- Helper Bit Functions ---
def int_to_bin_list(val: int, num_bits: int) -> List[int]:
    """Converts integer to binary list [MSB, ..., LSB]."""
    return [(val >> (num_bits - 1 - i)) & 1 for i in range(num_bits)]

def bin_list_to_int(bits: List[int]) -> int:
    """Converts binary list [MSB, ..., LSB] to integer."""
    val = 0
    for b in bits:
        val = (val << 1) | (1 if b else 0)
    return val

def get_variable_names(num_bits: int) -> List[str]:
    """Returns variable labels ordered from MSB to LSB matching the student's lecture notebook convention
    where QA is MSB (bit N-1), QB is bit N-2, QC is bit N-3, etc.
    e.g. for 3 bits: ['QA', 'QB', 'QC'].
    e.g. for 4 bits: ['QA', 'QB', 'QC', 'QD'].
    """
    letters = ['A', 'B', 'C', 'D', 'E']
    return [f'Q{letters[i]}' for i in range(min(num_bits, len(letters)))]


# --- Quine-McCluskey Boolean Minimizer & K-Map Grouping ---
class QuineMcCluskey:
    """Quine-McCluskey algorithm for minimal Sum of Products (SOP)."""
    def __init__(self, num_vars: int):
        self.num_vars = num_vars

    def count_ones(self, term: str) -> int:
        return term.count('1')

    def combine_terms(self, term1: str, term2: str) -> Optional[str]:
        diff_count = 0
        diff_idx = -1
        for i in range(self.num_vars):
            if term1[i] != term2[i]:
                diff_count += 1
                diff_idx = i
        if diff_count == 1:
            res = list(term1)
            res[diff_idx] = '-'
            return "".join(res)
        return None

    def get_implicant_minterms(self, implicant: str) -> List[int]:
        """Expands implicant string with '-' into covering minterm integers."""
        dash_indices = [i for i, ch in enumerate(implicant) if ch == '-']
        n_dashes = len(dash_indices)
        minterms = []
        for p in range(1 << n_dashes):
            t = list(implicant)
            for di, idx in enumerate(dash_indices):
                t[idx] = '1' if (p & (1 << (n_dashes - 1 - di))) else '0'
            minterms.append(int("".join(t), 2))
        return sorted(minterms)

    def solve(self, minterms: List[int], dont_cares: List[int]) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Returns:
            (terms_str_list, groups_metadata)
        """
        if not minterms:
            return (["0"], [])
        
        all_terms = sorted(list(set(minterms + dont_cares)))
        if len(all_terms) == (1 << self.num_vars) and len(minterms) > 0:
            # Check if all possible minterms are covered
            # If all are 1 or X and minterms span completely
            if set(minterms + dont_cares) == set(range(1 << self.num_vars)):
                return (["1"], [{'implicant': '-' * self.num_vars, 'minterms': list(range(1 << self.num_vars)), 'term_str': '1'}])

        # Convert to binary strings
        fmt = f"0{self.num_vars}b"
        current_groups: Dict[int, Dict[str, bool]] = {}
        for m in all_terms:
            b_str = format(m, fmt)
            ones = self.count_ones(b_str)
            current_groups.setdefault(ones, {})[b_str] = False

        prime_implicants = set()

        while current_groups:
            next_groups: Dict[int, Dict[str, bool]] = {}
            max_ones = max(current_groups.keys()) if current_groups else 0
            
            for ones in sorted(current_groups.keys()):
                if ones + 1 not in current_groups:
                    continue
                for t1 in current_groups[ones]:
                    for t2 in current_groups[ones + 1]:
                        combined = self.combine_terms(t1, t2)
                        if combined:
                            current_groups[ones][t1] = True
                            current_groups[ones + 1][t2] = True
                            n_ones = combined.replace('-', '').count('1')
                            next_groups.setdefault(n_ones, {})[combined] = False

            # Collect uncombined as prime implicants
            for ones in current_groups:
                for t, combined in current_groups[ones].items():
                    if not combined:
                        prime_implicants.add(t)

            current_groups = next_groups

        # Prime implicant chart
        chart: Dict[int, List[str]] = {m: [] for m in minterms}
        pi_coverage: Dict[str, List[int]] = {}
        for pi in prime_implicants:
            covered = [m for m in self.get_implicant_minterms(pi) if m in chart]
            pi_coverage[pi] = covered
            for m in covered:
                chart[m].append(pi)

        # Find essential prime implicants
        selected_pis = set()
        covered_minterms = set()

        for m, pis in chart.items():
            if len(pis) == 1:
                selected_pis.add(pis[0])
                covered_minterms.update(pi_coverage[pis[0]])

        # Greedy set cover for remaining
        uncovered = set(minterms) - covered_minterms
        remaining_pis = list(prime_implicants - selected_pis)
        
        while uncovered and remaining_pis:
            # Pick PI covering the most uncovered minterms
            remaining_pis.sort(key=lambda p: len(set(pi_coverage[p]) & uncovered), reverse=True)
            best_pi = remaining_pis[0]
            gain = len(set(pi_coverage[best_pi]) & uncovered)
            if gain == 0:
                break
            selected_pis.add(best_pi)
            uncovered -= set(pi_coverage[best_pi])
            remaining_pis.remove(best_pi)

        if not selected_pis:
            return (["0"], [])

        # Build human-readable terms
        var_names = get_variable_names(self.num_vars)
        result_terms = []
        groups_meta = []
        
        for pi in sorted(selected_pis):
            term_parts = []
            for i, ch in enumerate(pi):
                if ch == '1':
                    term_parts.append(var_names[i])
                elif ch == '0':
                    term_parts.append(f"{var_names[i]}'")
            
            term_parts.sort(key=lambda x: x[1])
            term_str = "".join(term_parts) if term_parts else "1"
            result_terms.append(term_str)
            groups_meta.append({
                'implicant': pi,
                'minterms': self.get_implicant_minterms(pi),
                'term_str': term_str
            })

        return (result_terms, groups_meta)


def evaluate_term_on_state(term_str: str, state_val: int, num_bits: int) -> int:
    """Evaluates Boolean term string e.g. 'QBQC' or 'QA'QB' or '1' or '0' for a given state integer."""
    if term_str == '1':
        return 1
    if term_str == '0':
        return 0
    
    var_names = get_variable_names(num_bits)
    bits = int_to_bin_list(state_val, num_bits)
    val_map = {var_names[i]: bits[i] for i in range(num_bits)}

    # Parse term components
    i = 0
    while i < len(term_str):
        if term_str[i:i+2] in val_map:
            var = term_str[i:i+2]
            i += 2
            inverted = False
            if i < len(term_str) and term_str[i] == "'":
                inverted = True
                i += 1
            actual = 1 - val_map[var] if inverted else val_map[var]
            if actual == 0:
                return 0
        else:
            i += 1
    return 1

def evaluate_sop_expression(sop_terms: List[str], state_val: int, num_bits: int) -> int:
    """Evaluates full SOP expression (OR of product terms) on state."""
    if not sop_terms or sop_terms == ["0"]:
        return 0
    if "1" in sop_terms:
        return 1
    for term in sop_terms:
        if evaluate_term_on_state(term, state_val, num_bits) == 1:
            return 1
    return 0


# --- K-Map Visual Data Generator ---
def generate_kmap_structure(num_vars: int, minterms: List[int], dont_cares: List[int], groups_meta: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generates structured K-Map representation with Gray code ordering,
    values ('0', '1', 'X'), and visual grouping coordinates.
    """
    var_names = get_variable_names(num_vars)
    minterm_set = set(minterms)
    dc_set = set(dont_cares)

    if num_vars == 2:
        # QA (rows: 0, 1), QB (cols: 0, 1)
        row_labels = ['0', '1']
        col_labels = ['0', '1']
        row_var = var_names[0]
        col_var = var_names[1]
        grid = []
        for r_idx, r in enumerate([0, 1]):
            row_data = []
            for c_idx, c in enumerate([0, 1]):
                m = (r << 1) | c
                val = '1' if m in minterm_set else ('X' if m in dc_set else '0')
                row_data.append({'row': r_idx, 'col': c_idx, 'minterm': m, 'val': val})
            grid.append(row_data)

        return {
            'num_vars': 2,
            'row_vars': row_var,
            'col_vars': col_var,
            'row_headers': row_labels,
            'col_headers': col_labels,
            'grid': grid,
            'groups': groups_meta
        }

    elif num_vars == 3:
        # QA (rows: 0, 1), QB QC (cols: 00, 01, 11, 10)
        row_labels = ['0', '1']
        col_labels = ['00', '01', '11', '10']
        col_values = [(0, 0), (0, 1), (1, 1), (1, 0)]
        row_var = var_names[0]
        col_var = f"{var_names[1]} {var_names[2]}"
        
        grid = []
        for r in range(2):
            row_data = []
            for c_idx, (b1, b2) in enumerate(col_values):
                m = (r << 2) | (b1 << 1) | b2
                val = '1' if m in minterm_set else ('X' if m in dc_set else '0')
                row_data.append({'row': r, 'col': c_idx, 'minterm': m, 'val': val})
            grid.append(row_data)

        return {
            'num_vars': 3,
            'row_vars': row_var,
            'col_vars': col_var,
            'row_headers': row_labels,
            'col_headers': col_labels,
            'grid': grid,
            'groups': groups_meta
        }

    elif num_vars == 4:
        # QA QB (rows: 00, 01, 11, 10), QC QD (cols: 00, 01, 11, 10)
        row_values = [(0, 0), (0, 1), (1, 1), (1, 0)]
        col_values = [(0, 0), (0, 1), (1, 1), (1, 0)]
        headers = ['00', '01', '11', '10']
        row_var = f"{var_names[0]} {var_names[1]}"
        col_var = f"{var_names[2]} {var_names[3]}"

        grid = []
        for r_idx, (a, b) in enumerate(row_values):
            row_data = []
            for c_idx, (c, d) in enumerate(col_values):
                m = (a << 3) | (b << 2) | (c << 1) | d
                val = '1' if m in minterm_set else ('X' if m in dc_set else '0')
                row_data.append({'row': r_idx, 'col': c_idx, 'minterm': m, 'val': val})
            grid.append(row_data)

        return {
            'num_vars': 4,
            'row_vars': row_var,
            'col_vars': col_var,
            'row_headers': headers,
            'col_headers': headers,
            'grid': grid,
            'groups': groups_meta
        }

    return {}


# --- Main Counter Synthesis Engine ---
class SynchronousCounterAssistant:
    """
    Complete 8-step Synchronous Counter Synthesis, Verification & Simulation.
    """
    def __init__(self, sequence: List[int], ff_type: str = 'JK', num_bits: Optional[int] = None):
        self.sequence = sequence
        self.ff_type = ff_type.upper()
        if self.ff_type not in FF_EXCITATION:
            raise ValueError(f"Unsupported Flip-Flop: {ff_type}. Choose from JK, SR, D, T.")

        max_val = max(sequence) if sequence else 0
        min_bits = max(2, math.ceil(math.log2(max_val + 1))) if max_val > 0 else 2
        self.num_bits = max(min_bits, num_bits) if num_bits else min_bits
        self.total_states = 1 << self.num_bits
        self.var_names = get_variable_names(self.num_bits)
        self.qm = QuineMcCluskey(self.num_bits)

    def generate_full_design(self) -> Dict[str, Any]:
        """Runs the entire 8-step pipeline and returns complete design artifacts."""
        # Step 1: Problem Definition
        problem_def = {
            'counter_name': f"{self.num_bits}-Bit Mod-{len(self.sequence)} Synchronous Counter ({self.ff_type} FF)",
            'sequence': self.sequence,
            'ff_type': self.ff_type,
            'num_bits': self.num_bits,
            'total_possible_states': self.total_states,
            'used_states': len(self.sequence),
            'unused_states_count': self.total_states - len(self.sequence),
            'variables': self.var_names
        }

        # Step 2: State Transitions
        transitions = []
        seq_len = len(self.sequence)
        for i in range(seq_len):
            ps = self.sequence[i]
            ns = self.sequence[(i + 1) % seq_len]
            transitions.append({'from': ps, 'to': ns})

        # Step 3 & 4: Present State & Next State Table with State Assignment
        ps_ns_table = []
        state_map = {self.sequence[i]: self.sequence[(i + 1) % seq_len] for i in range(seq_len)}
        used_set = set(self.sequence)

        for s in range(self.total_states):
            is_used = s in used_set
            ns = state_map[s] if is_used else None
            ps_bits = int_to_bin_list(s, self.num_bits)
            ns_bits = int_to_bin_list(ns, self.num_bits) if ns is not None else [None] * self.num_bits

            ps_ns_table.append({
                'decimal_ps': s,
                'ps_bits': ps_bits,
                'ps_bin': "".join(map(str, ps_bits)),
                'decimal_ns': ns if is_used else 'X (Unused)',
                'ns_bits': ns_bits,
                'ns_bin': "".join(map(str, ns_bits)) if is_used else '---',
                'is_used': is_used
            })

        # Step 5: Excitation Table Reference
        ff_ref = []
        for (qn, qnext), inputs in FF_EXCITATION[self.ff_type].items():
            ff_ref.append({
                'Qn': qn,
                'Qn_plus_1': qnext,
                'inputs': inputs
            })

        # Step 6: Counter Excitation Table & Minterm / Don't Care extraction
        # Flip-flop inputs ordered naturally (Stage A, Stage B, Stage C, Stage D)
        # e.g. for JK: JA, KA, JB, KB, JC, KC
        natural_letters = sorted([v[1] for v in self.var_names])
        ff_input_names = []
        if self.ff_type == 'JK':
            for letter in natural_letters:
                ff_input_names.extend([f"J{letter}", f"K{letter}"])
        elif self.ff_type == 'SR':
            for letter in natural_letters:
                ff_input_names.extend([f"S{letter}", f"R{letter}"])
        elif self.ff_type in ('D', 'T'):
            for letter in natural_letters:
                ff_input_names.append(f"{self.ff_type}{letter}")

        counter_excitation_table = []
        # Store minterms and dont cares for each input
        minterms_dict: Dict[str, List[int]] = {inp: [] for inp in ff_input_names}
        dontcares_dict: Dict[str, List[int]] = {inp: [] for inp in ff_input_names}

        for row in ps_ns_table:
            s = row['decimal_ps']
            is_used = row['is_used']
            row_inputs = {}

            # Map bit variables for clean column lookup
            ps_bits = row['ps_bits']
            ns_bits = row['ns_bits']
            ps_bits_dict = {self.var_names[i]: ps_bits[i] for i in range(self.num_bits)}
            ns_bits_dict = {self.var_names[i]: (ns_bits[i] if is_used else None) for i in range(self.num_bits)}

            if is_used:
                for bit_idx in range(self.num_bits):
                    qn = ps_bits[bit_idx]
                    qn1 = ns_bits[bit_idx]
                    letter = self.var_names[bit_idx][1]
                    ff_in = FF_EXCITATION[self.ff_type][(qn, qn1)]
                    
                    for k, val in ff_in.items():
                        inp_label = f"{k}{letter}"
                        row_inputs[inp_label] = val
                        if val == '1':
                            minterms_dict[inp_label].append(s)
                        elif val == 'X':
                            dontcares_dict[inp_label].append(s)
            else:
                # Unused state: all flip flop inputs are don't care initially
                for inp_label in ff_input_names:
                    row_inputs[inp_label] = 'X'
                    dontcares_dict[inp_label].append(s)

            counter_excitation_table.append({
                'state': s,
                'ps_bin': row['ps_bin'],
                'ns_bin': row['ns_bin'],
                'ps_bits': ps_bits,
                'ns_bits': ns_bits,
                'ps_bits_dict': ps_bits_dict,
                'ns_bits_dict': ns_bits_dict,
                'is_used': is_used,
                'inputs': row_inputs
            })

        # Step 7: K-Map Simplification & Derived Boolean Equations
        kmap_results = {}
        equations = {}
        
        for inp in ff_input_names:
            m_list = sorted(minterms_dict[inp])
            d_list = sorted(dontcares_dict[inp])
            terms, groups_meta = self.qm.solve(m_list, d_list)
            
            # Format SOP
            if terms == ["1"]:
                sop_expr = "1"
            elif terms == ["0"]:
                sop_expr = "0"
            else:
                sop_expr = " + ".join(terms)

            equations[inp] = {
                'sop': sop_expr,
                'terms': terms,
                'minterms': m_list,
                'dont_cares': d_list
            }

            kmap_results[inp] = generate_kmap_structure(self.num_bits, m_list, d_list, groups_meta)

        # Step 8: Unused State & Lockout / Self-Recovery Verification
        lockout_report = self.verify_lockout_and_self_recovery(equations)

        # Step 9: Logic Circuit Gate Synthesis & Netlist
        circuit_netlist = self.generate_circuit_netlist(equations)

        # Step 10: AI Layer & Circuit Metrics
        metrics = self.calculate_circuit_metrics(equations, circuit_netlist, lockout_report)

        return {
            'step1_problem': problem_def,
            'step2_state_diagram': {
                'nodes': self.sequence,
                'transitions': transitions,
                'all_states': list(range(self.total_states))
            },
            'step3_present_next_table': ps_ns_table,
            'step4_state_assignment': {
                'num_bits': self.num_bits,
                'encoding': 'Standard Binary',
                'variables': self.var_names
            },
            'step5_ff_excitation_ref': {
                'ff_type': self.ff_type,
                'table': ff_ref
            },
            'step6_excitation_table': {
                'input_names': ff_input_names,
                'rows': counter_excitation_table,
                'minterms': minterms_dict,
                'dont_cares': dontcares_dict
            },
            'step7_kmaps_and_equations': {
                'equations': equations,
                'kmaps': kmap_results
            },
            'step8_circuit_netlist': circuit_netlist,
            'unused_state_analysis': lockout_report,
            'ai_circuit_metrics': metrics
        }

    def verify_lockout_and_self_recovery(self, equations: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates the actual hardware transition for each unused state using synthesized logic.
        Determines whether the counter is self-starting or prone to lockout deadlock.
        """
        used_set = set(self.sequence)
        unused_states = [s for s in range(self.total_states) if s not in used_set]

        # Calculate actual next state for EVERY state 0 .. 2^N - 1
        hardware_next_states = {}
        for s in range(self.total_states):
            curr_bits = int_to_bin_list(s, self.num_bits)
            next_bits = []

            for bit_idx in range(self.num_bits):
                letter = self.var_names[bit_idx][1]
                q_curr = curr_bits[bit_idx]

                # Evaluate inputs for this bit
                bit_inputs = {}
                if self.ff_type == 'JK':
                    j_val = evaluate_sop_expression(equations[f"J{letter}"]['terms'], s, self.num_bits)
                    k_val = evaluate_sop_expression(equations[f"K{letter}"]['terms'], s, self.num_bits)
                    bit_inputs = {'J': j_val, 'K': k_val}
                elif self.ff_type == 'SR':
                    s_val = evaluate_sop_expression(equations[f"S{letter}"]['terms'], s, self.num_bits)
                    r_val = evaluate_sop_expression(equations[f"R{letter}"]['terms'], s, self.num_bits)
                    bit_inputs = {'S': s_val, 'R': r_val}
                elif self.ff_type == 'D':
                    d_val = evaluate_sop_expression(equations[f"D{letter}"]['terms'], s, self.num_bits)
                    bit_inputs = {'D': d_val}
                elif self.ff_type == 'T':
                    t_val = evaluate_sop_expression(equations[f"T{letter}"]['terms'], s, self.num_bits)
                    bit_inputs = {'T': t_val}

                q_next = eval_next_state_bit(self.ff_type, q_curr, bit_inputs)
                next_bits.append(q_next)

            next_s = bin_list_to_int(next_bits)
            hardware_next_states[s] = next_s

        # Trace each unused state
        trace_results = []
        is_self_starting = True
        lockout_states = []

        for u in unused_states:
            path = [u]
            curr = u
            visited = {u: 0}
            recovered = False
            trap_cycle = []

            for step in range(1, self.total_states + 2):
                nxt = hardware_next_states[curr]
                path.append(nxt)
                if nxt in used_set:
                    recovered = True
                    break
                if nxt in visited:
                    # Trapped in an unused cycle or self-loop!
                    loop_start = visited[nxt]
                    trap_cycle = path[loop_start:-1]
                    break
                visited[nxt] = step
                curr = nxt

            if not recovered:
                is_self_starting = False
                lockout_states.append(u)

            trace_results.append({
                'unused_state': u,
                'binary': "".join(map(str, int_to_bin_list(u, self.num_bits))),
                'immediate_next_state': hardware_next_states[u],
                'trace_path': path,
                'enters_valid_cycle': recovered,
                'trap_cycle': trap_cycle if not recovered else None
            })

        return {
            'has_unused_states': len(unused_states) > 0,
            'unused_count': len(unused_states),
            'unused_states': unused_states,
            'is_self_starting': is_self_starting,
            'lockout_states': lockout_states,
            'hardware_next_states': hardware_next_states,
            'trace_details': trace_results,
            'verdict': 'Self-Starting & Self-Clearing Counter' if is_self_starting else 'WARNING: Lockout Trap Detected!'
        }

    def generate_circuit_netlist(self, equations: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generates gate-level netlist and schematic wiring metadata."""
        gates = []
        wire_connections = []
        ff_blocks = []

        ordered_vars = list(self.var_names)
        for bit_idx, var in enumerate(ordered_vars):
            letter = var[1]
            is_msb = (bit_idx == 0)
            is_lsb = (bit_idx == len(ordered_vars) - 1)
            role_label = " (MSB)" if is_msb else (" (LSB)" if is_lsb else "")
            ff_blocks.append({
                'id': f"FF_{letter}",
                'bit': bit_idx,
                'letter': letter,
                'label': f"Flip-Flop {letter}{role_label}",
                'type': self.ff_type,
                'out_q': var,
                'out_q_bar': f"{var}'",
                'clk': 'CLK',
                'is_lsb': is_lsb,
                'is_msb': is_msb
            })

        gate_counter = 1
        for inp_name, eq in equations.items():
            terms = eq['terms']
            if terms == ["1"]:
                wire_connections.append({'from': 'VCC (Logic 1)', 'to': inp_name})
            elif terms == ["0"]:
                wire_connections.append({'from': 'GND (Logic 0)', 'to': inp_name})
            else:
                product_outputs = []
                for term in terms:
                    # Count literals
                    lits = self.parse_literals_from_term(term)
                    if len(lits) == 1:
                        product_outputs.append(lits[0])
                    else:
                        g_id = f"AND_{gate_counter}"
                        gate_counter += 1
                        gates.append({
                            'id': g_id,
                            'type': 'AND',
                            'inputs': lits,
                            'output': f"out_{g_id}"
                        })
                        product_outputs.append(f"out_{g_id}")

                if len(product_outputs) == 1:
                    wire_connections.append({'from': product_outputs[0], 'to': inp_name})
                else:
                    g_id = f"OR_{gate_counter}"
                    gate_counter += 1
                    gates.append({
                        'id': g_id,
                        'type': 'OR',
                        'inputs': product_outputs,
                        'output': f"out_{g_id}"
                    })
                    wire_connections.append({'from': f"out_{g_id}", 'to': inp_name})

        return {
            'flip_flops': ff_blocks,
            'gates': gates,
            'wires': wire_connections,
            'common_clock': 'Synchronous Clock (CLK) distributed to all flip-flops in parallel'
        }

    def parse_literals_from_term(self, term: str) -> List[str]:
        """Extracts inputs e.g. 'QBQC' -> ['QB', 'QC'], or 'QA'QB' -> [\"QA'\", 'QB']."""
        lits = []
        i = 0
        while i < len(term):
            if term[i:i+2] in self.var_names:
                var = term[i:i+2]
                i += 2
                if i < len(term) and term[i] == "'":
                    lits.append(f"{var}'")
                    i += 1
                else:
                    lits.append(var)
            else:
                i += 1
        return lits

    def calculate_circuit_metrics(self, equations: Dict[str, Dict[str, Any]], netlist: Dict[str, Any], lockout: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates digital engineering metrics and AI synthesis insights."""
        num_ff = self.num_bits
        num_and_gates = sum(1 for g in netlist['gates'] if g['type'] == 'AND')
        num_or_gates = sum(1 for g in netlist['gates'] if g['type'] == 'OR')
        
        # Estimate inverter gates needed if inverted outputs are not directly wired from Q' pin
        inverter_count = 0  # In modern ICs, Q_bar is natively available on the flip flop!

        total_gates = num_and_gates + num_or_gates + inverter_count
        # Approximate CMOS transistor count: FF ~ 24T, 2-in AND ~ 6T, 2-in OR ~ 6T
        est_transistors = (num_ff * 24) + (num_and_gates * 6) + (num_or_gates * 6)
        
        # Approximate propagation delay (assuming standard 74HC series: gate ~ 8ns, FF setup/clk-to-Q ~ 14ns)
        gate_levels = 0
        if num_and_gates > 0:
            gate_levels += 1
        if num_or_gates > 0:
            gate_levels += 1
        est_tpd_ns = 14 + (gate_levels * 8)
        max_clock_freq_mhz = round(1000.0 / est_tpd_ns, 1)

        insights = []
        if lockout['is_self_starting']:
            insights.append("✓ Self-Starting: The counter automatically recovers to the main counting cycle from all unused states.")
        else:
            insights.append(f"⚠ Lockout Warning: Counter can get trapped in unused states: {lockout['lockout_states']}. A power-on reset (POR) or modified K-map is recommended.")

        if self.ff_type == 'JK':
            insights.append("• JK Flip-Flops offer maximum 'Don't Care' exploitation, yielding the smallest combinatorial logic gating.")
        elif self.ff_type == 'T':
            insights.append("• T Flip-Flops are optimal for binary counters where bits toggle at harmonic frequencies.")
        elif self.ff_type == 'D':
            insights.append("• D Flip-Flops provide simplest next-state equations (D = Q+) and easiest FPGA/ASIC synthesis.")

        return {
            'flip_flop_count': num_ff,
            'and_gates': num_and_gates,
            'or_gates': num_or_gates,
            'total_combinational_gates': total_gates,
            'estimated_transistors': est_transistors,
            'propagation_delay_ns': est_tpd_ns,
            'max_clock_frequency_mhz': max_clock_freq_mhz,
            'ai_insights': insights
        }

    def simulate_clock_cycles(self, num_cycles: int = 16, initial_state: Optional[int] = None) -> List[Dict[str, Any]]:
        """Simulates sequence of clock pulses and logs transitions."""
        design = self.generate_full_design()
        hw_next = design['unused_state_analysis']['hardware_next_states']
        
        curr = initial_state if initial_state is not None else self.sequence[0]
        history = []

        for cycle in range(num_cycles + 1):
            bits = int_to_bin_list(curr, self.num_bits)
            history.append({
                'cycle': cycle,
                'state': curr,
                'binary': "".join(map(str, bits)),
                'bits': bits,
                'is_used': curr in set(self.sequence)
            })
            curr = hw_next[curr]

        return history
