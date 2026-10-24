# Synchronous Counter Design Assistant
### EC2201 Unit III: Synchronous Sequential Circuits
**Course Context**: Anna University / Autonomous Syllabus - Sequential Circuits  
**Student**: Sabariayyan P (Section B)  
**Registered Date**: 09 Sept 2026  
**Status**: Completed, Verified & Authenticated  

---

## 🌟 Overview
The **Synchronous Counter Design Assistant** is an educational engineering software and real-time simulation platform built for students and faculty of **EC2201 (Sequential Circuits)**. It automates the complete **8-step synchronous counter design pipeline** directly reflecting lecture notebooks and syllabus requirements, while providing interactive logic analyzers, visual Karnaugh maps, connected IEEE standard schematics, and automated lockout / self-recovery verification.

---

## ⚡ Instant Direct Access (No Login Barrier)

The website opens directly to the design portal with 0 barrier:
- **Instant Launch**: Opening the site immediately takes you to the full design environment.
- **Student Profile**: Automatically presets student identity **SABARIAYYAN P (Section B)** in the top header.
- **Offline & Standalone Ready**: Can be opened via Flask (`python app.py`) or by opening `index.html` directly in any browser or VS Code Live Server.

---

## ⚡ Connected Logic Circuit Schematic (Image 5 Replicated)

In Step 8, the logic circuit is rendered as a **fully connected physical schematic** matching your lecture notes:
- **Flip-Flops ($FF_A, FF_B, FF_C$)**: Displayed in horizontal alignment ($FF_A$ MSB $\to$ $FF_B$ $\to$ $FF_C$ LSB) with input pins ($J, K$ or $S, R$ or $D$ or $T$) on the left, output pins ($Q, \overline{Q}$) on the right, and clock pin at the bottom.
- **IEEE Standard Logic Gates**:
  - **AND Gates**: Rendered with standard IEEE shape (flat back, parallel sides, semi-circular front arc).
  - **OR Gates**: Rendered with curved concave back and pointed front.
- **Direct Wire Routing**:
  - For **3-Bit Mod-8 Up Counter (JK FF)**:
    - Pins $J_C, K_C$ connect together via a vertical jumper and connect straight up to the **$V_{CC}$ (+5V) power rail**!
    - Output $Q_C$ routes out, taps via a solder junction dot, and connects directly into both $J_B$ and $K_B$ pins of $FF_B$!
    - An IEEE standard **AND gate** is positioned overhead between $FF_A$ and $FF_B$:
      - Input 1 receives the $Q_B$ output wire.
      - Input 2 receives the $Q_C$ output wire.
      - Output wire routes directly into both $J_A$ and $K_A$ of $FF_A$!
    - All flip-flop clock pins connect into the common horizontal **Synchronous Clock Rail (CLK)** at the bottom with yellow solder dots.

---

## 🚀 How to Run in VS Code

### Prerequisites
- Python 3.8+ installed.

### Option 1: 1-Click Launch (Windows)
1. Open the project folder in **VS Code**.
2. Double-click `run.bat` or run in terminal:
   ```cmd
   .\run.bat
   ```
   Or in PowerShell:
   ```powershell
   .\run.ps1
   ```
3. Your browser will automatically open at: **`http://127.0.0.1:5000`**
4. Log in with:
   - **Username**: `sabariayyan`
   - **Password**: `password123`

### Option 2: Terminal Launch
1. Open terminal inside the project directory:
   ```bash
   python app.py
   ```
2. Navigate to `http://127.0.0.1:5000` in Google Chrome or Edge.

---

## 🧪 Running Automated Tests
To run all 15 test cases (10 normal + 5 edge) in terminal:
```bash
python test_runner.py
```
Outputs test summary table and logs results to `data/test_results_summary.csv`.

To regenerate the synthetic test dataset:
```bash
python generate_dataset.py
```

---

## 📂 Project Structure
```text
synchronous_counter_assistant/
│
├── app.py                     # Flask web server with authentication & REST API
├── counter_engine.py          # Core Digital Logic & Quine-McCluskey K-map engine
├── test_runner.py             # Automated test suite (15 test cases)
├── generate_dataset.py        # Synthetic test dataset generator
├── requirements.txt           # Python dependencies
├── run.bat                    # 1-click Windows launcher
├── run.ps1                    # 1-click PowerShell launcher
├── README.md                  # User manual and setup guide
├── PROJECT_REPORT.md          # Comprehensive academic engineering report
│
├── templates/
│   ├── login.html             # Project Portal login screen
│   └── index.html             # Main dashboard with connected circuit layout
│
├── static/
│   ├── css/
│   │   └── style.css          # Modern engineering dark stylesheet
│   └── js/
│       └── app.js             # Interactive controller, connected SVG schematic, waveform engine
│
└── data/
    ├── synthetic_counter_dataset.csv  # Reproducible test dataset (128 records)
    ├── synthetic_counter_dataset.json # JSON format dataset
    ├── test_cases.json                # Test suite definitions
    └── test_results_summary.csv       # Verification summary log
```
