# QuantumBench

QuantumBench is a cross-platform benchmarking and visualization tool for quantum circuit simulators.  
It enables researchers and enterprise developers to compare performance and fidelity of quantum simulations across popular frameworks like Qiskit, PennyLane, and Cirq — all from a simple and interactive web interface.

---

## Features

- Run benchmark tests on quantum circuits across multiple backends (Qiskit, Cirq, PennyLane)
- **Robust Execution**: Handles large circuits with memory safety checks (>24 qubits protected)
- **Real Hardware Persistence**: Easily fetch and select IBM Quantum devices without losing state
- **Windows Optimized**: Built-in fixes for common PennyLane DLL errors
- Visualize execution time, fidelity, and memory usage

---

## Getting Started

### Prerequisites

- Python 3.9 or above  
- pip package manager  

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/quantum-bench.git
   cd quantum-bench
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv env
   # Windows
   .\env\Scripts\activate
   # Linux/macOS
   source env/bin/activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Running the App

Run the Streamlit interface:
```bash
streamlit run main.py
```
Open the URL shown in your terminal (usually http://localhost:8501) to use the app.

## Usage

1. **Upload or Paste** your QASM code (OpenQASM 2.0 supported).
2. **Select Backends**:
   - **Simulators**: Qiskit Aer, Cirq, PennyLane (Pure Python mode).
   - **Hardware**: Enter your IBM Cloud CRN & API Key -> Click "Fetch" -> Select Devices.
3. Click **RUN BENCHMARK**.
4. View results in the **Master Dashboard**, **Data Table**, and **Memory Matrix**.

### Note on Stability
- **PennyLane**: Uses a custom pure-Python converter to ensure stability on all platforms (bypassing potentially broken plugins).
- **Large Circuits**: Local simulators are capped at 24 qubits to prevent System OOM crashes.
- **Hardware Timeouts**: The app waits 60s for hardware results, then reports "Queued" to avoid freezing. 

 ## Behind the Scenes (Architecture)
# Backend: app/runner.py

Contains logic to:

Parse uploaded QASM code

Transpile it

Simulate using Qiskit's AerSimulator

Return execution time, fidelity, and statevector

# Frontend: main.py
Built using Streamlit

Handles:

File upload

Simulator selection

Displaying results cleanly

Deployment link :https://adwaithav-quantum-bench-main-umerpy.streamlit.app/



# Contributing
Contributions are welcome! Feel free to open issues or submit pull requests.
Please follow the existing code style and include tests where appropriate.


# Contact
Created by Adwaitha V— feel free to reach out!
GitHub: https://github.com/AdwaithaV
Email: adwaithav063@gmail.com 
## License

This project is licensed under the [MIT License](LICENSE).
