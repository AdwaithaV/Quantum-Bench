# QuantumBench

QuantumBench is a cross-platform benchmarking and visualization tool for quantum circuit simulators.  
It enables researchers and enterprise developers to compare performance and fidelity of quantum simulations across popular frameworks like Qiskit, PennyLane, and Cirq — all from a simple and interactive web interface.

---

## Features

- Run benchmark tests on quantum circuits across multiple backends  
- Visualize execution time and fidelity comparisons via intuitive graphs  
- Support for uploading custom circuits or choosing from built-in examples  
- Export benchmark results in CSV format  
- Lightweight, modular design for easy extension  

---

```
quantumbench/
├── app/ ← Main application logic (Streamlit or CLI-based)
│ ├── init.py
│ ├── runner.py ← Runs circuits on different simulators
│ ├── visualizer.py ← Handles graphing/plotting results
│ ├── utils.py ← Shared helper functions
├── circuits/ ← Predefined or uploaded circuits
├── tests/ ← Unit tests
├── requirements.txt ← Python dependencies
├── README.md
├── main.py ← Entry point (for CLI or Streamlit)
└── LICENSE
```

## Getting Started

### Prerequisites

- Python 3.9 or above  
- pip package manager  

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/quantum-bench.git
   cd quantum-bench
2.(Optional) Create and activate a virtual environment:
```bash
   python -m venv env
source env/bin/activate   # Linux/macOS
.\env\Scripts\activate    # Windows
```
3.Install required packages:
```bash
pip install -r requirements.txt
```
**Running the App**
Run the Streamlit interface:
```bash
streamlit run run_app.py
```
Open the URL shown in your terminal (usually http://localhost:8501) to use the app.
# Usage

Upload your .qasm file (e.g., a Bell state circuit)

Select the simulator backend (only Qiskit available now)

Click Run Benchmark

View:

Execution time

Fidelity

Output statevector

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



# Contributing
Contributions are welcome! Feel free to open issues or submit pull requests.
Please follow the existing code style and include tests where appropriate.


# Contact
Created by Adwaitha V— feel free to reach out!
GitHub: https://github.com/AdwaithaV
Email: adwaithav063@gmail.com 
## License

This project is licensed under the [MIT License](LICENSE).
