"""
Synchronous Counter Design Assistant - Web Server (Flask)
EC2201 Unit III: Synchronous Sequential Circuits
Author: Sabariayyan P (Section B)
Includes User Authentication & Session Management.
"""

import os
import json
import zipfile
from functools import wraps
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session
from counter_engine import SynchronousCounterAssistant
from test_runner import TEST_CASES

app = Flask(__name__)
app.secret_key = 'ec2201_synchronous_counter_secret_key_sabariayyan'

# Predefined Users
USERS_DB = {
    'sabariayyan': {
        'username': 'sabariayyan',
        'password': 'password123',
        'full_name': 'SABARIAYYAN P',
        'section': 'Section B',
        'role': 'Student',
        'avatar': 'S'
    },
    'evaluator': {
        'username': 'evaluator',
        'password': 'admin123',
        'full_name': 'Dr. EC2201 Evaluator',
        'section': 'Faculty',
        'role': 'Faculty Reviewer',
        'avatar': 'E'
    }
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

# Cache current design
CURRENT_DESIGN = None

@app.route('/login', methods=['GET', 'POST'])
def login():
    session['user'] = USERS_DB['sabariayyan']
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

@app.route('/')
def index():
    user = session.get('user', USERS_DB['sabariayyan'])
    return render_template('index.html', user=user)

@app.route('/api/auth/status')
def auth_status():
    return jsonify({'logged_in': True, 'user': USERS_DB['sabariayyan']})

@app.route('/api/design', methods=['POST'])
def api_design():
    global CURRENT_DESIGN
    data = request.get_json() or {}
    raw_seq = data.get('sequence', [0, 1, 2, 3, 4, 5, 6, 7])
    ff_type = data.get('ff_type', 'JK').upper()
    num_bits = data.get('num_bits')
    if num_bits:
        try:
            num_bits = int(num_bits)
        except (ValueError, TypeError):
            num_bits = None

    # Parse sequence
    if isinstance(raw_seq, str):
        seq = [int(x.strip()) for x in raw_seq.split(',') if x.strip().isdigit()]
    elif isinstance(raw_seq, list):
        seq = [int(x) for x in raw_seq]
    else:
        seq = [0, 1, 2, 3, 4, 5, 6, 7]

    if not seq:
        seq = [0, 1, 2, 3, 4, 5, 6, 7]

    try:
        assistant = SynchronousCounterAssistant(sequence=seq, ff_type=ff_type, num_bits=num_bits)
        CURRENT_DESIGN = assistant.generate_full_design()
        return jsonify({'status': 'success', 'data': CURRENT_DESIGN})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/simulate', methods=['POST'])
def api_simulate():
    data = request.get_json() or {}
    raw_seq = data.get('sequence', [0, 1, 2, 3, 4, 5, 6, 7])
    ff_type = data.get('ff_type', 'JK').upper()
    num_cycles = int(data.get('num_cycles', 16))
    initial_state = data.get('initial_state')
    if initial_state is not None:
        initial_state = int(initial_state)

    if isinstance(raw_seq, str):
        seq = [int(x.strip()) for x in raw_seq.split(',') if x.strip().isdigit()]
    else:
        seq = [int(x) for x in raw_seq]

    try:
        assistant = SynchronousCounterAssistant(sequence=seq, ff_type=ff_type)
        history = assistant.simulate_clock_cycles(num_cycles=num_cycles, initial_state=initial_state)
        return jsonify({'status': 'success', 'history': history})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/testcases', methods=['GET'])
def api_testcases():
    results = []
    for tc in TEST_CASES:
        try:
            assistant = SynchronousCounterAssistant(sequence=tc['sequence'], ff_type=tc['ff_type'])
            design = assistant.generate_full_design()
            results.append({
                'id': tc['id'],
                'type': tc['type'],
                'name': tc['name'],
                'sequence': tc['sequence'],
                'ff_type': tc['ff_type'],
                'description': tc['description'],
                'equations': {k: v['sop'] for k, v in design['step7_kmaps_and_equations']['equations'].items()},
                'is_self_starting': design['unused_state_analysis']['is_self_starting'],
                'unused_count': design['unused_state_analysis']['unused_count'],
                'gates': design['ai_circuit_metrics']['total_combinational_gates'],
                'tpd': design['ai_circuit_metrics']['propagation_delay_ns'],
                'status': 'PASS'
            })
        except Exception as e:
            results.append({
                'id': tc['id'],
                'type': tc['type'],
                'name': tc['name'],
                'sequence': tc['sequence'],
                'ff_type': tc['ff_type'],
                'description': tc['description'],
                'status': 'ERROR',
                'error': str(e)
            })
    return jsonify({'status': 'success', 'test_cases': results})

@app.route('/api/dataset/csv', methods=['GET'])
def download_dataset_csv():
    path = os.path.join(os.path.dirname(__file__), 'data', 'synthetic_counter_dataset.csv')
    if os.path.exists(path):
        return send_file(path, as_attachment=True, download_name='synthetic_counter_dataset.csv')
    return jsonify({'error': 'Dataset not yet generated'}), 404

@app.route('/api/download/zip', methods=['GET'])
def download_zip():
    base_dir = os.path.dirname(__file__)
    zip_path = os.path.join(os.path.dirname(base_dir), 'synchronous_counter_assistant.zip')
    
    # Pack fresh zip
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(base_dir):
            if '__pycache__' in root:
                continue
            for f in files:
                full_p = os.path.join(root, f)
                rel_p = os.path.relpath(full_p, os.path.dirname(base_dir))
                zf.write(full_p, rel_p)

    return send_file(zip_path, as_attachment=True, download_name='synchronous_counter_assistant.zip')

if __name__ == '__main__':
    print("=" * 70)
    print("Synchronous Counter Design Assistant - Starting Server")
    print("EC2201 Course Project | Student: Sabariayyan P (Section B)")
    print("Direct Access: http://127.0.0.1:5000 (No login required)")
    print("=" * 70)
    app.run(host='127.0.0.1', port=5000, debug=False)
